import configparser
import copy
import math

from collections import Counter

import os
from hyperconverged.models import *
from base_sizer.solver.attrib import BaseConstants
from .attrib import HyperConstants
from .node_sizing import *
from .wl import *


class UtilizationGenerator(object):

    def __init__(self, sizer_instance):
        def define_configs():
            """
            Thresholds defined as a python config file in sizer/sizing_config.cfg. Currently assumes numbers,
            no strings.
            """
            config = configparser.ConfigParser()
            if 'OPENSHIFT_REPO_DIR' in os.environ:
                from local_settings import BASE_DIR
            else:
                from sizer.local_settings import BASE_DIR

            config.read(os.path.join(BASE_DIR, 'sizer/sizing_config.cfg'))
            '''Define version variables for use within the sizer'''
            config_section = 'Versions'

            self.sizer_version = config.get(config_section, 'Sizer_Version')
            self.hx_version = config.get(config_section, 'HX_Version')

        self.replication = False
        self.sizer_instance = sizer_instance
        self.result_name = sizer_instance.result_name
        self.parts_table = sizer_instance.parts_table
        self.hypervisor = sizer_instance.hypervisor
        define_configs()

    def set_RF_String(self):

        if self.highest_rf == 2:
            return "RF2"
        elif self.highest_rf == 3:
            return "RF3"
        else:
            return "RF3"

    def build_multi_cluster_json(self, cluster_data):

        res_json = list()

        overall_summary = dict()
        summary_info = dict()

        overall_summary['clusters'] = list()
        # Only for fixed_cluster without workload. else this list will be empty
        overall_summary['no_wl_clusters'] = list()

        summary_info[BaseConstants.CAPEX] = 0
        summary_info[HyperConstants.OPEX] = 0
        summary_info['num_nodes'] = 0
        summary_info[HyperConstants.RACK_UNITS] = 0
        summary_info[HyperConstants.FAULT_TOLERANCE_COUNT] = 0
        summary_info['total_gpu_price'] = 0
        power_consumption = 0
        num_chassis = 0
        chassis_ru = 0

        for cluster_results in cluster_data:

            cluster_set_array = list()
            cluster_id = 0
            wl_present = True

            for cluster_index in range(0, len(cluster_results)):
                cluster_id += 1
                res = cluster_results[cluster_index][0]

                gpu_used = 0
                rack_units = 0

                for accessory in res[HyperConstants.ACC]:
                    if 'GPU' in accessory[HyperConstants.ACC_NAME]:
                        gpu_used = accessory[HyperConstants.ACC_COUNT]

                wls = cluster_results[cluster_index][1]
                self.replication = any(wl.attrib.get(HyperConstants.REPLICATION_FLAG, False) for wl in wls)

                settings = cluster_results[cluster_index][2]

                self.highest_rf = settings[HyperConstants.REPLICATION_FACTOR]
                self.RF_String = self.set_RF_String()
                if wls:
                    self.Fault_Tolerance = max(wl.attrib[HyperConstants.FAULT_TOLERANCE] for wl in wls)
                else:
                    wl_present = False
                    self.Fault_Tolerance = 1

                cluster_json = dict()
                stat_list = list()
                web_stat_list = list()

                wl_json = list()

                self.sizer_instance.hercules = res[HyperConstants.NODE].hercules_on

                for wl in wls:

                    cap_type = 'hercules' if res[HyperConstants.NODE].hercules_on else 'normal'

                    wl.capsum[cap_type][BaseConstants.IOPS] = 0

                    for iops_key in wl.original_iops_sum:

                        if iops_key not in res[HyperConstants.NODE].attrib[BaseConstants.IOPS_CONV_FAC][self.RF_String]:

                            if iops_key == HyperConstants.CONTAINER:
                                #10.x
                                if wl.attrib['storage_protocol'] == 'NFS':
                                    iops_conv_factor = \
                                        float(
                                            res[HyperConstants.NODE].attrib[BaseConstants.IOPS_CONV_FAC][self.RF_String]
                                            [HyperConstants.VSI][0]) * 0.5
                                else:
                                    iops_conv_factor = \
                                        float(
                                            res[HyperConstants.NODE].attrib[BaseConstants.IOPS_CONV_FAC][self.RF_String]
                                            [HyperConstants.VSI][1]) * 0.5

                            if iops_key == HyperConstants.AIML or iops_key == HyperConstants.ANTHOS or iops_key == HyperConstants.ROBO_BACKUP:
                                # 10.x
                                if wl.attrib['storage_protocol'] == 'NFS':
                                    iops_conv_factor = \
                                        float(
                                            res[HyperConstants.NODE].attrib[BaseConstants.IOPS_CONV_FAC][self.RF_String]
                                            [HyperConstants.VSI][0])
                                else:
                                    iops_conv_factor = \
                                        float(
                                            res[HyperConstants.NODE].attrib[BaseConstants.IOPS_CONV_FAC][self.RF_String]
                                            [HyperConstants.VSI][1])
                        else:

                            if wl.attrib['storage_protocol'] == 'NFS':
                                iops_conv_factor = float(
                                    res[HyperConstants.NODE].attrib[BaseConstants.IOPS_CONV_FAC][self.RF_String][
                                        iops_key][0])

                            else:
                                iops_conv_factor = float(
                                    res[HyperConstants.NODE].attrib[BaseConstants.IOPS_CONV_FAC][self.RF_String][
                                        iops_key][1])

                        pcnt_increase = 0

                        # below extra condition is because robo scaling already handles the % increase in performance
                        if res[HyperConstants.NODE].attrib[HyperConstants.TYPE] == 'cto' and \
                                res[HyperConstants.NODE].attrib[BaseConstants.SUBTYPE] in [HyperConstants.ROBO_NODE,
                                                                                           HyperConstants.AF_ROBO_NODE,
                                                                                           HyperConstants.ROBO_TWO_NODE,
                                                                                           HyperConstants.AF_ROBO_TWO_NODE,
                                                                                           HyperConstants.ROBO_240,
                                                                                           HyperConstants.ROBO_AF_240
                                                                                           ]:

                            pass

                        else:

                            if res[HyperConstants.NODE].hercules_on:
                                pcnt_increase += HyperConstants.HERCULES_IOPS[iops_key]

                            if res[HyperConstants.NODE].hx_boost_on:
                                pcnt_increase += HyperConstants.HX_BOOST_IOPS[iops_key]

                        iops_conv_factor *= (1 + pcnt_increase / 100.0)

                        wl.capsum[cap_type][BaseConstants.IOPS] += wl.original_iops_sum[iops_key] / iops_conv_factor

                    wl.attrib[BaseConstants.IOPS_CONV_FAC] = iops_conv_factor

                    replication_traffic = getattr(wl, 'replication_traffic', 0)

                    if self.replication:
                        if wl.attrib['storage_protocol'] == 'NFS':
                            wl.attrib['replication_iops'] = \
                                replication_traffic / float(res[HyperConstants.NODE].attrib[BaseConstants.IOPS_CONV_FAC]
                                                        [self.RF_String][iops_key][0])
                        else:
                            wl.attrib['replication_iops'] = \
                                replication_traffic / float(res[HyperConstants.NODE].attrib[BaseConstants.IOPS_CONV_FAC]
                                                        [self.RF_String][iops_key][1])

                    # Calculating desktops per node for VDI workloads
                    if wl.attrib[BaseConstants.WL_TYPE] == HyperConstants.VDI:
                        total_nodes = res[HyperConstants.NUM] + res.get(HyperConstants.NUM_COMPUTE, 0)
                        wl.attrib['desktops_per_node'] = int(ceil(float(wl.num_inst) / total_nodes))

                    wl_json.append(wl.to_json())

                fault_tolerance_nodes = settings[HyperConstants.FAULT_TOLERANCE]

                if wls:
                    for j, cap in enumerate(HyperConstants.STAT_LIST):
                        util_list, web_util_list = self.generate_utilization_list(res, fault_tolerance_nodes, wls, cap, j, cluster_index)
                        web_stat_list.extend(web_util_list)
                        stat_list.extend(util_list)

                cluster_json['node_info'], new_chassis, new_chassis_ru = self.generate_node_info(res,
                                                                                                 fault_tolerance_nodes,
                                                                                                 str(cluster_id),
                                                                                                 gpu_used)

                num_chassis += new_chassis
                chassis_ru += new_chassis_ru

                if len(wls) == 1 and wls[0].attrib[BaseConstants.WL_TYPE] == HyperConstants.VDI:
                    maxdesktop = self.calculate_maxdesktopVDI(wls[0], res)
                    cluster_json['maxdesktop'] = maxdesktop

                if any(wl.attrib[HyperConstants.INTERNAL_TYPE] == HyperConstants.RDSH for wl in wls):
                    self.rdsh_host_data(wls, res)

                for node_info in cluster_json['node_info']:
                    rack_units += node_info[HyperConstants.RACK_UNITS]
                    power_consumption += node_info[HyperConstants.POWER_CONSUMPTION]

                cluster_json[HyperConstants.RACK_UNITS] = rack_units
                cluster_json['wl_list'] = wl_json
                cluster_json['Utilization'] = stat_list if stat_list else list()
                cluster_json['utilization_web'] = web_stat_list if web_stat_list else list()
                cluster_json['settings'] = settings
                cluster_json['accessories'] = res[HyperConstants.ACC]
                cluster_json[BaseConstants.PRICE] = res[BaseConstants.PRICE]
                cluster_json['required_hxdp'] = self.sizer_instance.get_hxdp_version(cluster_json)
                cluster_set_array += [copy.deepcopy(cluster_json)]

                for node_info in cluster_json['node_info']:

                    summary_info[BaseConstants.CAPEX] += \
                        node_info[BaseConstants.CAPEX]['value'][0][HyperConstants.TAG_VAL]

                    summary_info[HyperConstants.OPEX] += \
                        node_info[HyperConstants.OPEX]['value'][0][HyperConstants.TAG_VAL]

                    summary_info['num_nodes'] += \
                        node_info[HyperConstants.NUM_NODES]

                summary_info[HyperConstants.RACK_UNITS] += cluster_json[HyperConstants.RACK_UNITS]

                summary_info[HyperConstants.FAULT_TOLERANCE_COUNT] += fault_tolerance_nodes

            if wl_present:
                overall_summary['clusters'] += [cluster_set_array]
            else:
                overall_summary['no_wl_clusters'] += [cluster_set_array]

        overall_summary['summary_info'] = summary_info

        overall_summary['sizer_version'] = self.sizer_version

        overall_summary['hx_version'] = self.hx_version

        overall_summary['power_consumption'] = power_consumption
        overall_summary['num_chassis'] = num_chassis
        overall_summary['chassis_ru'] = chassis_ru
        overall_summary['result_name'] = self.result_name

        res_json.append(overall_summary)

        return res_json

    def generate_utilization_list(self, res, fault_tolerance_nodes, wls, cap, j, cluster_index):

        wl_total = dict()
        node_total = dict()
        node_total_ft = dict()
        raw_node_total = dict()
        wl_site_ft = dict()
        stat_list = list()
        web_stat_list = list()

        wl_type = wls[0].attrib[HyperConstants.INTERNAL_TYPE]

        if (cap == BaseConstants.IOPS and wl_type in [HyperConstants.AIML, HyperConstants.ANTHOS]) or \
                (cap in [BaseConstants.CPU, BaseConstants.RAM, BaseConstants.IOPS] and
                 wl_type in [HyperConstants.VEEAM]):

            util_dict = {
                HyperConstants.TAG_NAME: HyperConstants.STAT_UNIT_LIST[j],
                HyperConstants.UTIL_STATUS: False
            }
            stat_list.append(util_dict)
            web_stat_list.append(util_dict)
            return stat_list, web_stat_list

        dr_workload_types = [HyperConstants.VSI, HyperConstants.DB, HyperConstants.OLTP, HyperConstants.OLAP,
                             HyperConstants.ORACLE, HyperConstants.OOLTP, HyperConstants.OOLAP]

        threshold_key = cap
        if cap == BaseConstants.HDD:
            if res[HyperConstants.NODE].attrib[BaseConstants.SUBTYPE] in [HyperConstants.ALL_FLASH,
                                                        HyperConstants.ALLNVME_NODE, HyperConstants.ALLNVME_NODE_8TB,
                                                        HyperConstants.ALL_FLASH_7_6TB, HyperConstants.AF_ROBO_NODE,
                                                        HyperConstants.AF_ROBO_TWO_NODE, HyperConstants.ROBO_AF_240]:
                threshold_key = HyperConstants.ALL_FLASH_HDD
            if res[HyperConstants.NODE].attrib[HyperConstants.DISK_CAGE] == HyperConstants.LARGE_FORM_FACTOR:
                threshold_key = HyperConstants.LFF_HDD

        if self.replication and wl_type in dr_workload_types and cap in [BaseConstants.CPU, BaseConstants.RAM,
                                                                         BaseConstants.IOPS]:

            wl_total[cap] = 0
            wl_site_ft[cap] = 0

            for wl in wls:

                if wl.attrib['replication_type'] == HyperConstants.ANY_CLUSTER:
                    wl_total[cap] += self.sizer_instance.get_req(wl, cap)

                elif cluster_index and wl.attrib['remote']:
                    wl_total[cap] += self.sizer_instance.get_req(wl, cap)

                elif not cluster_index and not wl.attrib['remote']:
                    wl_total[cap] += self.sizer_instance.get_req(wl, cap)

                elif not cluster_index and wl.attrib['remote']:
                    if cap == BaseConstants.IOPS:
                        wl_total[cap] += wl.attrib['replication_iops']
                    wl_site_ft[cap] += self.sizer_instance.get_req(wl, cap)

                elif cluster_index and not wl.attrib['remote']:
                    if cap == BaseConstants.IOPS:
                        wl_total[cap] += wl.attrib['replication_iops']
                    wl_site_ft[cap] += self.sizer_instance.get_req(wl, cap)

                if cap == BaseConstants.IOPS:
                    wl_site_ft[cap] -= wl.attrib['replication_iops']
        else:
            wl_total[cap] = sum(self.sizer_instance.get_req(wl, cap) for wl in wls)
            wl_site_ft[cap] = 0

        if cap == BaseConstants.IOPS and wl_type == HyperConstants.CONTAINER:

            node_total[cap] = res[HyperConstants.NODE].cap[cap] * \
                              (HyperConstants.MAX_CONTAINER_IOPS_NODES + fault_tolerance_nodes)

            raw_node_total[cap] = res[HyperConstants.NODE].raw_cap[cap] * \
                                  (HyperConstants.MAX_CONTAINER_IOPS_NODES + fault_tolerance_nodes)

            node_total_ft[cap] = HyperConstants.MAX_CONTAINER_IOPS_NODES * res[HyperConstants.NODE].cap[cap]

        else:

            node_total[cap] = res[HyperConstants.NUM] * res[HyperConstants.NODE].cap[cap]

            raw_node_total[cap] = res[HyperConstants.NUM] * res[HyperConstants.NODE].raw_cap[cap]

            node_total_ft[cap] = (res[HyperConstants.NUM] - fault_tolerance_nodes) * res[HyperConstants.NODE].cap[cap]

        if res.get(HyperConstants.COMPUTE) and res[HyperConstants.COMPUTE]:

            node_total[cap] += res[HyperConstants.NUM_COMPUTE] * res[HyperConstants.COMPUTE].cap[cap]

            raw_node_total[cap] += res[HyperConstants.NUM_COMPUTE] * res[HyperConstants.COMPUTE].raw_cap[cap]

            node_total_ft[cap] += res[HyperConstants.NUM_COMPUTE] * res[HyperConstants.COMPUTE].cap[cap]

        if not node_total[cap]:
            node_total[cap] = 1
        if not node_total_ft[cap]:
            node_total_ft[cap] = 1

        if cap == BaseConstants.HDD:
            node_total_ft[cap] = node_total[cap]

        scaling_factor = 1

        if cap == BaseConstants.CPU:

            if wl_type in [HyperConstants.VDI, HyperConstants.VDI_INFRA, HyperConstants.VDI_HOME, HyperConstants.RDSH,
                           HyperConstants.RDSH_HOME]:

                clock_speed_mult = float(self.sizer_instance.base_cpu.speed)
                wl_total[cap] *= clock_speed_mult
                wl_site_ft[cap] *= clock_speed_mult
                raw_node_total[cap] *= clock_speed_mult
                node_total[cap] *= clock_speed_mult
                node_total_ft[cap] *= clock_speed_mult
                op_ratio = 1

            else:
                if wl_type in [HyperConstants.EPIC, HyperConstants.ANTHOS]:
                    op_ratio = 1
                else:
                    ops = Counter(wl.attrib[HyperConstants.VCPUS_PER_CORE] for wl in wls)
                    op_ratio = ops.most_common(1)[0][0]
                wl_total[cap] = wl_total[cap] * op_ratio
                wl_site_ft[cap] = wl_site_ft[cap] * op_ratio
                raw_node_total[cap] = raw_node_total[cap] * op_ratio
                node_total[cap] = node_total[cap] * op_ratio
                node_total_ft[cap] = node_total_ft[cap] * op_ratio

        elif cap == BaseConstants.HDD:

            reduced_total = 0
            original_wl_total = 0

            for wl in wls:
                reduced_total += self.sizer_instance.get_req(wl, cap)
                original_wl_total += wl.original_size

            if original_wl_total > 0:
                scaling_factor = reduced_total / float(original_wl_total)
            else:
                scaling_factor = 1

            op_ratio = 100.0 / scaling_factor - 100

            node_total[cap] = node_total[cap] / self.highest_rf
            node_total_ft[cap] = node_total_ft[cap] / self.highest_rf
            raw_node_total[cap] = raw_node_total[cap] / self.highest_rf

        else:
            op_ratio = 1

        threshold_consumption = node_total[cap] * (1 - self.sizer_instance.get_threshold_value(wl_type, threshold_key))

        self.output_intermediate_calculation(res, wl_type, cap, op_ratio, scaling_factor)

        node_data = [raw_node_total, node_total, node_total_ft]

        wl_total_ft = deepcopy(wl_total)
        if cap == BaseConstants.IOPS and wl_type in [HyperConstants.VDI_INFRA, HyperConstants.VDI]:

            vdi_infra = sum(wl.attrib[HyperConstants.INTERNAL_TYPE] == HyperConstants.VDI_INFRA for wl in wls)

            additional_iops = vdi_infra * 0.1 * node_total[cap]
            wl_total[cap] += additional_iops

            additional_iops = vdi_infra * 0.1 * node_total_ft[cap]
            wl_total_ft[cap] += additional_iops

        wl_data = [wl_total, wl_site_ft, threshold_consumption, wl_total_ft]
        util_settings = {
            'ratio': op_ratio,
            'scaling_factor': scaling_factor,
            BaseConstants.WL_TYPE: wl_type
        }

        util_dict = self.build_result_util_categories(j, cap, wl_data, node_data, util_settings)
        stat_list.append(util_dict)
        web_util_dict ={
            HyperConstants.TAG_NAME: util_dict[HyperConstants.TAG_NAME],
            HyperConstants.WL_UTILIZATION: ceil(util_dict[HyperConstants.WL_UTILIZATION]),
            HyperConstants.FT_UTIL: ceil(util_dict[HyperConstants.FT_UTIL]),
            HyperConstants.SITE_FT_UTIL:ceil(util_dict[HyperConstants.SITE_FT_UTIL]), 
            HyperConstants.FREE_UTIL: ceil(util_dict[HyperConstants.FREE_UTIL]),
            HyperConstants.UNITS: util_dict[HyperConstants.UNITS]
        }
        web_stat_list.append(web_util_dict)
        return stat_list, web_stat_list

    def output_intermediate_calculation(self, res, wl_type, cap, op_ratio, scaling_factor):

        # for cap in CAP_LIST:
        threshold_key = cap
        if cap == BaseConstants.HDD:
            if res[HyperConstants.NODE].attrib[BaseConstants.SUBTYPE] in [HyperConstants.ALL_FLASH,
                                                    HyperConstants.AF_ROBO_NODE, HyperConstants.ALLNVME_NODE,
                                                    HyperConstants.ALLNVME_NODE_8TB, HyperConstants.ALL_FLASH_7_6TB,
                                                    HyperConstants.AF_ROBO_TWO_NODE]:
                threshold_key = HyperConstants.ALL_FLASH_HDD
            if res[HyperConstants.NODE].attrib[HyperConstants.DISK_CAGE] == HyperConstants.LARGE_FORM_FACTOR:
                threshold_key = HyperConstants.LFF_HDD

        if cap == BaseConstants.CPU:

            raw_cores_total = \
                (res[HyperConstants.NODE].raw_cap[cap] / res[HyperConstants.NODE].attrib[HyperConstants.SPECLNT]) * \
                res[HyperConstants.NUM]

            raw_cores_adjspeclnt = res[HyperConstants.NODE].raw_cap[cap] * res[HyperConstants.NUM]

            cores_total = res[HyperConstants.NODE].cap[cap] * res[HyperConstants.NUM] * op_ratio

            if wl_type == HyperConstants.VDI:
                clock_speed_mult = float(res[HyperConstants.NODE].attrib[BaseConstants.CLOCK_SPEED])
                raw_cores_adjspeclnt = raw_cores_adjspeclnt * clock_speed_mult
                cores_total = cores_total * clock_speed_mult

            cpu_threshold = self.sizer_instance.get_threshold_value(wl_type, threshold_key)
            cores_total_afterthreshold = cores_total * cpu_threshold

            res[HyperConstants.NODE].attrib[HyperConstants.CPU_OPRATIO] = op_ratio
            res[HyperConstants.NODE].attrib[HyperConstants.RAW_CORES_TOTAL] = raw_cores_total
            res[HyperConstants.NODE].attrib[HyperConstants.RAW_CORES_ADJSPECLNT] = raw_cores_adjspeclnt
            res[HyperConstants.NODE].attrib[HyperConstants.CORES_TOTAL_POSTOVERHEAD] = cores_total
            res[HyperConstants.NODE].attrib[HyperConstants.CORES_TOTAL_POSTTHRESHOLD] = cores_total_afterthreshold
            res[HyperConstants.NODE].attrib[HyperConstants.NODE_OVERHEAD] = res[HyperConstants.NODE].overhead

        elif cap == BaseConstants.RAM:

            raw_memory_size = res[HyperConstants.NODE].raw_cap[cap] * res[HyperConstants.NUM]
            memory_afteroverhead = res[HyperConstants.NODE].cap[cap] * res[HyperConstants.NUM]
            memory_threshold = self.sizer_instance.get_threshold_value(wl_type, threshold_key)
            memory_afterthreshold = memory_afteroverhead * memory_threshold

            res[HyperConstants.NODE].attrib[HyperConstants.RAM_OPRATIO] = op_ratio
            res[HyperConstants.NODE].attrib[HyperConstants.RAW_RAM_TOTAL] = raw_memory_size
            res[HyperConstants.NODE].attrib[HyperConstants.RAM_TOTAL_POSTOVERHEAD] = memory_afteroverhead
            res[HyperConstants.NODE].attrib[HyperConstants.RAM_TOTAL_POSTTHRESHOLD] = memory_afterthreshold

        elif cap == BaseConstants.HDD:

            raw_disk = res[HyperConstants.NODE].raw_cap[cap] * res[HyperConstants.NUM]
            disk_afterRF = raw_disk / self.highest_rf
            disk_afteroverhead = (res[HyperConstants.NODE].cap[cap] * res[HyperConstants.NUM]) / self.highest_rf
            disk_threshold = self.sizer_instance.get_threshold_value(wl_type, threshold_key)
            disk_afterthreshold = disk_afteroverhead * disk_threshold

            res[HyperConstants.NODE].attrib[HyperConstants.HDD_OPRATIO] = op_ratio
            res[HyperConstants.NODE].attrib[HyperConstants.RAW_HDD_TOTAL] = raw_disk
            res[HyperConstants.NODE].attrib[HyperConstants.HDD_TOTAL_POSTRF] = disk_afterRF
            res[HyperConstants.NODE].attrib[HyperConstants.HDD_TOTAL_POSTOVERHEAD] = disk_afteroverhead
            res[HyperConstants.NODE].attrib[HyperConstants.HDD_TOTAL_POSTTHRESHOLD] = disk_afterthreshold
            res[HyperConstants.NODE].attrib[HyperConstants.HIGHEST_RF] = self.highest_rf
            res[HyperConstants.NODE].attrib[HyperConstants.THRESHOLD_KEY] = threshold_key
            res[HyperConstants.NODE].attrib[HyperConstants.SCALING_FACTOR] = scaling_factor
            res[HyperConstants.NODE].attrib[HyperConstants.NODE_OVERHEAD] = res[HyperConstants.NODE].overhead

        elif cap == BaseConstants.IOPS:

            raw_iops = res[HyperConstants.NODE].raw_cap[cap] * res[HyperConstants.NUM]
            iops_afterConversion = res[HyperConstants.NODE].cap[cap] * res[HyperConstants.NUM]

            res[HyperConstants.NODE].attrib[HyperConstants.RAW_IOPS_TOTAL] = raw_iops
            res[HyperConstants.NODE].attrib[HyperConstants.IOPS_TOTAL_POSTIOPSCONV] = iops_afterConversion

        elif cap == BaseConstants.VRAM:

            raw_gpu_size = res[HyperConstants.NODE].raw_cap[cap] * res[HyperConstants.NUM]

            res[HyperConstants.NODE].attrib[HyperConstants.RAW_VRAM_TOTAL] = raw_gpu_size

        if res.get(HyperConstants.COMPUTE):
            for cap in HyperConstants.CAP_LIST:
                if cap == BaseConstants.CPU:

                    raw_cores_total = \
                        (res[HyperConstants.COMPUTE].raw_cap[cap] /
                         res[HyperConstants.COMPUTE].attrib[HyperConstants.SPECLNT]) * res[HyperConstants.NUM_COMPUTE]

                    raw_cores_adjspeclnt = res[HyperConstants.COMPUTE].raw_cap[cap] * res[HyperConstants.NUM_COMPUTE]

                    cores_total = res[HyperConstants.COMPUTE].cap[cap] * res[HyperConstants.NUM_COMPUTE]

                    if wl_type == HyperConstants.VDI:
                        clock_speed_mult = float(res[HyperConstants.COMPUTE].attrib[BaseConstants.CLOCK_SPEED])
                        raw_cores_adjspeclnt = raw_cores_adjspeclnt * clock_speed_mult
                        cores_total = cores_total * clock_speed_mult

                    cpu_threshold = self.sizer_instance.get_threshold_value(wl_type, threshold_key)
                    cores_total_afterthreshold = cores_total * cpu_threshold

                    res[HyperConstants.COMPUTE].attrib[HyperConstants.RAW_CORES_TOTAL] = raw_cores_total

                    res[HyperConstants.COMPUTE].attrib[HyperConstants.RAW_CORES_ADJSPECLNT] = raw_cores_adjspeclnt

                    res[HyperConstants.COMPUTE].attrib[HyperConstants.CORES_TOTAL_POSTOVERHEAD] = cores_total

                    res[HyperConstants.COMPUTE].attrib[HyperConstants.CORES_TOTAL_POSTTHRESHOLD] = \
                        cores_total_afterthreshold

                    res[HyperConstants.COMPUTE].attrib[HyperConstants.NODE_OVERHEAD] = \
                        res[HyperConstants.COMPUTE].overhead

                elif cap == BaseConstants.RAM:

                    raw_memory_size = res[HyperConstants.COMPUTE].raw_cap[cap] * res[HyperConstants.NUM_COMPUTE]

                    memory_afteroverhead = res[HyperConstants.COMPUTE].cap[cap] * res[HyperConstants.NUM_COMPUTE]

                    memory_threshold = self.sizer_instance.get_threshold_value(wl_type, threshold_key)

                    memory_afterthreshold = memory_afteroverhead * memory_threshold

                    res[HyperConstants.COMPUTE].attrib[HyperConstants.RAW_RAM_TOTAL] = raw_memory_size

                    res[HyperConstants.COMPUTE].attrib[HyperConstants.RAM_TOTAL_POSTOVERHEAD] = memory_afteroverhead

                    res[HyperConstants.COMPUTE].attrib[HyperConstants.RAM_TOTAL_POSTTHRESHOLD] = memory_afterthreshold

    @staticmethod
    def build_result_util_categories(j, cap, wl_data, node_data, util_settings):

        op_ratio = util_settings['ratio']
        scaling_factor = util_settings['scaling_factor']
        wl_type = util_settings[BaseConstants.WL_TYPE]

        output_wl_total = dict()
        wl_total = wl_data[0]
        wl_site_ft = wl_data[1]
        threshold_consumption = wl_data[2]
        wl_total_ft = wl_data[3]

        raw_node_total = node_data[0][cap]
        node_total = node_data[1][cap]
        ft_node_total = node_data[2][cap]

        if not raw_node_total:
            raw_node_total = 1
        if not node_total:
            node_total = 1
        if not ft_node_total:
            ft_node_total = 1

        wl_util = wl_total[cap] * 100.0 / node_total

        if not wl_util:
            ft_util = 0
        else:
            ft_util = (wl_total_ft[cap] * 100.0 / ft_node_total)

        threshold_util = threshold_consumption / node_total * 100.0

        site_ft_util = (wl_total[cap] + wl_site_ft[cap]) * 100.0 / ft_node_total
        free_util = 100 - threshold_util - wl_util

        util_dict = {
            HyperConstants.UTIL_STATUS: True,
            HyperConstants.TAG_NAME: HyperConstants.STAT_UNIT_LIST[j],
            HyperConstants.WL_UTILIZATION: wl_util,
            HyperConstants.FT_UTIL: ft_util,
            HyperConstants.SITE_FT_UTIL: site_ft_util,
            HyperConstants.THRESHOLD_UTILIZATION: threshold_util,
            HyperConstants.FREE_UTIL: free_util,
            HyperConstants.RATIO: op_ratio
        }

        if cap == BaseConstants.IOPS:
            sizing_threshold = ((wl_util + free_util) / 100.0) * node_total
            workload_total = wl_total[cap]
            cap_unit = HyperConstants.STAT_UNITS[j]

        elif cap == BaseConstants.HDD or cap == BaseConstants.SSD:

            if node_total > 1000:
                output_wl_total[cap] = wl_total[cap] / 1000.0
                raw_output_node_total = node_total / 1000.0
                cap_unit = 'TB'
                raw_output_node_total_binarybyte = raw_output_node_total * HyperConstants.TB_TO_TIB_CONVERSION
                binarybyte_unit = 'TiB'
                scaled_node_total_binarybyte = \
                    raw_output_node_total / scaling_factor * HyperConstants.TB_TO_TIB_CONVERSION

            else:
                output_wl_total[cap] = wl_total[cap]
                raw_output_node_total = node_total
                cap_unit = 'GB'
                raw_output_node_total_binarybyte = raw_output_node_total * HyperConstants.GB_TO_GIB_CONVERSION
                binarybyte_unit = 'GiB'
                scaled_node_total_binarybyte = \
                    raw_output_node_total / scaling_factor * HyperConstants.GB_TO_GIB_CONVERSION

            scaled_node_total = raw_output_node_total / scaling_factor

            sizing_threshold = ((wl_util + free_util) / 100.0) * scaled_node_total

            sizing_threshold_binarybyte = ((wl_util + free_util) / 100.0) * scaled_node_total_binarybyte

            workload_total = output_wl_total[cap] / scaling_factor

            node_total = scaled_node_total

            node_total_binarybyte = scaled_node_total_binarybyte

            util_dict.update({
                HyperConstants.USABLE_VAL: raw_output_node_total,
                HyperConstants.USABLE_VAL_BINARYBYTE: raw_output_node_total_binarybyte,
                HyperConstants.BINARYBYTE_UNIT: binarybyte_unit,
                BaseConstants.NODE_VAL_BINARYBYTE: node_total_binarybyte,
                BaseConstants.BEST_PRACTICE_BINARYBYTE: sizing_threshold_binarybyte
            })
        else:
            sizing_threshold = ((wl_util + free_util) / 100.0) * ft_node_total
            node_total = ft_node_total
            if wl_type in [HyperConstants.VDI, HyperConstants.VDI_INFRA, HyperConstants.VDI_HOME, HyperConstants.RDSH,
                           HyperConstants.RDSH_HOME] and cap == BaseConstants.CPU:
                workload_total = wl_total[cap]
                cap_unit = 'GHz'
            else:
                workload_total = wl_total[cap]
                cap_unit = HyperConstants.STAT_UNITS[j]

        util_dict.update({
            BaseConstants.WORKLOAD_VAL: workload_total,
            BaseConstants.NODE_VAL: node_total,
            BaseConstants.TOTAL_NODE_VAL: raw_node_total,
            HyperConstants.UNITS: cap_unit,
            BaseConstants.BEST_PRACTICE: sizing_threshold
        })
        return util_dict

    def generate_node_info(self, res, fault_tolerance_nodes, cluster_id, gpu_used):

        return_node_info = list()
        num_chassis = 0
        chassis_ru = 0

        # First element is HX node, Second is Compute
        for node_type, count in [(HyperConstants.NODE, HyperConstants.NUM), (HyperConstants.COMPUTE,
                                                                             HyperConstants.NUM_COMPUTE)]:

            node_details = res.get(node_type)

            if not node_details:
                continue

            node_count = res[count]

            capex_list = node_details.get_capex(node_count)

            opex_list = node_details.get_opex(node_count, self.sizer_instance.vdi_user)

            summary_list = node_details.get_summary(node_count, self.sizer_instance.vdi_user,
                                                    self.sizer_instance.vm_user, self.sizer_instance.db_user,
                                                    self.sizer_instance.raw_user, self.sizer_instance.robo_user,
                                                    self.sizer_instance.oracle_user)

            if node_details.attrib.get('use_chassis') and node_type == HyperConstants.COMPUTE:

                node_power_consumption = self.parts_table.get_part_attrib(node_details.attrib['chassis_options'],
                                                                          HyperConstants.POWER)

                individual_ru = \
                    self.parts_table.get_part_attrib(node_details.attrib['chassis_options'], HyperConstants.RACK_SPACE)

                compute_clusters = int(ceil(node_count/8.0))

                num_chassis += compute_clusters

                chassis_ru += individual_ru * compute_clusters

                rack_units = chassis_ru
            else:
                node_power_consumption = node_details.attrib[HyperConstants.POWER] * node_count
                rack_units = node_count * node_details.attrib[HyperConstants.RACK_SPACE]

            node_config = {
                BaseConstants.DISPLAY_NAME: 'Cluster_' + cluster_id,
                HyperConstants.MODEL_DETAILS: node_details.get_model_details(gpu_used),
                HyperConstants.BOM_MODEL_DETAILS: node_details.get_bom_details(),
                HyperConstants.NUM_NODES: node_count,
                HyperConstants.FAULT_TOLERANCE_COUNT: fault_tolerance_nodes if node_type == HyperConstants.NODE else 0,
                HyperConstants.POWER_CONSUMPTION: node_power_consumption,
                BaseConstants.CAPEX: capex_list,
                HyperConstants.OPEX: opex_list,
                HyperConstants.SUMMARY: summary_list,
                HyperConstants.RACK_UNITS: rack_units,
                HyperConstants.HERCULES_CONF: node_details.hercules_on,
                HyperConstants.HX_BOOST_CONF: node_details.hx_boost_on
            }

            mod_lan = node_details.get_mod_lan()
            if mod_lan:
                node_config[HyperConstants.MOD_LAN] = mod_lan

            return_node_info.append(node_config)
        return return_node_info, num_chassis, chassis_ru

    def calculate_maxdesktopVDI(self, wl, res):

        wl_num_inst = wl.num_inst

        wl_cpu = self.sizer_instance.get_req(wl, BaseConstants.CPU) / wl_num_inst
        wl_ram = self.sizer_instance.get_req(wl, BaseConstants.RAM) / wl_num_inst
        wl_ssd = self.sizer_instance.get_req(wl, BaseConstants.SSD) / wl_num_inst
        wl_hdd = self.sizer_instance.get_req(wl, BaseConstants.HDD) / wl_num_inst
        wl_vram = self.sizer_instance.get_req(wl, BaseConstants.VRAM) / wl_num_inst

        hc_node = res[HyperConstants.NODE]

        cpu_threshold = self.sizer_instance.get_threshold_value(HyperConstants.VDI, BaseConstants.CPU)

        cpu_overhead = hc_node.overhead[BaseConstants.CPU]

        total_cores = ((hc_node.raw_cap[BaseConstants.CPU] * cpu_threshold) - cpu_overhead) * \
                      (res[HyperConstants.NUM] - self.Fault_Tolerance)

        if wl_cpu:
            maxvmbycpu = total_cores / wl_cpu
        else:
            maxvmbycpu = 0

        ram_threshold = self.sizer_instance.get_threshold_value(HyperConstants.VDI, BaseConstants.RAM)

        ram_overhead = hc_node.overhead[BaseConstants.RAM]

        total_ram = ((hc_node.raw_cap[BaseConstants.RAM] * ram_threshold) - ram_overhead) * \
                    (res[HyperConstants.NUM] - self.Fault_Tolerance)

        if wl_ram:
            maxvmbyram = total_ram / wl_ram
        else:
            maxvmbyram = 0

        ssd_threshold = self.sizer_instance.get_threshold_value(HyperConstants.VDI, BaseConstants.SSD)

        total_ssd = hc_node.cap[BaseConstants.SSD] * ssd_threshold * (res[HyperConstants.NUM] - self.Fault_Tolerance)

        if wl_ssd:
            maxvmbyssd = math.floor(total_ssd / wl_ssd)
        else:
            maxvmbyssd = 0

        hdd_threshold = self.sizer_instance.get_threshold_value(HyperConstants.VDI, BaseConstants.HDD)

        total_hdd = \
            (hc_node.cap[BaseConstants.HDD] * hdd_threshold) * res[HyperConstants.NUM] / float(self.highest_rf)

        if wl_hdd:
            maxvmbyhdd = math.floor(total_hdd / wl_hdd)
        else:
            maxvmbyhdd = 0

        maxvmbyvram = 0

        if hc_node.attrib[BaseConstants.VRAM]:

            vram_threshold = self.sizer_instance.get_threshold_value(HyperConstants.VDI, BaseConstants.VRAM)

            vram_value = hc_node.cap[BaseConstants.VRAM] * vram_threshold

            acc_list = res['accessory']

            for accessory in acc_list:
                if accessory['type'] == BaseConstants.GPU:
                    total_vram = vram_value * accessory['count']
                    maxvmbyvram += math.floor(total_vram / wl_vram if wl_vram else 1)

        if res.get(HyperConstants.COMPUTE) and res[HyperConstants.COMPUTE]:

            compute_node = res[HyperConstants.COMPUTE]

            total_cores = compute_node.cap[BaseConstants.CPU] * cpu_threshold * res[HyperConstants.NUM_COMPUTE]

            maxvmbycpu += total_cores / wl_cpu

            total_ram = compute_node.cap[BaseConstants.RAM] * ram_threshold * res[HyperConstants.NUM_COMPUTE]

            maxvmbyram += total_ram / wl_ram

        maxvmbycpu = math.floor(maxvmbycpu)

        maxvmbyram = math.floor(maxvmbyram)

        maxdesktoplist = [maxvmbycpu, maxvmbyram, maxvmbyssd, maxvmbyhdd]

        if maxvmbyvram:

            maxdesktoplist.append(maxvmbyvram)

        maxdesktop = int(min(maxdesktoplist))

        return maxdesktop

    @staticmethod
    def rdsh_host_data(workloads, result):

        hx_count = result[HyperConstants.NUM]
        co_count = result[HyperConstants.NUM_COMPUTE]

        total_count = float(hx_count + co_count)

        for wl in filter(lambda x: x.attrib[HyperConstants.INTERNAL_TYPE] == HyperConstants.RDSH, workloads):

            wl.attrib['users_per_host'] = int(ceil(wl.attrib['total_users'] / total_count))
            wl.attrib['vms_per_host'] = int(ceil(wl.num_vms / total_count))
