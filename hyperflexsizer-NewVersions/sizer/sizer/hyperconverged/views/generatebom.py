# coding: utf-8
""" This script generates Sizer BOM """
# import sys,os
# import logging
import json
import datetime
import os
import xlsxwriter
import math
import copy
import urllib
from math import ceil
from collections import OrderedDict
from collections import defaultdict
from copy import deepcopy

from hyperconverged.models import Part, Thresholds
from hyperconverged.solver.attrib import HyperConstants
from sizer.local_settings import BASE_DIR


class Report(object):

    def __init__(self, s_data):
        self.scenario_data = json.loads(s_data)


class BOMexcel(Report):

    def __init__(self, scenario_data):

        Report.__init__(self, scenario_data)

        scenario_name = self.scenario_data['name']
        currentdatetime = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
        bom_name = scenario_name + "_" + str(currentdatetime) + ".xlsx"

        bom_name = os.path.join(BASE_DIR, bom_name)
        self.bom_name = bom_name
        self.workbook = xlsxwriter.Workbook(bom_name)

    @staticmethod
    def get_bom_nodes_details(cluster_list, fi_option, isstretchcluster, isepiccluster):

        # multipleof = 2 if isstretchcluster else 1
        if isstretchcluster:
            multipleof = 2
        elif isepiccluster:
            multipleof = cluster_list[0]['wl_list'][0]['num_clusters']
        else:
            multipleof = 1

        node_list = list()
        accessory_list = list()

        for cdata in cluster_list:

            # To check how many add-on HDD drives have been added.
            acc_hdd_count = 0

            if 'accessories' in cdata:
                accessory_info_list = cdata['accessories']
                for accessory_data in accessory_info_list:
                    if accessory_data['type'] == "Capacity Drive":
                        acc_hdd_count += accessory_data['count'] * accessory_data['bundle_count']

            node_info_list = cdata['node_info']

            bom_wl_list = ', '.join([wldata['wl_name'] for wldata in cdata['wl_list']])
            server_type = 'M5'
            for node_data in node_info_list:
                node_name = node_data['model_details']['name']
                if 'M6' in node_name:
                    server_type = 'M6'
                node_desc_map = node_data['model_details']['node_description']
                subtype = node_data['model_details']['subtype']

                node_count = node_data['num_nodes']

                node_desc = list()
                node_desc.append(node_desc_map['CPU'])
                node_desc.append(node_desc_map['RAM'])

                if 'HDD' in node_desc_map:
                    node_desc.append(node_desc_map['HDD'])

                if 'SSD' in node_desc_map:
                    node_desc.append(node_desc_map['SSD'])

                if 'GPU_USERS' in node_desc_map:
                    node_desc.append(node_desc_map['GPU_USERS'])

                rus = list()
                rack_space = node_data['model_details']['rack_space']

                if rack_space == 1:
                    rval = str(rack_space) + " RU"
                    rus.insert(0, rval)

                elif rack_space >= 2:
                    rval = str(rack_space) + " RU"
                    rus.insert(0, rval)

                node_desc = node_desc + rus

                node_dict = dict()
                node_dict['header'] = node_name
                node_dict['desc'] = node_desc
                node_dict['count'] = node_count * multipleof
                node_dict['isstretch'] = isstretchcluster
                node_dict['bom_wl_list'] = "Workloads: " + bom_wl_list

                # To check how many add-on GPU have been added in case of -C480- node, 8 GPU's are built-in

                acc_gpu_count = 0
                acc_gpu_name = ""
                if subtype == 'aiml' and '-C480-' in node_name:
                    acc_gpu_count = node_dict['count'] * node_data['model_details']['gpu_slots']
                    acc_gpu_name = node_data['model_details']['gpu_bom_name']

                if 'Bundle' in node_data['model_details']['type']:

                    if 'bom_package_name' in node_data['bom_details']:
                        node_dict['bom_package_name'] = node_data['bom_details']['bom_package_name']
                        node_dict['bom_package_qty'] = 1

                    if 'bom_name' in node_data['bom_details']:
                        node_dict['bom_name'] = node_data['bom_details']['bom_name']

                    if 'bom_fi_package_name' in node_data['bom_details']:
                        node_dict['bom_fi_package_name'] = node_data['bom_details']['bom_fi_package_name']

                    if ('HX-FI-6332' == fi_option) or ('HX-FI-6332-16UP' == fi_option):
                        fi_option = fi_option + "_M5"

                    if ('HX-FI-6454' == fi_option):
                        fi_option = fi_option + "_SP"

                    if 'fi_options' in node_data['bom_details'] and fi_option in node_data['bom_details']['fi_options']:
                        node_dict['fi_options'] = fi_option

                    if 'bom_add_memory_name' in node_data['bom_details'] and \
                            node_data['bom_details']['bom_add_mem_slots'] != 0:
                        node_dict['bom_add_memory_name'] = node_data['bom_details']['bom_add_memory_name']

                        # Change as for Base ram slots is 6 in CCW, additional ram is missed
                        remain_mem_addon = 0
                        if node_data['model_details']['subtype'] in [HyperConstants.HYPER, HyperConstants.ALL_FLASH]:
                            difference = node_data['bom_details']['ram_slots'] - \
                                         node_data['bom_details']['bom_add_mem_slots']

                            if difference >= 8:
                                remain_mem_addon = difference - 6      # as 6 is integrated slot

                        node_dict['bom_add_memory_qty'] = \
                            (node_data['bom_details']['bom_add_mem_slots'] + remain_mem_addon) * \
                            node_data['num_nodes'] * multipleof

                    if 'bom_40g_name' in node_data['bom_details']:
                        node_dict['bom_40g_name'] = node_data['bom_details']['bom_40g_name']
                        node_dict['bom_40g_count_qty'] = \
                            node_data['bom_details']['bom_40g_count'] * node_data['num_nodes'] * multipleof

                    if 'bom_10g_name' in node_data['bom_details']:
                        node_dict['bom_10g_name'] = node_data['bom_details']['bom_10g_name']
                        node_dict['bom_10g_count_qty'] = \
                            node_data['bom_details']['bom_10g_count'] * node_data['num_nodes'] * multipleof

                    if 'bom_dual_switch_name' in node_data['bom_details']:
                        node_dict['bom_dual_switch_name'] = node_data['bom_details']['bom_dual_switch_name']
                        node_dict['bom_dual_switch_count_qty'] = \
                            node_data['bom_details']['bom_dual_switch_count'] * node_data['num_nodes'] * multipleof

                    if 'disk_package' in node_data['bom_details']:
                        node_dict['disk_package'] = node_data['bom_details']['disk_package']
                        node_dict['disk_package_qty'] = 1 * node_data['num_nodes'] * multipleof

                    if 'bom_hercules_part' in node_data['bom_details']:
                        node_dict['bom_hercules_part'] = node_data['bom_details']['bom_hercules_part']
                        node_dict['bom_hercules_count_qty'] = \
                            node_data['bom_details']['bom_hercules_count'] * node_data['num_nodes'] * multipleof

                elif 'UCSC' in node_data['bom_details']['bom_name']:
                    node_dict['bom_name'] = node_data['bom_details']['bom_name']
                    node_dict['cpu_part'] = node_data['bom_details']['cpu_bom_name']
                    node_dict['cpu_qty'] = node_data['bom_details']['cpu_socket_count'] * node_data['num_nodes']
                    node_dict['mem_part'] = node_data['bom_details']['ram_bom_name']
                    node_dict['mem_qty'] = node_data['bom_details']['ram_slots'] * node_data['num_nodes']

                else:

                    if 'bom_package_name' in node_data['bom_details']:
                        node_dict['bom_package_name'] = node_data['bom_details']['bom_package_name']
                        node_dict['bom_package_qty'] = 1

                    if 'bom_fi_package_name' in node_data['bom_details']:
                        node_dict['bom_fi_package_name'] = node_data['bom_details']['bom_fi_package_name']

                    if 'bom_raid_name' in node_data['bom_details']:
                        node_dict['bom_raid_name'] = node_data['bom_details']['bom_raid_name']
                        node_dict['bom_raid_qty'] = 1 * node_data['num_nodes'] * multipleof

                    if 'bom_system_drive' in node_data['bom_details']:
                        node_dict['bom_system_drive'] = node_data['bom_details']['bom_system_drive']
                        node_dict['bom_system_qty'] = 1 * node_data['num_nodes'] * multipleof

                    if 'bom_boot_drive' in node_data['bom_details']:
                        node_dict['bom_boot_drive'] = node_data['bom_details']['bom_boot_drive']
                        node_dict['bom_boot_qty'] = 1 * node_data['num_nodes'] * multipleof

                    if 'fi_options' in node_data['bom_details'] and fi_option in node_data['bom_details']['fi_options']:
                        node_dict['fi_options'] = fi_option

                    node_dict['bom_name'] = node_data['bom_details']['bom_name']
                    if "UCS" in node_data['bom_details']['cpu_bom_name']:
                        node_data['bom_details']['cpu_bom_name'] = node_data['bom_details']['cpu_bom_name'][3:]
                        node_data['bom_details']['cpu_bom_name'] = 'HX'+node_data['bom_details']['cpu_bom_name']
                    node_dict['cpu_part'] = node_data['bom_details']['cpu_bom_name']
                    node_dict['cpu_qty'] = \
                        node_data['bom_details']['cpu_socket_count'] * node_data['num_nodes'] * multipleof

                    if isepiccluster:
                        if "UCS" in node_data['bom_details']['ram_bom_name']:
                            node_data['bom_details']['ram_bom_name'] = node_data['bom_details']['ram_bom_name'][3:]
                            node_data['bom_details']['ram_bom_name'] = 'HX' + node_data['bom_details']['ram_bom_name']
                        ram_name = node_data['bom_details']['ram_bom_name']
                        if ram_name.find('#') != -1:
                            ram_name_list = ram_name.split("#")

                            node_dict['mem_part'] = ram_name_list[0]
                            node_dict['mem_qty'] = node_data['bom_details']['ram_slots'] * \
                                                   node_data['num_nodes'] * multipleof

                            node_dict['mem_part1'] = ram_name_list[1]

                        else:
                            node_dict['mem_part'] = node_data['bom_details']['ram_bom_name']
                            node_dict['mem_qty'] = node_data['bom_details']['ram_slots'] * \
                                                   node_data['num_nodes'] * multipleof
                    else:
                        if "UCS" in node_data['bom_details']['ram_bom_name']:
                            node_data['bom_details']['ram_bom_name'] = node_data['bom_details']['ram_bom_name'][3:]
                            node_data['bom_details']['ram_bom_name'] = 'HX' + node_data['bom_details']['ram_bom_name']
                        ram_name = node_data['bom_details']['ram_bom_name']
                        if ram_name.find('#') != -1:
                            ram_name_list = ram_name.split("#")

                            node_dict['mem_part'] = ram_name_list[0]
                            node_dict['mem_qty'] = node_data['bom_details']['ram_slots'] * \
                                                   node_data['num_nodes'] * multipleof

                            node_dict['mem_part1'] = ram_name_list[1]

                        else:
                            node_dict['mem_part'] = node_data['bom_details']['ram_bom_name']
                            node_dict['mem_qty'] = node_data['bom_details']['ram_slots'] * node_data[
                                'num_nodes'] * multipleof

                    if 'hdd_bom_name' in node_data['bom_details']:
                        add_riser = False
                        if server_type == 'M6' and '220' not in node_data['bom_details']['bom_name'] and \
                                node_data['bom_details']['riser_options'] == 'Storage':
                            max_node_hdd_slot = max(node_data['bom_details']['original_hdd_slot'])
                            if max_node_hdd_slot < node_data['bom_details']['hdd_slots']:
                                add_riser = True
                                no_of_riser_hdd = node_data['bom_details']['hdd_slots'] - max_node_hdd_slot
                                node_data['bom_details']['hdd_slots'] -= no_of_riser_hdd

                                if 'L' in node_name:
                                    riser_hdd = deepcopy(node_data['bom_details']['hdd_bom_name'])
                                    riser_hdd = riser_hdd[:-1]
                                    riser_hdd += 'M'
                                    node_dict['riser3_hdd_part'] = riser_hdd
                                    node_dict['riser3_hdd_qty'] = no_of_riser_hdd * node_data['num_nodes']

                                else:
                                    if no_of_riser_hdd <= 2:
                                        node_dict['riser1_hdd_part'] = node_data['bom_details']['hdd_bom_name']
                                        node_dict['riser1_hdd_qty'] = no_of_riser_hdd * node_data['num_nodes']

                                    if no_of_riser_hdd > 2:
                                        node_dict['riser1_hdd_part'] = node_data['bom_details']['hdd_bom_name']
                                        node_dict['riser1_hdd_qty'] = 2 * node_data['num_nodes']
                                        no_of_riser_hdd -= 2
                                        node_dict['riser3_hdd_part'] = node_data['bom_details']['hdd_bom_name']
                                        node_dict['riser3_hdd_qty'] = no_of_riser_hdd * node_data['num_nodes']

                        node_dict['hdd_part'] = node_data['bom_details']['hdd_bom_name']
                        node_dict['hdd_qty'] = \
                            node_data['bom_details']['hdd_slots'] * node_data['num_nodes'] * multipleof
                        # Minus the additional HDD accessory count from hdd_qty
                        node_dict['hdd_qty'] -= (acc_hdd_count * multipleof)

                    if 'ssd_bom_name' in node_data['bom_details']:
                        node_dict['ssd_part'] = node_data['bom_details']['ssd_bom_name']
                        node_dict['ssd_qty'] = \
                            node_data['bom_details']['ssd_slots'] * node_data['num_nodes'] * multipleof

                    if 'bom_add_memory_name' in node_data['bom_details'] and \
                            node_data['bom_details']['bom_add_mem_slots'] != 0:
                        node_dict['bom_add_memory_name'] = node_data['bom_details']['bom_add_memory_name']
                        node_dict['bom_add_memory_qty'] = \
                            node_data['bom_details']['bom_add_mem_slots'] * node_data['num_nodes'] * multipleof

                    if 'bom_40g_name' in node_data['bom_details']:
                        node_dict['bom_40g_name'] = node_data['bom_details']['bom_40g_name']
                        node_dict['bom_40g_count_qty'] = \
                            node_data['bom_details']['bom_40g_count'] * node_data['num_nodes'] * multipleof

                    if 'bom_10g_name' in node_data['bom_details']:
                        node_dict['bom_10g_name'] = node_data['bom_details']['bom_10g_name']
                        node_dict['bom_10g_count_qty'] = \
                            node_data['bom_details']['bom_10g_count'] * node_data['num_nodes'] * multipleof

                    if 'bom_dual_switch_name' in node_data['bom_details']:
                        node_dict['bom_dual_switch_name'] = node_data['bom_details']['bom_dual_switch_name']
                        node_dict['bom_dual_switch_count_qty'] = \
                            node_data['bom_details']['bom_dual_switch_count'] * node_data['num_nodes'] * multipleof

                    if 'bom_hercules_part' in node_data['bom_details']:
                        node_dict['bom_hercules_part'] = node_data['bom_details']['bom_hercules_part']
                        node_dict['bom_hercules_count_qty'] = \
                            node_data['bom_details']['bom_hercules_count'] * node_data['num_nodes'] * multipleof

                    if add_riser:
                        if 'L' in node_name:
                            node_dict['riser3_part'] = node_data['bom_details']['riser_bom_name'][1]
                            node_dict['riser3_qty'] = 1 * node_data['num_nodes']
                        else:
                            node_dict['riser1_part'] = node_data['bom_details']['riser_bom_name'][0]
                            node_dict['riser1_qty'] = 1 * node_data['num_nodes']
                            node_dict['riser3_part'] = node_data['bom_details']['riser_bom_name'][1]
                            node_dict['riser3_qty'] = 1 * node_data['num_nodes']

                # Adding Chassis part into bom
                if subtype == 'compute' and node_name.find("B200") != -1:
                    if 'chassis_bom_name' in node_data['bom_details']:
                        node_dict['chassis_bom_name'] = node_data['bom_details']['chassis_bom_name']
                        node_dict['chassis_qty'] = node_data['bom_details']['chassis_count']

                flag = False
                if not node_list:
                    node_list.append(node_dict)
                else:
                    for nlistdata in node_list:
                        if nlistdata['header'] == node_name and nlistdata['desc'] == node_desc:
                            count = int(nlistdata['count'])
                            total_count = count + int(node_count)
                            nlistdata['count'] = total_count
                            flag = True
                            break

                    if not flag:
                        node_list.append(node_dict)

            if server_type == 'M5':
                if 'accessories' in cdata:
                    accessory_info_list = cdata['accessories']
                    for accessory_data in accessory_info_list:
                        accessory_name = accessory_data['part_name']
                        accessory_desc = accessory_data['part_description']
                        accessory_count = accessory_data['count']

                        accessory_dict = dict()
                        accessory_dict['header'] = accessory_name
                        accessory_dict['description'] = accessory_desc
                        accessory_dict['count'] = accessory_count * multipleof
                        accessory_dict['bom_name'] = accessory_name

                        flag = False
                        if not accessory_list:
                            accessory_list.append(accessory_dict)
                        else:
                            for nlistdata in accessory_list:
                                if nlistdata['header'] == accessory_name and nlistdata['description'] == accessory_desc:
                                    count = int(nlistdata['count'])
                                    total_count = count + int(accessory_count)
                                    nlistdata['count'] = total_count
                                    flag = True
                                    break

                            if not flag:
                                accessory_list.append(accessory_dict)

            else:
                if 'accessories' in cdata:
                    accessory_info_list = cdata['accessories']
                    accessory_info_list = cdata['accessories']
                    for accessory_data in accessory_info_list:
                        accessory_name = accessory_data['part_name']
                        accessory_desc = accessory_data['part_description']
                        accessory_count = accessory_data['count']

                        accessory_dict = dict()
                        accessory_dict['header'] = accessory_name
                        accessory_dict['description'] = accessory_desc
                        accessory_dict['count'] = accessory_count * multipleof
                        accessory_dict['bom_name'] = accessory_name

                        accessory_list.append(accessory_dict)

            if acc_gpu_count:
                for acc_list in accessory_list:
                    if acc_list['bom_name'] == acc_gpu_name:
                        acc_list['count'] -= acc_gpu_count

        for index in range(len(node_list)):
            node_list[index]['description'] = ' | '.join(node_list[index]['desc'])

        node_details_table = node_list + accessory_list
        return node_details_table

    def create_bom_excel_sheet(self, wl_result_data, fipackage_count, fi_option, uploadbom):

        # cluster_list = self.scenario_data['workload_result'][0]['clusters']
        cluster_list = wl_result_data['clusters']

        # this loop is for delete cluster pairs in EPIC workload, as only one set will be outputting
        for tmp_cluster_data in cluster_list:
            dc_map_dict = defaultdict()
            for each_cluster in tmp_cluster_data:

                epiccluster = any(wl_list_tmp['wl_type'] == 'EPIC' for wl_list_tmp in each_cluster['wl_list'])
                if epiccluster:
                    dc_name = each_cluster['wl_list'][0]['dc_name']
                    if dc_name not in dc_map_dict:
                        dc_map_dict[dc_name] = each_cluster['wl_list'][0]['num_clusters']

            if dc_map_dict:
                if 'DC1' in dc_map_dict:
                    beggining_index = 1
                    end_index = dc_map_dict['DC1']
                    del tmp_cluster_data[beggining_index:end_index]

                if 'DC2' in dc_map_dict:
                    if 'DC1' not in dc_map_dict:
                        beggining_index = 1
                    elif 'DC1' in dc_map_dict:
                        beggining_index = 2

                    del tmp_cluster_data[beggining_index:]

        flat_list = [item for sublist in cluster_list for item in sublist]
        bom_node_details_table = list()

        processes_flat_list = list()
        for cluster_data in flat_list:
            isstretchcluster = any(wl_list['cluster_type'] == 'stretch' for wl_list in cluster_data['wl_list'])

            if not isstretchcluster:
                processes_flat_list.append(cluster_data)
            else:
                processes_flat_list.append(cluster_data)
                cl_index = flat_list.index(cluster_data)
                # Deleting the next stretch pair cluster info from list
                del flat_list[cl_index + 1]

        # for cluster_data in flat_list:
        for cluster_data in processes_flat_list:
            # Add Node Results per Cluster
            node_input = list()
            # node_input.append({'node_info':cluster_data['node_info']})
            node_input.append(cluster_data)

            isstretchcluster = any(wl_list['cluster_type'] == 'stretch' for wl_list in cluster_data['wl_list'])

            isepiccluster = any(wl_list_tmp['wl_type'] == 'EPIC' for wl_list_tmp in cluster_data['wl_list'])

            node_details_table = self.get_bom_nodes_details(node_input, fi_option, isstretchcluster, isepiccluster)

            for ndata in node_details_table:
                bom_node_details_table.append(ndata)

        part_details_table = OrderedDict()
        row_index = 0

        LineNumberID = 0
        ParentName = "NoParent"
        for data in bom_node_details_table:

            ParentID = 0
            wl_list = data['bom_wl_list'] if 'bom_wl_list' in data else ""

            if fipackage_count > 0:
                if 'isstretch' in data and data['isstretch']:
                    if 'fi_options' not in data:
                        fi_parts = Part.objects.filter(name=fi_option)
                    else:
                        fi_parts = Part.objects.filter(name=data['fi_options'])

                    if fi_parts:
                        fi_bom_package_name = fi_parts[0].part_json['non_package_bom_name']
                        if uploadbom:
                            LineNumberID += 1
                            part_details_per_row = [fi_bom_package_name, 2, 0, 1, 0, LineNumberID, 0, "NoParent", ""]
                        else:
                            part_details_per_row = [fi_bom_package_name, 2, 0, 1, 0]

                        row_name = "row" + str(row_index)
                        part_details_table[row_name] = part_details_per_row
                        row_index += 1

                        fipackage_count -= 1

            if fipackage_count > 0:
                if 'bom_fi_package_name' in data:
                    fipackage_count -= 1

                    if 'fi_options' in data:
                        if uploadbom:
                            LineNumberID += 1
                            part_details_per_row = [data['bom_fi_package_name'], data['bom_package_qty'],
                                                    0, 1, 0, LineNumberID, ParentID, "NoParent", wl_list]
                            ParentID = LineNumberID
                            ParentName = data['bom_fi_package_name']
                        else:
                            part_details_per_row = [data['bom_fi_package_name'], data['bom_package_qty'], 0, 1, 0]

                        row_name = "row" + str(row_index)
                        part_details_table[row_name] = part_details_per_row
                        row_index += 1

                        fi_parts = Part.objects.filter(name=data['fi_options'])
                        if fi_parts:
                            fi_bom_package_name = fi_parts[0].part_json['package_bom_name']
                            if uploadbom:
                                LineNumberID += 1
                                part_details_per_row = [fi_bom_package_name, 2, 0, 1, 0,
                                                        LineNumberID, ParentID, ParentName, wl_list]
                            else:
                                part_details_per_row = [fi_bom_package_name, 2, 0, 1, 0]

                            row_name = "row" + str(row_index)
                            part_details_table[row_name] = part_details_per_row
                            row_index += 1

                            included_software_licenses = fi_parts[0].part_json['included_software_licenses']
                            additional_license_per_fi = 1 + data['count'] - included_software_licenses
                            additional_license = additional_license_per_fi * 2

                            if additional_license > 0:
                                license_part = fi_parts[0].part_json['software_license_part']
                                if uploadbom:
                                    LineNumberID += 1
                                    part_details_per_row = [license_part, additional_license, 0, 1, 0,
                                                            LineNumberID, ParentID, ParentName, wl_list]
                                else:
                                    part_details_per_row = [license_part, additional_license, 0, 1, 0]

                                row_name = "row" + str(row_index)
                                part_details_table[row_name] = part_details_per_row
                                row_index += 1

                    # back-up name if the clusters do not support that FI
                    if 'fi_options' not in data:
                        fi_parts = Part.objects.filter(name=fi_option)
                        if fi_parts:
                            fi_non_bom_package_name = fi_parts[0].part_json['non_package_bom_name']
                            if uploadbom:
                                ParentID = 0
                                LineNumberID += 1
                                part_details_per_row = [fi_non_bom_package_name, 2, 0, 1, 0,
                                                        LineNumberID, ParentID, "NoParent", wl_list]
                            else:
                                part_details_per_row = [fi_non_bom_package_name, 2, 0, 1, 0]
                            row_name = "row" + str(row_index)
                            part_details_table[row_name] = part_details_per_row
                            row_index += 1

                        if uploadbom:
                            ParentID = 0
                            LineNumberID += 1
                            part_details_per_row = [data['bom_package_name'], data['bom_package_qty'], 0, 1, 0,
                                                    LineNumberID, ParentID, "NoParent", wl_list]
                            ParentID = LineNumberID
                            ParentName = data['bom_package_name']
                        else:
                            part_details_per_row = [data['bom_package_name'], data['bom_package_qty'], 0, 1, 0]

                        row_name = "row" + str(row_index)
                        part_details_table[row_name] = part_details_per_row
                        row_index += 1

                elif 'bom_package_name' in data:
                    if uploadbom:
                        LineNumberID += 1
                        part_details_per_row = [data['bom_package_name'], data['bom_package_qty'], 0, 1, 0,
                                                LineNumberID, ParentID, ParentName, wl_list]
                        ParentID = LineNumberID
                        ParentName = data['bom_package_name']
                    else:
                        part_details_per_row = [data['bom_package_name'], data['bom_package_qty'], 0, 1, 0]

                    row_name = "row" + str(row_index)
                    part_details_table[row_name] = part_details_per_row
                    row_index += 1

            else:
                if 'bom_package_name' in data:
                    if uploadbom:
                        LineNumberID += 1
                        part_details_per_row = [data['bom_package_name'], data['bom_package_qty'], 0, 1, 0,
                                                LineNumberID, ParentID, ParentName, wl_list]
                        ParentID = LineNumberID
                        ParentName = data['bom_package_name']
                    else:
                        part_details_per_row = [data['bom_package_name'], data['bom_package_qty'], 0, 1, 0]

                    row_name = "row" + str(row_index)
                    part_details_table[row_name] = part_details_per_row
                    row_index += 1

            if 'bom_package_name' in data:
                if 'M6' in data['bom_package_name']:
                    if uploadbom:
                        LineNumberID += 1
                        part_details_per_row = ['HXDP-SW', 1, 0, 1, 0,
                                            LineNumberID, ParentID, ParentName, wl_list]
                        ParentID = LineNumberID
                        ParentName = data['bom_package_name']
                    else:
                        part_details_per_row = ['HXDP-SW', 1, 0, 1, 0]

                    row_name = "row" + str(row_index)
                    part_details_table[row_name] = part_details_per_row
                    row_index += 1

            if 'bom_name' in data:
                if uploadbom:
                    LineNumberID += 1
                    part_details_per_row = [data['bom_name'], data['count'], 0, 1, 0,
                                            LineNumberID, ParentID, ParentName, wl_list]
                    ParentID = LineNumberID
                    ParentName = data['bom_name']
                else:
                    part_details_per_row = [data['bom_name'], data['count'], 0, 1, 0]

                row_name = "row" + str(row_index)
                part_details_table[row_name] = part_details_per_row
                row_index += 1

            if 'cpu_part' in data:
                if uploadbom:
                    LineNumberID += 1
                    part_details_per_row = [data['cpu_part'], data['cpu_qty'], 0, 1, 0,
                                            LineNumberID, ParentID, ParentName, wl_list]
                else:
                    part_details_per_row = [data['cpu_part'], data['cpu_qty'], 0, 1, 0]

                row_name = "row" + str(row_index)
                part_details_table[row_name] = part_details_per_row
                row_index += 1

            if 'bom_raid_name' in data:
                if uploadbom:
                    LineNumberID += 1
                    part_details_per_row = [data['bom_raid_name'], data['bom_raid_qty'], 0, 1, 0,
                                            LineNumberID, ParentID, ParentName, wl_list]
                else:
                    part_details_per_row = [data['bom_raid_name'], data['bom_raid_qty'], 0, 1, 0]

                row_name = "row" + str(row_index)
                part_details_table[row_name] = part_details_per_row
                row_index += 1

            if 'mem_part' in data:
                if uploadbom:
                    LineNumberID += 1
                    part_details_per_row = [data['mem_part'], data['mem_qty'], 0, 1, 0,
                                            LineNumberID, ParentID, ParentName, wl_list]
                else:
                    part_details_per_row = [data['mem_part'], data['mem_qty'], 0, 1, 0]

                row_name = "row" + str(row_index)
                part_details_table[row_name] = part_details_per_row
                row_index += 1

            if 'mem_part1' in data:
                if uploadbom:
                    LineNumberID += 1
                    part_details_per_row = [data['mem_part1'], data['mem_qty'], 0, 1, 0,
                                            LineNumberID, ParentID, ParentName, wl_list]
                else:
                    part_details_per_row = [data['mem_part1'], data['mem_qty'], 0, 1, 0]

                row_name = "row" + str(row_index)
                part_details_table[row_name] = part_details_per_row
                row_index += 1

            if 'hdd_part' in data:
                if uploadbom:
                    LineNumberID += 1
                    part_details_per_row = [data['hdd_part'], data['hdd_qty'], 0, 1, 0,
                                            LineNumberID, ParentID, ParentName, wl_list]
                else:
                    part_details_per_row = [data['hdd_part'], data['hdd_qty'], 0, 1, 0]

                row_name = "row" + str(row_index)
                part_details_table[row_name] = part_details_per_row
                row_index += 1

            if 'riser1_hdd_part' in data:
                if uploadbom:
                    LineNumberID += 1
                    part_details_per_row = [data['riser1_hdd_part'], data['riser1_hdd_qty'], 0, 1, 0,
                                            LineNumberID, ParentID, ParentName, wl_list]
                else:
                    part_details_per_row = [data['riser1_hdd_part'], data['riser1_hdd_qty'], 0, 1, 0]

                row_name = "row" + str(row_index)
                part_details_table[row_name] = part_details_per_row
                row_index += 1

            if 'riser3_hdd_part' in data:
                if uploadbom:
                    LineNumberID += 1
                    part_details_per_row = [data['riser3_hdd_part'], data['riser3_hdd_qty'], 0, 1, 0,
                                            LineNumberID, ParentID, ParentName, wl_list]
                else:
                    part_details_per_row = [data['riser3_hdd_part'], data['riser3_hdd_qty'], 0, 1, 0]

                row_name = "row" + str(row_index)
                part_details_table[row_name] = part_details_per_row
                row_index += 1

            if 'ssd_part' in data:
                if uploadbom:
                    LineNumberID += 1
                    part_details_per_row = [data['ssd_part'], data['ssd_qty'], 0, 1, 0,
                                            LineNumberID, ParentID, ParentName, wl_list]
                else:
                    part_details_per_row = [data['ssd_part'], data['ssd_qty'], 0, 1, 0]

                row_name = "row" + str(row_index)
                part_details_table[row_name] = part_details_per_row
                row_index += 1

            if 'bom_system_drive' in data:
                if uploadbom:
                    LineNumberID += 1
                    part_details_per_row = [data['bom_system_drive'], data['bom_system_qty'], 0, 1, 0,
                                            LineNumberID, ParentID, ParentName, wl_list]
                else:
                    part_details_per_row = [data['bom_system_drive'], data['bom_system_qty'], 0, 1, 0]

                row_name = "row" + str(row_index)
                part_details_table[row_name] = part_details_per_row
                row_index += 1

            if 'bom_boot_drive' in data:
                if uploadbom:
                    LineNumberID += 1
                    part_details_per_row = [data['bom_boot_drive'], data['bom_boot_qty'], 0, 1, 0,
                                            LineNumberID, ParentID, ParentName, wl_list]
                else:
                    part_details_per_row = [data['bom_boot_drive'], data['bom_boot_qty'], 0, 1, 0]

                row_name = "row" + str(row_index)
                part_details_table[row_name] = part_details_per_row
                row_index += 1

            if 'disk_package' in data:
                if uploadbom:
                    LineNumberID += 1
                    part_details_per_row = [data['disk_package'], data['disk_package_qty'], 0, 1, 0,
                                            LineNumberID, ParentID, ParentName, wl_list]
                else:
                    part_details_per_row = [data['disk_package'], data['disk_package_qty'], 0, 1, 0]

                row_name = "row" + str(row_index)
                part_details_table[row_name] = part_details_per_row
                row_index += 1

            if 'bom_add_memory_name' in data:
                if uploadbom:
                    LineNumberID += 1
                    part_details_per_row = [data['bom_add_memory_name'], data['bom_add_memory_qty'], 0, 1, 0,
                                            LineNumberID, ParentID, ParentName, wl_list]
                else:
                    part_details_per_row = [data['bom_add_memory_name'], data['bom_add_memory_qty'], 0, 1, 0]

                row_name = "row" + str(row_index)
                part_details_table[row_name] = part_details_per_row
                row_index += 1

            if 'bom_40g_name' in data:
                if uploadbom:
                    LineNumberID += 1
                    part_details_per_row = [data['bom_40g_name'], data['bom_40g_count_qty'], 0, 1, 0,
                                            LineNumberID, ParentID, ParentName, wl_list]
                else:
                    part_details_per_row = [data['bom_40g_name'], data['bom_40g_count_qty'], 0, 1, 0]

                row_name = "row" + str(row_index)
                part_details_table[row_name] = part_details_per_row
                row_index += 1

            if 'bom_10g_name' in data:
                if uploadbom:
                    LineNumberID += 1
                    part_details_per_row = [data['bom_10g_name'], data['bom_10g_count_qty'], 0, 1, 0,
                                            LineNumberID, ParentID, ParentName, wl_list]
                else:
                    part_details_per_row = [data['bom_10g_name'], data['bom_10g_count_qty'], 0, 1, 0]

                row_name = "row" + str(row_index)
                part_details_table[row_name] = part_details_per_row
                row_index += 1

            if 'bom_dual_switch_name' in data:
                if uploadbom:
                    LineNumberID += 1
                    part_details_per_row = [data['bom_dual_switch_name'], data['bom_dual_switch_count_qty'], 0, 1, 0,
                                            LineNumberID, ParentID, ParentName, wl_list]
                else:
                    part_details_per_row = [data['bom_dual_switch_name'], data['bom_dual_switch_count_qty'], 0, 1, 0]

                row_name = "row" + str(row_index)
                part_details_table[row_name] = part_details_per_row
                row_index += 1

            if 'bom_hercules_part' in data:
                if uploadbom:
                    LineNumberID += 1
                    part_details_per_row = [data['bom_hercules_part'], data['bom_hercules_count_qty'], 0, 1, 0,
                                            LineNumberID, ParentID, ParentName, wl_list]
                else:
                    part_details_per_row = [data['bom_hercules_part'], data['bom_hercules_count_qty'], 0, 1, 0]

                row_name = "row" + str(row_index)
                part_details_table[row_name] = part_details_per_row
                row_index += 1

            if 'chassis_bom_name' in data:
                if uploadbom:
                    LineNumberID += 1
                    part_details_per_row = [data['chassis_bom_name'], data['chassis_qty'], 0, 1, 0,
                                            LineNumberID, ParentID, ParentName, wl_list]
                else:
                    part_details_per_row = [data['chassis_bom_name'], data['chassis_qty'], 0, 1, 0]

                row_name = "row" + str(row_index)
                part_details_table[row_name] = part_details_per_row
                row_index += 1

            if 'riser1_part' in data:
                if uploadbom:
                    LineNumberID += 1
                    part_details_per_row = [data['riser1_part'], data['riser1_qty'], 0, 1, 0,
                                            LineNumberID, ParentID, ParentName, wl_list]
                else:
                    part_details_per_row = [data['riser1_part'], data['riser1_qty'], 0, 1, 0]

                row_name = "row" + str(row_index)
                part_details_table[row_name] = part_details_per_row
                row_index += 1

            if 'riser3_part' in data:
                if uploadbom:
                    LineNumberID += 1
                    part_details_per_row = [data['riser3_part'], data['riser3_qty'], 0, 1, 0,
                                            LineNumberID, ParentID, ParentName, wl_list]
                else:
                    part_details_per_row = [data['riser3_part'], data['riser3_qty'], 0, 1, 0]

                row_name = "row" + str(row_index)
                part_details_table[row_name] = part_details_per_row
                row_index += 1

        wb = self.workbook
        # worksheet = wb.add_worksheet('BOM Report')
        sheetname = "BOM for " + wl_result_data['result_name']
        worksheet = wb.add_worksheet(sheetname)

        # Adjust the column width.
        if uploadbom:
            column_width = [25, 10, 20, 10, 12, 12, 12, 20, 20]
        else:
            column_width = [25, 10, 20, 10, 12]

        tablehdr = wb.add_format({'bold': True, 'font_size': '12'})
        nodehdr = wb.add_format({'bold': True, 'font_size': '11'})

        # Header
        if uploadbom:
            hdr = ['Part Number', 'Quantity', 'Duration (Mnths)', 'List Price', 'Discount %',
                   'LineNumberID', 'ParentID', 'ParentName', 'WorkloadsList']
        else:
            hdr = ['Part Number', 'Quantity', 'Duration (Mnths)', 'List Price', 'Discount %']

        # Fixed Rows and columns for table. Here col=1 means second column.
        row = 0

        for colindex in range(0, len(hdr)):
            worksheet.set_column(row, colindex, column_width[colindex])
            worksheet.write(row, colindex, hdr[colindex], tablehdr)

        row = 1
        col = 0

        for rowindex in range(0, len(part_details_table)):
            key_name = "row" + str(rowindex)
            part_data_list = part_details_table[key_name]

            for item in part_data_list:

                worksheet.set_column(row, col, column_width[col])
                worksheet.write(row, col, item)

                if not col and \
                        (item.endswith("-FI") or not item.find("UCS-SP") or not item.find("UCSC-") or
                         not item.find("UCSB-") or item.find("M4-") != -1 or item.find("2X0C") != -1 or
                         item.find("HXDP") != -1 or item.find("M5-") != -1):
                    worksheet.write(row, col, item, nodehdr)

                col += 1

            row += 1
            col = 0

    def close(self):

        wb = self.workbook
        wb.close()

        return self.bom_name


