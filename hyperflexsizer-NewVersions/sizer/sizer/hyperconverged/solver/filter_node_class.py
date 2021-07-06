from base_sizer.solver.attrib import BaseConstants
from .attrib import HyperConstants
from .node_sizing import HyperConvergedNode
from hyperconverged.exception import HXException
from copy import deepcopy
import copy

class FilterNode(object):

    def __init__(self, nodes):

        self.GPU_Capable = False
        self.DB_Capable = False
        self.wl_sum = dict()

        self.bundle_list = list()
        self.cto_list = list()

        self.hyperconverged_node_list = list()
        self.compute_node_list = list()
        self.all_flash_node_list = list()
        self.robo_node_list = list()
        self.epic_node_list = list()
        self.veeam_node_list = list()

        self.cto_hyperconverged = list()
        self.cto_compute = list()
        self.cto_all_flash = list()
        self.cto_robo = list()
        self.cto_epic = list()
        self.cto_veeam = list()

        if nodes:
            self.load_nodes(nodes)
            self.find_heterogenous_nodes()

    def load_nodes(self, nodes):

        for node_name, hercules_avail, hx_boost_avail, node_json in nodes:

            if node_json[BaseConstants.NODE_TYPE] == BaseConstants.BUNDLE:

                self.bundle_list.append(HyperConvergedNode(node_name, hercules_avail, hx_boost_avail, node_json))

            elif node_json[BaseConstants.NODE_TYPE] == BaseConstants.CTO:

                self.cto_list.append(HyperConvergedNode(node_name, hercules_avail, hx_boost_avail, node_json))

            else:
                self.logger.error("%s Unknown Model Type = %s" %
                                  (self.logger_header, node_json[BaseConstants.NODE_TYPE]))

    def find_heterogenous_nodes(self):

        """
        Used to generate node lists for usage later, along with eliminate border cases caused by filtering.
        """

        for node in self.bundle_list:

            if node.attrib[BaseConstants.SUBTYPE] in [HyperConstants.HYPER, HyperConstants.LFF_NODE,
                                                      HyperConstants.LFF_12TB_NODE]:
                self.hyperconverged_node_list.append(node)

            elif node.attrib[BaseConstants.SUBTYPE] in [HyperConstants.COMPUTE, HyperConstants.AIML_NODE]:
                self.compute_node_list.append(node)

            elif node.attrib[BaseConstants.SUBTYPE] in [HyperConstants.ALL_FLASH, HyperConstants.ALLNVME_NODE_8TB,
                                                        HyperConstants.ALLNVME_NODE, HyperConstants.ALL_FLASH_7_6TB]:
                self.all_flash_node_list.append(node)

            elif node.attrib[BaseConstants.SUBTYPE] in [HyperConstants.ROBO_NODE, HyperConstants.AF_ROBO_NODE,
                                                        HyperConstants.ROBO_TWO_NODE, HyperConstants.AF_ROBO_TWO_NODE,
                                                        HyperConstants.ROBO_240, HyperConstants.ROBO_AF_240]:
                self.robo_node_list.append(node)

            elif node.attrib[BaseConstants.SUBTYPE] in [HyperConstants.EPIC_NODE]:
                self.epic_node_list.append(node)

            elif node.attrib[BaseConstants.SUBTYPE] in [HyperConstants.VEEAM_NODE]:
                self.veeam_node_list.append(node)

        self.amend_cto_list()

        for node in self.cto_list:

            if node.attrib[BaseConstants.SUBTYPE] in [HyperConstants.HYPER,
                                                      HyperConstants.LFF_12TB_NODE]:

                self.cto_hyperconverged.append(node)

            elif node.attrib[BaseConstants.SUBTYPE] in [HyperConstants.LFF_NODE]:
                self.cto_hyperconverged.append(node)
                self.cto_veeam.append(node)

            elif node.attrib[BaseConstants.SUBTYPE] in [HyperConstants.COMPUTE, HyperConstants.AIML_NODE]:
                self.cto_compute.append(node)

            elif node.attrib[BaseConstants.SUBTYPE] in [HyperConstants.ALL_FLASH, HyperConstants.ALLNVME_NODE_8TB,
                                                        HyperConstants.ALLNVME_NODE, HyperConstants.ALL_FLASH_7_6TB]:
                self.cto_all_flash.append(node)

            elif node.attrib[BaseConstants.SUBTYPE] in [HyperConstants.ROBO_NODE, HyperConstants.AF_ROBO_NODE,
                                                        HyperConstants.ROBO_TWO_NODE, HyperConstants.AF_ROBO_TWO_NODE,
                                                        HyperConstants.ROBO_240, HyperConstants.ROBO_AF_240]:
                self.cto_robo.append(node)

            elif node.attrib[BaseConstants.SUBTYPE] in [HyperConstants.EPIC_NODE]:
                self.cto_epic.append(node)

            elif node.attrib[BaseConstants.SUBTYPE] in [HyperConstants.VEEAM_NODE, HyperConstants.LFF_NODE]:
                self.cto_veeam.append(node)

    def amend_cto_list(self):

        """
        Check if any of the nodes contain custom HDD, those with specific cluster max, slots, static overhead. In such
        case, create a separate node for the custom HDD and add to the cto_list.
        """
        new_nodes = list()
        old_nodes = list()
        for node in self.cto_list:

            lst_hdd_option = deepcopy(node.attrib[HyperConstants.HDD_OPT])
            for hdd_part in lst_hdd_option:

                if self.parts_table.is_part_attrib(hdd_part, HyperConstants.CUSTOM):

                    node.attrib[HyperConstants.HDD_OPT].remove(hdd_part)

                    custom_properties = self.parts_table.get_part_attrib(hdd_part, HyperConstants.CUSTOM)

                    new_node = deepcopy(node)
                    new_node.name = node.name + " [" + hdd_part.split(' ')[0] + "_HDD]"
                    new_node.attrib[HyperConstants.HDD_OPT] = [hdd_part]
                    new_node.attrib[BaseConstants.HDD_SLOTS] = custom_properties[BaseConstants.HDD_SLOTS]
                    new_node.attrib[BaseConstants.STATIC_OVERHEAD] = custom_properties[BaseConstants.STATIC_OVERHEAD]
                    new_node.attrib[BaseConstants.SUBTYPE] = custom_properties[BaseConstants.SUBTYPE]
                    new_nodes.append(new_node)

            # check if the original node has any HDDs other than the custom. If not remove from the node_list
            if not node.attrib[HyperConstants.HDD_OPT]:
                old_nodes.append(node)

        for old_node in old_nodes:
            self.cto_list.remove(old_node)

        self.cto_list.extend(new_nodes)

    def validate_node_list(self, node_list, cluster_type, wl_list):

        if not node_list:

            if cluster_type == HyperConstants.ORACLE:

                raise HXException('No_DB_Nodes' + self.logger_header)

            elif cluster_type == HyperConstants.SPLUNK:

                raise HXException('SPLUNK_AF_Nodes' + self.logger_header)

            else:

                raise HXException("No Hyperflex nodes could be selected due to filters, Please check the filters")

        if cluster_type in [HyperConstants.VDI, HyperConstants.RDSH] and \
                self.check_gpu_requirement(wl_list) and not any(max(node.attrib[HyperConstants.PCIE_SLOTS])
                                                                for node in node_list):

            raise HXException("No_GPU_Nodes" + self.logger_header)

        if cluster_type == HyperConstants.AIML and \
                not any(max(node.attrib[HyperConstants.PCIE_SLOTS]) for node in node_list) and \
                not all(wl.attrib['input_type'] == "Video" and wl.attrib['expected_util'] == 'Serious Development'
                        for wl in wl_list):

            raise HXException("No_GPU_Nodes" + self.logger_header)

    def get_compatible_nodes(self, cluster_type, bundle_only, wl_list):

        node_list = list()

        if cluster_type in [HyperConstants.DB, HyperConstants.ORACLE, HyperConstants.SPLUNK, HyperConstants.CONTAINER]:

            if bundle_only == HyperConstants.BUNDLE_ONLY:
                node_list.extend(self.all_flash_node_list)

            elif bundle_only == HyperConstants.CTO_ONLY:
                node_list.extend(self.cto_all_flash)

            else:
                node_list.extend(self.all_flash_node_list)
                node_list.extend(self.cto_all_flash)

        elif cluster_type == HyperConstants.ROBO or cluster_type == HyperConstants.ROBO_BACKUP_SECONDARY:

            if bundle_only == HyperConstants.BUNDLE_ONLY:
                node_list.extend(self.robo_node_list)

            elif bundle_only == HyperConstants.CTO_ONLY:
                node_list.extend(self.cto_robo)

            else:
                node_list.extend(self.robo_node_list)
                node_list.extend(self.cto_robo)

        elif cluster_type == HyperConstants.EPIC:

            if bundle_only == HyperConstants.BUNDLE_ONLY:
                node_list.extend(self.epic_node_list)

            elif bundle_only == HyperConstants.CTO_ONLY:
                node_list.extend(self.cto_epic)

            else:
                node_list.extend(self.epic_node_list)
                node_list.extend(self.cto_epic)

        elif cluster_type == HyperConstants.VEEAM:

            if bundle_only == HyperConstants.BUNDLE_ONLY:
                node_list.extend(self.veeam_node_list)

            elif bundle_only == HyperConstants.CTO_ONLY:
                node_list.extend(self.cto_veeam)

            else:
                node_list.extend(self.veeam_node_list)
                node_list.extend(self.cto_veeam)

        else:

            if bundle_only == HyperConstants.BUNDLE_ONLY:
                node_list.extend(self.hyperconverged_node_list)
                node_list.extend(self.all_flash_node_list)

            elif bundle_only == HyperConstants.CTO_ONLY:
                node_list.extend(self.cto_hyperconverged)
                node_list.extend(self.cto_all_flash)

            else:
                node_list.extend(self.hyperconverged_node_list)
                node_list.extend(self.all_flash_node_list)

                node_list.extend(self.cto_hyperconverged)
                node_list.extend(self.cto_all_flash)

        compute_list = list()

        if bundle_only == HyperConstants.BUNDLE_ONLY:
            compute_list.extend(self.compute_node_list)

        elif bundle_only == HyperConstants.CTO_ONLY:
            compute_list.extend(self.cto_compute)

        else:
            compute_list.extend(self.compute_node_list)
            compute_list.extend(self.cto_compute)

        if self.current_cluster == HyperConstants.STRETCH:
            # Copy because its causing Hercules availability false for Normal cluster
            node_list = copy.deepcopy(node_list)
            for node in node_list:
                node.hercules_avail = True

            node_list = list(filter(lambda node: 'SED' not in node.name, node_list))

        self.validate_node_list(node_list, cluster_type, wl_list)

        return node_list, compute_list

    def check_gpu_requirement(self, wl_list):

        self.wl_sum[HyperConstants.VRAM] = sum(self.get_req(wl, HyperConstants.VRAM) for wl in wl_list)
        return bool(self.wl_sum[HyperConstants.VRAM])

    def filter_vic(self, node_list, robo_wls):

        def search_ssd_opts(node):

            if search_term == 'SINGLE':
                node.attrib[HyperConstants.SSD_OPT] = [ssd for ssd in node.attrib[HyperConstants.SSD_OPT]
                                                       if '40G-10G' not in ssd and 'DUAL' not in ssd]
            else:
                node.attrib[HyperConstants.SSD_OPT] = [ssd for ssd in node.attrib[HyperConstants.SSD_OPT]
                                                       if search_term in ssd]

            if not node.attrib[HyperConstants.SSD_OPT]:
                return False
            else:
                return True

        mod_lan_list = [wl.attrib[HyperConstants.MOD_LAN] for wl in robo_wls]

        if HyperConstants.MOD_10G in mod_lan_list:
            search_term = '40G-10G'
        elif HyperConstants.DUAL_SWITCH in mod_lan_list:
            search_term = 'DUAL'
        elif HyperConstants.SINGLE_SWITCH in mod_lan_list:
            search_term = 'SINGLE'
        else:
            search_term = ''

        return [node for node in node_list if search_ssd_opts(node)]

    def post_partn_fil(self, nodes, computes, cluster_type, partn_grp):

        filtered_nodes = deepcopy(nodes)
        filtered_computes = deepcopy(computes)

        if len(partn_grp) > 1:
            # DR cluster = True

            for node in filtered_nodes:
                node.hercules_avail = False

        if cluster_type == HyperConstants.EPIC:

            # when its an EPIC cluster, only one workload sits in one cluster
            cpu = partn_grp[0][0].attrib['cpu']
            cpu = cpu.split(' ')[-1]

            # No CPU filter required because we have separate node for EPIC wls
            filtered_nodes = [node for node in filtered_nodes if cpu in node.attrib[HyperConstants.CPU_OPT][0]]

            filtered_computes = [node for node in filtered_computes if node.attrib['subtype'] == 'compute']

        if cluster_type == HyperConstants.ROBO or cluster_type == HyperConstants.ROBO_BACKUP_SECONDARY:

            filtered_nodes = self.filter_vic(filtered_nodes, partn_grp[0])

        if cluster_type == HyperConstants.VDI:

            # Restrict LFF from VDI workloads
            filtered_nodes = [node for node in filtered_nodes
                              if node.attrib[HyperConstants.DISK_CAGE] != HyperConstants.LARGE_FORM_FACTOR]

            if any(wl.attrib.get(HyperConstants.GPU_STATUS, False) for wl in partn_grp[0]):

                gpu_nodes = list()

                frame_buff_req = [getattr(wl, 'frame_buff', 0) for wl in partn_grp[0]
                                  if wl.attrib.get(HyperConstants.GPU_STATUS, False)]

                for node in filtered_nodes:

                    if node.attrib['pcie_slots'] == [0]:
                        continue

                    node.hercules_avail = False

                    usable_gpus = list()

                    for gpu in node.attrib[HyperConstants.GPU_OPT]:

                        frame_buff_list = self.parts_table.get_part_attrib(gpu, HyperConstants.FRAME_BUFF)

                        if all(buffer_req in frame_buff_list for buffer_req in frame_buff_req):

                            usable_gpus.append(gpu)

                    if usable_gpus:

                        node.attrib[HyperConstants.GPU_OPT] = usable_gpus
                        gpu_nodes.append(node)

                filtered_nodes = gpu_nodes

        # # Check for 7.6 TB SSD disks are NOT allowed in Hyper-V
        # if self.hypervisor == 'hyperv':
        #
        #     hyperv_nodes = list()
        #
        #     for node in filtered_nodes:
        #
        #         disks_intersect_list = [hdd for hdd in node.attrib['hdd_options'] if '7.6TB' not in hdd]
        #         if not disks_intersect_list:
        #             continue
        #
        #         node.attrib['hdd_options'] = disks_intersect_list
        #         hyperv_nodes.append(node)
        #
        #     filtered_nodes = deepcopy(hyperv_nodes)

        self.validate_node_list(filtered_nodes, cluster_type, partn_grp[0])

        return filtered_nodes, filtered_computes

    def pre_partn_filter(self, nodes, computes, cluster_type, wl_list):

        filtered_nodes = list()
        filtered_computes = list()

        for node in nodes:

            if any(wl.attrib[HyperConstants.INTERNAL_TYPE] == HyperConstants.RDSH for wl in wl_list):

                new_node = deepcopy(node)

                for wl in filter(lambda x: x.attrib[HyperConstants.INTERNAL_TYPE] == HyperConstants.RDSH, wl_list):

                    for cpu in node.attrib['cpu_options']:

                        cpu_clock = float(self.parts_table.get_part_attrib(cpu, HyperConstants.FREQUENCY))
                        cpu_capacity = float(self.parts_table.get_part_attrib(cpu, "capacity"))

                        if cpu in new_node.attrib['cpu_options'] and ((cpu_clock * cpu_capacity) < wl.clock_per_vm):
                            new_node.attrib['cpu_options'].remove(cpu)

                if new_node.attrib['cpu_options']:

                    filtered_nodes.append(new_node)

            elif cluster_type == HyperConstants.AIML:

                new_node = deepcopy(node)

                gpu_type = wl_list[0].attrib['gpu_type']

                if (all(x.attrib['input_type'] == 'Text Input' for x in wl_list) or
                    not all(x.attrib['input_type'] == 'Video' and x.attrib['expected_util'] == 'Serious Development'
                            for x in wl_list)) and new_node.attrib['pcie_slots'] == [0]:
                    continue

                new_node.attrib['gpu_options'] = \
                    list(filter(lambda x:
                                self.parts_table.get_part_attrib(x, 'filter_tag') == gpu_type and 'V100-32' not in x,
                                new_node.attrib['gpu_options']))

                if new_node.attrib['gpu_options']:
                    filtered_nodes.append(new_node)

            elif cluster_type == HyperConstants.ROBO or cluster_type == HyperConstants.ROBO_BACKUP_SECONDARY:

                highest_rf = max(wl.attrib[HyperConstants.REPLICATION_FACTOR] for wl in wl_list)

                if highest_rf == 3:
                    if node.attrib['subtype'] in [HyperConstants.ROBO_NODE, HyperConstants.AF_ROBO_NODE,
                                                HyperConstants.ROBO_240, HyperConstants.ROBO_AF_240]:
                        filtered_nodes.append(deepcopy(node))
                else:
                    filtered_nodes.append(deepcopy(node))

            else:

                filtered_nodes.append(deepcopy(node))

        if not filtered_nodes and any(wl.attrib[HyperConstants.INTERNAL_TYPE] == HyperConstants.RDSH for wl in wl_list):
            raise HXException("Unable to find a CPU that can fit an entire VM. Please check the filters")

        if not filtered_nodes and any((wl.attrib[HyperConstants.INTERNAL_TYPE] == HyperConstants.ROBO or wl.attrib[HyperConstants.INTERNAL_TYPE] == HyperConstants.ROBO_BACKUP_SECONDARY) for wl in wl_list):
            raise HXException("ROBO_WL_RF3")

        for co_node in computes:

            new_co_node = deepcopy(co_node)

            if cluster_type == HyperConstants.AIML:

                if any(wl.attrib['input_type'] == "Video" and wl.attrib['expected_util'] == 'Serious Development'
                       for wl in wl_list):

                    if new_co_node.attrib[BaseConstants.SUBTYPE] != HyperConstants.AIML_NODE:
                        continue

                elif new_co_node.attrib[BaseConstants.SUBTYPE] == HyperConstants.AIML_NODE:
                    continue

                filtered_computes.append(new_co_node)

            elif new_co_node.attrib[BaseConstants.SUBTYPE] == HyperConstants.AIML_NODE:
                continue

            else:

                filtered_computes.append(new_co_node)

        return filtered_nodes, filtered_computes
