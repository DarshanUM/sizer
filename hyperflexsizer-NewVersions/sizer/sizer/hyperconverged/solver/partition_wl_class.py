import json
import logging
from math import ceil

from hyperconverged.exception import HXException
from base_sizer.solver.attrib import BaseConstants
from .node_sizing import HyperConvergedNode
from .attrib import HyperConstants

from .seed_node_parts_calculations import SeedNode
from operator import itemgetter

logger = logging.getLogger(__name__)


class PartitionWl(object):

    def __init__(self, sizer_instance, node_list, wl_list, cluster_type):

        self.node_list = node_list
        self.wl_list = wl_list
        self.cluster_type = cluster_type
        self.sizer_instance = sizer_instance
        self.slot_dict = None
        self.max_mem_limit = 0
        self.max_specint = 0
        self.static_overhead = None

        self.iops_conv_fac = self.sizer_instance.iops_conv_fac
        self.logger_header = self.sizer_instance.logger_header
        self.hypervisor = self.sizer_instance.hypervisor
        self.current_cluster = self.sizer_instance.current_cluster
        self.parts_table = self.sizer_instance.parts_table
        self.get_req = self.sizer_instance.get_req
        self.get_max_cluster_value = self.sizer_instance.get_max_cluster_value
        self.calc_raw_sw_price = self.sizer_instance.calc_raw_sw_price

        self.hc_node_max = 0
        self.comp_node_max = 0
        self.vdi_gpu_exists = False

        if self.sizer_instance.settings_json[HyperConstants.HERCULES_CONF] == HyperConstants.DISABLED:
            self.sizer_instance.hercules = False
        else:
            self.sizer_instance.hercules = any(node.hercules_avail for node in node_list)

        if self.sizer_instance.settings_json[HyperConstants.HX_BOOST_CONF] == HyperConstants.DISABLED:
            self.sizer_instance.hx_boost = False
        else:
            self.sizer_instance.hx_boost = any(node.hx_boost_avail for node in node_list)

        self.dr_exists = any(wl.attrib.get(HyperConstants.REPLICATION_FLAG, False) for wl in wl_list)

        if self.dr_exists:
            self.sizer_instance.hercules = False

    def get_partitioned_list(self):

        if len(self.wl_list) == 2 and self.wl_list[0].attrib['wl_name'] == self.wl_list[1].attrib['wl_name']:

            if self.wl_list[0].attrib['replication_type'] == HyperConstants.NORMAL:

                return [([self.wl_list[0]], [self.wl_list[1]])]

            else:

                return [([self.wl_list[1]], [self.wl_list[0]])]

        elif len(self.wl_list) > 1:

            if self.cluster_type == HyperConstants.VDI and any(wl.attrib.get(HyperConstants.GPU_STATUS, False)
                                                               for wl in self.wl_list):
                self.vdi_gpu_exists = True
                return self.partition_gpu_workloads()

            self.partn_pre_req()
            return self.partition_workloads()

        else:

            return [(self.wl_list,)]

    def partition_gpu_workloads(self):

        def filter_any_gpu_wls():

            if not clusters:
                return

            wl_gpu_dict['any'] = list()

            for index in range(len(clusters)-1, -1, -1):

                if all(getattr(x, 'frame_buff', 0) in any_gpu for x in clusters[index][0]):

                    wl_gpu_dict['any'].extend(clusters[index][0])
                    clusters.pop(index)

        p40_gpu = [3072, 6144, 12288, 24576]
        v100_32_gpu = [32768]
        any_gpu = [0, 512, 1024, 2048, 4096, 8192, 16384]

        '''
        In above list number represent frame buffer. 0 frame buffer represents all workloads with no GPU requirement
        '''

        wl_gpu_dict = {
            'P40': p40_gpu,
            'V100-32': v100_32_gpu,
            'any': any_gpu
        }

        clusters = list()

        for gpu_str, gpu_set in wl_gpu_dict.items():

            wl_gpu_dict[gpu_str] = list(filter(lambda x: getattr(x, 'frame_buff', 0) in gpu_set, self.wl_list))

        if wl_gpu_dict['P40']:

            self.wl_list = wl_gpu_dict['P40']
            self.partn_pre_req()
            self.wl_list = wl_gpu_dict['P40'] + wl_gpu_dict['any']

            clusters.extend(self.partition_workloads())

            filter_any_gpu_wls()

        if wl_gpu_dict['V100-32']:

            self.wl_list = wl_gpu_dict['V100-32']
            self.partn_pre_req()
            self.wl_list = wl_gpu_dict['V100-32'] + wl_gpu_dict['any']

            clusters.extend(self.partition_workloads())

            filter_any_gpu_wls()

        if not clusters or wl_gpu_dict['any']:

            self.wl_list = wl_gpu_dict['any']
            self.partn_pre_req()

            clusters.extend(self.partition_workloads())

        return clusters

    def partn_pre_req(self):

        self.sizer_instance.highest_rf = max(wl.attrib[HyperConstants.REPLICATION_FACTOR] for wl in self.wl_list)
        self.sizer_instance.RF_String = self.sizer_instance.set_RF_String()
        self.sizer_instance.Fault_Tolerance = max(wl.attrib[HyperConstants.FAULT_TOLERANCE] for wl in self.wl_list)

        self.node_data = self.generate_seed_node()

        logger.info("%s Node: %s" % (self.logger_header,
                                     self.node_data[HyperConstants.NODE].attrib[BaseConstants.MODEL]))

        logger.info("%s Node Part: %s" % (self.logger_header,
                                          self.node_data[HyperConstants.NODE].attrib[HyperConstants.SSD_PART]))

        logger.info("%s Node Part: %s" % (self.logger_header,
                                          self.node_data[HyperConstants.NODE].attrib[HyperConstants.HDD_PART]))

        self.clusters = self.create_clusters()

        logger.info("%s Clusters = %s" % (self.logger_header, self.clusters))

        '''
        Initialize workload placement variable in the cluster, then place workloads
        '''

        for cluster in self.clusters:

            # Primary Cluster Workloads
            cluster.append(list())

            # Secondary Cluster Workloads
            cluster.append(list())

    def partition_workloads(self):

        hc_node = self.node_data[HyperConstants.NODE]
        comp_node = self.node_data[HyperConstants.COMPUTE]

        '''
        Separate clustering functionality for replication workloads.
        '''

        if self.dr_exists:

            local_primary = list()
            local_secondary = list()
            remote_primary = list()
            remote_secondary = list()
            any_cluster = list()

            for wl in self.wl_list:

                if wl.attrib['replication_type'] == HyperConstants.ANY_CLUSTER:
                    any_cluster.append(wl)
                elif wl.attrib['replication_type'] == HyperConstants.NORMAL and not wl.attrib['remote']:
                    local_primary.append(wl)
                elif wl.attrib['replication_type'] == HyperConstants.NORMAL and wl.attrib['remote']:
                    local_secondary.append(wl)
                elif wl.attrib['replication_type'] == HyperConstants.REPLICATED and wl.attrib['remote']:
                    remote_primary.append(wl)
                elif wl.attrib['replication_type'] == HyperConstants.REPLICATED and not wl.attrib['remote']:
                    remote_secondary.append(wl)

            if not self.sizer_instance.partition_wl:

                local_secondary_dr_count = sum(wl.num_inst for wl in local_secondary)
                remote_secondary_dr_count = sum(wl.num_inst for wl in remote_secondary)

                if local_secondary_dr_count > 1500 or remote_secondary_dr_count > 1500:
                    msg = "The number of instances in a DR cluster cannot be more than 1500. " \
                          "Can't place into single cluster."
                    raise HXException("DR_CLUSTER_LIMIT |" + msg)

                return [(local_primary + local_secondary + any_cluster, remote_primary + remote_secondary)]

            wl_dict = {
                'local_primary': local_primary,
                'local_secondary': local_secondary,
                'remote_primary': remote_primary,
                'remote_secondary': remote_secondary,
                'any_cluster': any_cluster
            }

            wl_partition_list = self.generate_repl_clusters(hc_node, comp_node, wl_dict, self.clusters)

        else:

            if not self.sizer_instance.partition_wl:
                return [(self.wl_list,)]

            wl_partition_list = self.generate_normal_clusters(hc_node, comp_node, self.clusters)

        return wl_partition_list

    def refresh_nodes_slots(self, subtype):

        self.node_list = [node for node in self.node_list if node.attrib[BaseConstants.SUBTYPE] == subtype]

        self.static_overhead = {cap: max(node.attrib['static_overhead'][self.hypervisor].get(cap, 0)
                                         for node in self.node_list)
                                for cap in [BaseConstants.CPU, BaseConstants.RAM, BaseConstants.HDD]}

        self.slot_dict = self.sizer_instance.get_slots(self.node_list)

    def generate_seed_node(self):

        """
        Generate Seed Node by solving for the optimal parts given the entire workload set.

        Calculate optimal CPU first, generate minimum number of servers from that,
        then derive the other parts to fit the number of servers.

        If the dimension cannot be satisfied in that number of servers, throw out the result
        due to the CPU being too dense.

        Lastly, check that the configurations generated can fit in the node list provided.
        If it cannot be satisfied, throw out the result.

        Pick densest result left over.
        """

        # Creating a set of all remaining subtypes
        subtype_set = {node.attrib['subtype'] for node in self.node_list}

        if self.cluster_type == HyperConstants.ROBO or self.cluster_type == HyperConstants.ROBO_BACKUP_SECONDARY:
            if HyperConstants.AF_ROBO_NODE in subtype_set:
                node_subtype = HyperConstants.AF_ROBO_NODE
            elif HyperConstants.AF_ROBO_TWO_NODE in subtype_set:
                node_subtype = HyperConstants.AF_ROBO_TWO_NODE
            elif HyperConstants.ROBO_TWO_NODE in subtype_set:
                node_subtype = HyperConstants.ROBO_TWO_NODE
            elif HyperConstants.ROBO_240 in subtype_set:
                node_subtype = HyperConstants.ROBO_240
            elif HyperConstants.ROBO_AF_240 in subtype_set:
                node_subtype = HyperConstants.ROBO_AF_240
            else:
                node_subtype = HyperConstants.ROBO_NODE

        elif self.cluster_type == HyperConstants.VEEAM:
            node_subtype = HyperConstants.VEEAM_NODE

        else:

            if len(subtype_set) == 1:

                node_subtype = subtype_set.pop()

            else:
                # priority list is as shown below
                # SFF (3.8TB or 1.2TB) -> NVMe (4TB, 1TB) -> LFF (6TB, 8TB) -> NVMe (8TB) -> LFF (12TB) -> SFF (7.6TB)

                if HyperConstants.ALL_FLASH in subtype_set:
                    node_subtype = HyperConstants.ALL_FLASH
                elif HyperConstants.HYPER in subtype_set:
                    node_subtype = HyperConstants.HYPER
                elif HyperConstants.ALLNVME_NODE in subtype_set:
                    node_subtype = HyperConstants.ALLNVME_NODE
                elif HyperConstants.LFF_NODE in subtype_set:
                    node_subtype = HyperConstants.LFF_NODE
                elif HyperConstants.ALLNVME_NODE_8TB in subtype_set:
                    node_subtype = HyperConstants.ALLNVME_NODE_8TB
                elif HyperConstants.LFF_12TB_NODE in subtype_set:
                    node_subtype = HyperConstants.LFF_12TB_NODE
                elif HyperConstants.ALL_FLASH_7_6TB in subtype_set:
                    node_subtype = HyperConstants.ALL_FLASH_7_6TB
                else:
                    raise Exception("Unknown node subtype found.")

        self.refresh_nodes_slots(node_subtype)
        seed_part_table = self.populate_part_list()

        parts_set = {x: self.solve_optimal_part_seed(x, seed_part_table, node_subtype) for x in HyperConstants.CAP_LIST}

        """
        Iterate all possible cpus and solve their combinations.
        If we find a combination, quit early, as the cpu list is sorted on price.
        """

        for cpu in parts_set[BaseConstants.CPU]:

            config = dict()

            config[BaseConstants.CPU] = cpu

            for cap in [BaseConstants.RAM, BaseConstants.HDD, BaseConstants.SSD, BaseConstants.VRAM]:

                cap_set = parts_set[cap]

                added = False

                parts = seed_part_table[cap]
                parts = self.get_part_combo(cpu[0], parts, self.node_list, cap)
                if not parts:
                    break

                part_set = [part_config for part_config in cap_set if cpu[2] > part_config[2] and
                            part_config[0] in parts]

                if part_set:
                    added = True
                    config[cap] = part_set[0]

                if not added:
                    break

            if added:
                break

        """
        If there is a dimension without a part, solve for the best possible part in that dimension,
        as the other dimensions are the primary constraining factor
        """
        for cap in [BaseConstants.RAM, BaseConstants.HDD, BaseConstants.SSD, BaseConstants.VRAM]:

            if cap == BaseConstants.VRAM and not sum(self.get_req(wl, cap) for wl in self.wl_list):
                config[BaseConstants.VRAM] = ['HX-GPU-T4-16', 0, 0, 0]
                continue

            if cap not in config:

                cap_set = parts_set[cap]

                parts = seed_part_table[cap]
                parts = self.get_part_combo(config[BaseConstants.CPU][0], parts, self.node_list, cap)

                if parts:
                    part_set = [part_config for part_config in cap_set if part_config[0] in parts]

                    if part_set:
                        config[cap] = part_set[0]

            """
            If we have an empty configuration here, throw exception and break, as we have a potential data issue.
            """

            if cap not in config:
                logger.info("%s Potential Data Issue: %s" % (self.logger_header, json.dumps(config)))
                raise HXException(self.logger_header + "Data_Issue")

        """
        Initialize new node, as we have a config.
        """
        seed_node = self.init_seed_node(config, node_subtype)

        self.hc_node_max = self.get_max_cluster_value(seed_node.attrib[BaseConstants.SUBTYPE],
                                                      seed_node.attrib[HyperConstants.DISK_CAGE],
                                                      self.hypervisor,
                                                      self.current_cluster)

        num, num_compute = self.get_node_count(config, node_subtype)

        if self.sizer_instance.heterogenous:

            seed_compute = self.init_seed_node(config, HyperConstants.COMPUTE)

            self.comp_node_max = self.get_max_cluster_value(seed_node.attrib[BaseConstants.SUBTYPE],
                                                            seed_node.attrib[HyperConstants.DISK_CAGE],
                                                            self.hypervisor, self.current_cluster, True)

        else:

            seed_compute = None
            self.comp_node_max = 0

        return {HyperConstants.NODE: seed_node,
                HyperConstants.COMPUTE: seed_compute,
                HyperConstants.NUM: num,
                HyperConstants.NUM_COMPUTE: num_compute}

    def get_node_count(self, config, node_subtype):

        if 'LFF' in config[BaseConstants.HDD][0]:
            disk_cage = 'LFF'
        else:
            disk_cage = 'SFF'

        if self.sizer_instance.heterogenous:

            comp, hx = \
                self.sizer_instance.get_comp_to_hx_ratio(node_subtype, disk_cage, self.hypervisor, self.current_cluster)

            total_nodes = max([config[key][2] for key in config])

            min_storage = max(config[BaseConstants.HDD][2],
                              config[BaseConstants.SSD][2],
                              int(ceil((total_nodes * hx) / float(hx + comp))))

            num_compute = total_nodes - min_storage

            if self.wl_list[0].attrib[HyperConstants.INTERNAL_TYPE] == HyperConstants.AIML and \
                    any(wl.attrib['input_type'] == "Video" and wl.attrib['expected_util'] == 'Serious Development'
                        for wl in self.wl_list):

                num_compute = max(num_compute, sum(wl.num_ds for wl in self.wl_list
                                                   if wl.attrib['input_type'] == "Video" and
                                                   wl.attrib['expected_util'] == 'Serious Development'))

            num = max(min_storage, (num_compute * hx) / comp)

        else:

            num_compute = 0
            num = max([config[key][2] for key in config])

        return num, num_compute

    # def decrease_true_min(self, config, parts, node_subtype):
    #
    #     true_min = max(config[key][2] for key in config)
    #     core_count = self.parts_table.get_part_attrib(config[BaseConstants.CPU][0], BaseConstants.CAPACITY)
    #
    #     original_sw_price = self.calc_raw_sw_price(2, core_count, BaseConstants.CTO, true_min, node_subtype)
    #     total_price_diff = 0
    #
    #     changed = True
    #
    #     while changed:
    #
    #         changes_list = list()
    #
    #         for cap in HyperConstants.CAP_LIST_CONF:
    #
    #             if cap != BaseConstants.CPU:
    #                 filter_parts = self.get_part_combo(config[BaseConstants.CPU][0], [part[0] for part in parts[cap]],
    #                                                    self.node_list, cap)
    #
    #             for part in parts[cap]:
    #
    #                 if cap != BaseConstants.CPU and part[0] not in filter_parts:
    #                     continue
    #
    #                 if part[2] < config[cap][2]:
    #
    #                     if cap == BaseConstants.CPU:
    #                         core_count = self.parts_table.get_part_attrib(part[0], BaseConstants.CAPACITY)
    #
    #                     new_sw_price = self.calc_raw_sw_price(2, core_count, BaseConstants.CTO, part[2], node_subtype)
    #                     sw_diff = new_sw_price - original_sw_price
    #
    #                     price_diff = \
    #                         self.parts_table.get_part_attrib(part[0], HyperConstants.CTO_PRICE) - \
    #                         self.parts_table.get_part_attrib(config[cap][0], HyperConstants.CTO_PRICE)
    #
    #                     if total_price_diff + price_diff < sw_diff:
    #                         total_price_diff += price_diff
    #                         config[cap] = part
    #                         changes_list.append(True)
    #                         break
    #                     else:
    #                         changes_list.append(False)
    #
    #         if not any(changes_list):
    #             changed = False

    def init_seed_node(self, config, node_subtype):

        total_price = 0

        new_node = HyperConvergedNode('Seed_Node', self.sizer_instance.hercules, self.sizer_instance.hx_boost,
                                      {'name': 'Seed_Node', 'type': 'cto', 'subtype': node_subtype})

        new_node.attrib[BaseConstants.STATIC_OVERHEAD] = {self.hypervisor: self.static_overhead}

        price_factor = HyperConstants.CTO_PRICE

        if 'LFF' in config[BaseConstants.HDD][0]:
            new_node.attrib[HyperConstants.DISK_CAGE] = 'LFF'
        else:
            new_node.attrib[HyperConstants.DISK_CAGE] = 'SFF'

        for key in HyperConstants.CAP_LIST:

            if key == BaseConstants.CPU:

                new_node, cpu_price = SeedNode.cpu_parts_price_calculation(key, config, self.parts_table,
                                                                           new_node, price_factor)
                total_price += cpu_price

            elif key == BaseConstants.RAM:

                new_node, ram_price = SeedNode.ram_parts_price_calculation(key, config, self.parts_table,
                                                                           new_node, price_factor, self.slot_dict[key])
                total_price += ram_price

            elif key == BaseConstants.HDD:

                new_node, hdd_price = SeedNode.hdd_parts_price_calculation(key, config, self.parts_table,
                                                                           new_node, price_factor, self.slot_dict[key])
                total_price += hdd_price

            elif key == BaseConstants.SSD:

                new_node, ssd_price = SeedNode.ssd_parts_price_calculation(key, config, self.parts_table,
                                                                           new_node, price_factor)
                new_node.attrib[BaseConstants.IOPS_CONV_FAC] = \
                    self.iops_conv_fac[new_node.attrib[HyperConstants.SSD_PART]][self.sizer_instance.threshold_factor]

                total_price += ssd_price

            elif key == BaseConstants.VRAM:

                if self.wl_list[0].attrib[HyperConstants.INTERNAL_TYPE] == HyperConstants.AIML and \
                        any(wl.attrib['input_type'] == "Video" and wl.attrib['expected_util'] == 'Serious Development'
                            for wl in self.wl_list):
                    max_slots_per_node = 5
                else:
                    max_slots_per_node = 2

                new_node, gpu_price = SeedNode.gpu_parts_price_calculation(key, config, self.parts_table,
                                                                           new_node, price_factor, max_slots_per_node)
                total_price += gpu_price

        new_node.attrib[BaseConstants.BASE_PRICE] = total_price

        for cap in HyperConstants.WL_CAP_LIST:
            new_node.calculate_overhead(cap, self.hypervisor)
            new_node.calc_cap(cap)
            new_node.calc_capex_opex()

        return new_node

    def populate_part_list(self):

        part_list = {BaseConstants.CPU: set(), BaseConstants.RAM: set(), BaseConstants.HDD: set(),
                     BaseConstants.SSD: set(), BaseConstants.VRAM: set()}

        '''
        Lists used for iterating through all the parts
        '''
        for node in self.node_list:
            for cpu in node.attrib[HyperConstants.CPU_OPT]:
                part_list[BaseConstants.CPU].add(cpu)
            for ram in node.attrib[HyperConstants.RAM_OPT]:
                part_list[BaseConstants.RAM].add(ram)
            for hdd in node.attrib[HyperConstants.HDD_OPT]:
                part_list[BaseConstants.HDD].add(hdd)
            for ssd in node.attrib[HyperConstants.SSD_OPT]:
                part_list[BaseConstants.SSD].add(ssd)
            for gpu in node.attrib[HyperConstants.GPU_OPT]:
                part_list[BaseConstants.VRAM].add(gpu)

        # convert set to list and return parts_list
        for key, value in part_list.items():
            part_list[key] = list(value)
        return part_list

    def calc_seed_part_overhead(self, part_name, part_count, cap, max_slots_per_node):

        if cap not in self.static_overhead:
            overhead_amt = 0
        else:
            overhead_amt = float(self.static_overhead[cap])

        if cap == BaseConstants.VRAM and not max_slots_per_node:
            max_slots_per_node = 1

        node_count = int(ceil(float(part_count) / float(max_slots_per_node)))

        if cap == BaseConstants.HDD:

            hdd_overhead = \
                (overhead_amt / 100.0) * self.parts_table.get_part_attrib(part_name, BaseConstants.CAPACITY) / \
                self.sizer_instance.highest_rf

            return part_count * hdd_overhead

        else:

            return overhead_amt * node_count

    def solve_optimal_part_seed(self, cap, parts, node_subtype):

        part_list = list()

        mlom_40_10 = False
        threshold_key = cap

        if (node_subtype in [HyperConstants.ROBO_NODE, HyperConstants.ROBO_TWO_NODE, HyperConstants.ROBO_240])\
                and cap == BaseConstants.SSD:
            mlom_40_10 = any('40G-10G' in part for part in parts[cap])

        if cap == BaseConstants.HDD:

            if node_subtype in [HyperConstants.ALL_FLASH, HyperConstants.ALL_FLASH_7_6TB, HyperConstants.ALLNVME_NODE,
                                HyperConstants.ALLNVME_NODE_8TB, HyperConstants.AF_ROBO_NODE,
                                HyperConstants.AF_ROBO_TWO_NODE, HyperConstants.ROBO_AF_240]:
                threshold_key = HyperConstants.ALL_FLASH_HDD
            elif node_subtype in [HyperConstants.LFF_NODE, HyperConstants.LFF_12TB_NODE]:
                threshold_key = HyperConstants.LFF_HDD

        if cap == BaseConstants.RAM:

            min_memory = 10000

            for part in parts[cap]:

                if '[CUSTOM]' in part:
                    slots = [12]
                elif '[CUSTOM_6SLOT]' in part:
                    slots = [6]
                else:
                    slots = self.slot_dict[cap]

                min_memory = min(min_memory, min(slots) * self.parts_table.get_part_attrib(part,
                                                                                           BaseConstants.CAPACITY))

            if all('M10' in part for part in parts[BaseConstants.VRAM]):

                self.max_mem_limit = 1000

        threshold = self.sizer_instance.get_threshold_value(self.wl_list[0].attrib[HyperConstants.INTERNAL_TYPE],
                                                            threshold_key)

        if cap == BaseConstants.SSD:

            if self.sizer_instance.hercules:
                cap_type = 'hercules'
            else:
                cap_type = 'normal'

            for part in parts[cap]:

                """
                Custom code to skip other SSDs when a 40G-10G part is available. Applicable to ROBO clusters
                """
                if (node_subtype in [HyperConstants.ROBO_NODE, HyperConstants.ROBO_TWO_NODE, HyperConstants.ROBO_240] ) \
                        and mlom_40_10 and '40G-10G' not in part:
                    continue

                for wl in self.wl_list:

                    wl.capsum[cap_type][BaseConstants.IOPS] = 0

                    for iops_key in wl.original_iops_sum:
                        status, iops_fac = self.sizer_instance.get_iops_value(part,
                                                                              self.sizer_instance.threshold_factor,
                                                                              self.sizer_instance.RF_String, iops_key,
                                                                              wl.attrib['storage_protocol'])

                        pcnt_increase = 0

                        if self.sizer_instance.hercules:
                            pcnt_increase += HyperConstants.HERCULES_IOPS[iops_key]

                        if self.sizer_instance.hx_boost:
                            pcnt_increase += HyperConstants.HX_BOOST_IOPS[iops_key]

                        iops_fac *= (1 + pcnt_increase / 100.0)

                        iops_fac *= self.max_specint / self.parts_table.get_part_attrib(HyperConstants.REF_IOPS_CPU,
                                                                                        HyperConstants.SPECLNT)

                        iops_fac *= self.sizer_instance.get_threshold_value(wl.attrib[HyperConstants.INTERNAL_TYPE],
                                                                            BaseConstants.IOPS,
                                                                            self.wl_list)

                        wl.capsum[cap_type][BaseConstants.IOPS] += wl.original_iops_sum[iops_key] / float(iops_fac)

                wl_sum_group = sum(self.get_req(wl, cap) for wl in self.wl_list)
                part_capacity = self.parts_table.get_part_attrib(part, BaseConstants.CAPACITY)

                cache_parts_needed = int(ceil(float(wl_sum_group) / float(part_capacity)))

                iops_parts_needed = int(ceil(sum(self.get_req(wl, BaseConstants.IOPS) for wl in self.wl_list)))

                parts_needed = max(cache_parts_needed, iops_parts_needed)

                price = parts_needed * self.parts_table.get_part_attrib(part, HyperConstants.CTO_PRICE)
                part_list.append([part, parts_needed, parts_needed, price])

        else:

            wl_sum = sum(self.get_req(wl, cap) for wl in self.wl_list)

            for part in parts[cap]:

                part_capacity = self.parts_table.get_part_attrib(part, BaseConstants.CAPACITY)

                if cap == BaseConstants.HDD:

                    slots = list(range(min(self.slot_dict[cap]), max(self.slot_dict[cap]) + 1))

                elif cap == BaseConstants.RAM:

                    if '[CUSTOM]' in part:
                        slots = [12]
                    elif '[CUSTOM_6SLOT]' in part:
                        slots = [6]
                    else:
                        slots = self.slot_dict[cap]

                else:

                    slots = self.slot_dict[cap]

                if cap == BaseConstants.RAM and min_memory < self.max_mem_limit:

                    slots = list(filter(lambda x: part_capacity * x <= self.max_mem_limit, slots))

                    if not slots:
                        continue

                max_slot_per_node = max(slots)

                if cap == BaseConstants.VRAM and \
                        self.wl_list[0].attrib[HyperConstants.INTERNAL_TYPE] == HyperConstants.AIML and \
                        any(wl.attrib['input_type'] == "Video" and wl.attrib['expected_util'] == 'Serious Development'
                            for wl in self.wl_list):

                    max_slot_per_node = 5

                if cap == BaseConstants.VRAM and self.vdi_gpu_exists:

                    frame_buff_list = self.parts_table.get_part_attrib(part, HyperConstants.FRAME_BUFF)

                    if not all(getattr(x, 'frame_buff', 0) in frame_buff_list for x in self.wl_list
                               if x.attrib.get(HyperConstants.GPU_STATUS, False)):

                        continue

                if cap in BaseConstants.CPU:

                    current_spec = self.parts_table.get_part_attrib(part, HyperConstants.SPECLNT)
                    part_capacity *= current_spec

                    self.max_specint = max(self.max_specint, current_spec)

                    self.max_mem_limit = max(self.max_mem_limit,
                                             int(self.parts_table.get_part_attrib(part, HyperConstants.RAM_LIMIT)) *
                                             max_slot_per_node)

                elif cap in BaseConstants.HDD:

                    part_capacity /= float(self.sizer_instance.highest_rf)

                parts_needed = float(wl_sum) / float(part_capacity)

                part_sum = \
                    (parts_needed * part_capacity * threshold) - \
                    self.calc_seed_part_overhead(part, parts_needed, cap, max_slot_per_node)

                while wl_sum > part_sum:

                    parts_needed += 1
                    part_sum = \
                        (parts_needed * part_capacity * threshold) - \
                        self.calc_seed_part_overhead(part, parts_needed, cap, max_slot_per_node)

                if not parts_needed:
                    # this condition satisfy only when required parts for the wrokload is zero
                    part_list.append([part, 0, 0, 0])
                    continue

                parts_needed = int(ceil(parts_needed))

                parts_needed += min(parts_needed % slot for slot in slots if slot)

                servers_needed = int(ceil(parts_needed / float(max_slot_per_node)))

                if cap == HyperConstants.VRAM:
                    servers_needed *= self.parts_table.get_part_attrib(part, HyperConstants.PCIE_REQ)

                price = parts_needed * self.parts_table.get_part_attrib(part, HyperConstants.CTO_PRICE)

                if cap in BaseConstants.CPU:

                    if self.hypervisor == 'esxi':
                        hypervisor_sw_price = 2 * HyperConstants.ESX_SOFTWARE_PRICE
                    else:
                        hypervisor_sw_price = 2 * self.parts_table.get_part_attrib(part, BaseConstants.CAPACITY) * \
                                              HyperConstants.HYPER_V_SOFTWARE_PRICE

                    orig_sw_cost = hypervisor_sw_price * servers_needed
                    price += orig_sw_cost

                part_list.append([part, parts_needed, servers_needed, price])

        if node_subtype in [HyperConstants.ROBO_NODE, HyperConstants.ROBO_TWO_NODE, HyperConstants.ROBO_240]:

            exceeds_max = list()
            remaining = list()

            for part in part_list:

                max_cluster = self.sizer_instance.get_max_cluster_value(node_subtype,
                                                                        HyperConstants.SMALL_FORM_FACTOR,
                                                                        'esxi',
                                                                        HyperConstants.NORMAL)

                if cap != BaseConstants.HDD:
                    max_cluster -= max(wl.attrib[HyperConstants.FAULT_TOLERANCE] for wl in self.wl_list)

                if part[2] > max_cluster:
                    exceeds_max.append(part)
                else:
                    remaining.append(part)

            return sorted(remaining, key=itemgetter(3)) + sorted(exceeds_max, key=itemgetter(3))

        return sorted(part_list, key=itemgetter(3))

    @staticmethod
    def get_part_combo(cpu, parts, node_list, cap):

        cpu_key = "cpu_options"

        if cap == BaseConstants.VRAM:
            option_key = "gpu_options"
        else:
            option_key = cap.lower() + "_options"

        parts = list({part for part in parts for node in node_list
                      if part in node.attrib[option_key] and cpu in node.attrib[cpu_key]})

        return parts

    def create_clusters(self):

        hc_node_count = self.node_data[HyperConstants.NUM]

        if self.sizer_instance.heterogenous and self.node_data[HyperConstants.COMPUTE]:
            comp_node_count = self.node_data[HyperConstants.NUM_COMPUTE]
        else:
            comp_node_count = 0

        num_clusters = max(int(ceil(float(hc_node_count + comp_node_count) / (self.hc_node_max + self.comp_node_max))),
                           int(ceil(float(hc_node_count) / self.hc_node_max)))

        '''
        If we have already found an optimal solution, return.
        '''
        if num_clusters == 1:
            return [[self.hc_node_max, self.comp_node_max, self.hc_node_max, self.comp_node_max]]

        clusters = list()

        for i in range(0, num_clusters):
            clusters.append([self.hc_node_max, self.comp_node_max, self.hc_node_max, self.comp_node_max])

        return clusters

    @staticmethod
    def get_connected_wl(wl_name, wl_list):

        for wl in wl_list:
            if wl.attrib.get('primary_wl_name', '') == wl_name:
                return wl

        return None

    def generate_normal_clusters(self, hc_node, comp_node, clusters):

        wl_input_list = self.generate_sorted_wl_list(hc_node, comp_node, self.wl_list)

        wl_partition_list = list()

        for wl in wl_input_list:

            # these workloads are connected to some other wl. hence not processed in isolation
            if 'primary_wl_name' in wl.attrib:
                continue

            wl_type = wl.attrib[HyperConstants.INTERNAL_TYPE]
            fit_wl = False

            for cluster in clusters:

                # conn wl refers to workload which should sit in same cluster as the current wl
                conn_wl = self.get_connected_wl(wl.attrib['wl_name'], wl_input_list)

                if conn_wl:
                    new_wl_set = cluster[4] + [wl, conn_wl]
                else:
                    new_wl_set = cluster[4] + [wl]

                fit_wl = self.check_capacity(hc_node, cluster[0], comp_node, cluster[1], wl_type, new_wl_set)

                if fit_wl:
                    cluster[4].append(wl)
                    if conn_wl:
                        cluster[4].append(conn_wl)
                    break

            '''
            No Cluster can fit this. Keep in separate cluster. Case should only happen for large workloads.
            '''
            if not fit_wl:
                if not conn_wl:
                    clusters.append([self.hc_node_max, self.comp_node_max, 0, 0, [wl], list()])
                else:
                    clusters.append([self.hc_node_max, self.comp_node_max, 0, 0, [wl, conn_wl], list()])

        for cluster in clusters:
            if cluster[4]:
                wl_partition_list.append(([cluster[4]]))

        return wl_partition_list

    def generate_sorted_wl_list(self, hc_node, compute_node, wl_list):

        temp_wl_list = list()

        wl_type = wl_list[0].attrib[HyperConstants.INTERNAL_TYPE]

        if self.sizer_instance.hercules:
            cap_type = 'hercules'
        else:
            cap_type = 'normal'

        for wl in wl_list:

            self.sizer_instance.highest_rf = 3
            self.sizer_instance.Fault_Tolerance = wl.attrib[HyperConstants.FAULT_TOLERANCE]
            self.sizer_instance.RF_String = self.sizer_instance.set_RF_String()

            wl_sum_group = dict()

            for cap in HyperConstants.WL_CAP_LIST:
                if cap == BaseConstants.IOPS:

                    wl.capsum[cap_type][cap] = 0
                    iops_dict = hc_node.attrib[BaseConstants.IOPS_CONV_FAC][self.sizer_instance.RF_String]

                    for iops_key, iops_value in wl.original_iops_sum.items():

                        # 10.2
                        if iops_key in [HyperConstants.CONTAINER, HyperConstants.AIML, HyperConstants.ANTHOS, HyperConstants.ROBO_BACKUP]:

                            if wl.attrib['storage_protocol'] == 'NFS':
                                iops_conv = float(iops_dict[HyperConstants.VSI][0]) / 2.0
                            else:
                                iops_conv = float(iops_dict[HyperConstants.VSI][1]) / 2.0
                        else:
                            if wl.attrib['storage_protocol'] == 'NFS':
                                iops_conv = float(iops_dict[iops_key][0])
                            else:
                                iops_conv = float(iops_dict[iops_key][1])

                        pcnt_increase = 0

                        if self.sizer_instance.hercules:
                            pcnt_increase += HyperConstants.HERCULES_IOPS[iops_key]

                        if self.sizer_instance.hx_boost:
                            pcnt_increase += HyperConstants.HX_BOOST_IOPS[iops_key]

                        iops_conv *= (1 + pcnt_increase / 100.0)

                        iops_conv *= self.max_specint / self.parts_table.get_part_attrib(HyperConstants.REF_IOPS_CPU,
                                                                                         HyperConstants.SPECLNT)

                        if wl.attrib[HyperConstants.INTERNAL_TYPE] == HyperConstants.VDI_INFRA:
                            wl.capsum[cap_type][cap] += 0.1 * self.hc_node_max
                        else:
                            wl.capsum[cap_type][cap] += wl.original_iops_sum[iops_key] / iops_conv

                wl_sum_group[cap] = self.get_req(wl, cap)

            max_util = self.generate_utilization(hc_node, compute_node, self.hc_node_max, wl_sum_group,
                                                 self.sizer_instance.Fault_Tolerance, wl_type)

            temp_wl_list.extend([[wl, max_util]])

        temp_wl_list = sorted(temp_wl_list, key=itemgetter(1), reverse=True)

        sorted_wl_list = [item[0] for item in temp_wl_list]

        return sorted_wl_list

    def generate_utilization(self, hc_node, compute_node, cluster_size, wl_sum_group, fault_tolerance, wl_type):
        """
        Generates utilizations for a cluster, with the appropriate fault tolerance built in.
        """

        node_sum = dict()
        util_array = list()

        cluster_size_wo_ft = cluster_size - fault_tolerance

        for cap in HyperConstants.WL_CAP_LIST:

            threshold_key = cap
            if cap == BaseConstants.HDD:
                if hc_node.attrib[BaseConstants.SUBTYPE] in [HyperConstants.ALL_FLASH, HyperConstants.ALL_FLASH_7_6TB,
                                                             HyperConstants.ALLNVME_NODE,
                                                             HyperConstants.ALLNVME_NODE_8TB,
                                                             HyperConstants.AF_ROBO_NODE,
                                                             HyperConstants.AF_ROBO_TWO_NODE,
                                                             HyperConstants.ROBO_AF_240]:
                    threshold_key = HyperConstants.ALL_FLASH_HDD

                if hc_node.attrib[HyperConstants.DISK_CAGE] == 'LFF':
                    threshold_key = HyperConstants.LFF_HDD

            threshold_value = self.sizer_instance.get_threshold_value(wl_type, threshold_key)
            hc_node_cap = float(hc_node.raw_cap[cap] * threshold_value - hc_node.overhead[cap])

            node_sum[cap] = hc_node_cap * cluster_size_wo_ft

            if cap in BaseConstants.HDD:
                node_sum[cap] = hc_node_cap * cluster_size / float(self.sizer_instance.highest_rf)

            if compute_node:
                node_sum[cap] += float(compute_node.cap[cap] * threshold_value) * cluster_size

            if node_sum[cap] <= 0:
                node_sum[cap] = 1

            utilization = float(wl_sum_group[cap]) / float(node_sum[cap])

            util_array.append(utilization)

        return max(util_array)

    def check_capacity(self, hc_node, hc_count, compute_node, compute_count, wl_type, wls):

        wl_sum = dict()

        for cap in HyperConstants.WL_CAP_LIST:
            wl_sum[cap] = sum(self.get_req(wl, cap) for wl in wls)

        if wl_type == HyperConstants.AIML:
            num_ds = sum(wl.num_ds for wl in wls if wl.attrib['input_type'] == "Video" and
                         wl.attrib['expected_util'] == 'Serious Development')
        else:
            num_ds = 0

        fault_tolerance = max(x.attrib[HyperConstants.FAULT_TOLERANCE] for x in wls)

        node_sum = dict()

        for cap in HyperConstants.CAP_LIST:

            threshold_key = cap
            if cap == BaseConstants.HDD:
                if hc_node.attrib[BaseConstants.SUBTYPE] in [HyperConstants.ALL_FLASH, HyperConstants.ALL_FLASH_7_6TB,
                                                             HyperConstants.ALLNVME_NODE,
                                                             HyperConstants.ALLNVME_NODE_8TB,
                                                             HyperConstants.AF_ROBO_NODE,
                                                             HyperConstants.AF_ROBO_TWO_NODE]:
                    threshold_key = HyperConstants.ALL_FLASH_HDD

                if hc_node.attrib[HyperConstants.DISK_CAGE] == 'LFF':
                    threshold_key = HyperConstants.LFF_HDD

            elif cap == BaseConstants.VRAM and self.vdi_gpu_exists:

                gpu_part = self.node_data[HyperConstants.NODE].attrib[HyperConstants.GPU_PART]

                frame_buff_list = self.parts_table.get_part_attrib(gpu_part, HyperConstants.FRAME_BUFF)

                if not all(getattr(x, 'frame_buff', 0) in frame_buff_list for x in wls
                           if x.attrib.get(HyperConstants.GPU_STATUS, False)):
                    return False

            threshold = self.sizer_instance.get_threshold_value(wl_type, threshold_key)

            if cap == BaseConstants.HDD:
                node_sum[cap] = ((hc_node.raw_cap[cap] * threshold / self.sizer_instance.highest_rf) -
                                 hc_node.overhead[cap]) * hc_count
            else:
                node_sum[cap] = ((hc_node.raw_cap[cap] * threshold) - hc_node.overhead[cap]) * \
                                (hc_count - fault_tolerance)

            if compute_node is not None:
                node_sum[cap] += float(compute_node.cap[cap] *
                                       self.sizer_instance.get_threshold_value(wl_type, threshold_key)) * compute_count

            if wl_sum[cap] > node_sum[cap] or num_ds > compute_count:
                return False

            if cap in BaseConstants.SSD and wl_sum[BaseConstants.IOPS] > \
                    (HyperConstants.MAX_CONTAINER_IOPS_NODES if wl_type == HyperConstants.CONTAINER else
                        hc_count - fault_tolerance):
                return False

        return True

    def generate_repl_clusters(self, hc_node, comp_node, wl_dict, clusters):

        """
        cluster Array index map:
        0 - Primary Hyperconverged Count
        1 - Primary Compute Count
        2 - Secondary Hyperconverged Count
        3 - Secondary Compute Count
        4 - Primary WL List
        5 - Secondary WL List
        """

        wl_partition_list = list()

        working_cluster = list()

        if wl_dict['local_primary']:
            working_cluster = self.generate_repl_primary_secondary(hc_node, comp_node, wl_dict,
                                                                   clusters)
        if wl_dict['remote_primary']:
            working_cluster = self.generate_repl_primary_secondary(hc_node, comp_node, wl_dict,
                                                                   working_cluster, replication_type='remote_primary')

        if wl_dict['any_cluster']:
            working_cluster = self.generate_repl_any(hc_node, comp_node, wl_dict, working_cluster)

        for cluster in working_cluster:

            if cluster[4] and cluster[5]:
                wl_partition_list.append((cluster[4], cluster[5]))
            elif cluster[5] and not cluster[4]:
                wl_partition_list.append((cluster[5],))
            elif cluster[4] and not cluster[5]:
                wl_partition_list.append((cluster[4],))

        return wl_partition_list

    def generate_repl_primary_secondary(self, hc_node, comp_node, wl_dict, clusters, replication_type='local_primary'):

        # Fit primary cluster workloads

        wl_input_list = self.generate_sorted_wl_list(hc_node, comp_node, wl_dict[replication_type])

        if replication_type == 'local_primary':

            iter_object = 'remote_secondary'
            prime_index = 4
            second_index = 5
            hc_prime_index = 0
            compute_prime_index = 1
            hc_second_index = 2
            compute_second_index = 3

        elif replication_type == 'remote_primary':

            iter_object = 'local_secondary'
            prime_index = 5
            second_index = 4
            hc_prime_index = 2
            compute_prime_index = 3
            hc_second_index = 0
            compute_second_index = 1

        for wl in wl_input_list:

            wl_type = wl.attrib[HyperConstants.INTERNAL_TYPE]
            secondary_wl = None

            if wl.attrib[HyperConstants.REPLICATION_AMT]:
                for secondary in wl_dict[iter_object]:
                    if wl.attrib['wl_name'] == secondary.attrib['wl_name']:
                        secondary_wl = secondary
                        break

            fit_wl_primary = False
            fit_wl_secondary = False

            for cluster in clusters:

                fit_wl_primary = self.check_capacity(hc_node, cluster[hc_prime_index], comp_node,
                                                     cluster[compute_prime_index], wl_type, cluster[prime_index] + [wl])

                fit_wl_secondary = self.check_capacity(hc_node, cluster[hc_second_index], comp_node,
                                                       cluster[compute_second_index], wl_type,
                                                       cluster[second_index] + [secondary_wl])

                # CR: DR VM Memory Overhead (maximum of 200 Replicated VMs/DBs across the entire DR Cluster)
                if secondary_wl:
                    dr_wl_total = secondary_wl.num_inst
                    for wls in cluster[second_index]:
                        if wls.attrib['replication_type'] == HyperConstants.REPLICATED:
                            dr_wl_total += wls.num_inst

                    if dr_wl_total > 200:

                        fit_wl_primary = False
                        fit_wl_secondary = False

                if secondary_wl and fit_wl_primary and fit_wl_secondary:

                    cluster[prime_index].append(wl)
                    cluster[second_index].append(secondary_wl)
                    break

                elif not secondary_wl and fit_wl_primary:
                    cluster[prime_index].append(wl)
                    break

            '''
            No Cluster can fit this. Keep in separate cluster. Case should only happen for large workloads.
            '''
            if not fit_wl_primary or (secondary_wl and not fit_wl_secondary):

                new_cluster = \
                    [self.hc_node_max, self.comp_node_max, self.hc_node_max, self.comp_node_max, list(), list()]

                new_cluster[prime_index].append(wl)

                if secondary_wl:
                    new_cluster[second_index].append(secondary_wl)

                clusters.append(new_cluster)

        return clusters

    def generate_repl_any(self, hc_node, comp_node, wl_dict, clusters):

        # Fit primary cluster workloads

        wl_input_list = self.generate_sorted_wl_list(hc_node, comp_node, wl_dict['any_cluster'])

        for wl in wl_input_list:

            wl_type = wl.attrib[HyperConstants.INTERNAL_TYPE]

            fit_wl_primary = False
            fit_wl_secondary = False

            for cluster in clusters:

                fit_wl_primary = self.check_capacity(hc_node, cluster[0], comp_node, cluster[1], wl_type,
                                                     cluster[4] + [wl])

                if fit_wl_primary:
                    cluster[4].append(wl)
                    break

                fit_wl_secondary = self.check_capacity(hc_node, cluster[2], comp_node, cluster[3], wl_type,
                                                       cluster[5] + [wl])

                if fit_wl_secondary:
                    cluster[5].append(wl)
                    break
            '''
            No Cluster can fit this. Keep in separate cluster. Case should only happen for large workloads.
            '''
            if not fit_wl_primary and not fit_wl_secondary:

                new_cluster = [self.hc_node_max, self.comp_node_max, self.hc_node_max, self.comp_node_max, [wl], list()]

                clusters.append(new_cluster)

        return clusters
