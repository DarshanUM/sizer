from .logger_class import SizerLogger
from .settings_class import InitThreshold, Hypervisor
from hyperconverged.models import Thresholds, IopsConvFactor, SpecIntData, Rules, Part
from hyperconverged.utilities.infinite_dict import infinite_dict
from hyperconverged.exception import HXException

from .attrib import HyperConstants
from base_sizer.solver.attrib import BaseConstants
from math import ceil


class Threshold(InitThreshold):

    def __init__(self, threshold_factor):
        InitThreshold.__init__(self, threshold_factor)
        self.thresholds = infinite_dict()
        self.load_thresholds()

    def load_thresholds(self):
        self.logger.debug('Initiating load thresholds for %s' % self.threshold_factor)
        threshold_table = Thresholds.objects.filter(threshold_category=self.threshold_factor)
        for threshold in threshold_table:
            self.thresholds[threshold.workload_type][threshold.threshold_category][threshold.threshold_key] = \
                threshold.threshold_value
        self.logger.debug('Exiting load threshold function for %s' % self.threshold_factor)

    def get_threshold_value(self, workload_type, threshold_key, workloads=None):

        workload_type = HyperConstants.ROBO if (workload_type == HyperConstants.ROBO_BACKUP_SECONDARY) else workload_type
        workload_type = HyperConstants.VSI if (workload_type == HyperConstants.ROBO_BACKUP) else workload_type
        try:
            threshold_value = self.thresholds[workload_type][self.threshold_factor][threshold_key]
        except KeyError:
            raise HXException("Missing_Threshold_Value" + self.logger_header)

        # 3 = Full Capacity
        if workload_type in [HyperConstants.VDI, HyperConstants.VDI_INFRA] and workloads and self.threshold_factor != 3:

            num_infra = \
                sum(wl.attrib[HyperConstants.INTERNAL_TYPE] == HyperConstants.VDI_INFRA for wl in workloads)

            threshold_value -= 10 * num_infra

        return threshold_value / 100.0


class Iops(Hypervisor):

    def __init__(self, threshold_factor, hypervisor):

        Hypervisor.__init__(self, threshold_factor, hypervisor)
        self.iops_conv_fac = infinite_dict()
        self.load_iops_table()

    def load_iops_table(self):

        iops_table = IopsConvFactor.objects.filter(hypervisor=self.get_hypervisor_value(),
                                                   threshold=self.threshold_factor)

        # 10.2 - iops of NFS and iSCSI are stored as a list
        for iops in iops_table:
            self.iops_conv_fac[iops.part_name][iops.threshold][iops.replication_factor][iops.workload_type] = \
                [iops.iops_conv_factor, iops.iscsi_iops]

    def get_iops_value(self, part_name, threshold_factor, rf_string, workload_type, protocol):

        # 10.2 new argument "protocol" is added to get_iops_value for either NFS or iSCSI
        workload_type = HyperConstants.ROBO if (workload_type == HyperConstants.ROBO_BACKUP_SECONDARY) else workload_type
        workload_type = HyperConstants.VSI if (workload_type == HyperConstants.ROBO_BACKUP) else workload_type
        if protocol == 'NFS':
            if workload_type in [HyperConstants.CONTAINER, HyperConstants.AIML, HyperConstants.ANTHOS]:

                iops_val = self.iops_conv_fac[part_name][threshold_factor][rf_string][HyperConstants.VSI][0]
                return True, iops_val * 0.5

            else:

                iops_val = self.iops_conv_fac[part_name][threshold_factor][rf_string][workload_type][0]
                return True, iops_val

        else:

            if workload_type in [HyperConstants.CONTAINER, HyperConstants.AIML, HyperConstants.ANTHOS]:

                iops_val = self.iops_conv_fac[part_name][threshold_factor][rf_string][HyperConstants.VSI][1]
                return True, iops_val * 0.5

            else:

                iops_val = self.iops_conv_fac[part_name][threshold_factor][rf_string][workload_type][1]
                return True, iops_val


