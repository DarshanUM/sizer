import logging
from math import ceil
from copy import deepcopy
from re import findall

from hyperconverged.exception import HXException
from .attrib import HyperConstants
from base_sizer.solver.sizing import Sizer
from base_sizer.solver.attrib import BaseConstants

from .hxdp_class import HXDataPlatform, fetch_rules
from .filter_node_class import FilterNode
from .workload_class import Workload
from .cluster_class import Cluster
from .partition_wl_class import PartitionWl
from .utilization_class import UtilizationGenerator

from operator import itemgetter
logger = logging.getLogger(__name__)

# import cProfile
# import pstats
# import StringIO


class HyperConvergedSizer(Sizer, HXDataPlatform, FilterNode, Workload, Cluster):

    def __init__(self, parts, nodes, wls, settings_json, scenario_id):

        HXDataPlatform.__init__(self, settings_json, scenario_id)

        if parts:
            self.load_parts(parts)

        FilterNode.__init__(self, nodes)
        Workload.__init__(self, wls)

        Cluster.__init__(self)
        self.filter_workload_list_to_cluster_type()

        self.highest_specint = 0

    def validate_wl_combo(self, bundle_only):

        if self.wl_dict[HyperConstants.NORMAL][HyperConstants.ROBO] or self.wl_dict[HyperConstants.NORMAL][HyperConstants.ROBO_BACKUP_SECONDARY] or \
                self.wl_dict[HyperConstants.STRETCH][HyperConstants.ROBO] or self.wl_dict[HyperConstants.STRETCH][HyperConstants.ROBO_BACKUP_SECONDARY]:

            if not self.cto_robo and not self.robo_node_list:
                raise HXException("No_ROBO_Nodes |" + self.logger_header)

        if not self.hyperconverged_node_list and not self.all_flash_node_list and \
                bundle_only == HyperConstants.BUNDLE_ONLY and \
                not self.cto_robo and not self.robo_node_list:
            raise HXException("No_HC_Nodes |" + self.logger_header)

        if not self.compute_node_list and self.heterogenous and bundle_only == HyperConstants.BUNDLE_ONLY:
            raise HXException("No_Compute_Nodes |" + self.logger_header)

    def solve(self, bundle_only):

        self.validate_wl_combo(bundle_only)

        for self.current_cluster, workloads_dict in self.wl_dict.items():

            '''
            Profiler attached to code to allow runtime checks. Can be removed if not necessary anymore. 
            '''
            logger.info('%s Start Sizing' % self.logger_header)

            # pr = cProfile.Profile()
            # pr.enable()

            for wl_type, wl_list in workloads_dict.items():

                if wl_type in [HyperConstants.ROBO, HyperConstants.VEEAM, HyperConstants.ROBO_BACKUP_SECONDARY]:
                    self.heterogenous = False
                else:
                    self.heterogenous = self.settings_json[HyperConstants.HETEROGENOUS]

                if wl_list and wl_type not in [HyperConstants.DB, HyperConstants.ORACLE, HyperConstants.VSI,
                                               HyperConstants.VDI_INFRA, HyperConstants.VDI, HyperConstants.RDSH,
                                               HyperConstants.EPIC, HyperConstants.AIML, HyperConstants.ANTHOS]:
                    
                    if wl_type in [HyperConstants.ROBO_BACKUP, HyperConstants.ROBO_BACKUP_SECONDARY]:
                        
                        for wl in wl_list:
                            backup_wl_list = list()
                            backup_wl_list.append(wl)
                            self.solve_multi_cluster_general(self.heterogenous, bundle_only, backup_wl_list, wl_type)
                    else:
                        self.solve_multi_cluster_general(self.heterogenous, bundle_only, wl_list, wl_type)

            self.heterogenous = self.settings_json[HyperConstants.HETEROGENOUS]

            if workloads_dict[HyperConstants.DB] or workloads_dict[HyperConstants.ORACLE] or \
                    workloads_dict[HyperConstants.VSI]:

                merged_wls = workloads_dict[HyperConstants.DB] + workloads_dict[HyperConstants.ORACLE] + \
                             workloads_dict[HyperConstants.VSI]

                if workloads_dict[HyperConstants.DB] or workloads_dict[HyperConstants.ORACLE]:
                    cluster_type = HyperConstants.ORACLE
                else:
                    cluster_type = HyperConstants.VSI

                self.solve_multi_cluster_general(self.heterogenous, bundle_only, merged_wls, cluster_type)

            if workloads_dict[HyperConstants.VDI] or workloads_dict[HyperConstants.VDI_INFRA] or \
                    workloads_dict[HyperConstants.RDSH]:

                merged_wls = workloads_dict[HyperConstants.VDI] + workloads_dict[HyperConstants.VDI_INFRA] + \
                             workloads_dict[HyperConstants.RDSH]

                self.solve_multi_cluster_general(self.heterogenous, bundle_only, merged_wls, HyperConstants.VDI)

            if workloads_dict[HyperConstants.ANTHOS]:
                self.solve_multi_cluster_general(self.heterogenous, bundle_only, workloads_dict[HyperConstants.ANTHOS], HyperConstants.ANTHOS)

            if workloads_dict[HyperConstants.EPIC]:
                self.solve_epic_cluster(self.heterogenous,
                                        bundle_only,
                                        workloads_dict[HyperConstants.EPIC],
                                        HyperConstants.EPIC)

            if workloads_dict[HyperConstants.AIML]:

                wl_group = \
                    list(filter(lambda x: x.attrib['input_type'] == 'Text Input', workloads_dict[HyperConstants.AIML]))

                if wl_group:
                    self.solve_multi_cluster_general(self.heterogenous, bundle_only, wl_group, HyperConstants.AIML)

                wl_group = \
                    list(filter(lambda x: x.attrib['input_type'] == 'Video', workloads_dict[HyperConstants.AIML]))

                if wl_group:
                    self.solve_multi_cluster_general(self.heterogenous, bundle_only, wl_group, HyperConstants.AIML)

            # pr.disable()
            # s = StringIO.StringIO()
            # sortby = 'cumulative'
            # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            # ps.print_stats()

            logger.info('%s Finished Sizing' % self.logger_header)

        cluster_data = self.cluster_result
        return UtilizationGenerator(self).build_multi_cluster_json(cluster_data)

    def solve_epic_cluster(self, heterogenous, bundle_only, wl_list, cluster_type):

        """
        Generate Node List, for usage in the partitioning and general sizing.
        """

        for workload in wl_list:

            epic_result = list()

            node_list, compute_list = self.get_compatible_nodes(cluster_type, bundle_only, [workload])
            filtered_nodes, filtered_computes = self.post_partn_fil(node_list, compute_list, cluster_type, [[workload]])

            slot_dict = self.get_slots(filtered_nodes)

            '''
            Solve CTO Nodes for each DC.
            '''
            for datacentre in workload.datacentres:
                if datacentre.attrib['concurrent_user_pcnt']:

                    self.result = list()
                    self.solve_cto_cluster(heterogenous, filtered_nodes, filtered_computes, [datacentre], slot_dict)

                    '''
                    Boundary condition for workflows that cannot fit in any node combination
                    '''
                    if not self.result:
                        wl_group_names = [str(workload.attrib["wl_name"])]
                        raise HXException("WL_Too_Large | " + str(wl_group_names) + self.logger_header)

                    settings = self.get_cluster_settings()
                    cl_result = [self.result[self.get_optimal_result(heterogenous)], [datacentre], settings]

                    for _ in range(datacentre.attrib['num_clusters']):
                        epic_result.append(deepcopy(cl_result))

            self.cluster_result.append(epic_result)

    def get_slots(self, node_list):

        slot_dict = dict()

        for cap in HyperConstants.CAP_LIST:

            slot_dict[cap] = set()
            _, slot_key = self.get_cap_keys(cap)

            for node in node_list:
                for slot in node.attrib[slot_key]:
                    slot_dict[cap].add(slot)

            slot_dict[cap] = list(slot_dict[cap])

        return slot_dict

    def solve_multi_cluster_general(self, heterogenous, bundle_only, wl_list, cluster_type):

        self.hercules = False
        self.hx_boost = False

        """
        Generate Node List, for usage in the partitioning and general sizing.
        """
        node_list, compute_list = self.get_compatible_nodes(cluster_type, bundle_only, wl_list)

        '''
        Partition Workloads. Change function if different strategy used.
        '''
        node_list, compute_list = self.pre_partn_filter(node_list, compute_list, cluster_type, wl_list)
        partitioner = PartitionWl(self, node_list, wl_list, cluster_type)
        wl_partition_list = partitioner.get_partitioned_list()

        slot_dict = self.get_slots(node_list)

        for group in wl_partition_list:

            self.result = list()

            '''
            Solve CTO Nodes.
            '''
            filtered_nodes, filtered_computes = self.post_partn_fil(node_list, compute_list, cluster_type, group)

            self.solve_cto_cluster(heterogenous, filtered_nodes, filtered_computes, group[0], slot_dict)

            '''
            Boundary condition for workflows that cannot fit in any node combination
            '''

            if not self.result:
                wl_group_names = [str(wl.attrib["wl_name"]) for wl in group[0]]
                raise HXException("WL_Too_Large | " + str(wl_group_names) + self.logger_header)

            settings = self.get_cluster_settings()
            primary_result = [self.result[self.get_optimal_result(heterogenous)], group[0], settings]

            if cluster_type in [HyperConstants.DB, HyperConstants.VSI, HyperConstants.ORACLE] and len(group) > 1:

                self.result = list()
                self.solve_cto_cluster(heterogenous, filtered_nodes, filtered_computes, group[1], slot_dict)
                secondary_result = [self.result[self.get_optimal_result(heterogenous)], group[1], settings]
                self.cluster_result.append([primary_result, secondary_result])

            elif self.current_cluster == HyperConstants.STRETCH:

                stretched_result = deepcopy(primary_result)
                self.cluster_result.append([primary_result, stretched_result])

            else:

                self.cluster_result.append([primary_result])

    def get_optimal_result(self, heterogenous):

        if heterogenous:
            min_count = self.result[0][HyperConstants.NUM] + self.result[0][HyperConstants.NUM_COMPUTE]
        else:
            min_count = self.result[0][HyperConstants.NUM]

        cost_difference = 1.1

        min_cost = self.result[0][BaseConstants.PRICE]
        min_result_index = 0

        for resultIndex in range(1, len(self.result)):

            percent_difference = float(self.result[resultIndex][BaseConstants.PRICE]) / float(min_cost)

            if percent_difference > cost_difference:
                break

            if heterogenous:
                node_count = self.result[resultIndex][HyperConstants.NUM] + \
                             self.result[resultIndex][HyperConstants.NUM_COMPUTE]
            else:
                node_count = self.result[resultIndex][HyperConstants.NUM]

            if node_count < min_count:
                min_count = node_count
                min_result_index = resultIndex

        return min_result_index

    @staticmethod
    def get_pricing(node, num_nodes):
        price = 0

        cpx_dict = node.get_capex(num_nodes)
        for i in cpx_dict[HyperConstants.VAL]:
            if i[HyperConstants.TAG_NAME] == HyperConstants.CAPEX_CPX:
                price = i[HyperConstants.TAG_VAL]

        return price

    def add_heterogenous_result(self, cluster_information):

        total_price = cluster_information[BaseConstants.PRICE]

        if len(self.result) == 0:
            self.result.insert(0, cluster_information)
            return

        for index in range(0, len(self.result)):
            if total_price < self.result[index][BaseConstants.PRICE] or \
                    (total_price == self.result[index][BaseConstants.PRICE] and
                     (cluster_information[HyperConstants.NUM] + cluster_information[HyperConstants.NUM_COMPUTE] <
                      self.result[index][HyperConstants.NUM] + self.result[index][HyperConstants.NUM_COMPUTE])):
                self.result.insert(index, cluster_information)
                return

        self.result.insert(index + 1, cluster_information)

    def print_result(self, level):

        logger.info(str(level))
        logger.info("WL Total")

        for cap in HyperConstants.CAP_LIST:
            logger.info(cap + " = " + str(self.wl_sum[cap]))

        for i in range(0, min(HyperConstants.TOP_VALUE, len(self.result))):

            logger.info("#i :%d" % (i + 1))
            logger.info("Price =%d" % (self.result[i][BaseConstants.PRICE]))
            logger.info("Num =%d" % (self.result[i][HyperConstants.NUM]))

            self.result[i][HyperConstants.NODE].print_cap()

    def get_cluster_settings(self):

        settings = dict()

        settings[HyperConstants.REPLICATION_FACTOR] = self.highest_rf
        settings[HyperConstants.FAULT_TOLERANCE] = self.Fault_Tolerance
        settings['threshold'] = self.threshold_factor
        settings['heterogenous'] = self.heterogenous

        return settings

    def set_RF_String(self):

        if self.highest_rf == 2:
            return "RF2"
        elif self.highest_rf == 3:
            return "RF3"
        else:
            return "RF3"

    def solve_cto_cluster(self, heterogenous, node_list, compute_list, group, slot_dict):

        self.populate_part_table(node_list, group)

        optimal_parts = dict()

        self.highest_rf = max(wl.attrib[HyperConstants.REPLICATION_FACTOR] for wl in group)
        self.RF_String = self.set_RF_String()
        self.Fault_Tolerance = max(wl.attrib[HyperConstants.FAULT_TOLERANCE] for wl in group)

        max_cluster_size = max(self.get_max_cluster_value(node.attrib[BaseConstants.SUBTYPE],
                                                          node.attrib[HyperConstants.DISK_CAGE],
                                                          self.hypervisor,
                                                          self.current_cluster)
                               for node in node_list)

        if heterogenous:
            compute_max = max(self.get_max_cluster_value(node.attrib[BaseConstants.SUBTYPE],
                                                         node.attrib[HyperConstants.DISK_CAGE], self.hypervisor,
                                                         self.current_cluster,
                                                         True)
                              for node in node_list)
        else:
            compute_max = 0

        min_cluster_size = self.get_minimum_size(node_list[0].attrib[BaseConstants.SUBTYPE],
                                                 self.Fault_Tolerance,
                                                 self.current_cluster, self.highest_rf) - self.Fault_Tolerance

        self.hercules = any(node.hercules_avail for node in node_list)
        self.hx_boost = any(node.hx_boost_avail for node in node_list)
        
        """ 
        Risers for M6 has support for either GPU or Disk or I/O at a time.
        When the user select riser option - PCIE, if workload requires GPU, then GPU riser are considered else
        PCIE risers are considered
        When the user select riser option - Storage, as Compute node wont support Disk, we need to increase the slots
        in the M6 240HX Node by 4. 
        """

        # This riser_options is for mapping
        riser_options = [1, 2, 3]
        additional_disk = False

        if self.server_type == 'M6':

            riser = node_list[0].attrib['riser_options']

            riser_240 = [{"GPU": ["UCSC-RIS1A-240M6", "UCSC-RIS2A-240M6", "UCSC-RIS3C-240M6"],
                          "DISK": ["HX-RIS1B-240M6", "HX-RIS3B-240M6"],
                          "IO": ["UCSC-RIS1A-240M6", "UCSC-RIS2A-240M6", "UCSC-RIS3A-240M6"]}]

            riser_220 = [{"GPU": ["UCSC-GPURKIT-C220"],
                          "IO": ["UCSC-R2R3-C220M6"]}]

            """For 240 riser options 1 and 3 are considered for sizing and if HERCULES available, riser 2 is included.
                and For 220 all the riser options 1,2 and 3 are taken by default """

            if riser == 'PCI-E':
                if any(wl.attrib.get(HyperConstants.GPU_STATUS, False) for wl in group):
                    selected_220riser = riser_220[0].pop("GPU")

                    if self.hercules:
                        selected_240riser = riser_240[0].pop("GPU")
                    else:
                        # remove riser 2 from options, if hercules unavailable
                        riser_options.pop(1)
                        riser_240[0]["GPU"].pop(1)
                        selected_240riser = riser_240[0].pop("GPU")
                else:
                    selected_240riser = riser_240[0].pop("IO")
                    selected_220riser = riser_220[0].pop("IO")

            elif riser == 'Storage':
                additional_disk = True
                selected_240riser = riser_240[0].pop("DISK")
                selected_220riser = []
                compute_riser = []

        for cap in HyperConstants.CAP_LIST:
            optimal_parts[cap] = self.solve_optimal_part(cap, heterogenous, group, min_cluster_size, max_cluster_size,
                                                         compute_max, slot_dict[cap], riser_options)

        error_overcommit_flag = False
        gbps_limit_exceeded = False
        gpu_limit_exceeded = False
        cpu_limit_exceeded = False

        settings = self.get_cluster_settings()
        node_results = list()

        if not heterogenous:
            compute_list = [None]

        self.find_large_vm_partition(group)
        original_slot = dict()

        for node in node_list:

            if node.hercules_avail:

                if self.settings_json[HyperConstants.HERCULES_CONF] == HyperConstants.FORCED:
                    hercules_opts = [True]
                elif self.settings_json[HyperConstants.HERCULES_CONF] == HyperConstants.DISABLED:
                    hercules_opts = [False]
                else:
                    hercules_opts = [True, False]

            else:

                hercules_opts = [False]

            if node.hx_boost_avail:

                if self.settings_json[HyperConstants.HX_BOOST_CONF] == HyperConstants.FORCED:
                    hx_boost_opts = [True]
                elif self.settings_json[HyperConstants.HX_BOOST_CONF] == HyperConstants.DISABLED:
                    hx_boost_opts = [False]
                else:
                    hx_boost_opts = [True, False]

            else:

                hx_boost_opts = [False]

            # Force Enable hx_boost if cluster having iSCSI
            for wl in group:
                if wl.attrib['storage_protocol'] and wl.attrib['storage_protocol'] == 'iSCSI':
                    hx_boost_opts = [True]
                    break

            for self.hercules in hercules_opts:

                for self.hx_boost in hx_boost_opts:

                    for node2 in compute_list:

                        new_node = deepcopy(node)
                        new_node2 = deepcopy(node2)

                        new_node.hercules_on = self.hercules
                        new_node.hx_boost_on = self.hx_boost

                        # If storage riser selected, then increase the slot by 4
                        if additional_disk:
                            original_slot[new_node.name] = deepcopy(new_node.attrib['hdd_slots'])
                            if "NVME" not in new_node.name and '220' not in new_node.name:
                                max_slot = new_node.attrib['hdd_slots'].pop()
                                new_node.attrib['hdd_slots'].append(max_slot + 4)

                        status = self.normalise_slots(heterogenous, new_node, new_node2, group)

                        if not status:
                            continue

                        status, fltd_optimals = self.filter_avail_parts(new_node, new_node2, group, optimal_parts,
                                                                        heterogenous)

                        if not status:
                            continue

                        node_config, overhead_exceeded, gbps_exceeded, gpu_exceeded, cpu_exceeded, status = \
                            self.generate_node_results(fltd_optimals, new_node, heterogenous, group, new_node2)

                        if status:
                            node_results.append([new_node, node_config, settings, new_node2])
                        elif gpu_exceeded:
                            gpu_limit_exceeded = True
                        elif cpu_exceeded:
                            cpu_limit_exceeded = True
                        elif overhead_exceeded:
                            error_overcommit_flag = True
                        elif gbps_exceeded:
                            gbps_limit_exceeded = True

        wl_group_names = [str(wl.attrib['wl_name']) for wl in group]

        if not node_results and cpu_limit_exceeded:
            if isinstance(cpu_exceeded, str):
                raise HXException(cpu_exceeded + ' |' + str(wl_group_names) + '|' + self.logger_header)
            else:
                raise HXException('CPU_RAM_Limit |' + str(wl_group_names) + '|' + self.logger_header)

        elif not node_results and gpu_limit_exceeded:
            raise HXException('M10_1TB_Limit |' + str(wl_group_names) + '|' + self.logger_header)

        elif not node_results and not error_overcommit_flag and not gbps_limit_exceeded:
            raise HXException('No_Part_Combination_Found |' + self.logger_header)

        elif not node_results and gbps_limit_exceeded:
            raise HXException("SSD parts unavailable|" + str(wl_group_names) + '|' + self.logger_header)

        elif not node_results and error_overcommit_flag:
            raise HXException('Part_Overhead_Exceeded |' + str(wl_group_names) + '|' + self.logger_header)

        for result in node_results:
            node1, num_nodes1, node1_price, node2, num_nodes2, node2_price, accessories = \
                self.solve_optimal_cluster_count(result, group)

            if self.server_type == 'M6':
                if '240' in node1.name:
                    if original_slot:
                        node1.orignal_hdd_slot = original_slot[node1.name]
                    node1.riser = selected_240riser
                else:
                    node1.riser = selected_220riser

                if node2:
                    if riser == 'Storage':
                        node2.riser = compute_riser
                    else:
                        if '240' in node2.name:
                            node2.riser = selected_240riser
                        else:
                            node2.riser = selected_220riser

            total_price = node1_price + node2_price + sum([acc[HyperConstants.ACC_PRICE] for acc in accessories])

            cluster_information = {HyperConstants.NODE: node1,
                                   HyperConstants.NUM: num_nodes1,
                                   BaseConstants.PRICE: total_price,
                                   HyperConstants.COMPUTE: node2,
                                   HyperConstants.NUM_COMPUTE: num_nodes2,
                                   HyperConstants.ACC: accessories}

            self.add_heterogenous_result(cluster_information)

    def normalise_slots(self, heterogenous, hx_node, compute_node, workloads):

        if not heterogenous:
            return True

        for cap in [BaseConstants.CPU, BaseConstants.RAM, BaseConstants.VRAM]:

            if cap == BaseConstants.VRAM and (compute_node.attrib[BaseConstants.SUBTYPE] == HyperConstants.AIML_NODE or
                                              not sum(self.get_req(wl, cap) for wl in workloads)):
                continue

            _, slot_key = self.get_cap_keys(cap)

            intersect_slots = \
                list(filter(lambda x: x in compute_node.attrib[slot_key], hx_node.attrib[slot_key]))

            if not intersect_slots:
                return False

            hx_node.attrib[slot_key] = intersect_slots
            compute_node.attrib[slot_key] = intersect_slots

        return True

    def filter_avail_parts(self, node, node2, workloads, optimal_parts, heterogenous):

        gpu_req = sum(self.get_req(wl, BaseConstants.VRAM) for wl in workloads)
        fltd_optimal_parts = dict()

        for cap, part_list in optimal_parts.items():

            fltd_optimal_parts[cap] = list()
            option_key, slot_key = self.get_cap_keys(cap)

            slots = node.attrib[slot_key]
            hx_options = node.attrib[option_key]

            for part in part_list:

                if cap == BaseConstants.VRAM:

                    if not gpu_req or all(wl.attrib[HyperConstants.INTERNAL_TYPE] == HyperConstants.AIML and
                                          wl.attrib['input_type'] == "Video" and
                                          wl.attrib['expected_util'] == 'Serious Development' for wl in workloads):

                        fltd_optimal_parts[cap].append(part)
                        break

                    if max(slots) < self.parts_table.get_part_attrib(part[0], HyperConstants.PCIE_REQ):

                        continue

                if node.hx_boost_on and cap == BaseConstants.CPU:

                    cores_per_cpu = self.parts_table.get_part_attrib(part[0], BaseConstants.CAPACITY)

                    if node.attrib[BaseConstants.SUBTYPE] in [HyperConstants.ALLNVME_NODE_8TB,
                                                              HyperConstants.ALLNVME_NODE]:

                        if cores_per_cpu < 16:

                            continue

                    elif cores_per_cpu < 12:

                        continue

                # Check if Part is available in hyperconverged node, and compute node if applicable.
                if part[0] not in hx_options:
                    continue

                if cap in [BaseConstants.HDD, BaseConstants.SSD] or not heterogenous:
                    fltd_optimal_parts[cap].append(part)
                    continue

                co_options = node2.attrib[option_key]

                if cap in [BaseConstants.CPU, BaseConstants.RAM, BaseConstants.VRAM] and part[0] not in co_options:

                    if cap == BaseConstants.VRAM and not self.validate_gpu_exists(part[0], co_options):
                        continue

                    elif not any(part[0] in option for option in co_options):
                        continue

                fltd_optimal_parts[cap].append(part)

            if not fltd_optimal_parts[cap]:
                return False, None

        return True, fltd_optimal_parts

    def validate_config(self, node, node2, node_config, group):

        comp_min, storage_min = self.get_hx_comp(node, node2, node_config, group)

        min_servers = comp_min + storage_min

        ram_cap = self.parts_table.get_part_attrib(node_config[BaseConstants.RAM][0], BaseConstants.CAPACITY)

        if '[CUSTOM]' in node_config[BaseConstants.RAM][0]:
            slots = [12]
        elif '[CUSTOM_6SLOT]' in node_config[BaseConstants.RAM][0]:
            slots = [6]
        else:
            slots = node.attrib[BaseConstants.RAM_SLOTS]

        ram_count_per_server = int(ceil(node_config[BaseConstants.RAM][1] / float(min_servers)))
        ram_count_per_server = min([ram_count for ram_count in slots if ram_count >= ram_count_per_server])

        ram_per_server = ram_count_per_server * ram_cap

        # If the node config is currently using M series GPUs, resolve the corner case of 1 TB of RAM limitation
        if node_config[BaseConstants.VRAM][1] and node_config[BaseConstants.VRAM][0] == 'HX-GPU-M10' and \
                ram_per_server > 1000:
            return BaseConstants.VRAM, 1000

        # If the node config has higher RAM per server then only M/L CPUs can be used
        cpu_ram_limit = self.parts_table.get_part_attrib(self.current_cpu, HyperConstants.RAM_LIMIT)
        node_ram_limit = node.attrib["cpu_socket_count"][0] * cpu_ram_limit

        if ram_per_server > node_ram_limit:
            return BaseConstants.CPU, ram_per_server

        return None, None

    @staticmethod
    def check_general_rules(ram, cpu):

        generic_rules = fetch_rules()

        for rule in generic_rules:
            if findall(rule.rule_json['cpu_options'], cpu) and findall(rule.rule_json['ram_options'], ram):
                return True

        return False

    def generate_node_results(self, optimal_parts, node, heterogenous, group, node2):

        excess_gpu_ram = False
        excess_cpu_ram = False

        node_config, error_part_overhead, gbps_limit_exceeded, status = \
            self.solve_optimal_config(optimal_parts, node, heterogenous, group, node2)

        if not status:
            return None, error_part_overhead, gbps_limit_exceeded, excess_gpu_ram, excess_cpu_ram, status

        node_config = self.true_min_decrease(optimal_parts, node, heterogenous, group, node2, node_config)

        to_edit, ram_limit = self.validate_config(node, node2, node_config, group)

        while to_edit:
            excess_gpu_ram, excess_cpu_ram, status = \
                self.correct_config(optimal_parts, node, heterogenous, group, node2, node_config, to_edit, ram_limit)

            if not status:
                return None, error_part_overhead, gbps_limit_exceeded, excess_gpu_ram, excess_cpu_ram, status

            to_edit, ram_limit = self.validate_config(node, node2, node_config, group)

        if status:
            node_config, error_msg, status = self.balance_parts(optimal_parts, node, heterogenous, group, node2, node_config)
            if status:
                return node_config, error_part_overhead, gbps_limit_exceeded, excess_gpu_ram, error_msg, status
            else:
                return None, error_part_overhead, gbps_limit_exceeded, excess_gpu_ram, error_msg, status

    def correct_config(self, optimal_parts, node, heterogenous, group, node2, node_config, to_edit, ram_limit):

        def replace_ram(max_ram_per_server):

            temp_node = deepcopy(node)

            option_key, slot_key = self.get_cap_keys(BaseConstants.RAM)

            for part in sorted(optimal_parts[BaseConstants.RAM],
                               key=lambda x: self.parts_table.get_part_attrib(x[0], BaseConstants.CAPACITY),
                               reverse=True):

                temp_ram_cap = self.parts_table.get_part_attrib(part[0], BaseConstants.CAPACITY)

                slots = node.attrib[slot_key]
                if '[CUSTOM]' in part[0]:
                    slots = [12]
                elif '[CUSTOM_6SLOT]' in part[0]:
                    slots = [6]

                for ram_count in sorted(slots, reverse=True):

                    if temp_ram_cap * ram_count > max_ram_per_server:
                        continue

                    temp_node.attrib[BaseConstants.RAM_SLOTS] = [ram_count]

                    part_found, _, _, new_part_details = self.configure_part(part, temp_node, BaseConstants.RAM,
                                                                             heterogenous, group, node2, slot_key)

                    if part_found:
                        node_config[BaseConstants.RAM] = new_part_details
                        return True

            return False

        if to_edit == BaseConstants.VRAM:

            # Trying to use a different GPU
            option_key, slot_key = self.get_cap_keys(BaseConstants.VRAM)
            filtered_gpus = list(filter(lambda x: 'GPU-M10' not in x[0], optimal_parts[BaseConstants.VRAM]))

            for part in filtered_gpus:

                part_found, _, _, new_part_details = self.configure_part(part, node, BaseConstants.VRAM, heterogenous,
                                                                         group, node2, slot_key)

                if part_found:

                    optimal_parts[BaseConstants.VRAM] = filtered_gpus
                    node_config[BaseConstants.VRAM] = new_part_details
                    return False, False, True

            # Last resort: Effectively increasing RAM server count
            if replace_ram(ram_limit):
                return False, False, True

            return True, False, False

        if to_edit == BaseConstants.CPU:

            # Trying to use a different CPU
            option_key, slot_key = self.get_cap_keys(BaseConstants.CPU)

            filtered_cpus = filter(lambda x: (self.parts_table.get_part_attrib(x[0], HyperConstants.RAM_LIMIT) *
                                              node.attrib['cpu_socket_count'][0]) >= ram_limit,
                                   optimal_parts[BaseConstants.CPU])

            for part in filtered_cpus:

                part_found, _, _, new_part_details = self.configure_part(part, node, BaseConstants.CPU, heterogenous,
                                                                         group, node2, slot_key)

                if part_found:

                    self.current_cpu = new_part_details[0]
                    optimal_parts[BaseConstants.CPU] = filtered_cpus
                    node_config[BaseConstants.CPU] = new_part_details

                    return False, False, True

            self.current_cpu = node_config[BaseConstants.CPU][0]

            # Last resort: Effectively increasing RAM server count
            if replace_ram(node.attrib["cpu_socket_count"][0] *
                           self.parts_table.get_part_attrib(self.current_cpu, HyperConstants.RAM_LIMIT)):

                return False, False, True

            return False, True, False

    def populate_part_table(self, node_list, workloads):

        """
        Populate the part lists in part_table based on nodes used in sizing.
        """
        self.parts_table.flush_part_list()

        for node in node_list:
            for cpu in node.attrib[HyperConstants.CPU_OPT]:
                self.parts_table.add_part_list(BaseConstants.CPU, cpu)
            for ram in node.attrib[HyperConstants.RAM_OPT]:
                self.parts_table.add_part_list(BaseConstants.RAM, ram)
            for hdd in node.attrib[HyperConstants.HDD_OPT]:
                self.parts_table.add_part_list(BaseConstants.HDD, hdd)
            for ssd in node.attrib[HyperConstants.SSD_OPT]:
                self.parts_table.add_part_list(BaseConstants.SSD, ssd)

            if not sum(self.get_req(wl, BaseConstants.VRAM) for wl in workloads):
                self.parts_table.add_part_list(BaseConstants.GPU, 'HX-GPU-T4-16')
                continue

            for gpu in node.attrib[HyperConstants.GPU_OPT]:
                self.parts_table.add_part_list(BaseConstants.GPU, gpu)

    def solve_optimal_part(self, cap, heterogenous, wl_group, min_cluster_size, max_cluster_size, compute_max, slots, riser_options):

        """
        After calculating workload sum, find optimal parts.
        """

        # this function is run prior to setting any specific node. hence uses hercules dictionary to fetch lower
        # values so that configure part can increase part count later but if hercules is disabled then it uses normal

        if cap not in BaseConstants.HDD:
            max_cluster_size -= self.Fault_Tolerance

        if cap == BaseConstants.CPU:
            self.highest_specint = 0

        if not self.hercules:
            cap_type = 'normal'
        else:
            cap_type = 'hercules'

        parts = self.parts_table.get_part_list(cap)

        error_part = ''
        error_count = 999
        error_node_count = 999

        if not parts:
            raise HXException("No_Usable_Part |" + cap + "|" + self.logger_header)

        if self.server_type == 'M6' and cap == BaseConstants.VRAM:
            if 2 in riser_options:
                # For 220 node, no need to extend slot
                if max(slots) != 3:
                    add_pcie = max(slots)+1
                    slots.append(add_pcie)

        sorted_usable_part = list()

        if cap == BaseConstants.VRAM:

            wl_sum_num_instance = 0
            for wl in wl_group:
                if wl.capsum[cap_type][cap] != 0 and hasattr(wl, 'num_inst'):
                    wl_sum_num_instance += wl.num_inst
                if wl.capsum[cap_type][cap] != 0 and hasattr(wl, 'num_vms'):
                    wl_sum_num_instance += wl.num_vms
                if wl.capsum[cap_type][cap] != 0 and hasattr(wl, 'num_ds'):
                    wl_sum_num_instance += wl.num_ds

            wl_sum_group = sum(wl.capsum[cap_type][cap] for wl in wl_group)
            max_pcie_per_node = max(slots)

            if not max_pcie_per_node:
                max_pcie_per_node = 1

            max_pcie = max_pcie_per_node * (max_cluster_size + compute_max)

            if wl_group[0].attrib[HyperConstants.INTERNAL_TYPE] == HyperConstants.AIML:
                serious_ds = sum(wl.num_ds for wl in wl_group if wl.attrib['input_type'] == "Video" and
                                 wl.attrib['expected_util'] == 'Serious Development')
            else:
                serious_ds = 0

            if serious_ds > compute_max:
                raise HXException('AIML DS' + '|' + str(compute_max) + '|' + str([str(wl.attrib['wl_name'])
                                                                                  for wl in wl_group]))

            for part in parts:

                part_capacity = self.parts_table.get_part_attrib(part, BaseConstants.CAPACITY)
                max_vgpu_per_slot = self.parts_table.get_part_attrib(part, BaseConstants.MAX_SESSION)
                
                num_parts_capacity = int(ceil(float(wl_sum_group) / float(part_capacity)))
                num_parts_session = int(ceil(float(wl_sum_num_instance) / float(max_vgpu_per_slot)))

                num_parts = max(num_parts_capacity, num_parts_session)

                if serious_ds:

                    max_gpu_per_node = (max_cluster_size * 2 + compute_max * 8) / \
                                       ((max_cluster_size + compute_max) *
                                        self.parts_table.get_part_attrib(part, HyperConstants.PCIE_REQ))

                    max_gpus = (max_cluster_size * 2 + compute_max * 8) / \
                               self.parts_table.get_part_attrib(part, HyperConstants.PCIE_REQ)

                else:

                    max_gpu_per_node = \
                        max_pcie_per_node / self.parts_table.get_part_attrib(part, HyperConstants.PCIE_REQ)

                    max_gpus = max_pcie / self.parts_table.get_part_attrib(part, HyperConstants.PCIE_REQ)

                num_servers = int(ceil(float(num_parts) / max_gpu_per_node))

                if num_parts > max_gpus:

                    if num_parts < error_count:
                        error_part = self.parts_table.get_part_attrib(part, HyperConstants.BOM_NAME)
                        error_count = num_parts
                        error_node_count = num_servers

                    continue

                if wl_sum_group:
                    min_gpus = min_cluster_size
                else:
                    min_gpus = 0

                single_part_price = self.parts_table.get_part_attrib(part, HyperConstants.CTO_PRICE)
                part_price = max(num_parts, min_gpus) * single_part_price

                sorted_usable_part.append([part, num_parts, part_price, single_part_price])

        elif cap in BaseConstants.SSD:

            container_iops_support = False

            max_ssd_per_node = max(slots)
            max_ssds = max_ssd_per_node * max_cluster_size
            min_ssds = min(slots) * min_cluster_size

            for part in parts:

                for wl in wl_group:

                    wl.capsum[cap_type][BaseConstants.IOPS] = 0

                    for iops_key in wl.original_iops_sum:

                        status, iops_fac = self.get_iops_value(part, self.threshold_factor, self.RF_String, iops_key,
                                                               wl.attrib['storage_protocol'])
                        iops_fac *= self.highest_specint

                        if cap_type == 'hercules':
                            iops_fac *= (1 + HyperConstants.HERCULES_IOPS[iops_key] / 100.0)

                        wl.capsum[cap_type][BaseConstants.IOPS] += wl.original_iops_sum[iops_key] / float(iops_fac)

                cache_req = sum(wl.capsum[cap_type][cap] for wl in wl_group)
                cache_cap = self.parts_table.get_part_attrib(part, BaseConstants.CAPACITY)

                cache_parts = int(ceil(cache_req / float(cache_cap)))
                cache_servers = int(ceil(cache_parts / float(max_ssd_per_node)))

                iops_parts = int(ceil(sum(wl.capsum[cap_type][BaseConstants.IOPS] for wl in wl_group)))
                iops_servers = int(ceil(iops_parts / float(max_ssd_per_node)))

                if cache_parts > max_ssds:

                    cap = BaseConstants.SSD

                    if cache_parts < error_count:
                        error_part = self.parts_table.get_part_attrib(part, HyperConstants.BOM_NAME)
                        error_count = cache_parts
                        error_node_count = cache_servers

                    continue

                spec_iops_fac = self.parts_table.get_part_attrib(HyperConstants.REF_IOPS_CPU,
                                                                 HyperConstants.SPECLNT) / self.highest_specint

                if wl_group[0].attrib[HyperConstants.INTERNAL_TYPE] == HyperConstants.CONTAINER:

                    if iops_parts * spec_iops_fac > HyperConstants.MAX_CONTAINER_IOPS_NODES * max_ssd_per_node:

                        cap = BaseConstants.IOPS

                        if iops_parts < error_count:
                            error_part = self.parts_table.get_part_attrib(part, HyperConstants.BOM_NAME)
                            error_count = iops_parts
                            error_node_count = iops_servers

                        continue

                    container_iops_support = True

                elif iops_parts * spec_iops_fac > max_ssds:

                    if iops_parts < error_count:
                        error_part = self.parts_table.get_part_attrib(part, HyperConstants.BOM_NAME)
                        error_count = iops_parts
                        error_node_count = iops_servers

                    continue

                num_parts = max(cache_parts, iops_parts)

                single_part_price = self.parts_table.get_part_attrib(part, HyperConstants.CTO_PRICE)
                part_price = max(min_ssds, num_parts) * single_part_price
                sorted_usable_part.append([part, num_parts, part_price, single_part_price])

        else:

            wl_sum_group = sum(wl.capsum[cap_type][cap] for wl in wl_group)
            max_slot_per_node = max(slots)
            min_parts = min(slots) * min_cluster_size

            if cap == BaseConstants.HDD:
                max_slots = max_slot_per_node * max_cluster_size
            else:
                max_slots = max_slot_per_node * (max_cluster_size + compute_max)

            for part in parts:

                part_capacity = self.parts_table.get_part_attrib(part, BaseConstants.CAPACITY)

                if cap in BaseConstants.HDD:
                    part_capacity /= float(self.highest_rf)
                elif cap in BaseConstants.CPU:
                    current_spec = self.parts_table.get_part_attrib(part, HyperConstants.SPECLNT)
                    self.highest_specint = max(current_spec, self.highest_specint)
                    part_capacity *= current_spec

                num_parts = int(ceil(float(wl_sum_group) / float(part_capacity)))
                num_servers = int(ceil(float(num_parts) / max_slot_per_node))

                if cap == BaseConstants.RAM:
                    if '[CUSTOM]' in part:
                        num_servers = int(ceil(num_parts / 12.0))
                    elif '[CUSTOM_6SLOT]' in part:
                        num_servers = int(ceil(num_parts / 6.0))

                if num_parts > max_slots:

                    if num_parts < error_count:
                        error_part = self.parts_table.get_part_attrib(part, HyperConstants.BOM_NAME)
                        error_count = num_parts
                        error_node_count = num_servers

                    continue

                if cap == BaseConstants.HDD:
                    slots = list(range(min(slots), max_slot_per_node + 1))

                elif cap == BaseConstants.RAM:
                    if '[CUSTOM]' in part:
                        slots = [12]
                    elif '[CUSTOM_6SLOT]' in part:
                        slots = [6]

                normalised = num_parts + min(num_parts % slot for slot in slots)

                single_part_price = self.parts_table.get_part_attrib(part, HyperConstants.CTO_PRICE)
                price = max(min_parts, normalised) * single_part_price
                sorted_usable_part.append([part, num_parts, price, single_part_price])

        if not sorted_usable_part:

            wl_group_names = [str(wl.attrib['wl_name']) for wl in wl_group]

            wl_type = wl_group[0].attrib[HyperConstants.INTERNAL_TYPE]

            if cap in [BaseConstants.SSD, BaseConstants.IOPS] and wl_type == HyperConstants.CONTAINER and \
                    not container_iops_support:

                error_cluster_size = HyperConstants.MAX_CONTAINER_IOPS_NODES
                raise HXException('CONTAINER_IOPS' + '|' + str(wl_group_names) + '|' + error_part + '|' +
                                  str(error_count) + '|' + str(error_node_count) + '|' + str(error_cluster_size) +
                                  '|' + self.logger_header + '|' + self.hypervisor)

            if heterogenous and cap in [BaseConstants.CPU, BaseConstants.RAM, BaseConstants.VRAM]:
                error_cluster_size = max_cluster_size + compute_max
            else:
                error_cluster_size = max_cluster_size

            if cap != BaseConstants.HDD:
                error_cluster_size += self.Fault_Tolerance
                error_node_count += self.Fault_Tolerance

            raise HXException('WL_Exceeds_Cap' + '|' + str(wl_group_names) + '|' + cap + '|' + error_part + '|' +
                              str(error_count) + '|' + str(error_node_count) + '|' + str(error_cluster_size) + '|' +
                              wl_type + '|' + self.logger_header + '|' + self.hypervisor)

        return sorted(sorted_usable_part, key=itemgetter(2))

    @staticmethod
    def get_cap_keys(cap):

        if cap == BaseConstants.VRAM:
            option_key = "gpu_options"
            slot_key = "pcie_slots"
        elif cap == BaseConstants.CPU:
            option_key = "cpu_options"
            slot_key = "cpu_socket_count"
        else:
            option_key = cap.lower() + "_options"
            slot_key = cap.lower() + "_slots"

        return option_key, slot_key

    def get_cheapest_part(self, cap, optimal_parts, node, heterogenous, wl_group, node2, optimal_config):

        option_key, slot_key = self.get_cap_keys(cap)

        error_overhead_flag = False
        gbps_limit_exceeded = False

        parts_to_remove = list()

        for part in optimal_parts[cap]:
            part_found, overhead_exceeded, gbps_exceeded, optimal_config[cap] = \
                self.configure_part(part, node, cap, heterogenous, wl_group, node2, slot_key)

            if part_found:

                if cap != BaseConstants.CPU:
                    break

                self.current_cpu = optimal_config[cap][0]

                ssd_overhead_exceeded, ssd_gbps_exceeded, ssd_status = \
                    self.get_cheapest_part(BaseConstants.SSD, optimal_parts, node, heterogenous, wl_group, node2,
                                           optimal_config)

                if ssd_status:

                    break

                else:

                    part_found = False

                    if ssd_overhead_exceeded:
                        error_overhead_flag = True
                    elif ssd_gbps_exceeded:
                        gbps_limit_exceeded = True

            else:

                parts_to_remove.append(part)

                if overhead_exceeded:
                    error_overhead_flag = True
                elif gbps_exceeded:

                    gbps_limit_exceeded = True

        if cap != BaseConstants.SSD and parts_to_remove:
            optimal_parts[cap] = [part for part in optimal_parts[cap] if part not in parts_to_remove]

        if not part_found:
            return error_overhead_flag, gbps_limit_exceeded, False
        elif cap == BaseConstants.CPU:
            self.current_cpu = optimal_config[BaseConstants.CPU][0]

        return False, False, True

    def solve_optimal_config(self, optimal_parts, node, heterogenous, wl_group, node2):

        optimal_config = dict()

        for cap in HyperConstants.CAP_LIST:

            if cap == BaseConstants.SSD:
                continue

            error_part_overhead, gbps_limit_exceeded, status = \
                self.get_cheapest_part(cap, optimal_parts, node, heterogenous, wl_group, node2, optimal_config)

            if not status:
                return None, error_part_overhead, gbps_limit_exceeded, False

        return optimal_config, False, False, True

    def get_min_ram_requirement(self, cap, node, wl_group, storage_protocol):

        min_ram_req = 0

        wl_type = wl_group[0].attrib[HyperConstants.INTERNAL_TYPE]

        if cap not in node.attrib[BaseConstants.STATIC_OVERHEAD][self.hypervisor]:
            controller_overhead = 0
        else:
            controller_overhead = float(node.attrib[BaseConstants.STATIC_OVERHEAD][self.hypervisor][cap])

        if storage_protocol:
            controller_overhead += 2

        if wl_type in [HyperConstants.VSI, HyperConstants.OLAP, HyperConstants.OLTP, HyperConstants.OOLAP,
                       HyperConstants.OOLTP]:
            for wl in wl_group:
                if 'ram_per_vm' in wl.attrib:
                    min_ram_req = max(min_ram_req, wl.attrib['ram_per_vm'])
                else:
                    min_ram_req = max(min_ram_req, wl.attrib['ram_per_db'])

            min_ram_req += controller_overhead

        return min_ram_req

    @staticmethod
    def get_min_iops_requirement(wl_group):

        if not any(wl.attrib[HyperConstants.INTERNAL_TYPE] in [HyperConstants.OLAP, HyperConstants.OOLAP]
                   for wl in wl_group):
            return 0

        return max(wl.attrib[HyperConstants.MBPS_PER_DB] / (64.0 / 1024) for wl in
                   filter(lambda x: x.attrib[HyperConstants.INTERNAL_TYPE] in [HyperConstants.OLAP,
                                                                               HyperConstants.OOLAP], wl_group))

    def configure_part(self, part, node, cap, heterogenous, wl_group, node2, slot_key):

        # Initialize Maximum Cluster Size

        max_cluster = self.get_max_cluster_value(node.attrib[BaseConstants.SUBTYPE],
                                                 node.attrib[HyperConstants.DISK_CAGE],
                                                 self.hypervisor,
                                                 self.current_cluster)

        compute_max = self.get_max_cluster_value(node.attrib[BaseConstants.SUBTYPE],
                                                 node.attrib[HyperConstants.DISK_CAGE],
                                                 self.hypervisor,
                                                 self.current_cluster,
                                                 True)

        part_name = part[0]

        wl_type = wl_group[0].attrib[HyperConstants.INTERNAL_TYPE]

        if cap == BaseConstants.SSD:
            part_count = 0
        else:
            part_count = part[1]

        # Workload calculations
        # Adjusting for the normalized IO/s of each scenario.
        if cap in BaseConstants.SSD:

            cap_type = 'hercules' if self.hercules else 'normal'

            min_iops_req = self.get_min_iops_requirement(wl_group)

            for wl in wl_group:
                wl.capsum[cap_type][BaseConstants.IOPS] = 0

                for iops_key in wl.original_iops_sum:
                    status, iops_fac = self.get_iops_value(part_name, self.threshold_factor, self.RF_String,
                                                           iops_key, wl.attrib['storage_protocol'])

                    if not status:
                        return False, False, False, list()

                    pcnt_increase = 0

                    if self.hercules:
                        pcnt_increase += HyperConstants.HERCULES_IOPS[iops_key]

                    if self.hx_boost:
                        pcnt_increase += HyperConstants.HX_BOOST_IOPS[iops_key]

                    iops_fac *= (1 + pcnt_increase / 100.0)

                    # this multiplication is being done as our IOPS numbers were derived while using 5120 CPU
                    iops_fac *= \
                        self.parts_table.get_part_attrib(self.current_cpu, HyperConstants.SPECLNT) / \
                        self.parts_table.get_part_attrib(HyperConstants.REF_IOPS_CPU, HyperConstants.SPECLNT)

                    if iops_key in [HyperConstants.OLAP, HyperConstants.OOLAP] and min_iops_req > iops_fac:
                        return False, False, True, list()

                    threshold = self.get_threshold_value(wl_type, BaseConstants.IOPS, wl_group)
                    iops_fac *= threshold
                    wl.capsum[cap_type][BaseConstants.IOPS] += wl.original_iops_sum[iops_key] / float(iops_fac)

        wl_sum_group = sum(self.get_req(wl, cap) for wl in wl_group)

        # Corner Case resolution for non-GPU workflows and AI/ML workflows with no storage requirements
        if not wl_sum_group and (cap == BaseConstants.VRAM or (wl_type == HyperConstants.AIML and cap in
                                                               [BaseConstants.HDD, BaseConstants.SSD])):
            return True, False, False, [part_name, 0, 0]

        if cap == BaseConstants.RAM and '[CUSTOM]' in part_name:
            max_slot_per_node = 12
        elif cap == BaseConstants.RAM and '[CUSTOM_6SLOT]' in part_name:
            max_slot_per_node = 6
        elif cap == BaseConstants.HDD:
            free_disk_slots = self.settings_json['free_disk_slots']
            max_slot_per_node = max(node.attrib[slot_key]) - free_disk_slots
        else:
            max_slot_per_node = max(node.attrib[slot_key])

        if cap == BaseConstants.VRAM and node2 and node2.attrib[BaseConstants.SUBTYPE] == HyperConstants.AIML_NODE:

            total_hx_gpus = max(node.attrib[slot_key]) * (max_cluster - self.Fault_Tolerance)
            total_co_gpus = max(node2.attrib[slot_key]) * compute_max
            max_slot_per_node = (total_hx_gpus + total_co_gpus) / (max_cluster + compute_max - self.Fault_Tolerance)

        if not max_slot_per_node and wl_sum_group:
            return False, False, False, list()

        if cap == BaseConstants.VRAM and self.parts_table.get_part_attrib(part_name,
                                                                          HyperConstants.PCIE_REQ) > max_slot_per_node:
            return False, False, False, list()

        if cap not in BaseConstants.HDD:
            maximum_slots = max_slot_per_node * (max_cluster - self.Fault_Tolerance)
        else:
            maximum_slots = max_slot_per_node * max_cluster

        if heterogenous and cap in [BaseConstants.CPU, BaseConstants.RAM, BaseConstants.VRAM]:
            maximum_slots += max_slot_per_node * compute_max

        storage_protocol = False

        if cap == BaseConstants.RAM:

            for wl in wl_group:
                if wl.attrib['storage_protocol'] and wl.attrib['storage_protocol'] == 'iSCSI':
                    _240nodes = ['HX-SP-240M5', 'HXAF-SP-240M5SX', 'HXAF-240M5SX', 'HX240C-M5']
                    for _240node in _240nodes:
                        if _240node in node.attrib['name']:
                            storage_protocol = True
                            break

        # Part configurations
        part_overhead = self.calculate_part_overhead(node, part_name, part_count, cap, slot_key, storage_protocol)

        threshold_key = cap
        if cap == BaseConstants.HDD:

            if node.attrib[BaseConstants.SUBTYPE] in [HyperConstants.ALL_FLASH, HyperConstants.AF_ROBO_NODE,
                                                      HyperConstants.ALLNVME_NODE, HyperConstants.ALLNVME_NODE_8TB,
                                                      HyperConstants.ALL_FLASH_7_6TB,
                                                      HyperConstants.AF_ROBO_TWO_NODE, HyperConstants.ROBO_AF_240]:
                threshold_key = HyperConstants.ALL_FLASH_HDD

            if node.attrib[HyperConstants.DISK_CAGE] == HyperConstants.LARGE_FORM_FACTOR:
                threshold_key = HyperConstants.LFF_HDD

        part_capacity = self.parts_table.get_part_attrib(part_name, BaseConstants.CAPACITY)

        if cap in BaseConstants.CPU:
            part_capacity *= self.parts_table.get_part_attrib(part_name, HyperConstants.SPECLNT)
        elif cap in BaseConstants.HDD:
            part_capacity /= float(self.highest_rf)

        if cap == BaseConstants.RAM:
            min_ram_req_per_server = self.get_min_ram_requirement(cap, node, wl_group, storage_protocol)
            if max_slot_per_node * part_capacity < min_ram_req_per_server:
                return False, False, False, list()

        part_sum = (part_count * part_capacity * self.get_threshold_value(wl_type, threshold_key)) - part_overhead

        # Check if we have more parts than we have slots in the server.
        if cap == BaseConstants.VRAM:
            maximum_slots /= self.parts_table.get_part_attrib(part_name, HyperConstants.PCIE_REQ)

        while wl_sum_group > part_sum:

            part_count += 1

            part_overhead = self.calculate_part_overhead(node, part_name, part_count, cap, slot_key, storage_protocol)

            part_sum = (part_count * part_capacity * self.get_threshold_value(wl_type, threshold_key)) - part_overhead

            if part_count > maximum_slots:

                return False, True, False, list()

        if cap == BaseConstants.RAM:

            projected_min_servers = int(ceil(part_count / float(max_slot_per_node)))

            part_count = max(part_count, min_ram_req_per_server / float(part_capacity) * projected_min_servers)

            if part_count > maximum_slots:

                return False, True, False, list()

        elif cap in BaseConstants.SSD:

            iops_parts = int(ceil(sum(self.get_req(wl, BaseConstants.IOPS) for wl in wl_group)))

            if wl_type == HyperConstants.CONTAINER:

                maximum_slots = max_slot_per_node * HyperConstants.MAX_CONTAINER_IOPS_NODES

            if iops_parts > maximum_slots:

                return False, True, False, list()

            part_count = max(part_count, iops_parts)

        divisor = float(max_slot_per_node)

        if cap == BaseConstants.VRAM:

            divisor /= self.parts_table.get_part_attrib(part_name, HyperConstants.PCIE_REQ)

        elif cap == BaseConstants.CPU:

            part_count = int(ceil(part_count / divisor)) * max_slot_per_node

        min_servers = int(ceil(float(part_count) / divisor))

        if cap in BaseConstants.HDD:

            min_servers -= self.Fault_Tolerance
            min_servers = max(0, min_servers)

        return True, False, False, [part_name, part_count, min_servers]

    def true_min_decrease(self, optimal_parts, node, heterogenous, wl_group, node2, node_config):

        """
        This function does the following:
        1. if the minimum node req in one dimension (true-min) greatly exceeds the minimum node req of other dimensions
        eg: CPU - 2
            RAM - 6
            HDD - 2
            SSD - 2
            Here constraint is RAM and it must be optimised such that node req for RAM decreases
        2. We can give slightly expensive part [for the constraint dimension] and reduce true-min
        3. Above thing can be done only when price increase is tolerable
        """

        def find_current_optimal(part_config):

            for op_part in optimal_parts[cap]:
                if op_part[0] == part_config[0]:
                    return op_part

        comp_min, storage_min = self.get_hx_comp(node, node2, node_config, wl_group)

        true_min = comp_min + storage_min

        # Below case returns node-config when min-cluster-size isn't satisfied and also for AI/ML workloads
        if true_min > max([node_config[key][2] for key in node_config]):
            return node_config
        elif (self.get_minimum_size(node.attrib[BaseConstants.SUBTYPE],
                                    self.Fault_Tolerance, self.current_cluster, self.highest_rf) - self.Fault_Tolerance) == \
                max([node_config[key][2] for key in node_config]):
            return node_config

        chassis_price = storage_min * node.attrib[BaseConstants.BASE_PRICE]
        if node2 and comp_min:
            chassis_price += comp_min * node2.attrib[BaseConstants.BASE_PRICE]

        if self.license_years:

            core_count = self.parts_table.get_part_attrib(node_config[BaseConstants.CPU][0], BaseConstants.CAPACITY)

            sw_cost = self.calc_raw_sw_price(node.attrib[BaseConstants.CPU_CNT][0], core_count,
                                             node.attrib[HyperConstants.TYPE], comp_min, storage_min,
                                             node.attrib[BaseConstants.SUBTYPE])

        change = \
            list(filter(lambda x: node_config[x][2] == true_min,
                        [BaseConstants.HDD, BaseConstants.CPU, BaseConstants.SSD, BaseConstants.RAM,
                         BaseConstants.VRAM]))

        change_or_retain = list()

        if BaseConstants.SSD in change:
            if BaseConstants.CPU not in change:
                change_or_retain.append(BaseConstants.CPU)
        elif BaseConstants.CPU in change:
            change_or_retain.append(BaseConstants.SSD)

        parts_to_use = dict()
        orig_price = dict()

        for cap in change + change_or_retain:

            crnt_part = find_current_optimal(node_config[cap])

            if cap == BaseConstants.SSD:

                parts = optimal_parts[cap]

            elif cap in change:

                parts = list(filter(lambda x: x[0] != crnt_part[0] and x[1] < crnt_part[1], optimal_parts[cap]))

            elif cap == BaseConstants.CPU:

                parts = list(filter(lambda x: x[1] >= crnt_part[1], optimal_parts[cap]))

            parts_to_use[cap] = parts

            orig_price[cap] = \
                node_config[cap][1] * self.parts_table.get_part_attrib(node_config[cap][0], HyperConstants.CTO_PRICE)

        new_node_config = deepcopy(node_config)
        constant = True

        for cap in [BaseConstants.HDD, BaseConstants.CPU, BaseConstants.SSD, BaseConstants.RAM, BaseConstants.VRAM]:

            if cap == BaseConstants.SSD or cap not in change + change_or_retain:
                continue

            temp_node_config = deepcopy(new_node_config)

            option_key, slot_key = self.get_cap_keys(cap)

            for part in parts_to_use[cap]:

                part_found, _, _, new_part_config = self.configure_part(part, node, cap, heterogenous, wl_group, node2,
                                                                        slot_key)

                if part_found:

                    if cap in change and new_part_config[2] >= new_node_config[cap][2]:
                        continue

                    temp_node_config[cap] = new_part_config

                    if cap != BaseConstants.CPU:

                        if cap == BaseConstants.HDD and BaseConstants.SSD in change:
                            exceptions = [BaseConstants.SSD]

                        elif cap == BaseConstants.RAM and BaseConstants.VRAM in change:
                            exceptions = [BaseConstants.VRAM]

                        else:
                            exceptions = None

                        temp_comp_min, temp_storage_min = \
                            self.get_hx_comp(node, node2, temp_node_config, wl_group, exceptions)

                        temp_chassis_price = temp_storage_min * node.attrib[BaseConstants.BASE_PRICE]

                        if node2 and temp_comp_min:
                            temp_chassis_price += temp_comp_min * node2.attrib[BaseConstants.BASE_PRICE]

                        # decrease in chassis price
                        chassis_price_diff = chassis_price - temp_chassis_price

                        # decrease in software price
                        if self.license_years:

                            sw_diff = \
                                sw_cost - self.calc_raw_sw_price(node.attrib[BaseConstants.CPU_CNT][0], core_count,
                                                                 node.attrib[HyperConstants.TYPE], temp_comp_min,
                                                                 temp_storage_min, node.attrib[BaseConstants.SUBTYPE])

                        else:

                            sw_diff = 0

                        # Increase in part prices
                        price_diff = \
                            (new_part_config[1] * self.parts_table.get_part_attrib(new_part_config[0],
                                                                                   HyperConstants.CTO_PRICE)) -\
                            orig_price[cap]

                        # This is to make sure that part replacement happens when increase in part price is lesser than
                        # what we save in chassis, sw price
                        if price_diff < sw_diff + chassis_price_diff:

                            new_node_config[cap] = new_part_config
                            constant = False
                            break

                        else:

                            continue

                    self.current_cpu = new_part_config[0]

                    core_count = self.parts_table.get_part_attrib(self.current_cpu, BaseConstants.CAPACITY)

                    cpu_price_diff = \
                        (new_part_config[1] * self.parts_table.get_part_attrib(new_part_config[0],
                                                                               HyperConstants.CTO_PRICE)) - \
                        orig_price[cap]

                    exceptions = list()

                    if BaseConstants.RAM in change:
                        exceptions.append(BaseConstants.RAM)

                    if BaseConstants.VRAM in change:
                        exceptions.append(BaseConstants.VRAM)

                    if not exceptions:
                        exceptions = None

                    for ssd in parts_to_use[BaseConstants.SSD]:

                        ssd_found, _, _, ssd_part_config = \
                            self.configure_part(ssd, node, BaseConstants.SSD, heterogenous, wl_group, node2, 'ssd_slots')

                        if ssd_found:

                            if BaseConstants.SSD in change and max(ssd_part_config[2], new_part_config[2]) >= \
                                    new_node_config[BaseConstants.SSD][2]:
                                continue

                            if BaseConstants.SSD in change_or_retain and ssd_part_config[2] > new_part_config[2]:
                                continue

                            temp_node_config[BaseConstants.SSD] = ssd_part_config

                            temp_comp_min, temp_storage_min = self.get_hx_comp(node, node2, temp_node_config,
                                                                               wl_group, exceptions)

                            temp_chassis_price = temp_storage_min * node.attrib[BaseConstants.BASE_PRICE]

                            if node2 and temp_comp_min:
                                temp_chassis_price += temp_comp_min * node2.attrib[BaseConstants.BASE_PRICE]

                            # decrease in chassis price
                            chassis_price_diff = chassis_price - temp_chassis_price

                            # decrease in software price
                            if self.license_years:

                                sw_diff = \
                                    sw_cost - self.calc_raw_sw_price(node.attrib[BaseConstants.CPU_CNT][0], core_count,
                                                                     node.attrib[HyperConstants.TYPE], temp_comp_min,
                                                                     temp_storage_min,
                                                                     node.attrib[BaseConstants.SUBTYPE])

                            else:

                                sw_diff = 0

                            ssd_price_diff = \
                                (ssd_part_config[1] * self.parts_table.get_part_attrib(ssd_part_config[0],
                                                                                       HyperConstants.CTO_PRICE)) - \
                                orig_price[BaseConstants.SSD]

                            # This is to make sure that part replacement happens when increase in part price is
                            # lesser than what we save in chassis, sw price
                            if cpu_price_diff + ssd_price_diff < sw_diff + chassis_price_diff:

                                new_node_config = temp_node_config
                                constant = False
                                break

                    else:

                        self.current_cpu = new_node_config[BaseConstants.CPU][0]
                        continue

                    break

        if constant:
            return node_config

        elif self.license_years:

            new_comp_min, new_storage_min = self.get_hx_comp(node, node2, new_node_config, wl_group)

            if new_comp_min == comp_min and new_storage_min == storage_min:
                return node_config

        return self.true_min_decrease(optimal_parts, node, heterogenous, wl_group, node2, new_node_config)

    def balance_parts(self, optimal_parts, node, heterogenous, wl_group, node2, node_config):

        """
        This function does the following:
        1. As this function is run after resolve-under-commit -> true-min cant be any lesser. Hence other fields which
           need nodes lesser than true-min can be refreshed such that their node count comes closed to true-min
        """

        def find_current_optimal(part_config):

            for op_part in optimal_parts[cap]:
                if op_part[0] == part_config[0]:
                    return op_part

        def price_post_slot_norm(part_type, part_name, part_count):

            if node.attrib[HyperConstants.TYPE] == BaseConstants.CTO:
                price_fac = HyperConstants.CTO_PRICE
            else:
                price_fac = HyperConstants.UNIT_PRICE

            if part_type == BaseConstants.CPU:

                return node.attrib['cpu_socket_count'][0] * true_min * self.parts_table.get_part_attrib(part_name,
                                                                                                        price_fac)

            elif part_type == BaseConstants.RAM:

                if '[CUSTOM]' in part_name:
                    return 12 * true_min * self.parts_table.get_part_attrib(part_name, price_fac)

                if '[CUSTOM_6SLOT]' in part_name:
                    return 6 * true_min * self.parts_table.get_part_attrib(part_name, price_fac)

                for ram_slot in sorted(node.attrib['ram_slots']):

                    if ram_slot * true_min >= part_count:
                        return ram_slot * true_min * self.parts_table.get_part_attrib(part_name, price_fac)

            elif part_type == BaseConstants.HDD:

                node_count = (storage_min + self.Fault_Tolerance)
                min_hdd = node_count * node.attrib['hdd_slots'][0]
                norm_hdd = max(min_hdd, part_count)
                norm_hdd = int(ceil(norm_hdd / float(node_count))) * node_count

                return norm_hdd * self.parts_table.get_part_attrib(part_name, price_fac)

            elif part_type == BaseConstants.SSD:

                return node.attrib['ssd_slots'][0] * storage_min * self.parts_table.get_part_attrib(part_name,
                                                                                                    price_fac)

        comp_min, storage_min = self.get_hx_comp(node, node2, node_config, wl_group)
        true_min = storage_min + comp_min

        new_node_config = deepcopy(node_config)

        change = \
            list(filter(lambda x: (x in [BaseConstants.CPU, BaseConstants.RAM] and node_config[x][2] < true_min) or
                             (x in [BaseConstants.HDD, BaseConstants.SSD] and node_config[x][2] < storage_min),
                   [BaseConstants.CPU, BaseConstants.RAM, BaseConstants.HDD, BaseConstants.SSD]))

        change_or_retain = list()

        if BaseConstants.SSD in change and BaseConstants.CPU not in change:
            change_or_retain.append(BaseConstants.CPU)

        for cap in change + change_or_retain:

            current_part = find_current_optimal(new_node_config[cap])

            option_key, slot_key = self.get_cap_keys(cap)

            if cap in [BaseConstants.SSD, BaseConstants.HDD]:
                ref_min = storage_min
            else:
                ref_min = true_min

            if cap == BaseConstants.SSD:

                parts = optimal_parts[cap]

            elif cap in change:

                parts = list(filter(lambda x: x[0] != current_part[0] and x[1] > current_part[1], optimal_parts[cap]))

            elif cap == BaseConstants.CPU:

                parts = list(filter(lambda x: (x[1] + (x[1] % node.attrib['cpu_socket_count'][0])) <=
                                         (node.attrib['cpu_socket_count'][0]) * true_min, optimal_parts[cap]))

            for part in parts:

                part_found, _, _, new_part_details = \
                    self.configure_part(part, node, cap, heterogenous, wl_group, node2, slot_key)

                if part_found and new_part_details[2] <= ref_min:
                    part_price_diff = price_post_slot_norm(cap, new_node_config[cap][0], new_node_config[cap][1]) - \
                                      price_post_slot_norm(cap, new_part_details[0], new_part_details[1])
                else:
                    continue

                if cap == BaseConstants.CPU:

                    self.current_cpu = new_part_details[0]

                    ssd_option_key, ssd_slot_key = self.get_cap_keys(BaseConstants.SSD)

                    for ssd in optimal_parts[BaseConstants.SSD]:

                        ssd_found, _, _, new_ssd_details = \
                            self.configure_part(ssd, node, BaseConstants.SSD, heterogenous, wl_group, node2,
                                                ssd_slot_key)

                        if ssd_found and new_ssd_details[2] <= storage_min:
                            ssd_price_diff = \
                                price_post_slot_norm(BaseConstants.SSD, new_ssd_details[0], new_ssd_details[1]) - \
                                price_post_slot_norm(BaseConstants.SSD, new_node_config[BaseConstants.SSD][0],
                                                     new_node_config[BaseConstants.SSD][1])
                            break
                    else:
                        self.current_cpu = new_node_config[cap][0]
                        continue

                    if part_price_diff + ssd_price_diff > 0:

                        new_node_config[cap] = new_part_details
                        new_node_config[BaseConstants.SSD] = new_ssd_details
                        break

                    else:

                        self.current_cpu = new_node_config[cap][0]
                        continue

                elif part_price_diff > 0:

                    new_node_config[cap] = new_part_details
                    break

        if self.is_large_vm:
            new_node_config = self.solve_large_vm(node, node2, new_node_config, wl_group, heterogenous, optimal_parts)
            if new_node_config is None:
                return None, "Large_Vm_Limit", False
            self.current_cpu = new_node_config[BaseConstants.CPU][0]
        
        '''
        Custom logic to replace Sky RAM with an equally capable Cascade RAM or vice versa
        '''
        is_ram_changed = False
        is_cpu_changed = False
        
        if not self.check_general_rules(new_node_config[BaseConstants.RAM][0], self.current_cpu):

            filtered_rams = list(filter(lambda x: self.check_general_rules(x[0], self.current_cpu),
                                   optimal_parts[BaseConstants.RAM]))

            current_ram_cap = self.parts_table.get_part_attrib(new_node_config[BaseConstants.RAM][0],
                                                               BaseConstants.CAPACITY)

            eq_cap_ram = [ram for ram in filtered_rams
                          if self.parts_table.get_part_attrib(ram[0], BaseConstants.CAPACITY) == current_ram_cap]

            ram_found = False

            if eq_cap_ram:

                new_node_config[BaseConstants.RAM][0] = eq_cap_ram[0][0]
                ram_found = True

            elif filtered_rams:

                # Below variable represents maximum memory CPU can reference
                cpu_ram_limit = self.parts_table.get_part_attrib(self.current_cpu, HyperConstants.RAM_LIMIT) * \
                                 node.attrib['cpu_socket_count'][0]

                # M10 GPUs can refer only 1000GiB of Memory
                if new_node_config[BaseConstants.VRAM][1] and new_node_config[BaseConstants.VRAM][0] == 'HX-GPU-M10':
                    node_ram_limit = min(1000, cpu_ram_limit)
                else:
                    node_ram_limit = cpu_ram_limit

                ram_option_key, ram_slot_key = self.get_cap_keys(BaseConstants.RAM)
                ram_confs = list()

                for ram in filtered_rams:

                    ram_cap = self.parts_table.get_part_attrib(ram[0], BaseConstants.CAPACITY)

                    valid_slots = [slot for slot in node.attrib[ram_slot_key] if slot * ram_cap <= node_ram_limit]

                    if '[CUSTOM]' in ram[0]:
                        valid_slots = [12] if 12 in valid_slots else []

                    if '[CUSTOM_6SLOT]' in ram[0]:
                        valid_slots = [6] if 6 in valid_slots else []

                    if valid_slots:
                        ram_confs.append((valid_slots, ram))

                ram_confs.sort(key=lambda x: max(x[0]) * x[1], reverse=True)

                for valid_slots, ram in ram_confs:

                    temp_node = deepcopy(node)
                    temp_node.attrib[ram_slot_key] = valid_slots

                    ram_found, _, _, new_ram_details = \
                        self.configure_part(ram, temp_node, BaseConstants.RAM, heterogenous, wl_group, node2,
                                            ram_slot_key)

                    if ram_found:
                        new_node_config[BaseConstants.RAM] = new_ram_details
                        is_ram_changed = True
                        break

            if not ram_found:

                filtered_cpus = list(filter(lambda x:
                                       self.check_general_rules(new_node_config[BaseConstants.RAM][0], x[0]),
                                       optimal_parts[BaseConstants.CPU]))

                filtered_cpus = \
                    filter(lambda x: x[1] == new_node_config[BaseConstants.CPU][1], filtered_cpus) + \
                    filter(lambda x: x[1] < new_node_config[BaseConstants.CPU][1], filtered_cpus) + \
                    filter(lambda x: x[1] > new_node_config[BaseConstants.CPU][1], filtered_cpus)

                cpu_option_key, cpu_slot_key = self.get_cap_keys(BaseConstants.CPU)

                for cpu in filtered_cpus:

                    cpu_found, _, _, new_cpu_details = \
                        self.configure_part(cpu, node, BaseConstants.CPU, heterogenous, wl_group, node2,
                                            cpu_slot_key)

                    if cpu_found:

                        self.current_cpu = new_cpu_details[0]

                        ssd_option_key, ssd_slot_key = self.get_cap_keys(BaseConstants.SSD)

                        for ssd in optimal_parts[BaseConstants.SSD]:

                            ssd_found, _, _, new_ssd_details = \
                                self.configure_part(ssd, node, BaseConstants.SSD, heterogenous, wl_group, node2,
                                                    ssd_slot_key)

                            if ssd_found and \
                                    (ssd == optimal_parts[BaseConstants.SSD][-1] or new_ssd_details[2] <= storage_min):
                                new_node_config[BaseConstants.SSD] = new_ssd_details
                                new_node_config[BaseConstants.CPU] = new_cpu_details
                                is_cpu_changed = True
                                break

                        else:
                            continue

                        break

        self.current_cpu = new_node_config[BaseConstants.CPU][0]

        if not self.check_general_rules(new_node_config[BaseConstants.RAM][0], self.current_cpu):
            return None, "No_Part_Combination_Found", False

        if self.is_large_vm and (is_ram_changed or is_cpu_changed):
            new_node_config = self.solve_large_vm(node, node2, new_node_config, wl_group, heterogenous, optimal_parts, True)
            if new_node_config is None:
                return None, "Large_Vm_Limit", False
        
        # Custom logic to adjust minimum number of disks if necessary to achieve IO/s requirements for ROBO workload
        if (wl_group[0].attrib[HyperConstants.INTERNAL_TYPE] in [HyperConstants.ROBO, HyperConstants.ROBO_BACKUP_SECONDARY]) and \
                node.attrib[HyperConstants.TYPE] == 'cto':

            hdd_part_count = new_node_config[BaseConstants.HDD][1]

            hdd_per_server = int(ceil(hdd_part_count / float(true_min + self.Fault_Tolerance)))

            if 'iops_hdd_slots' in node.attrib:
                max_diff = node.attrib['iops_hdd_slots'] - min(node.attrib[BaseConstants.HDD_SLOTS])

            else:
                max_diff = max(node.attrib[BaseConstants.HDD_SLOTS]) - min(node.attrib[BaseConstants.HDD_SLOTS])

            if hdd_per_server < min(node.attrib[BaseConstants.HDD_SLOTS]):
                hdd_per_server = min(node.attrib[BaseConstants.HDD_SLOTS])

            if hdd_per_server < max(node.attrib[BaseConstants.HDD_SLOTS]):

                cur_iops_conv_fac = self.get_scaled_conv_fac(new_node_config[BaseConstants.SSD][0],
                                                                 hdd_per_server, max_diff,
                                                                 node.hercules_on, node.hx_boost_on)

                if wl_group[0].attrib['storage_protocol']  == 'NFS':

                    current_iops_conv_fac = cur_iops_conv_fac[0] * \
                                            self.parts_table.get_part_attrib(self.current_cpu, HyperConstants.SPECLNT) / \
                                            self.parts_table.get_part_attrib(HyperConstants.REF_IOPS_CPU,
                                                                             HyperConstants.SPECLNT)

                else:
                    current_iops_conv_fac = cur_iops_conv_fac[1] * \
                                            self.parts_table.get_part_attrib(self.current_cpu, HyperConstants.SPECLNT) / \
                                            self.parts_table.get_part_attrib(HyperConstants.REF_IOPS_CPU,
                                                                             HyperConstants.SPECLNT)

                normalized_iops = 0
                for wl in wl_group:
                    normalized_iops += wl.original_iops_sum[HyperConstants.ROBO] / float(current_iops_conv_fac)

                while normalized_iops > true_min:

                    hdd_per_server += 1

                    cur_iops_conv_fac = self.get_scaled_conv_fac(new_node_config[BaseConstants.SSD][0],
                                                                     hdd_per_server, max_diff,
                                                                     node.hercules_on, node.hx_boost_on)

                    if wl_group[0].attrib['storage_protocol'] == 'NFS':

                        current_iops_conv_fac = cur_iops_conv_fac[0] * \
                                                self.parts_table.get_part_attrib(self.current_cpu,
                                                                                 HyperConstants.SPECLNT) / \
                                                self.parts_table.get_part_attrib(HyperConstants.REF_IOPS_CPU,
                                                                                 HyperConstants.SPECLNT)

                    else:
                        current_iops_conv_fac = cur_iops_conv_fac[1] * \
                                                self.parts_table.get_part_attrib(self.current_cpu,
                                                                                 HyperConstants.SPECLNT) / \
                                                self.parts_table.get_part_attrib(HyperConstants.REF_IOPS_CPU,
                                                                                 HyperConstants.SPECLNT)

                    normalized_iops = 0

                    for wl in wl_group:
                        normalized_iops += wl.original_iops_sum[HyperConstants.ROBO] / float(current_iops_conv_fac)

            new_fixed_amount = hdd_per_server * (true_min + self.Fault_Tolerance)

            new_node_config[BaseConstants.HDD][1] = new_fixed_amount

        return new_node_config, False, True

    def calculate_part_overhead(self, node, part_name, part_count, cap, slot_key, storage_protocol):

        if not max(node.attrib[slot_key]):
            return 0

        if cap not in node.attrib[BaseConstants.STATIC_OVERHEAD][self.hypervisor]:
            overhead_amt = 0
        else:
            overhead_amt = float(node.attrib[BaseConstants.STATIC_OVERHEAD][self.hypervisor][cap])

        node_count = int(ceil(float(part_count) / float(max(node.attrib[slot_key]))))

        # Node count normalization
        node_count = max(node_count, (self.get_minimum_size(node.attrib[BaseConstants.SUBTYPE],
                                                            self.Fault_Tolerance,
                                                            self.current_cluster, self.highest_rf) - self.Fault_Tolerance))

        node_count = min(node_count, (self.get_max_cluster_value(node.attrib[BaseConstants.SUBTYPE],
                                                                 node.attrib[HyperConstants.DISK_CAGE],
                                                                 self.hypervisor,
                                                                 self.current_cluster) - self.Fault_Tolerance))

        if cap == BaseConstants.RAM and storage_protocol and overhead_amt:
            overhead_amt += 2

        if cap == BaseConstants.CPU and node.hx_boost_on and overhead_amt:
            overhead_amt += 2

        if cap == BaseConstants.HDD:

            hdd_overhead = \
                (overhead_amt / 100.0) * self.parts_table.get_part_attrib(part_name, BaseConstants.CAPACITY) / \
                self.highest_rf

            return part_count * hdd_overhead

        else:

            return overhead_amt * node_count

    def solve_optimal_cluster_count(self, result, group):

        node = result[0]
        node_data = result[1]
        compute_node = result[3]

        ram_calc_min = node_data[BaseConstants.RAM][2]

        compute_min, storage_min = self.get_hx_comp(node, compute_node, node_data, group)

        true_min = storage_min + compute_min

        if storage_min > ram_calc_min:
            overhead_ram_diff = storage_min - ram_calc_min
        else:
            overhead_ram_diff = 0

        accessories = list()

        if compute_min and group[0].attrib[HyperConstants.INTERNAL_TYPE] == HyperConstants.AIML:

            pcie_req = self.parts_table.get_part_attrib(node_data[BaseConstants.VRAM][0], HyperConstants.PCIE_REQ)

            min_gpu_cards = int(min(compute_node.attrib[HyperConstants.PCIE_SLOTS]) / pcie_req)
            max_gpu_cards = int(max(compute_node.attrib[HyperConstants.PCIE_SLOTS]) / pcie_req)
            for cards_per_node in range(min_gpu_cards, max_gpu_cards + 1):
                if cards_per_node * compute_min >= node_data[BaseConstants.VRAM][1]:
                    gpus_from_compute = cards_per_node * compute_min
                    break
            else:
                gpus_from_compute = cards_per_node * compute_min

            gpus_from_hx = 0
            min_gpu_cards = int(min(node.attrib[HyperConstants.PCIE_SLOTS]) / pcie_req)
            max_gpu_cards = int(max(node.attrib[HyperConstants.PCIE_SLOTS]) / pcie_req)
            for cards_per_node in range(min_gpu_cards, max_gpu_cards + 1):
                if cards_per_node * storage_min >= node_data[BaseConstants.VRAM][1] - gpus_from_compute > 0:
                    gpus_from_hx = cards_per_node * storage_min

        else:

            gpus_from_compute = int(ceil(node_data[BaseConstants.VRAM][1] / float(true_min))) * compute_min

            gpus_from_hx = int(ceil(node_data[BaseConstants.VRAM][1] / float(true_min))) * storage_min

        new_node, total_price, hc_accessories = self.initialize_cto_node(node, node_data, storage_min,
                                                                         true_min, overhead_ram_diff,
                                                                         self.Fault_Tolerance, None, group,
                                                                         gpus_from_hx, gpus_from_compute)

        accessories.extend(hc_accessories)

        if compute_min:
            new_compute_node, total_compute_price, compute_accessories = self.initialize_cto_node(compute_node,
                                                                                                  node_data,
                                                                                                  compute_min, true_min,
                                                                                                  0, 0, new_node, group,
                                                                                                  gpus_from_hx,
                                                                                                  gpus_from_compute)
            accessories.extend(compute_accessories)
        else:
            new_compute_node = None
            total_compute_price = 0

        return new_node, storage_min + self.Fault_Tolerance, total_price, new_compute_node, compute_min, \
               total_compute_price, accessories

    def get_hx_comp(self, node, compute, node_data, wl_group, exceptions=None):

        new_node_data = deepcopy(node_data)

        for cap in new_node_data:
            new_node_data[cap][2] += self.Fault_Tolerance

        true_min = max(new_node_data[cap][2] for cap in new_node_data if not exceptions or cap not in exceptions)

        comp, hx = self.get_comp_to_hx_ratio(node.attrib[BaseConstants.SUBTYPE], node.attrib[HyperConstants.DISK_CAGE],
                                             self.hypervisor, self.current_cluster)

        hx_min = self.get_minimum_size(node.attrib[BaseConstants.SUBTYPE], self.Fault_Tolerance, self.current_cluster,
                                       self.highest_rf)

        true_min = max(true_min, hx_min)

        if self.heterogenous:

            comp_max = self.get_possible_computes(self.current_cluster, node.attrib[HyperConstants.DISK_CAGE], node.attrib[BaseConstants.SUBTYPE])

            if compute.attrib[BaseConstants.SUBTYPE] == HyperConstants.AIML_NODE:
                comp_min = sum(wl.num_ds for wl in wl_group if wl.attrib['input_type'] == "Video" and
                                                            wl.attrib['expected_util'] == 'Serious Development')
            else:
                comp_min = 0

        else:

            comp_min = 0
            comp_max = 0

        storage_req = max(0 if exceptions and BaseConstants.HDD in exceptions else new_node_data[BaseConstants.HDD][2],
                          int(ceil((true_min * hx) / float(hx + comp))),
                          int(ceil(comp_min * hx / float(comp))),  # This has been added because of AIML compute node
                          0 if exceptions and BaseConstants.SSD in exceptions else new_node_data[BaseConstants.SSD][2],
                          hx_min)

        compute_req = max(comp_min, true_min - storage_req)
        if compute_req > comp_max:
            storage_req += (compute_req - comp_max)
            compute_req = comp_max

        return compute_req, storage_req - self.Fault_Tolerance

    def calculate_software_price(self, new_node, total_nodes, include_node_mul=True):

        if not self.license_years:
            return 0

        cpu_count = new_node.attrib[BaseConstants.CPU_CNT]
        core_count = new_node.attrib[HyperConstants.CORES_PER_CPU_PRESPECLNT]
        node_subtype = new_node.attrib[BaseConstants.SUBTYPE]

        if node_subtype not in [HyperConstants.COMPUTE, HyperConstants.AIML_NODE]:

            node_type = new_node.attrib[HyperConstants.TYPE]

            if self.current_cluster == 'STRETCH' or new_node.hercules_on:
                license_type = 'PREMIUM'
            else:
                license_type = 'STANDARD'

            hyperflex_sw_price = HyperConstants.LICENSE[license_type]['%s_%s' % (node_type, self.license_years)]

            # 25% discount for ROBO HX licenses
            if node_subtype in [HyperConstants.ROBO_NODE, HyperConstants.AF_ROBO_NODE, HyperConstants.ROBO_240,
                                HyperConstants.ROBO_TWO_NODE, HyperConstants.AF_ROBO_TWO_NODE, HyperConstants.ROBO_AF_240]:
                hyperflex_sw_price *= 0.75

            if self.hypervisor == 'esxi':
                hypervisor_sw_price = cpu_count * HyperConstants.ESX_SOFTWARE_PRICE
            else:
                hypervisor_sw_price = cpu_count * core_count * HyperConstants.HYPER_V_SOFTWARE_PRICE

            total_sw_price = hyperflex_sw_price + hypervisor_sw_price

            if include_node_mul:
                total_sw_price = total_nodes * total_sw_price

            return total_sw_price

        else:

            if self.hypervisor == 'esxi':
                hypervisor_sw_price = cpu_count * HyperConstants.ESX_SOFTWARE_PRICE
            else:
                hypervisor_sw_price = cpu_count * core_count * HyperConstants.HYPER_V_SOFTWARE_PRICE

            if include_node_mul:
                hypervisor_sw_price *= total_nodes

            return hypervisor_sw_price

    def calc_raw_sw_price(self, cpu_count, core_count, node_type, compute_node_count, hx_node_count, node_subtype):

        """
        Specialized Version of Software Price Calculation for Undercommit solving.
        """

        if not self.license_years:
            return 0

        if self.current_cluster == 'STRETCH' or self.hercules:
            license_type = 'PREMIUM'
        else:
            license_type = 'STANDARD'

        hyperflex_sw_price = HyperConstants.LICENSE[license_type]['%s_%s' % (node_type, self.license_years)]

        # 25% discount for ROBO HX licenses
        if node_subtype in [HyperConstants.ROBO_NODE, HyperConstants.AF_ROBO_NODE, HyperConstants.ROBO_240,
                            HyperConstants.ROBO_TWO_NODE, HyperConstants.AF_ROBO_TWO_NODE, HyperConstants.ROBO_AF_240]:
            hyperflex_sw_price *= 0.75

        if self.hypervisor == 'esxi':
            hypervisor_sw_price = cpu_count * HyperConstants.ESX_SOFTWARE_PRICE
        else:
            hypervisor_sw_price = cpu_count * core_count * HyperConstants.HYPER_V_SOFTWARE_PRICE

        total_sw_price = hx_node_count * (hyperflex_sw_price + hypervisor_sw_price) + compute_node_count * \
                         hypervisor_sw_price

        return total_sw_price

    def get_price_factor(self, node_type):
        """
        method to return the actual fraction of price after taking discount into consideration.
        :param node_type:used to determine which discount percentage to use
        :return: 1 for 0 discount, else decimal less than 1 i.e. this when multiplied with total price gives effective
        price
        """
        if node_type == BaseConstants.BUNDLE:
            discount = self.bundle_discount_percent
        elif node_type == BaseConstants.CTO:
            discount = self.cto_discount_percent
        else:
            raise Exception("Node subtype does not match")
        return 1 - discount / 100.0

    @staticmethod
    def validate_gpu_exists(part_name, part_options):

        if part_name == 'HX-GPU-M10' and ('UCSC-GPU-M10' in part_options or 'HX-GPU-M10' in part_options):
            return True
        else:
            for option in part_options:
                if part_name in option:
                    return True
        return False

    def initialize_cto_node(self, new_node, node_configuration, node_count, true_min, overhead_ram_diff,
                            fault_tolerance, hc_node, wl_group, gpus_from_hx, gpus_from_compute):

        total_price = 0

        storage_protocol = False

        for wl in wl_group:
            if wl.attrib['storage_protocol'] and wl.attrib['storage_protocol'] == 'iSCSI':
                _240nodes = ['HX-SP-240M5', 'HXAF-SP-240M5SX', 'HXAF-240M5SX', 'HX240C-M5']
                for _240node in _240nodes:
                    if _240node in new_node.attrib['name']:
                        storage_protocol = True
                        break

        if new_node.attrib[HyperConstants.TYPE] == BaseConstants.BUNDLE:
            price_factor = BaseConstants.PART_PRICE
        else:
            price_factor = HyperConstants.CTO_PRICE

        accessories = list()

        for key in HyperConstants.CAP_LIST:
            if key == BaseConstants.CPU:

                new_node.attrib[HyperConstants.CPU_PART] = node_configuration[key][0]

                new_node.attrib[HyperConstants.CPU_AVAILABILITY] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.CPU_PART],
                                                     BaseConstants.AVAILABILITY)

                #if new_node.attrib[BaseConstants.SUBTYPE] in [HyperConstants.COMPUTE, HyperConstants.AIML_NODE] and \
                     #   'UCS' in new_node.attrib[HyperConstants.BOM_NAME]:
                    # new_node.attrib[HyperConstants.CPU_PART] += '[UCS]'

                new_node.attrib[BaseConstants.CLOCK_SPEED] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.CPU_PART],
                                                     BaseConstants.CLOCK_SPEED)

                new_node.attrib[BaseConstants.BASE_CPU_CLOCK] = self.base_cpu.speed

                new_node.attrib[HyperConstants.CORES_PER_CPU_PRESPECLNT] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.CPU_PART], BaseConstants.CAPACITY)

                new_node.attrib[HyperConstants.SPECLNT] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.CPU_PART], HyperConstants.SPECLNT)

                new_node.attrib[BaseConstants.CORES_PER_CPU] = \
                    new_node.attrib[HyperConstants.CORES_PER_CPU_PRESPECLNT] * new_node.attrib[HyperConstants.SPECLNT]

                cores_per_server = int(ceil(node_configuration[key][1] / float(true_min)))
                if new_node.attrib[BaseConstants.SUBTYPE] in [HyperConstants.AIML_NODE, HyperConstants.COMPUTE]:
                    new_node.attrib[BaseConstants.CPU_CNT] = hc_node.attrib[BaseConstants.CPU_CNT]
                else:
                    new_node.attrib[BaseConstants.CPU_CNT] = \
                        min([core_count for core_count in new_node.attrib[BaseConstants.CPU_CNT]
                             if core_count >= cores_per_server])

                new_node.attrib[HyperConstants.CPU_DESCR] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.CPU_PART],
                                                     HyperConstants.DESCRIPTION)

                new_node.attrib[HyperConstants.TDP] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.CPU_PART], HyperConstants.TDP)

                new_node.attrib[HyperConstants.CPU_PRICE] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.CPU_PART], price_factor)

                new_node.attrib[HyperConstants.BOM_CPU_PART] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.CPU_PART], HyperConstants.BOM_NAME)

                new_node.attrib[HyperConstants.BOM_CPU_DESCR] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.CPU_PART], HyperConstants.BOM_DESCR)

                total_price += \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.CPU_PART], price_factor) * \
                    new_node.attrib[BaseConstants.CPU_CNT]

            elif key == BaseConstants.RAM:

                new_node.attrib[HyperConstants.RAM_PART] = node_configuration[key][0]

                new_node.attrib[HyperConstants.RAM_AVAILABILITY] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.RAM_PART],
                                                     BaseConstants.AVAILABILITY)

                if new_node.attrib[HyperConstants.TYPE] == 'bundle':
                    new_node.attrib[BaseConstants.MIN_SLOTS] = min(new_node.attrib[BaseConstants.RAM_SLOTS])

                new_node.attrib[BaseConstants.RAM_SIZE] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.RAM_PART], BaseConstants.CAPACITY)

                if new_node.attrib[BaseConstants.SUBTYPE] in [HyperConstants.COMPUTE, HyperConstants.AIML_NODE]:

                    # if 'UCS' in new_node.attrib[HyperConstants.BOM_NAME]:
                    #    new_node.attrib[HyperConstants.RAM_PART] += '[UCS]'

                    new_node.attrib[BaseConstants.RAM_SLOTS] = hc_node.attrib[BaseConstants.RAM_SLOTS]
                    ram_per_server = hc_node.attrib[BaseConstants.RAM_SLOTS]

                else:

                    if overhead_ram_diff > 0:
                        static_overhead = float(new_node.attrib[BaseConstants.STATIC_OVERHEAD][self.hypervisor]
                                                [BaseConstants.RAM])

                        if storage_protocol:
                            static_overhead += 2

                        additional_ram = int(ceil(static_overhead *
                                                  overhead_ram_diff / new_node.attrib[BaseConstants.RAM_SIZE]))
                    else:
                        additional_ram = 0

                    min_ram_req_per_server = self.get_min_ram_requirement(key, new_node, wl_group, storage_protocol)
                    min_ram_per_server = \
                        int(ceil(min_ram_req_per_server / new_node.attrib[BaseConstants.RAM_SIZE]))

                    ram_per_server = max(int(ceil((node_configuration[key][1] + additional_ram) / float(true_min))),
                                         min_ram_per_server)

                    if '[CUSTOM]' in new_node.attrib[HyperConstants.RAM_PART]:
                        new_node.attrib[BaseConstants.RAM_SLOTS] = 12
                    elif '[CUSTOM_6SLOT]' in new_node.attrib[HyperConstants.RAM_PART]:
                        new_node.attrib[BaseConstants.RAM_SLOTS] = 6
                    else:
                        new_node.attrib[BaseConstants.RAM_SLOTS] = min([ram_count for ram_count in
                                                                        new_node.attrib[BaseConstants.RAM_SLOTS]
                                                                        if ram_count >= ram_per_server])

                    ram_per_server = new_node.attrib[BaseConstants.RAM_SLOTS]

                new_node.attrib[HyperConstants.RAM_DESCR] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.RAM_PART],
                                                     HyperConstants.DESCRIPTION)

                if new_node.attrib[HyperConstants.TYPE] == 'cto':
                    new_node.attrib[BaseConstants.MIN_SLOTS] = new_node.attrib[BaseConstants.RAM_SLOTS]

                new_node.attrib[HyperConstants.RAM_PRICE] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.RAM_PART], price_factor)

                new_node.attrib[HyperConstants.BOM_RAM_PART] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.RAM_PART], HyperConstants.BOM_NAME)

                new_node.attrib[HyperConstants.BOM_RAM_DESCR] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.RAM_PART], HyperConstants.BOM_DESCR)

                new_node.attrib[HyperConstants.BOM_ADD_MEM] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.RAM_PART],
                                                     HyperConstants.BOM_ADD_MEM)

                total_price += \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.RAM_PART], price_factor) * \
                    ram_per_server

            elif key == BaseConstants.HDD:

                new_node.attrib[HyperConstants.HDD_PART] = node_configuration[key][0]

                new_node.attrib[HyperConstants.HDD_AVAILABILITY] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.HDD_PART],
                                                     BaseConstants.AVAILABILITY)

                new_node.attrib[BaseConstants.MAX_HDD_SLOTS] = max(new_node.attrib[BaseConstants.HDD_SLOTS])

                min_slots = min(new_node.attrib[BaseConstants.HDD_SLOTS])

                if new_node.attrib[BaseConstants.SUBTYPE] in [HyperConstants.COMPUTE, HyperConstants.AIML_NODE]:
                    hdd_per_server = 0
                else:
                    hdd_per_server = int(ceil(node_configuration[key][1] / float(node_count + self.Fault_Tolerance)))
                    if hdd_per_server < min_slots:
                        hdd_per_server = min_slots

                new_node.attrib[BaseConstants.MIN_HDD_SLOTS] = min_slots

                new_node.attrib[BaseConstants.HDD_SLOTS] = hdd_per_server

                new_node.attrib[BaseConstants.HDD_SIZE] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.HDD_PART], BaseConstants.CAPACITY)

                new_node.attrib[HyperConstants.HDD_DESCR] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.HDD_PART],
                                                     HyperConstants.DESCRIPTION)

                new_node.attrib[HyperConstants.HDD_TYPE] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.HDD_PART], HyperConstants.HDD_TYPE)

                new_node.attrib[HyperConstants.HDD_PRICE] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.HDD_PART], price_factor)

                new_node.attrib[HyperConstants.BOM_HDD_PART] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.HDD_PART], HyperConstants.BOM_NAME)

                new_node.attrib[HyperConstants.BOM_HDD_DESCR] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.HDD_PART], HyperConstants.BOM_DESCR)

                if new_node.attrib[HyperConstants.TYPE] == 'bundle' and hdd_per_server > min_slots:

                    total_price += \
                        self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.HDD_PART], price_factor) * \
                        min_slots

                    total_extra_hdds = (node_count + self.Fault_Tolerance) * (hdd_per_server - min_slots)

                    hdd_add_part = \
                        self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.HDD_PART], 'hdd_add_part')

                    hdd_accessories = self.get_additional_hdd_parts(hdd_add_part, total_extra_hdds)

                    for accessory in hdd_accessories:
                        accessories.append(accessory)
                else:
                    total_price += \
                        self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.HDD_PART], price_factor) * \
                        hdd_per_server

            elif key == BaseConstants.SSD:

                new_node.attrib[HyperConstants.SSD_PART] = node_configuration[key][0]

                if new_node.attrib[BaseConstants.SUBTYPE] in [HyperConstants.COMPUTE, HyperConstants.AIML_NODE]:
                    ssd_per_server = 0
                    new_node.attrib[BaseConstants.IOPS] = 0
                else:
                    ssd_per_server = 1
                    new_node.attrib[BaseConstants.IOPS] = 1

                new_node.attrib[BaseConstants.SSD_SLOTS] = ssd_per_server

                new_node.attrib[BaseConstants.SSD_SIZE] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.SSD_PART], BaseConstants.CAPACITY)

                new_node.attrib[HyperConstants.SSD_DESCR] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.SSD_PART],
                                                     HyperConstants.DESCRIPTION)

                new_node.attrib[HyperConstants.SSD_FULL_SIZE] = new_node.attrib[BaseConstants.SSD_SIZE]

                new_node.attrib[HyperConstants.SSD_OUTPUT_CAPACITY] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.SSD_PART],
                                                     HyperConstants.OUTPUT_CAPACITY)

                new_node.attrib[HyperConstants.SSD_PRICE] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.SSD_PART], price_factor)

                new_node.attrib[HyperConstants.SSD_AVAILABILITY] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.SSD_PART],
                                                     BaseConstants.AVAILABILITY)

                new_node.attrib[BaseConstants.IOPS_CONV_FAC] = \
                    deepcopy(self.iops_conv_fac[new_node.attrib[HyperConstants.SSD_PART]][self.threshold_factor])

                # 10.2
                # creation of container iops in new_node

                new_node.attrib[BaseConstants.IOPS_CONV_FAC][self.RF_String][HyperConstants.CONTAINER] = \
                    [new_node.attrib[BaseConstants.IOPS_CONV_FAC][self.RF_String][HyperConstants.VSI][0] / 2.0,
                     new_node.attrib[BaseConstants.IOPS_CONV_FAC][self.RF_String][HyperConstants.VSI][1] / 2.0]

                if (new_node.attrib[BaseConstants.SUBTYPE] in ['robo', 'robo_two_node', 'robo_240']) and \
                        new_node.attrib[HyperConstants.TYPE] == 'cto':

                    if 'iops_hdd_slots' in new_node.attrib:
                        max_diff = new_node.attrib['iops_hdd_slots'] - new_node.attrib[BaseConstants.MIN_HDD_SLOTS]
                    else:
                        max_diff = new_node.attrib[BaseConstants.MAX_HDD_SLOTS] - \
                                   new_node.attrib[BaseConstants.MIN_HDD_SLOTS]

                    new_node.attrib[BaseConstants.IOPS_CONV_FAC][self.RF_String][HyperConstants.ROBO] = \
                        self.get_scaled_conv_fac(new_node.attrib[HyperConstants.SSD_PART],
                                                 new_node.attrib[BaseConstants.HDD_SLOTS], max_diff,
                                                 new_node.hercules_on, new_node.hx_boost_on)

                for wl_type in new_node.attrib[BaseConstants.IOPS_CONV_FAC][self.RF_String]:
                    current_spec = self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.CPU_PART],
                                                                    HyperConstants.SPECLNT)

                    ref_spec = float(self.parts_table.get_part_attrib(HyperConstants.REF_IOPS_CPU,
                                                                      HyperConstants.SPECLNT))

                    if wl_group[0].attrib['storage_protocol'] == 'NFS':
                        new_node.attrib[BaseConstants.IOPS_CONV_FAC][self.RF_String][wl_type][0] *= current_spec / ref_spec
                    else:
                        new_node.attrib[BaseConstants.IOPS_CONV_FAC][self.RF_String][wl_type][1] *= current_spec / ref_spec

                new_node.attrib[HyperConstants.BOM_SSD_PART] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.SSD_PART], HyperConstants.BOM_NAME)

                new_node.attrib[HyperConstants.BOM_SSD_DESCR] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.SSD_PART], HyperConstants.BOM_DESCR)

                total_price += \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.SSD_PART], price_factor) * \
                    ssd_per_server

            elif key == BaseConstants.VRAM:

                if new_node.attrib[BaseConstants.SUBTYPE] in [HyperConstants.COMPUTE, HyperConstants.AIML_NODE]:

                    if node_configuration[key][0] == 'HX-GPU-M10' and 'UCS' in new_node.attrib[HyperConstants.BOM_NAME]:
                        new_node.attrib[HyperConstants.GPU_PART] = 'UCSC-GPU-M10'
                    else:
                        new_node.attrib[HyperConstants.GPU_PART] = node_configuration[key][0]

                    gpus_per_server = int(ceil(gpus_from_compute / float(node_count)))

                else:

                    new_node.attrib[HyperConstants.GPU_PART] = node_configuration[key][0]
                    gpus_per_server = int(ceil(gpus_from_hx / float(node_count)))

                total_gpus = gpus_per_server * node_count

                new_node.attrib[HyperConstants.GPU_AVAILABILITY] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.GPU_PART],
                                                     BaseConstants.AVAILABILITY)

                new_node.attrib[HyperConstants.GPU_SLOTS] = gpus_per_server

                new_node.attrib[HyperConstants.GPU_CAP] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.GPU_PART],
                                                     BaseConstants.CAPACITY)

                new_node.attrib[HyperConstants.GPU_DESCR] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.GPU_PART],
                                                     HyperConstants.DESCRIPTION)

                new_node.attrib[HyperConstants.GPU_PRICE] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.GPU_PART], price_factor)

                new_node.attrib[BaseConstants.VRAM] = \
                    new_node.attrib[HyperConstants.GPU_SLOTS] * new_node.attrib[HyperConstants.GPU_CAP]

                new_node.attrib[HyperConstants.BOM_GPU_PART] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.GPU_PART], HyperConstants.BOM_NAME)
                new_node.attrib[HyperConstants.BOM_GPU_DESCR] = \
                    self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.GPU_PART], HyperConstants.BOM_DESCR)

                total_gpu_price = self.parts_table.get_part_attrib(new_node.attrib[HyperConstants.GPU_PART],
                                                                   HyperConstants.CTO_PRICE) * total_gpus

                if total_gpus:
                    gpu_acc = dict()
                    if new_node.attrib[HyperConstants.GPU_PART] == 'HX-GPU-220-T4-16':
                        gpu_acc[HyperConstants.ACC_NAME] = new_node.attrib[HyperConstants.BOM_GPU_PART]
                    else:
                        gpu_acc[HyperConstants.ACC_NAME] = new_node.attrib[HyperConstants.GPU_PART]

                    gpu_acc[HyperConstants.ACC_DESCR] = new_node.attrib[HyperConstants.GPU_DESCR]
                    gpu_acc[HyperConstants.ACC_COUNT] = \
                        total_gpus + new_node.attrib[HyperConstants.GPU_SLOTS] * fault_tolerance
                    gpu_acc[HyperConstants.ACC_TYPE] = 'GPU'
                    gpu_acc[HyperConstants.ACC_BUNDLE_COUNT] = 1
                    gpu_acc[HyperConstants.ACC_PRICE] = total_gpu_price
                    accessories.append(gpu_acc)

        total_price += new_node.attrib[BaseConstants.BASE_PRICE]
        new_node.attrib[BaseConstants.BASE_PRICE] = total_price

        if new_node.attrib[BaseConstants.SUBTYPE] in [HyperConstants.COMPUTE, HyperConstants.AIML_NODE]:

            total_nodes = node_count

        else:

            total_nodes = node_count + fault_tolerance

            if new_node.hercules_on:
                total_price += HyperConstants.HERCULES_CARD_COST

        total_price = total_price * total_nodes

        total_price += self.calculate_software_price(new_node, total_nodes)

        if 'use_chassis' in new_node.attrib.keys() and new_node.attrib['use_chassis']:
            chassis_price = self.parts_table.get_part_attrib(new_node.attrib['chassis_options'],
                                                             HyperConstants.UNIT_PRICE)

            num_chassis = int(ceil(node_count / 8.0))

            total_price += num_chassis * chassis_price

            new_node.attrib[HyperConstants.BOM_CHASSIS_NAME] = \
                self.parts_table.get_part_attrib(new_node.attrib['chassis_options'], HyperConstants.BOM_NAME)

            new_node.attrib[HyperConstants.BOM_CHASSIS_DESCR] = \
                self.parts_table.get_part_attrib(new_node.attrib['chassis_options'], HyperConstants.BOM_DESCR)

            new_node.attrib[HyperConstants.BOM_CHASSIS_COUNT] = num_chassis

        for cap in HyperConstants.WL_CAP_LIST:
            new_node.calculate_overhead(cap, self.hypervisor, storage_protocol)
            new_node.calc_cap(cap)
            new_node.calc_capex_opex()

        total_price *= self.get_price_factor(new_node.attrib[HyperConstants.TYPE])
        return new_node, total_price, accessories

    def solve_optimum_ram_per_server(self, ram_part_count, minimum_servers, ram_slots):

        min_ram_slots = int(ceil(ram_part_count / float(minimum_servers)))

        if min_ram_slots <= 8 and 8 in ram_slots:
            min_ram_slots = 8
        elif min_ram_slots <= 16 and 16 in ram_slots:
            min_ram_slots = 16
        elif min_ram_slots <= 24 and 24 in ram_slots:
            min_ram_slots = 24
        else:
            raise HXException("Ram_Too_Large " + self.logger_header)

        return min_ram_slots

    def get_additional_hdd_parts(self, hdd_part, part_count):

        accessories = list()

        single_drive_price = self.parts_table.get_part_attrib(hdd_part, BaseConstants.PART_PRICE)

        drive_pack_options = self.parts_table.get_part_attrib(hdd_part, 'drive_pack_option')

        sorted_drive_packs = list()

        if len(drive_pack_options) > 0:
            for drive_pack in drive_pack_options:
                drive_pack_cap = self.parts_table.get_part_attrib(drive_pack, BaseConstants.CAPACITY)
                drive_pack_price = self.parts_table.get_part_attrib(drive_pack, BaseConstants.PART_PRICE)

                if drive_pack_price / float(drive_pack_cap) > single_drive_price:
                    continue

                sorted_drive_packs.append([drive_pack, drive_pack_cap])

            sorted_drive_packs = sorted(sorted_drive_packs, key=itemgetter(1), reverse=True)

        current_count = part_count

        for drive_pack in sorted_drive_packs:
            drive_packs_used = current_count / drive_pack[1]

            if drive_packs_used > 0:
                current_count -= drive_packs_used * drive_pack[1]
                hdd_acc = dict()
                hdd_acc[HyperConstants.ACC_NAME] = drive_pack[0]
                hdd_acc[HyperConstants.ACC_DESCR] = \
                    self.parts_table.get_part_attrib(drive_pack[0], HyperConstants.DESCRIPTION)
                hdd_acc[HyperConstants.ACC_COUNT] = drive_packs_used
                hdd_acc[HyperConstants.ACC_TYPE] = 'Capacity Drive'
                hdd_acc[HyperConstants.ACC_BUNDLE_COUNT] = drive_pack[1]
                hdd_acc[HyperConstants.ACC_PRICE] = \
                    drive_packs_used * self.parts_table.get_part_attrib(drive_pack[0], BaseConstants.PART_PRICE)
                accessories.append(hdd_acc)

        if current_count > 0:
            hdd_acc = dict()
            hdd_acc[HyperConstants.ACC_NAME] = self.parts_table.get_part_attrib(hdd_part, HyperConstants.BOM_NAME)
            hdd_acc[HyperConstants.ACC_DESCR] = self.parts_table.get_part_attrib(hdd_part, HyperConstants.DESCRIPTION)
            hdd_acc[HyperConstants.ACC_COUNT] = current_count
            hdd_acc[HyperConstants.ACC_TYPE] = 'Capacity Drive'
            hdd_acc[HyperConstants.ACC_BUNDLE_COUNT] = 1
            hdd_acc[HyperConstants.ACC_PRICE] = single_drive_price * current_count
            accessories.append(hdd_acc)

        return accessories

    def get_scaled_conv_fac(self, ssd_part, hdd_per_server, max_diff, hercules, hx_boost):

        # 10.2
        if self.iops_conv_fac[ssd_part][self.threshold_factor][self.RF_String][HyperConstants.ROBO]:
            status = True
            max_iops = self.iops_conv_fac[ssd_part][self.threshold_factor][self.RF_String][HyperConstants.ROBO]

        if not status:
            raise HXException(self.logger_header + "Missing_IOPS_Value")

        conv_fac_table = self.parts_table.get_part_attrib(ssd_part, BaseConstants.MIN_IOPS_CONV_FAC)

        min_iops = conv_fac_table[self.threshold_factor][self.RF_String][HyperConstants.ROBO]

        pcnt_increase = 0

        if hercules:
            pcnt_increase += HyperConstants.HERCULES_IOPS[HyperConstants.ROBO]

        if hx_boost:
            pcnt_increase += HyperConstants.HX_BOOST_IOPS[HyperConstants.ROBO]

        min_iops *= (1 + pcnt_increase / 100.0)

        iops_conv_fac = []

        for dif_iops in max_iops:
            dif_iops *= (1 + pcnt_increase / 100.0)

            iops_conv_fac.append(dif_iops - (dif_iops - min_iops) * (1 - (hdd_per_server - 3) / float(max_diff)))

        return iops_conv_fac


    def solve_large_vm(self, hx_node, co_node, init_node_config, wl_group, heterogenous, optimal_parts, increase_node_count = False):

        """
        This function does the following:
        1. check if user requirement for CPU and RAM is high for a particular workload
        2. If yes, increase the Compute Node based on below logic
        3. increase_node_count = True, execute only increase the node count logic
        """

        def find_current_optimal(part_config):

            for op_part in optimal_parts[cap]:
                if op_part[0] == part_config[0]:
                    return op_part

        def find_part_capacity(part_name):

            return self.parts_table.get_part_attrib(part_name, BaseConstants.CAPACITY)

        def get_current_ram_capacity(part_info, true_min):

            ram_capacity = find_part_capacity(part_info[0])

            if '[CUSTOM]' in part_info[0]:
                return 12 * ram_capacity
            else:
                for ram_slot in hx_node.attrib[BaseConstants.RAM_SLOTS]:
                    if ram_slot * true_min >= part_info[1]:
                        return ram_slot * ram_capacity

        def check_vm_fit(cap, number_of_vm, part_info, true_min):

            if cap == BaseConstants.RAM:

                current_ram_capacity = get_current_ram_capacity(part_info, true_min)

                if (number_of_vm * self.large_ram_req) + ram_overhead_amt > current_ram_capacity:
                    return False, 0
                else:
                    return True, current_ram_capacity

            elif cap == BaseConstants.CPU:

                for cpu_slots in hx_node.attrib[BaseConstants.CPU_CNT]:
                    if cpu_slots * true_min >= part_info[1]:
                        break

                curr_core_per_node = cpu_slots * find_part_capacity(part_info[0]) * find_cpu_specint(part_info[0])

                if (number_of_vm * self.large_cpu_req) + cpu_overhead_amt > curr_core_per_node:
                    return False, 0

                return True, 0

        def get_cpu_ram_limit(part_name):

            cpu_ram_limit = self.parts_table.get_part_attrib(part_name, HyperConstants.RAM_LIMIT)
            node_ram_limit = hx_node.attrib["cpu_socket_count"][0] * cpu_ram_limit

            return node_ram_limit

        def find_cpu_specint(part_name):

            return self.parts_table.get_part_attrib(part_name, HyperConstants.SPECLNT)

        def calculate_node_price(part_info, hx_min, co_min):

            max_node_count = hx_min + co_min
            if hx_node.attrib[HyperConstants.TYPE] == BaseConstants.CTO:
                price_fac = HyperConstants.CTO_PRICE
            else:
                price_fac = HyperConstants.UNIT_PRICE

            # part_type == BaseConstants.CPU:

            cpu_price = hx_node.attrib['cpu_socket_count'][0] * max_node_count * \
                        self.parts_table.get_part_attrib(part_info[BaseConstants.CPU][0], price_fac)

            # calculate ram price
            ram_price = 0
            if '[CUSTOM]' in part_info[BaseConstants.RAM][0]:
                ram_price = 12 * max_node_count * self.parts_table.get_part_attrib(part_info[BaseConstants.RAM][0],
                                                                                   price_fac)

            for ram_slot in sorted(hx_node.attrib['ram_slots']):
                if ram_slot * max_node_count >= part_info[BaseConstants.RAM][1]:
                    ram_price = ram_slot * max_node_count * self.parts_table.get_part_attrib(
                        part_info[BaseConstants.RAM][0], price_fac)

            # part_type == BaseConstants.SSD:
            ssd_price = hx_node.attrib['ssd_slots'][0] * storage_min * \
                        self.parts_table.get_part_attrib(part_info[BaseConstants.SSD][0], price_fac)

            total_price = cpu_price + ram_price + ssd_price
            
            chassis_price = calculate_chassis_price(part_info, hx_min, co_min)
            return total_price + chassis_price
        
        def calculate_chassis_price(part_info, hx_min, co_min ):
            chassis_price = hx_min * hx_node.attrib[BaseConstants.BASE_PRICE]
            if co_node and co_min:
                chassis_price += comp_min * co_node.attrib[BaseConstants.BASE_PRICE]
            
            if self.license_years:
                core_count = self.parts_table.get_part_attrib(part_info[BaseConstants.CPU][0], BaseConstants.CAPACITY)

                sw_cost = self.calc_raw_sw_price(hx_node.attrib[BaseConstants.CPU_CNT][0], core_count,
                                                hx_node.attrib[HyperConstants.TYPE], co_min, hx_min,
                                                hx_node.attrib[BaseConstants.SUBTYPE])
            return chassis_price + sw_cost

            
        # PART 1 -- Try to decrease #VMs per node so that node count goes up
        # Take a deepcopy before apply the changes of part 1
        node_config1 = deepcopy(init_node_config)
        max_node_count = max(node_config1[cap][2] for cap in node_config1)

        for cpu_slots in hx_node.attrib[BaseConstants.CPU_CNT]:
            if cpu_slots * max_node_count >= node_config1[BaseConstants.CPU][1]:
                break

        cpu_core = find_part_capacity(node_config1[BaseConstants.CPU][0])
        cpu_specint = find_cpu_specint(node_config1[BaseConstants.CPU][0])

        # Number of reference cores the system provides per node
        curr_core_per_node = cpu_slots * cpu_core * cpu_specint

        if '[CUSTOM]' in node_config1[BaseConstants.RAM][0]:
            ram_slots = 12
        else:
            for ram_slots in hx_node.attrib[BaseConstants.RAM_SLOTS]:
                if ram_slots * max_node_count >= node_config1[BaseConstants.RAM][1]:
                    break

        ram_capacity = find_part_capacity(node_config1[BaseConstants.RAM][0])
        current_ram_capacity = ram_slots * ram_capacity

        comp_min, storage_min = self.get_hx_comp(hx_node, co_node, node_config1, wl_group)
        total_node = storage_min + comp_min

        num_large_vms = max(self.num_large_vms_cpu, self.num_large_vms_ram)
        vm_per_node = ceil(num_large_vms / float(total_node))

        # get CPU overhead per node
        cpu_overhead_amt = hx_node.attrib[BaseConstants.STATIC_OVERHEAD][self.hypervisor].get(BaseConstants.CPU, 0)

        # get RAM overhead per node
        ram_overhead_amt = hx_node.attrib[BaseConstants.STATIC_OVERHEAD][self.hypervisor].get(BaseConstants.RAM, 0)

        vm_node_change = False

        while (((vm_per_node * self.large_cpu_req) + cpu_overhead_amt > curr_core_per_node) or \
                ((vm_per_node * self.large_ram_req) + ram_overhead_amt > current_ram_capacity)):

            vm_per_node -= 1
            vm_node_change = True

            if vm_per_node == 0:
                node_config1 = None

        if node_config1:

            new_total_node = int(ceil(num_large_vms / vm_per_node))

            if new_total_node == total_node or not vm_node_change:
                return node_config1

            extra_nodes = new_total_node - total_node

            # change CPU - increment CPU node count
            node_config1[BaseConstants.CPU][2] += extra_nodes
            node_config1[BaseConstants.CPU][1] += (extra_nodes * cpu_slots)

            # change RAM - increment RAM node count
            node_config1[BaseConstants.RAM][2] += extra_nodes
            node_config1[BaseConstants.RAM][1] += (extra_nodes * ram_slots)

            # check for exceeding Max_Cluster_Size
            hx_max_cluster = self.get_max_cluster_value(hx_node.attrib[BaseConstants.SUBTYPE],
                                                        hx_node.attrib[HyperConstants.DISK_CAGE],
                                                        self.hypervisor,
                                                        self.current_cluster)

            compute_max = self.get_max_cluster_value(hx_node.attrib[BaseConstants.SUBTYPE],
                                                     hx_node.attrib[HyperConstants.DISK_CAGE],
                                                     self.hypervisor,
                                                     self.current_cluster,
                                                     True)

            max_cluster_size = hx_max_cluster - self.Fault_Tolerance
            if heterogenous:
                max_cluster_size += compute_max

            # override total_node with old value
            comp_min, storage_min = self.get_hx_comp(hx_node, co_node, node_config1, wl_group)
            total_node = storage_min + comp_min

            # check if size is not exceeding max_cluster_size
            if total_node > max_cluster_size:
                node_config1 = None

        # call after balance_parts logic
        if increase_node_count:
            return node_config1 if node_config1 else None
        
        # PART 2 -- check for denser CPU or RAM and check for price. total_node is the max node count limit
        # take a deepcopy before apply part 2 changes
        node_config2 = deepcopy(init_node_config)
        max_node_count = max(init_node_config[cap][2] for cap in init_node_config)

        parts_to_use = dict()
        refresh_parts = [BaseConstants.CPU, BaseConstants.RAM, BaseConstants.SSD]

        for cap in refresh_parts:

            if cap == BaseConstants.SSD:

                parts = optimal_parts[cap]

            else:

                current_part = find_current_optimal(node_config2[cap])
                parts = list(filter(lambda x: x[1] <= current_part[1], optimal_parts[cap]))

            parts_to_use[cap] = parts

        new_ram_capacity = get_current_ram_capacity(node_config2[BaseConstants.RAM], max_node_count)

        # to check both CPU and RAM found. False = one of the CPU or RAM not found
        is_alter_node_config = True
        for cap in [BaseConstants.RAM, BaseConstants.CPU]:

            # set the  number of VMs per node
            vm_per_node = int(ceil((self.num_large_vms_ram if cap == BaseConstants.RAM else self.num_large_vms_cpu) / float(max_node_count)))
            max_node_count = max(node_config2[cap][2] for cap in node_config2)
            option_key, slot_key = self.get_cap_keys(cap)

            for part in parts_to_use[cap]:

                part_found, _, _, part_config = \
                    self.configure_part(part, hx_node, cap, heterogenous, wl_group, co_node, slot_key)

                if part_found and part_config[2] <= node_config2[cap][2]:

                    temp_node_count = max(max_node_count, part_config[2])

                    # other_cap = BaseConstants.CPU if cap == BaseConstants.RAM else BaseConstants.RAM
                    if cap == BaseConstants.RAM:

                        is_fit, ram_capacity = check_vm_fit(cap, vm_per_node, part_config, temp_node_count)

                        if is_fit:
                            new_ram_capacity = ram_capacity
                            node_config2[cap] = part_config
                            break

                    elif cap == BaseConstants.CPU:

                        is_fit, _ = check_vm_fit(cap, vm_per_node, part_config, temp_node_count)

                        cpu_ram_limit = get_cpu_ram_limit(part_config[0])

                        if is_fit and cpu_ram_limit >= new_ram_capacity and part_config[0] == node_config2[cap][0]:

                            break

                        elif is_fit and cpu_ram_limit >= new_ram_capacity:

                            # change ssd details
                            ssd_option_key, ssd_slot_key = self.get_cap_keys(BaseConstants.SSD)

                            for ssd_part in parts_to_use[BaseConstants.SSD]:

                                ssd_found, _, _, new_ssd_details = \
                                    self.configure_part(ssd_part, hx_node, BaseConstants.SSD, heterogenous, wl_group,
                                                        co_node, ssd_slot_key)

                                if ssd_found and (new_ssd_details[2] <= node_config2[cap][2]):

                                    node_config2[BaseConstants.SSD] = new_ssd_details
                                    # change CPU
                                    node_config2[cap] = part_config
                                    break

                            else:

                                continue

                            break
                else:

                    continue
            else:
                is_alter_node_config = False

        if node_config1 and is_alter_node_config:

            # -- choose the bese node based on price between increase_node_config VS alter_node_config
            comp, storage = self.get_hx_comp(hx_node, co_node, node_config1, wl_group)
            node_price1 = calculate_node_price(node_config1, storage , comp)

            comp, storage = self.get_hx_comp(hx_node, co_node, node_config2, wl_group)
            node_price2 = calculate_node_price(node_config2, storage , comp)

            final_node_config = node_config1 if node_price1 < node_price2 else node_config2

        elif node_config1:

            final_node_config = node_config1

        elif is_alter_node_config:

            final_node_config = node_config2

        else:
            # when both methods didn't work. Need to handle this
            return None

        # set optimal parts for CPU and RAM - required in the logic for RAM and CPU rules - balance_parts function
        optimal_parts[BaseConstants.RAM] = list(filter(lambda x: x[1] <= final_node_config[BaseConstants.RAM][1],
                                                  optimal_parts[BaseConstants.RAM]))

        optimal_parts[BaseConstants.CPU] = list(filter(lambda x: x[1] <= final_node_config[BaseConstants.CPU][1],
                                                  optimal_parts[BaseConstants.CPU]))

        # return temp_node_config if is_node_config_change else new_node_config
        return final_node_config

    def find_large_vm_partition(self, wl_group):
        """
        check if any large vm exists
        """

        #initilize for each partition
        self.large_cpu_req = 0
        self.large_ram_req = 0
        self.num_large_vms_cpu = 0
        self.num_large_vms_ram = 0
        self.is_large_vm = False
        
        # define large VM and RAM size
        large_ram = 256  # in Gib
        large_cpu = 16  # in cores

        vcpu_reqs = list()
        ram_reqs = list()

        for wl in wl_group:

            if wl.attrib[HyperConstants.INTERNAL_TYPE] in [HyperConstants.VSI]:

                vcpu_reqs.append((wl.num_inst, wl.attrib[HyperConstants.VCPUS_PER_VM],
                                  wl.attrib[HyperConstants.VCPUS_PER_CORE]))

                ram_reqs.append((wl.num_inst, wl.attrib[HyperConstants.RAM_PER_VM]))

            elif wl.attrib[HyperConstants.INTERNAL_TYPE] in [HyperConstants.OLAP, HyperConstants.OLTP,
                                                             HyperConstants.OOLAP, HyperConstants.OOLTP]:

                vcpu_reqs.append((wl.num_inst, wl.attrib[HyperConstants.VCPUS_PER_DB],
                                  wl.attrib[HyperConstants.VCPUS_PER_CORE]))

                ram_reqs.append((wl.num_inst, wl.attrib[HyperConstants.RAM_PER_DB]))

        # set the required large VM and large RAM size
        if vcpu_reqs and max(vcpu_req[1] for vcpu_req in vcpu_reqs) >= large_cpu:
            self.large_cpu_req = max(vcpu_req[1] for vcpu_req in vcpu_reqs)

        if ram_reqs and max(ram_req[1] for ram_req in ram_reqs) >= large_ram:
            self.large_ram_req = max(ram_req[1] for ram_req in ram_reqs)

        if self.large_ram_req or self.large_cpu_req:

            self.is_large_vm = True

            for num_vms, vcpu_req, _ in vcpu_reqs:
                if vcpu_req == self.large_cpu_req:
                    self.num_large_vms_cpu = num_vms
                    break

            for num_vms, ram_req in ram_reqs:
                if ram_req == self.large_ram_req:
                    self.num_large_vms_ram = num_vms
                    break

            # number of VM instance.
            # self.num_large_vms = max(self.num_large_vms_cpu, self.num_large_vms_ram)

            # Setting number of Pcores needed. For this we need to consider over-provisioning. Condition is for when only RAM is large
            if self.large_cpu_req:
                self.large_cpu_req /= min(vcpu_req[2] for vcpu_req in vcpu_reqs if vcpu_req[1] == self.large_cpu_req)