def generate_bom(scenario_data, request_data):

    rdata = json.loads(request_data)

    # Format Version
    if 'nodetype' in rdata:

        sdata = json.loads(scenario_data)
        if rdata['nodetype'] == 'Fixed_Config':
            # cluster_name = rdata.get("cluster_name","") 
            # fixed_wl_res = sdata['fixed_workload_result'][cluster_name]
            fixed_wl_res = sdata['fixed_workload_result']
            wl_result_data = dict()
            wl_result_data['clusters'] = list()
            wl_result_data['result_name'] = rdata['nodetype']
            for clus_data in fixed_wl_res:
                if 'clusters' in clus_data and clus_data['clusters']:
                    wl_result_data['clusters'].extend(clus_data['clusters'])
                elif 'no_wl_clusters' in clus_data and clus_data['no_wl_clusters']:
                    wl_result_data['clusters'].extend(clus_data['no_wl_clusters'])

            fipackage_count = rdata.get('fipackage_count', 0)
            fi_option = rdata.get('fipackage_name', "HX-FI-6332")
            uploadbom = rdata.get('uploadbom', False)
            bom = BOMexcel(scenario_data)
            bom.create_bom_excel_sheet(wl_result_data, fipackage_count, fi_option, uploadbom)
            bom_path = bom.close()

            return bom_path
        else:
            wl_result_list = sdata['workload_result']

            for wl_result_data in wl_result_list:

                if wl_result_data['result_name'] == rdata['nodetype']:

                    fipackage_count = rdata.get('fipackage_count', 0)
                    fi_option = rdata.get('fipackage_name', "HX-FI-6332")
                    uploadbom = rdata.get('uploadbom', False)
                    bom = BOMexcel(scenario_data)
                    bom.create_bom_excel_sheet(wl_result_data, fipackage_count, fi_option, uploadbom)
                    bom_path = bom.close()

                    return bom_path