class HXDataPlatform(SizerLogger, Iops, Threshold):

    def initialise_settings(self, settings_json):

        self.settings_json = settings_json
        self.result_name = self.settings_json[BaseConstants.RESULT_NAME]
        self.partition_wl = False if self.settings_json.get(HyperConstants.SINGLE_CLUSTER, False) else True
        self.heterogenous = self.settings_json[HyperConstants.HETEROGENOUS]
        self.hercules = False
        self.hx_boost = False
        self.license_years = self.settings_json.get(HyperConstants.LICENSE_YEARS, 3)
        self.bundle_discount_percent = self.settings_json.get(HyperConstants.BUNDLE_DISCOUNT, 0)
        self.cto_discount_percent = self.settings_json.get(HyperConstants.CTO_DISCOUNT, 0)
        self.base_cpu = SpecIntData.objects.get(is_base_model=True)
        if 'server_type' in self.settings_json:
            self.server_type = self.settings_json['server_type']

    def __init__(self, settings_json, scenario_id):

        self.initialise_settings(settings_json)

        SizerLogger.__init__(self, scenario_id)
        Threshold.__init__(self, self.settings_json[HyperConstants.THRESHOLD])
        Iops.__init__(self, self.settings_json[HyperConstants.THRESHOLD], self.settings_json[BaseConstants.HYPERVISOR])

    @staticmethod
    def get_minimum_size(subtype, fault_tolerance, cluster_type, replication_factor):

        if subtype in [HyperConstants.ROBO_NODE, HyperConstants.AF_ROBO_NODE,
                       HyperConstants.ROBO_TWO_NODE, HyperConstants.AF_ROBO_TWO_NODE]:
            if replication_factor == 3:
                return 3
            else:
                return 2
        elif subtype in [HyperConstants.ROBO_240, HyperConstants.ROBO_AF_240]:
            return 3

        if cluster_type == HyperConstants.STRETCH:
            return 2

        min_size = 3
        if 2 <= fault_tolerance <= 4:
            return fault_tolerance + min_size

        return min_size

    @staticmethod
    def get_max_cluster_value(node_type, disk_cage, hypervisor, cluster_type, compute=False):

        """
        This function should be static as it is being used in ReverseSizerFilter.
        This function returns maxium nodes possible i.e. if maximum nodes per cluster is 64 and if we can have up to 32
        HX nodes, it returns 32 CO nodes even though a combination of 12 HX, 52 CO nodes can exist
        This assumption doesnt affect sizing as it serves as limiting factor for part sizing. since the final number
        used by resource solver is either addition of HX,CO or only HX, it wont affect sizing
        """
        if cluster_type == HyperConstants.STRETCH:
            if node_type in [HyperConstants.LFF_NODE, HyperConstants.LFF_12TB_NODE]:
                max_cluster = 8

            else:
                max_cluster = 16

        elif hypervisor == 'hyperv':
            max_cluster = 16

        elif node_type in [HyperConstants.ROBO_NODE, HyperConstants.AF_ROBO_NODE, HyperConstants.ROBO_240, HyperConstants.ROBO_AF_240]:
            max_cluster = 4

        elif node_type in [HyperConstants.ROBO_TWO_NODE, HyperConstants.AF_ROBO_TWO_NODE]:
            max_cluster = 2

        elif node_type in [HyperConstants.VEEAM_NODE]:
            max_cluster = 8

        elif node_type in [HyperConstants.LFF_NODE, HyperConstants.LFF_12TB_NODE]:
            max_cluster = 16

        elif disk_cage == HyperConstants.SMALL_FORM_FACTOR:
            max_cluster = 32

        else:
            raise Exception('Could not return the max cluster size i.e. unrecognizable combination')

        if compute:
            if cluster_type == HyperConstants.STRETCH:
                max_cluster = min(max_cluster * HXDataPlatform.get_comp_to_hx_ratio(node_type, disk_cage, hypervisor,
                                                                                     cluster_type)[0], 16)
            else:
                max_cluster = min(max_cluster * HXDataPlatform.get_comp_to_hx_ratio(node_type, disk_cage, hypervisor,
                                                                                     cluster_type)[0], 32)

        return max_cluster

    @staticmethod
    def get_possible_computes(cluster_type, disk_cage, node_subtype):

        """
        This function was written in order to return actual number of compute node possible. For stretch clusters in
        each site HX+CO can go up to 32 but CO can go up to 21 [because of 2:1 restriction](This was assumed as 16 in
        above function because we had assumed HX as 16 nodes)
        """
        if cluster_type == HyperConstants.STRETCH:

            if disk_cage == HyperConstants.SMALL_FORM_FACTOR:
                return 21
            else:
                return 16
        else:
            return 32

    @staticmethod
    def get_comp_to_hx_ratio(node_type, disk_cage, hypervisor, cluster_type):

        # 2,1 means for each HX node there can be 2 compute nodes
        if hypervisor == 'hyperv':
            return 1, 1
        else:
            return 2, 1

    def get_hxdp_version(self, res_dict):

        node_detail = dict()

        for node_info in res_dict['node_info']:
            if node_info[HyperConstants.MODEL_DETAILS][BaseConstants.SUBTYPE] != HyperConstants.COMPUTE:
                subtype = node_info[HyperConstants.MODEL_DETAILS][BaseConstants.SUBTYPE]

            node_detail[node_info[HyperConstants.MODEL_DETAILS][BaseConstants.SUBTYPE]] = dict()

            subtype_dict = node_detail[node_info[HyperConstants.MODEL_DETAILS][BaseConstants.SUBTYPE]]
            subtype_dict[HyperConstants.NUM_NODES] = node_info[HyperConstants.NUM_NODES]
            subtype_dict[BaseConstants.MODEL] = node_info[HyperConstants.MODEL_DETAILS][BaseConstants.MODEL]
            subtype_dict[HyperConstants.DISK_CAGE] = node_info[HyperConstants.MODEL_DETAILS][HyperConstants.DISK_CAGE]
            subtype_dict[HyperConstants.SSD_PART] = \
                node_info[HyperConstants.MODEL_DETAILS].get(HyperConstants.SSD_PART, '')

        if HyperConstants.COMPUTE in node_detail and \
                node_detail[HyperConstants.COMPUTE][HyperConstants.NUM_NODES] > \
                node_detail[subtype][HyperConstants.NUM_NODES]:
            return '3.0'

        if (HyperConstants.ALL_FLASH not in subtype and
            node_detail[subtype][HyperConstants.NUM_NODES] > 8) or \
                (node_detail[subtype][HyperConstants.NUM_NODES] > 16):
            return '3.0'

        if node_detail[subtype][HyperConstants.DISK_CAGE] == HyperConstants.LARGE_FORM_FACTOR:
            return '3.0'

        if 'COLDSTREAM' in node_detail[subtype][HyperConstants.SSD_PART]:
            return '3.0'

        # To support fixed_config without workload - check for wl_list is added.
        if res_dict['wl_list'] and res_dict['wl_list'][0][HyperConstants.CLUSTER_TYPE] == HyperConstants.STRETCH:
            return '3.0'

        if self.hypervisor == 'hyperv':
            return '3.0'

        return '2.6'


def fetch_rules():

    return Rules.objects.all()