'''
    DO NOT REMOVE THESE COMMENTED CODES
    def solve_generic_sizing(self, node1, node2, wl_sums, MaxCluster, wl_type):
        MAX_CLUSTER = self.get_max_cluster_value(node1.attrib[SUBTYPE],
                                                 node1.attrib[DISK_CAGE],
                                                 self.hypervisor,
                                                 self.current_cluster)

        min_nodes = self.get_minimum_size(node1.attrib[SUBTYPE], self.Fault_Tolerance)

        if MaxCluster:
            MaxCluster = MAX_CLUSTER
        else:
            MaxCluster = 9999

        N1 = LpVariable("N1", min_nodes-self.Fault_Tolerance, MaxCluster-self.Fault_Tolerance, LpInteger)
        # GPU Variable
        N3 = LpVariable("N3", 0, 9999, LpInteger)

        if node2:
            N2 = LpVariable("N2", 0, MaxCluster, LpInteger)
            N4 = LpVariable("N4", 0, 9999, LpInteger)
        prob = LpProblem("Generic Solution", LpMinimize)

        # construct equation for software price & get discount price

        node1_base_hx_esx = (node1.attrib[BASE_PRICE] + self.calculate_software_price(node1, 0, False)) * \
                            self.get_price_factor(node1.attrib[TYPE]) * N1
        if node2:
            node2_base_hx_esx = (node2.attrib[BASE_PRICE] + self.calculate_software_price(node2, 0, False)) * \
                                self.get_price_factor(node2.attrib[TYPE]) * N2
            if node2.attrib.get("use_chassis"):
                Bool = LpVariable("Bool", 0, 1, LpInteger)
                chassis_price = self.parts_table.get_part_attrib(node2.attrib['chassis_options'], UNIT_PRICE)
                prob += node1_base_hx_esx + node2_base_hx_esx + \
                        node1.attrib[GPU_PRICE]*N3 + node2.attrib[GPU_PRICE]*N4 + \
                        Bool*chassis_price
                prob += N2 <= Bool * 50
            else:
                prob += node1_base_hx_esx + node2_base_hx_esx + \
                        node1.attrib[GPU_PRICE]*N3 + node2.attrib[GPU_PRICE]*N4
            prob += N2 <= N1 + self.Fault_Tolerance
        else:
            prob += node1_base_hx_esx + node1.attrib[GPU_PRICE]*N3
        # capacity constriant equation formation
        for cap in CAP_LIST:
            if node1.attrib[SUBTYPE] == ALL_FLASH and cap == HDD:
                threshold_key = ALL_FLASH_HDD
            else:
                threshold_key = cap

            if node1.attrib[HyperConstants.DISK_CAGE] == HyperConstants.LARGE_FORM_FACTOR and cap == BaseConstants.HDD:
                threshold_key = HyperConstants.LFF_HDD
            threshold_value = self.get_threshold_value(wl_type, threshold_key)

            if self.Fault_Tolerance > 0 and cap in [HDD]:

                hdd_cap = wl_sums[cap] - node1.raw_cap[cap] * threshold_value * self.Fault_Tolerance + node1.overhead[cap]

                if node2:
                    compute_hdd_capacity = node2.cap[cap]*N2
                else:
                    compute_hdd_capacity = 0
                prob += ((node1.raw_cap[cap]*N1 + compute_hdd_capacity) * threshold_value -
                         node1.overhead[cap]*N1) / float(self.highest_rf) \
                        >= hdd_cap
            elif cap in [VRAM]:
                if node2:
                    compute_gpu_capacity = node2.attrib[GPU_CAP]*N4
                else:
                    compute_gpu_capacity = 0
                prob += (node1.attrib[GPU_CAP] * N3 + compute_gpu_capacity) * threshold_value \
                        >= wl_sums[cap]
                prob += N3 <= N1 * node1.attrib[GPU_SLOTS]
                if compute_gpu_capacity:
                    prob += N4 <= N2 * node2.attrib[GPU_SLOTS]
#            elif cap in [SSD] and node1.attrib[SUBTYPE] == 'all-flash':
#                continue 
            else:
                if node2:
                    compute_capacity = node2.cap[cap]*N2
                else:
                    compute_capacity = 0
                prob += (node1.raw_cap[cap]*N1 + compute_capacity) * threshold_value - node1.overhead[cap]*N1 \
                        >= wl_sums[cap]
        # prob.writeLP("Generic.lp")
        prob.solve(GLPK_CMD(msg=0))

        if LpStatus[prob.status] == 'Optimal':
            use_chassis = False
            for variable in prob.variables():
                if variable.name == 'N1':
                    num_nodes1 = int(variable.varValue) + self.Fault_Tolerance
                elif variable.name == 'N2':
                    num_nodes2 = int(variable.varValue)
                elif variable.name == 'N3':
                    num_gpu1 = int(variable.varValue)
                elif variable.name == 'N4':
                    num_gpu2 = int(variable.varValue)
                elif variable.name == 'Bool':
                    if variable.varValue == 1:
                        use_chassis = True

            if wl_sums[VRAM] > 0 and num_gpu1 + self.Fault_Tolerance <= num_nodes1 * node1.attrib[GPU_SLOTS]:
                num_gpu1 += self.Fault_Tolerance
            elif wl_sums[VRAM] > 0 and not node2 is None and node2.attrib[GPU_SLOTS] > 0:

                necessary_nodes = int(ceil(self.Fault_Tolerance / float(node2.attrib[GPU_SLOTS])))

                if num_gpu2 + self.Fault_Tolerance <= num_nodes2 * node2.attrib[GPU_SLOTS]:
                    num_gpu2 += self.Fault_Tolerance
                elif num_nodes2 + necessary_nodes <= MAX_CLUSTER:
                    num_nodes2 += necessary_nodes
                    num_gpu2 += self.Fault_Tolerance
                else:
                    return False, list()
            elif wl_sums[VRAM] > 0:
                return False, list()

            node1_price = self.get_pricing(node1, num_nodes1)
            node1_gpu_price = num_gpu1 * node1.attrib[GPU_PRICE]
            if node2 is not None:
                node2_price = self.get_pricing(node2, num_nodes2)
                if use_chassis:
                    node2_price += chassis_price
                node2_gpu_price = num_gpu2 * node2.attrib[GPU_PRICE]
            else:
                num_nodes2 = 0
                node2_price = 0
                node2_gpu_price = 0
                num_gpu2 = 0

            accessories = list()
            if num_gpu1 > 0:
                hc_gpu = dict()
                hc_gpu[ACC_NAME] = node1.attrib[GPU_PART]
                hc_gpu[ACC_DESCR] = node1.attrib[GPU_DESCR]
                hc_gpu[ACC_COUNT] = num_gpu1
                hc_gpu[ACC_TYPE] = 'GPU'
                hc_gpu[ACC_BUNDLE_COUNT] = 1
                hc_gpu[ACC_PRICE] = node1_gpu_price
                accessories.append(hc_gpu)
            if num_gpu2 > 0:
                compute_gpu = dict()
                compute_gpu[ACC_NAME] = node2.attrib[GPU_PART]
                compute_gpu[ACC_DESCR] = node2.attrib[GPU_DESCR]
                compute_gpu[ACC_COUNT] = num_gpu2
                compute_gpu[ACC_TYPE] = 'GPU'
                compute_gpu[ACC_BUNDLE_COUNT] = 1
                compute_gpu[ACC_PRICE] = node2_gpu_price
                accessories.append(compute_gpu)         

            total_price = node1_price + node2_price + sum([acc[ACC_PRICE] for acc in accessories])

            cluster_information = {NODE : node1, NUM : num_nodes1, PRICE : total_price , COMPUTE : node2,\
                                   NUM_COMPUTE : num_nodes2, ACC: accessories}

            self.add_heterogenous_result(cluster_information)

            return True,[num_nodes1, num_nodes2, node1_price+node2_price+node1_gpu_price+node2_gpu_price]

        else:
#            logger.error("Unable to Solve. LP Status: %s" %LpStatus[prob.status])
            return False, list()

        def log_results_to_csv(self, heterogenous):

        if os.environ.has_key('OPENSHIFT_REPO_DIR'):
            from local_settings import BASE_DIR
            fileHandler = open(os.path.join(BASE_DIR,"log.csv"), "w")
        else:
            from sizer.local_settings import BASE_DIR
            fileHandler = open(os.path.join(BASE_DIR,"log.csv"), "w")

        for item in self.result:
            hyperconverged_node = item[NODE]
            hyperconverged_node_count = item[NUM]

            outputString = hyperconverged_node.attrib[MODEL] + "," + str(hyperconverged_node_count) + "," + str(hyperconverged_node.attrib[RAM_SLOTS]) + ","

            if heterogenous:
                compute_node = item[COMPUTE]
                compute_count = item[NUM_COMPUTE]

                outputString += compute_node.attrib[MODEL] + "," + str(compute_count) + "," 

            outputString += str(item[PRICE]) + "\n"

            fileHandler.write(outputString)

        fileHandler.close()

    def log_results_to_general_log(self, heterogenous):

        for item in self.result:
            hyperconverged_node = item[NODE]
            hyperconverged_node_count = item[NUM]

            outputString = hyperconverged_node.attrib[MODEL] + "," + str(hyperconverged_node_count) + "," + str(hyperconverged_node.attrib[RAM_SLOTS]) + ","

            if heterogenous and item[COMPUTE] is not None:
                compute_node = item[COMPUTE]
                compute_count = item[NUM_COMPUTE]

                outputString += compute_node.attrib[MODEL] + "," + str(compute_count) + ","

            outputString += str(item[PRICE])

            logger.info(" %s %s" %(self.logger_header, outputString))
'''
