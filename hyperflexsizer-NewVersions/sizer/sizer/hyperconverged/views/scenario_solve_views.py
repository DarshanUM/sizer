import copy
# import json
# import subprocess
# from ctypes import *
# from sizer.local_settings import BASE_DIR
# import os
# lib = cdll.LoadLibrary(os.path.join(BASE_DIR, "gorefactor/solvesizing.so"))

from hyperconverged.models import Node, Results, Scenario, Part, Thresholds, SpecIntData, SharedScenario, \
    feature_permission, FixedResults, EstimateDetails

from hyperconverged.serializer.WorkloadSerializer import WorkloadSerializer, WorkloadGetSerializer, \
    ScenarioGetSerializer, WorkloadPostSerializer, WorkloadGetDetailSerializer, ScenarioCloneSerializer, \
    ResultsSerializer, GenerateReportSerializer, GenerateBOMexcelSerializer, SharedScenarioSerializer, FixedResultsSerializer

from hyperconverged.solver.sizing import HyperConvergedSizer
from hyperconverged.solver.reverse_sizing import WorkloadAdder

from hyperconverged.exception import HXException, RXException
from hyperconverged.solver.attrib import HyperConstants
from base_sizer.solver.attrib import BaseConstants
from hyperconverged.views.home_page_views import HomePage

from utils.utility import *
from utils.baseview import BaseView

from hyperconverged.utilities.get_serializer import get_wl_serializer_details

from hyperconverged.views.utility_views import get_version_configs, get_configs, feature_decorator, fetch_scenario

from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status

import logging

logger = logging.getLogger(__name__)

# class go_string(Structure):
#     _fields_ = [
#         ("p", c_char_p),
#         ("n", c_int)]


def filter_node_and_part_data(filters, result_name, disk_option, cache_option, server_type, hypervisor,
                              hercules, cpu_ram_gen, hx_boost, free_disk_slots):

    parts = Part.objects.filter(status=True)
    nodes = Node.objects.filter(status=True)

    hx_cpu_clock = {part.name: '%.1f' % float(part.part_json['frequency']) for part in parts
                    if part.part_json['type'] == 'CPU' and '_UCS' not in part.name}

    node_jsons = list()
    part_jsons = list()

    for node in nodes:
        node_json = node.node_json

        if server_type != 'ALL':
            if not node.name.__contains__(server_type):
                continue

        if hypervisor == 'hyperv':

            lst_hdd_option = copy.deepcopy(node_json['hdd_options'])
            for hdd_part in lst_hdd_option:

                if '12TB' in hdd_part:
                    node_json['hdd_options'].remove(hdd_part)

            node.hercules_avail = False
            node.hx_boost_avail = False

            if '[SED]' in node.name or '[NVME]' in node.name:
                continue

        if result_name == 'All-Flash' and \
                node_json['subtype'] not in [HyperConstants.COMPUTE, HyperConstants.AIML_NODE] and 'AF' not in node.name:
            continue

        if result_name == 'All NVMe' and node_json['subtype'] not in [HyperConstants.COMPUTE] and \
                'NVME' not in node.name:
            continue

        if filters["Node_Type"]:

            if node_json['subtype'] not in ['compute', 'veeam', HyperConstants.AIML_NODE]:

                for node_filter in filters['Node_Type']:
                    '''
                    Node string now comes as HXAF-220M4S or HX240C [LFF]. Since we dont have SFF in the strings, Some 
                    pre-processing is required.
                    '''

                    if '[LFF]' in node_filter and node_json[BaseConstants.SUBTYPE] == HyperConstants.LFF_NODE:
                        node_filter_part = node_filter.split(' ')
                        if node_filter_part[0] in node.name:
                            break
                        else:
                            continue

                    elif '[7.6TB]' in node_filter and \
                            node_json[BaseConstants.SUBTYPE] == HyperConstants.ALL_FLASH_7_6TB:
                        node_filter_part = node_filter.split(' ')
                        if node_filter_part[0] in node.name:
                            break
                        else:
                            continue

                    elif '[NVME]' in node_filter and node_json[BaseConstants.SUBTYPE] == HyperConstants.ALLNVME_NODE:
                        node_filter_part = node_filter.split(' ')
                        if node_filter_part[0] in node.name:
                            break
                        else:
                            continue

                    elif '[1 CPU]' in node_filter and '[1 CPU]' in node.name:
                        node_filter_part = node_filter.split(' ')
                        if node_filter_part[0] in node.name:
                            break
                        else:
                            continue

                    elif node_json[BaseConstants.SUBTYPE] in [HyperConstants.ROBO_NODE, HyperConstants.AF_ROBO_NODE]:
                        if '[SD EDGE]' in node_filter:
                            node_filter_part = node_filter.split(' ')
                            if node_filter_part[0] in node.name:
                                break
                            else:
                                continue

                        if 'M5SD' not in node.name:
                            if node_filter in node.name:
                                break

                    elif node_json[BaseConstants.SUBTYPE] not in [HyperConstants.ALLNVME_NODE, HyperConstants.LFF_NODE]\
                            and node_filter in node.name and node_json[HyperConstants.DISK_CAGE] == 'SFF':
                        break
                else:
                    continue

        if filters['Compute_Type'] and node_json['subtype'] in [HyperConstants.COMPUTE, HyperConstants.AIML_NODE]:

            for node_filter in filters['Compute_Type']:

                node_filter = node_filter.split('-')
                '''
                because node filter is ['HX', 'B200'] or ['UCS', 'B200'] and computes can be 'UCSB-SP-B200',
                'UCSC-C200' etc
                '''
                if node_filter[0] in node.name and node_filter[1] in node.name:
                    break
            else:
                continue

        if cpu_ram_gen != 'ALL':

            cpu_intersect_list = list()

            for node_cpu in node_json['cpu_options']:

                try:
                    filter_tag = parts.get(name=node_cpu).part_json['filter_tag']

                    if cpu_ram_gen in filter_tag:
                        cpu_intersect_list.append(node_cpu)

                except Part.DoesNotExist:
                    continue

            if not cpu_intersect_list:
                continue

            node_json['cpu_options'] = cpu_intersect_list

            ram_intersect_list = list()

            for node_ram in node_json['ram_options']:

                try:
                    filter_tag = parts.get(name=node_ram).part_json['filter_tag']

                    if cpu_ram_gen in filter_tag:
                        ram_intersect_list.append(node_ram)

                except Part.DoesNotExist:
                    continue

            if not ram_intersect_list:
                continue

            node_json['ram_options'] = ram_intersect_list

        if filters["CPU_Type"]:

            cpu_intersect_list = list()

            for node_cpu in node_json['cpu_options']:

                try:
                    filter_tag = parts.get(name=node_cpu).part_json['filter_tag']
                except Part.DoesNotExist:
                    continue

                for cpu_type in filters['CPU_Type']:

                    # below condition is present in order to handle "8180 (20, 1.2)" where 8180 is cpu name
                    if cpu_type.split(' (')[0] in filter_tag:
                        cpu_intersect_list.append(node_cpu)
                        break

            if not cpu_intersect_list:
                continue

            node_json['cpu_options'] = cpu_intersect_list

        if filters["Clock"]:

            cpu_options = node_json['cpu_options']

            cpu_intersect_list = [cpu_part for cpu_part in cpu_options if hx_cpu_clock[cpu_part.split('_')[0]] in
                                  filters['Clock']]

            if not cpu_intersect_list:
                continue

            node_json['cpu_options'] = cpu_intersect_list

        if filters['RAM_Slots']:

            intersection = set(node_json['ram_slots']).intersection(set(filters['RAM_Slots']))

            if not intersection:
                continue

            node_json['ram_slots'] = list(intersection)

        if filters['RAM_Options']:

            ram_intersect_list = list()

            for node_ram in node_json['ram_options']:

                try:
                    filter_tag = parts.get(name=node_ram).part_json['filter_tag']
                except Part.DoesNotExist:
                    continue

                for ram_type in filters['RAM_Options']:
                    if ram_type in filter_tag:
                        if '[CUSTOM]' not in node_ram or not filters['RAM_Slots'] or 12 in filters['RAM_Slots'] or \
                                '[CUSTOM_6SLOT]' not in node_ram:
                            ram_intersect_list.append(node_ram)
                        break

            if not ram_intersect_list:
                continue

            node_json['ram_options'] = ram_intersect_list

        if filters["GPU_Type"]:

            if node_json['pcie_slots'] != [0]:

                gpu_intersect_list = list()

                for node_gpu in node_json['gpu_options']:

                    try:
                        filter_tag = parts.get(name=node_gpu).part_json['filter_tag']
                    except Part.DoesNotExist:
                        continue

                    for gpu_type in filters['GPU_Type']:

                        if gpu_type == filter_tag:
                            gpu_intersect_list.append(node_gpu)
                            break

                if not gpu_intersect_list:
                    node_json['pcie_slots'] = [0]
                    node_json['gpu_options'] = list()
                else:
                    node_json['gpu_options'] = gpu_intersect_list
            else:
                node_json['gpu_options'] = list()

        if node_json['subtype'] not in ['compute', HyperConstants.AIML_NODE]:

            if hercules == HyperConstants.DISABLED:

                node.hercules_avail = False

            elif hercules == HyperConstants.FORCED:

                if not node.hercules_avail:
                    continue

                node_json['pcie_slots'] = [0]

            if hx_boost == HyperConstants.DISABLED:

                node.hx_boost_avail = False

            elif hx_boost == HyperConstants.FORCED:

                if not node.hx_boost_avail:
                    continue

            # Free slot feature logic
            min_hdd_slots = min(node_json['hdd_slots'])
            max_hdd_slots = max(node_json['hdd_slots'])
            
            if(free_disk_slots > max_hdd_slots) or ((max_hdd_slots - min_hdd_slots) < free_disk_slots):
                continue
            if (disk_option == "LFF" and node_json[HyperConstants.DISK_CAGE] != 'LFF') or \
                    (disk_option == "SED" and '[SED]' not in node.name) or \
                    (disk_option == "NON-SED" and '[SED]' in node.name):
                continue

            if disk_option == 'FIPS':
                disk_intersect_list = [node_hdd for node_hdd in node_json['hdd_options'] if disk_option in node_hdd]
                if not disk_intersect_list:
                    continue

                node_json['hdd_options'] = disk_intersect_list

            if filters['Disk_Options']:

                disk_intersect_list = list()

                for node_hdd in node_json['hdd_options']:

                    for disk_type in filters['Disk_Options']:

                        if disk_type.split(' ')[0] in node_hdd and (('NVMe' in disk_type and 'NVMe' in node_hdd) or
                                                                    ('SSD' in disk_type and 'SSD' in node_hdd) or
                                                                    ('HDD' in disk_type and 'HDD' in node_hdd)):
                            disk_intersect_list.append(node_hdd)
                            break

                if not disk_intersect_list:
                    continue

                node_json['hdd_options'] = disk_intersect_list

            if cache_option != "ALL":

                ssd_intersect_list = [ssd for ssd in node_json['ssd_options'] if cache_option in ssd]
                if not ssd_intersect_list:
                    continue

                node_json['ssd_options'] = ssd_intersect_list

            if filters['Cache_Options']:

                cache_intersect_list = list()

                for node_ssd in node_json['ssd_options']:

                    for disk_type in filters['Cache_Options']:

                        if disk_type.split(' ')[0] in node_ssd:
                            cache_intersect_list.append(node_ssd)
                            break

                if not cache_intersect_list:
                    continue

                node_json['ssd_options'] = cache_intersect_list

            for gen in ['IceLake', 'Cascade']:

                if all(gen in cpu for cpu in node_json['cpu_options']):
                    node_json['ram_options'] = [ram for ram in node_json['ram_options'] if gen in ram]

                elif all(gen in ram for ram in node_json['ram_options']):
                    node_json['cpu_options'] = [cpu for cpu in node_json['cpu_options'] if gen in cpu]

            if not (node_json['cpu_options'] and node_json['ram_options']):
                continue

            if 'Riser_options' in filters:
                node_json['riser_options'] = filters['Riser_options']
            else:
                node_json['riser_options'] = 'Storage'

        node_jsons.append((node.name, node.hercules_avail, node.hx_boost_avail, node_json))

    for part in parts:
        part.part_json['name'] = part.name
        part_jsons.append(part.part_json)

    return node_jsons, part_jsons, parts


def workload_parser(wl):
    serializer = WorkloadGetDetailSerializer(wl)
    data = serializer.data
    if not isinstance(data['settings_json'], list):
        data['settings_json'] = [data['settings_json']]
    return data


def validate_nodes_post_filter(nodes, parts_qry, settings_json, wl_list):
    """
    currently being used to determine if we have at least one AF node after filtering to produce an AF result.
    :param nodes:
    :param settings_json:
    :return:
    """

    if settings_json['cpu_generation'] in ['recommended', 'cascade']:

        # if settings_json['bundle_only']:
        #
        #     return "Bundle nodes do not yet support Cascade Lake CPUs. Please change the filters"

        if any(wl[BaseConstants.WL_TYPE] == HyperConstants.VEEAM for wl in wl_list):

            return "Veeam is currently not supported with Cascade Lake CPUs. Please change the filters"

    if settings_json['hypervisor'] == 'hyperv':

        if settings_json['hercules_conf'] == HyperConstants.FORCED:
            return "Hardware acceleration isn't supported with Hyper-V. Please change the filters"

        if settings_json['hx_boost_conf'] == HyperConstants.FORCED:
            return "HX-Boost isn't supported with Hyper-V. Please change the filters"

        if settings_json['disk_option'] in ['SED', 'FIPS'] or settings_json['cache_option'] == 'SED':
            return "SED/FIPS disks currently aren't supported with Hyper-V. Please change the filters"

        if any(wl[BaseConstants.WL_TYPE] == HyperConstants.VEEAM for wl in wl_list):
            return "Veeam is currently not supported with Hyper-V. Please change the filters"

        if any(wl[BaseConstants.WL_TYPE] == HyperConstants.SPLUNK for wl in wl_list):
            return "Splunk is currently not supported with Hyper-V. Please change the filters"

        if settings_json['result_name'] in ['All NVMe'] and not any(
                [True if 'NVME' in node[0] else False for node in nodes]):
            return "All NVMe isn't supported with Hyper-V."

    if settings_json['disk_option'] in ['SED', 'FIPS'] or settings_json['cache_option'] == 'SED':

        if any(wl[BaseConstants.WL_TYPE] == HyperConstants.VEEAM for wl in wl_list):
            return "VEEAM is currently not supported with SED/FIPS disks. Please change the filters"

        if any(wl[BaseConstants.WL_TYPE] == HyperConstants.EPIC for wl in wl_list):
            return "EPIC is currently not supported with SED/FIPS disks. Please change the filters"

        if settings_json['hercules_conf'] == HyperConstants.FORCED:
            return "SED/FIPS disks currently aren't supported on hardware accelerated nodes. Please check the filters."

        if not any([True if 'SED' in node[0] else False for node in nodes]):
            return 'No valid SED/FIPS disks could be selected. Please check the filters.'

    if any(wl[BaseConstants.WL_TYPE] == HyperConstants.ROBO for wl in wl_list):

        if settings_json['hypervisor'] == 'hyperv':
            return "Edge is currently not supported with Hyper-V. Please change the filters"

        if settings_json['disk_option'] in ['SED', 'FIPS'] or settings_json['cache_option'] == 'SED':
            return "Edge is currently not supported with SED/FIPS disks. Please change the filters"

        if settings_json['cache_option'] == 'NVMe':
            return "Edge is currently not supported with NVMe disks. Please change the filters"

        if settings_json['cache_option'] == 'Optane':
            return "Edge is currently not supported with Optane disks. Please change the filters"

        # if settings_json['bundle_only']:
        #
        #     return "No Bundle ROBO nodes exist. Please change the filters"

    if any(wl.get(HyperConstants.VDI_DIRECTORY, False) or wl.get(HyperConstants.RDSH_DIRECTORY, False)
           for wl in wl_list):

        if settings_json['hypervisor'] == 'hyperv':
            return "Home Directories are currently not supported with Hyper-V. Please change the filters"


    if any(wl.get(HyperConstants.GPU_STATUS, 0) or wl[BaseConstants.WL_TYPE] == HyperConstants.AIML for wl in wl_list):

        if settings_json['hypervisor'] == 'hyperv':
            return "GPU workloads currently aren't supported with Hyper-V. Please change the filters"

        if settings_json['hercules_conf'] == HyperConstants.FORCED:
            return "GPU workloads currently aren't supported on hardware accelerated nodes. Please change the filters"

    if settings_json['filters']['GPU_Type']:

        gpus = parts_qry.filter(part_json__contains="GPU")

        for wl in filter(lambda x: x.get(HyperConstants.GPU_STATUS, 0), wl_list):

            if list(filter(lambda x: x.part_json['filter_tag'] in settings_json['filters']['GPU_Type'] and
                                     int(wl[HyperConstants.VIDEO_RAM]) in x.part_json["frame_buff"], gpus)):

                continue

            else:

                return "None of the selected GPUs can support the frame buffer requirement of %s. Please change the " \
                       "filters" % wl['wl_name']

    if any(wl.get(HyperConstants.CLUSTER_TYPE, HyperConstants.NORMAL) == HyperConstants.STRETCH for wl in wl_list):

        if settings_json['disk_option'] in ['SED', 'FIPS'] or settings_json['cache_option'] == 'SED':

            return "SED/FIPS drives are not supported in Stretch configurations. Please change the filters"

    if any(wl.get(HyperConstants.REPLICATION_FLAG, False) for wl in wl_list):

        if settings_json['hercules_conf'] == HyperConstants.FORCED:
            return "Replication is not allowed on a hardware accelerated configuration. Please change the filters"

    if settings_json['result_name'] == 'All-Flash':

        if any(wl[BaseConstants.WL_TYPE] == HyperConstants.VEEAM for wl in wl_list):
            return "VEEAM is currently not supported with All-Flash nodes."

        if not any(['AF' in node[0] for node in nodes]):
            return "No All-Flash nodes could be selected due to filters. Please change the filters"

    if not any([True if node[-1]['subtype'] not in [HyperConstants.COMPUTE, HyperConstants.AIML_NODE] else False
                for node in nodes]):
        return "No Hyperflex nodes could be selected due to filters, Please change the filters"

    if any(wl[BaseConstants.WL_TYPE] == HyperConstants.AIML and wl['input_type'] == "Video" and
           wl['expected_util'] == 'Serious Development' for wl in wl_list):

        if not settings_json['heterogenous']:
            return "\"HyperFlex only\" configurations don't support Video-Serious development AI/ML workloads. " \
                   "Please change the filters"

        if settings_json['filters']['Compute_Type'] and 'HX-C480' not in settings_json['filters']['Compute_Type']:
            return "HX-C480 compute node is mandatory when we have Video-Serious development AI/ML workloads. " \
                   "Please change the filters"

    if any(wl[BaseConstants.WL_TYPE] == HyperConstants.EPIC for wl in wl_list) and \
            settings_json['cpu_generation'] in ['recommended']:

        return "Epic workloads can only use \"Intel Platinum 8268\" or \"Intel Gold 6254\". Please change the filters"

    return None


class ScenarioSolve(BaseView):
    """
    Retrieve, update or delete a Workload .
    """

    def get(self, request, id, format=None):
        try:
            workload = Scenario.objects.get(id=id)
        except Scenario.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        sScenario = SharedScenario.objects.filter(scenario_id=id, userid=self.username)

        if not workload.username == self.username and len(sScenario) == 0:
            return Response({'status': 'error',
                             'errorMessage': 'Unauthorized Access'},
                            status=status.HTTP_400_BAD_REQUEST)

        ReturnData = self.fetch_scenario_info(workload)
        return Response(ReturnData)

    '''
    Validate if the workload can sit in the selected the cluster -- during add workload 
    '''
    def validate_cluster_support(self, scenario_id, cluster_name, wl_list):
        try:
            res_cluster_name = None
            error_msg = None
            if(cluster_name != "auto"):
                fixed_result = FixedResults.objects.get(scenario_id = scenario_id, cluster_name = cluster_name)
                res_cluster_name, error_msg = self.find_supported_cluster(fixed_result.settings_json, wl_list)

            else:
                fixed_result = Results.objects.get(scenario_id = scenario_id, name ='Fixed_Config')
                for cluster_setting in fixed_result.settings_json:
                    res_cluster_name, error_msg = self.find_supported_cluster(cluster_setting, wl_list)
                    if(res_cluster_name):
                        break

            if error_msg:
                return Response({'status': 'error',"res_cluster_name": res_cluster_name, "errorMessage": error_msg},status=status.HTTP_404_NOT_FOUND )
            else:
                return Response({"res_cluster_name": res_cluster_name}, status = status.HTTP_200_OK)

        except Results.DoesNotExist:
            return Response({'status': 'error', "errorMessage": "Invalid scenario id"},status=status.HTTP_404_NOT_FOUND )
            # return {"errorMessage": "Invalid scenario id" }
        except FixedResults.DoesNotExist:
            return Response({'status': 'error', "errorMessage": "Invalid scenario or cluster name"},status=status.HTTP_404_NOT_FOUND )
            # return {'status': 'error',"res_cluster_name": res_cluster_name, "errorMessage": "Invalid scenario or cluster name"}


    '''
    This method is called when cluster selection as AUTO and we have clusters in Fixed_Configuration 
    '''
    def find_supported_cluster(self, cluster_setting, wl_list):

        get_wl_serializer_details(wl_list)
        # cluster_setting = fixed_result.settings_json
        size_wl_list = list()
        wl_req_len = len(wl_list)
        input_from_ui = cluster_setting['workloads']
        for n in range(0,wl_req_len):
            if((wl_list[n]['wl_name']  in  input_from_ui) or wl_list[n].get('isDirty')):
                size_wl_list.append(wl_list[n])

        try:
            WorkloadAdder(settings_json= [cluster_setting],
                                        workload_list=size_wl_list)
            return  cluster_setting['cluster_name'], None
        except RXException as error:
            return None, str(error)


    '''
    Fixed scenario logic is implemented. isDirty - to identify if the workloaded is added/modified
    '''
    def handle_fixed_scenario(self, to_serialize, request_data, scenario_object, fixed_setting_json_arr):

        # is_fixed_config = False # this data has to come from request_data (UI)

        error_msg = ""
        setting_count = len(fixed_setting_json_arr)
        response = list()
        # iterate each
        for fixed_setting_json in fixed_setting_json_arr:

            # if(not fixed_setting_json['isDirty']):
            #     continue
            if not ('result_name' in fixed_setting_json):
                fixed_setting_json['result_name'] = 'Fixed_Config'
            wl_isDirty = False
            setting_name = fixed_setting_json['cluster_name']
            if setting_name == 'cluster_default':
                continue
            if fixed_setting_json['hercules_conf'] == 'enabled':
                fixed_setting_json['hercules_conf'] = 'disabled'

            if fixed_setting_json['hx_boost_conf'] == 'enabled':
                fixed_setting_json['hx_boost_conf'] = 'disabled'

            if 'sky' in (fixed_setting_json['node_properties']['cpu'][0]).lower():
                return 'Sizing Failed. One of the cluster in Fixed_result contain Skylake CPU or RAM which are deprecated. Please create a new sceanrio with new CPU/RAM'
            to_serialize['settings_json'] = fixed_setting_json #request_data['settings_json'][0]
            serializer = WorkloadPostSerializer(data=to_serialize)
            if not serializer.is_valid():
                error = serializer.errors
                return error
                # return Response({'status': 'error', 'errorCode': 4, 'errorMessage': error},
                #                 status=status.HTTP_403_FORBIDDEN)

            # scenario_object.workload_json = request_data # this is required to store UI data info. this is also not requried because in the previous method is already saved
            # scenario_object.settings_json = [request_data['settings_json'][0],fixed_setting_json] # this may not required - code need to change
            # error_msg = None


            # size_wl_list = copy.deepcopy(request_data['wl_list'])
            size_wl_list = list()
            req_len = len(request_data['wl_list'])
            input_from_ui = fixed_setting_json['workloads']
            set_input_from_ui = set(input_from_ui)
            lst_wl_type = list()
            for n in range(0,req_len):
                wl_isDirty = request_data['wl_list'][n]['isDirty']

                # if((request_data['wl_list'][n]['wl_name']  in  input_from_ui)):
                if((request_data['wl_list'][n]['wl_name']  in  input_from_ui) or ('wl_cluster_name' in request_data['wl_list'][n] and  wl_isDirty and request_data['wl_list'][n]['wl_cluster_name'] == setting_name)):
                    size_wl_list.append(request_data['wl_list'][n])
                    # adding workload where wl_name is not present in selected cluster
                    set_input_from_ui.add(request_data['wl_list'][n]['wl_name'] )
                    lst_wl_type.append(request_data['wl_list'][n][HyperConstants.INTERNAL_TYPE])

                request_data['wl_list'][n]['isDirty'] = False # reset the isDirty tag

            response = list()
            fixed_setting_json['workloads'] = list(set_input_from_ui)
            fixed_setting_json['workloads_type'] = lst_wl_type
            try:
                workload_adder = WorkloadAdder(settings_json= [fixed_setting_json],
                                            workload_list=size_wl_list)
                response = workload_adder.get_util()
                if len(size_wl_list) > 0:
                    response[0].pop('no_wl_clusters', 'No Key found')
                    cluster_utilizations = response[0]['clusters'][0][0]['Utilization']
                    cluster_wl_type = response[0]['clusters'][0][0]['wl_list'][0][HyperConstants.INTERNAL_TYPE]
                    workload_adder.validate_utilizations(cluster_utilizations, cluster_wl_type)
                else:
                    logger.info("handle_fixed_scenario: Fixed config cluster has no workload result. Scenario_id:"+ str(scenario_object.id) + " cluster_name:"+  setting_name)
                    response[0].pop('clusters', 'No Key found')

            except RXException as error:
                error_msg = str(error)

            # Sizing calculator result irrespective of Sizing failure
            try:
                # scenario_settings = fixed_setting_json
                if 'EOLed' in error_msg:
                    default_settings_json = HomePage.get_fixed_default_settings(scenario_object)
                    error_msg += " (" + setting_name + "- Using default node for Calculator result)"
                    fixed_setting_json['node_properties'] = default_settings_json['node_properties']

                sizingcalc_response = WorkloadAdder.get_sizing_calculator_result(fixed_setting_json)
                if response:
                    response[0]['sizing_calculator'] = sizingcalc_response
                    response[0]['cluster_name'] = setting_name
                else:
                    sizingcalc_result = dict()
                    sizingcalc_result['cluster_name'] = setting_name
                    sizingcalc_result['result_name'] = fixed_setting_json['result_name']
                    sizingcalc_result['sizing_calculator'] = sizingcalc_response
                    response.append(sizingcalc_result)

            except RXException as calcerror:
                calcerror = str(calcerror)

            self.save_fixed_result(setting_name, response , scenario_object.id, fixed_setting_json, error_msg)

            # request_data['settings_json'][0]['result_name'] = 'Fixed_Config'
        self.save_result('Fixed_Config', response, fixed_setting_json_arr , scenario_object.id, error_msg)

    def clear_fixed_result_json(self,id):
        fix_res = FixedResults.objects.filter(scenario_id=id)
        for res in fix_res:
            res.delete()
            # res.error_json = dict()
            # res.result_json = list()
            # res.save()
        # return res.settings_json

    def post(self, request, id, format=None):

        try:
            work_load = Scenario.objects.get(id=id)
        except Scenario.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        sScenario = SharedScenario.objects.filter(scenario_id=id, userid=self.username)

        if work_load.username != self.username and len(sScenario) == 0:
            return Response({'status': 'error',
                             'errorMessage': 'Unauthorized Access'},
                            status=status.HTTP_400_BAD_REQUEST)

        if len(sScenario) and not sScenario[0].acl:
            return Response({'status': 'error',
                         'errorMessage': 'Write access permission is required to modify Scenario'},
                        status=status.HTTP_400_BAD_REQUEST)

        # TODO: in UI- send isFixed - if only isFixed need to size
        data = JSONParser().parse(request)

        errorMessage, isValidate = self.process_scenario_sizing(data, work_load)
        if isValidate:
            return errorMessage
        if errorMessage:
            return Response({'status': 'error', 'errorCode': 4, 'errorMessage': errorMessage}, status=status.HTTP_403_FORBIDDEN)
        return Response(list(), status=status.HTTP_200_OK)

    def process_scenario_sizing(self, data, work_load):

        ddl_cluster = data.get('ddl_cluster_name', None)

        if(ddl_cluster):
            validate_msg = self.validate_cluster_support(work_load.id, ddl_cluster, data['wl_list'])
            return validate_msg, True

        sizing_for = data.get('sizing_for', 'optimal')
        ddl_sizing_res_arr = data.get('ddl_sizing_res_arr', 'all')
        # data['settings_json'][3]= self.delete_the_function(id)

        overwrite = data.get('overwrite', False)
        settings_json_array = data['settings_json']

        # this condition is for the last wl when we delete it/for the first time scenario is created
        serializer_data, replication_enabled = get_wl_serializer_details(data['wl_list'])
        serializer_data['sizing_type'] = data['sizing_type']

        fixed_serializer_data = copy.deepcopy(serializer_data)

        if len(data['wl_list']) == 0:
            # if data['sizing_type'] == 'optimal':
            # work_load.settings_json = data["settings_json"]
            work_load.workload_result = list()
            work_load.workload_json = list()
            work_load.sizing_type = data['sizing_type']
            work_load.save()

            for settings_json in settings_json_array:
                if isinstance(settings_json, list):
                    error_msg = self.handle_fixed_scenario(to_serialize = fixed_serializer_data, request_data = data, scenario_object = work_load, fixed_setting_json_arr = settings_json)
                    if error_msg:
                        return error_msg
                        # return Response({'status': 'error', 'errorCode': 4, 'errorMessage': error_msg}, status=status.HTTP_403_FORBIDDEN)
                    continue

                # TODO:UI FIX FOR M6
                # if settings_json['filters']['CPU_Type'] is None:
                #    settings_json['filters']['CPU_Type'] = list()

                result_name = settings_json['result_name']
                if result_name == "Lowest_Cost":
                    settings_json["ddl_sizing_res_arr"] = ddl_sizing_res_arr

                self.save_result(result_name, list(), settings_json, work_load.id, error=None)

            return None, False
            # return Response(workload_parser(work_load), status=status.HTTP_200_OK)

        wl_list = list()
        resp = ''

        # 10.2 - Storage_protocol - iSCSI is only available for DB Wl, Compute and Capacity Sizer Wl now
        # By default NFS is selected for all other Wl so set the value as NFS for all remaining Wl

        for wtype, wdetail in data.items():
            if wtype == 'wl_list':
                for workload in wdetail:
                    if 'storage_protocol' not in workload:
                        workload['storage_protocol'] = 'NFS'
                    wl_list.append(workload)

        temp_resp = list()
        temp_resp_error = list()

        for settings_json in settings_json_array:

            if isinstance(settings_json, list):
                if sizing_for == 'optimal':
                    continue
                result_name = "Fixed_Config"  # settings_json[0]['result_name']
                if result_name in ddl_sizing_res_arr:
                    error_msg = self.handle_fixed_scenario(to_serialize=fixed_serializer_data, request_data = data,scenario_object = work_load, fixed_setting_json_arr = settings_json)
                    if error_msg:
                        return error_msg, False
                        # return Response({'status': 'error', 'errorCode': 4, 'errorMessage': error_msg}, status=status.HTTP_403_FORBIDDEN)
                # wl = work_load
                # wl.workload_json = data
                # wl.save()
                continue
            else:
                result_name = settings_json['result_name']
                if result_name == "Lowest_Cost":
                    settings_json["ddl_sizing_res_arr"] = ddl_sizing_res_arr
                    if sizing_for == 'fixed':
                        self.save_result(result_name, resp, settings_json, work_load.id, None, False)
                        continue

                if sizing_for == 'fixed':
                    continue
            # if result_name == "Fixed_Config":

            # TODO:UI FIX FOR M6
            # if settings_json['filters']['CPU_Type'] is None:
            #    settings_json['filters']['CPU_Type'] = list()

            # if 'Riser_options' not in settings_json['filters']:
            #    settings_json['filters']['Riser_options'] = 'Storage'

            serializer_data['settings_json'] = settings_json

            filters = settings_json['filters']

            if replication_enabled:
                settings_json['dr_enabled'] = True
            else:
                settings_json['dr_enabled'] = False

            bundle_only = settings_json["bundle_only"]
            disk_option = settings_json["disk_option"]
            cache_option = settings_json["cache_option"]
            server_type = settings_json["server_type"]
            cpu_ram_gen = settings_json["cpu_generation"]
            hypervisor = settings_json["hypervisor"]
            hercules = settings_json["hercules_conf"]
            hx_boost = settings_json["hx_boost_conf"]

            free_disk_slots = 0
            if 'free_disk_slots' in settings_json:
                free_disk_slots = settings_json['free_disk_slots']
            else:
                settings_json['free_disk_slots'] = free_disk_slots

            serializer = WorkloadPostSerializer(data=serializer_data)
            if not serializer.is_valid():
                error = serializer.errors
                return error, False

            if wl_list:

                if result_name in ddl_sizing_res_arr:
                    nodes, parts, parts_qry = filter_node_and_part_data(filters, result_name, disk_option,
                                                                        cache_option, server_type, hypervisor,
                                                                        hercules, cpu_ram_gen, hx_boost, free_disk_slots)

                    errors = validate_nodes_post_filter(nodes, parts_qry, settings_json, wl_list)
                else:
                    errors = result_name + " is not selected. Please change the filters to see the result."

                resp = list()
                try:
                    if not errors:
                        # cmd = os.path.join(BASE_DIR, "gorefactor/solvesizing")
                        # proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                        #         stderr=subprocess.PIPE)
                        # (output, err) = proc.communicate()
                        # proc_status = proc.wait()

                        # r=lib.fun(10,20)


                        # lib.bar.restype = c_char_p
                        # a = lib.bar(b, c_char_p(str))
                        # lib.Hello(c_char_p(b'testString'))
                        # b = go_string(c_char_p(b'testString'), len('testString'))
                        # lib.Hello(b, c_char_p(b'testString'))

                        
                        # setting_dump = json.dumps(settings_json)
                        # wl_list_dump = json.dumps(wl_list)
                        # nodes_dump = json.dumps(nodes)
                        # go_setting = go_string(c_char_p(setting_dump.encode('utf-8')), len(setting_dump))
                        # go_wl_list = go_string(c_char_p(wl_list_dump.encode('utf-8')), len(wl_list_dump))
                        # go_node = go_string(c_char_p(nodes_dump.encode('utf-8')), len(nodes_dump))
                        # lib.SolveSizing(go_setting, go_wl_list,go_node, work_load.id, "")
                        
                        solver = HyperConvergedSizer(parts, nodes, wl_list, settings_json, work_load.id)
                        resp = solver.solve(bundle_only)
                except HXException as e:
                    errors = str(e)
            
            if overwrite:
                self.save_result(result_name, resp, settings_json, work_load.id, errors)
            else:
                temp_resp.extend(resp)
                if errors:
                    temp_resp_error = [{'message': errors, 'result_name': result_name}]

        
        wl = work_load
        wl.workload_json = data
        wl.status = True

        wl.save()
        return None, False

    def put(self, request, id, format=None):

        try:
            work_load = Scenario.objects.get(id=id)
        except Scenario.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        sScenario = SharedScenario.objects.filter(scenario_id=id, userid=self.username)
        if not work_load.username == self.username and len(sScenario) == 0:
            return Response({'status': 'error', 'errorMessage': 'Unauthorized Access'},
                            status=status.HTTP_400_BAD_REQUEST)

        if len(sScenario) and not sScenario[0].acl:
            return Response({'status': 'error',
                             'errorMessage': 'Write access permission is required to modify Scenario'},
                            status=status.HTTP_400_BAD_REQUEST)

        if work_load.settings_json is None:
            work_load.settings_json = dict()

        data = JSONParser().parse(request)

        if 'settings_json' not in data.keys():
            raise Exception("No_Settings_Json | " + str(id) + "|")

        '''
        Check uniqueness of the scenario name and username, if scenario name is provided for update.
        '''

        if 'name' in data.keys():
            workloads = Scenario.objects.filter(status=True, name=data['name'], username=self.username).order_by('name')

            if len(workloads) > 1 or (len(workloads) == 1 and not (workloads[0].id == int(id))):
                return Response({'status': 'error', 'errorMessage': 'Scenario name must be unique to the user.'},
                                status=status.HTTP_400_BAD_REQUEST)

            work_load.name = data['name']

        if 'settings_json' in data.keys():
            work_load.settings_json = data['settings_json']

            scenario_result = Results.objects.filter(scenario_id=id)
            for result in scenario_result:
                if result.name != 'Fixed_Config':
                    result.settings_json['account'] = data['settings_json'][0]['account'] \
                        if 'account' in data['settings_json'][0] else ""
                    result.save()

        work_load.save()

        serializer = WorkloadGetDetailSerializer(work_load)

        return Response(serializer.data, status=status.HTTP_200_OK)

    """
    To delete the scenario from home page
    """
    def delete(self, request, id, format=None):
        try:
            work_load = Scenario.objects.get(id=id)
        except Scenario.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not work_load.username == self.username:
            return Response({'status': 'error', 'errorMessage': 'Unauthorized Access. Only owner can delete scenario'},
                            status=status.HTTP_400_BAD_REQUEST)

        workload_results = Results.objects.filter(scenario_id=work_load.id)

        for result in workload_results:
            result.delete()

        # Delete all the results from Fixed Result Table 
        fixed_results =  FixedResults.objects.filter(scenario_id=work_load.id)
        for result in fixed_results:
            result.delete()
        
        work_load.delete()

        # Deleting entries from shared scenario table
        shared_result = SharedScenario.objects.filter(scenario_id=id)
        shared_result.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def save_result(result_name, result, settings, id, error, save_resp = True):
        results = Results.objects.filter(scenario_id=id, name=result_name)

        if len(results) == 0:
            # if there is no entry in the result table
            new_result = Results()
            if save_resp:
                new_result.result_json = result
            new_result.settings_json = settings
            new_result.name = result_name
            new_result.scenario_id = id
            new_result.error_json = {'message': error, 'result_name': result_name}
            new_result.save()
        else:
            # if record already exist
            saved_result = results[0]
            if save_resp:
                saved_result.result_json = result
            saved_result.settings_json = settings
            saved_result.error_json = {'message': error, 'result_name': result_name}
            saved_result.save()

    @staticmethod
    def save_fixed_result(cluster_name, result, id, settings, error):
        results = FixedResults.objects.filter(scenario_id=id, cluster_name=cluster_name)

        if len(results) == 0:
            # if there is no entry in the result table
            new_result = FixedResults()
            new_result.result_json = result
            new_result.cluster_name = cluster_name
            new_result.scenario_id = id
            new_result.settings_json = settings
            new_result.error_json = {'message': error, 'result_name': 'Fixed_Config', 'cluster_name': cluster_name}
            new_result.save()
        else:
            # if record already exist
            saved_result = results[0]
            saved_result.result_json = result
            saved_result.settings_json = settings
            saved_result.error_json = {'message': error, 'result_name': 'Fixed_Config', 'cluster_name': cluster_name}
            saved_result.save()


    """
    Used by both Get and Post Sceanrio to fetch the particular scenario info to send to the UI
    """
    @staticmethod
    def fetch_scenario_info(workload):
        
        serializer = WorkloadGetDetailSerializer(workload)
        results = Results.objects.filter(scenario_id=workload.id)
        # Fetching only the recent five successfully created estimate id to display in the UI
        estimate_details = EstimateDetails.objects.filter(scenario_id=workload.id, estimate_response='success').values('estimate_id').order_by('id')[::-1][:5]

        ReturnData = dict()
        fixed_warning = ""
        optimal_warning = ""
        ReturnData['id'] = serializer.data['id']
        ReturnData['name'] = serializer.data['name']
        ReturnData['sizing_type'] = serializer.data['sizing_type']
        wl_list = serializer.data['workload_json']['wl_list'] if 'wl_list' in serializer.data['workload_json'] else list()
        new_wl_list = list()
        for wl in wl_list:
            if wl[HyperConstants.INTERNAL_TYPE] == HyperConstants.ROBO_BACKUP:
                copy_wl = copy.deepcopy(wl)
                copy_wl[HyperConstants.WL_TYPE] = HyperConstants.ROBO
                copy_wl[HyperConstants.WL_NAME] += '_BACKUP'
                copy_wl[HyperConstants.INTERNAL_TYPE] = HyperConstants.ROBO_BACKUP_SECONDARY
                new_wl_list.append(copy_wl)
        if new_wl_list:
            wl_list.extend(new_wl_list)
            serializer.data['workload_json']['wl_list'] = wl_list
        ReturnData['workload_json'] = serializer.data['workload_json']
        ReturnData['scen_label'] = serializer.data['scen_label']
        ReturnData['updated_date'] = serializer.data['updated_date']
        ReturnData['ddl_sizing_res_arr'] = ["All-Flash", "Lowest_Cost", "All NVMe", "Fixed_Config"]

        sharedScenarios = SharedScenario.objects.filter(scenario_id=workload.id)
        if len(sharedScenarios) > 0:
            ReturnData['sharedcount'] = len(sharedScenarios)
        else:
            ReturnData['sharedcount'] = 0

        if len(results):
            result_data = list()
            fix_result_data = list()
            settings_data = list()
            error_list = list()
            # if serializer.data['sizing_type'] == 'optimal':
            result_mapper = {"All-Flash": 1, "Lowest_Cost": 0, "All NVMe": 2, "Fixed_Config": 3}
            # else:
            #     result_mapper = {'Fixed Config': 0}
            index = 0
            for result in results:

                # result_data.extend(result.result_json)
                if isinstance(result.settings_json, list):
                    index = 3# "Fixed_Config": 3
                    fixed_results = FixedResults.objects.filter(scenario_id=workload.id)
                    if len(fixed_results):
                        for fixed_res in fixed_results:
                            fix_result_data.extend(fixed_res.result_json)
                            if (not fixed_warning) and \
                                    (fixed_res.settings_json['cluster_name'] != 'cluster_default') and \
                                    'sky' in (fixed_res.settings_json['node_properties']['cpu'][0]).lower():
                                fixed_warning = 'Results contains Skylake CPU which are deprecated. Kindly create another scenario. CPU filters are replaced with default settings.'
                            if 'message' in fixed_res.error_json and fixed_res.error_json['message']:
                                error_list.append(fixed_res.error_json)
                    else:
                        fix_result_data.extend(result.result_json)
                        if 'message' in result.error_json and result.error_json['message']:
                            error_list.append(result.error_json)
                else:

                    # if(not optimal_warning and len(list(filter(lambda cpu_type: cpu_type[1] == 2 , result.settings_json['filters']['CPU_Type'])))):
                    #     optimal_warning ="One of the Result contains Skylake CPU which are depreceted. Sizing/Resizing may generate loss of data."
                    # remove all skylake CPU,RAM and CPU Generation from filters
                    result.settings_json['filters']['CPU_Type'] = list(filter(lambda cpu_type: cpu_type[1] == '2', result.settings_json['filters']['CPU_Type']))
                    result.settings_json['cpu_generation'] = 'recommended' if 'sky' in result.settings_json['cpu_generation'] else result.settings_json['cpu_generation']

                    if result.settings_json["result_name"] == "Lowest_Cost" and 'ddl_sizing_res_arr' in result.settings_json:
                        ReturnData['ddl_sizing_res_arr'] = result.settings_json["ddl_sizing_res_arr"]
                    index = result_mapper.get(result.settings_json["result_name"])
                    result_data.extend(result.result_json)
                    if not optimal_warning:
                        optimal_warning = ScenarioSolve.check_skylak_part(result.result_json)

                if not index:
                    index = 0

                settings_data.insert(index, result.settings_json)

                if 'message' in result.error_json and result.error_json['message'] and index !=3:
                    error_list.append(result.error_json)

            result_data.extend(fix_result_data)
            # fixed_merge: when new scenario is created - workload_result used to be empty.
            # but now result_data will have 1 result which is from Fix_config
            ReturnData['workload_result'] = result_data
            ReturnData['settings_json'] = settings_data
            ReturnData['errors'] = error_list

        else:
            ReturnData['workload_result'] = serializer.data['workload_result']
            ReturnData['settings_json'] = [serializer.data['settings_json']]
        ReturnData['scenario_warning'] = optimal_warning if optimal_warning else fixed_warning
        estimated_id = ['New']
        estimate_details = [list(li.values()) for li in estimate_details]
        [estimated_id.append(ids[0]) for ids in estimate_details if ids[0] not in estimated_id]
        ReturnData['estimate_id_res'] = estimated_id
        return ReturnData
    
    """
    Check for deprecated Skylak CPU in the resized data
    """
    @staticmethod
    def check_skylak_part(result_json):
        for clusters in result_json:
            for optimal in clusters['clusters']:
                for utilization in optimal:
                    for node_info in utilization['node_info']:
                            if 'sky' in (node_info['model_details']['cpu_part']).lower():
                                    optimal_warning ="One of the Results contains Skylake CPU which are deprecated. Sizing/Resizing may fail or replace with the new Parts. CPU filters are replaced with default settings."
                                    return optimal_warning
        return ""

# class get_all_scenarios(BaseView):
#
#     """
#     Retrieve all  Workloads .
#     """
#
#     def get(self, request, format=None):
#         try:
#             tkn = request.META["HTTP_AUTHORIZATION"]
#         except:
#             str = {'status':'error', 'errorCode':'101', 'errorMessage':MSG_101}
#             return Response(str)
#         status, usrname = user_verification(tkn)
#         scenario_list = list()
#         if status == False:
#             return Response({'status':'error', 'errorCode':'102', 'errorMessage':MSG_102})
#         try:
#             work_load = Scenario.objects.filter(added_by_id=usrname.id, status=True). \
#                 defer('workload_json','workload_result', 'status', 'created_date').order_by('name')
#         except Scenario.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#
#         serializer = ScenarioGetSerializer(work_load, many=True)
#         resp = {"scenario_list":serializer.data}
#         return Response(resp)


class ResultDetails(BaseView):
    def get(self, request, id, format=None):

        try:
            scenario = Scenario.objects.get(id=id)
        except Scenario.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        sScenario = SharedScenario.objects.filter(scenario_id=id, userid=self.username)
        if not scenario.username == self.username and len(sScenario) == 0:
            return Response({'status': 'error', 'errorMessage': 'Unauthorized Access'},
                            status=status.HTTP_400_BAD_REQUEST)

        results = Results.objects.filter(scenario_id=id).order_by("name")

        resultsArray = list()

        for result in results:
            result_json = ResultsSerializer(result).data
            resultsArray.append(result_json)

        return Response(resultsArray)

    def put(self, request, scenario_id, format=None):

        try:
            scenario = Scenario.objects.get(id=scenario_id)
        except Scenario.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        shared_scenario = SharedScenario.objects.filter(scenario_id=scenario_id,
                                                        userid=self.username)
        if not scenario.username == self.username and not shared_scenario:
            return Response({'status': 'error', 'errorMessage': 'Unauthorized Access'},
                            status=status.HTTP_400_BAD_REQUEST)

        data = JSONParser().parse(request)

        result_filter = Results.objects.filter(scenario_id=scenario_id)

        if "error_json" not in data:
            data["error_json"] = dict()
        for index, result_check in enumerate(result_filter):
            if result_check:
                result_object = result_check
            else:
                result_object = Results()
            if not data["result_json"]:
                result_object.result_json = list()
            else:
                result_object.result_json = [data["result_json"]]
            result_object.settings_json = data["settings_json"][index]
            result_object.error_json = data["error_json"]

            if not result_check:
                result_object.scenario_id = scenario_id
                result_object.name = data["settings_json"][index]["result_name"]
            result_object.save()

        return Response(status=status.HTTP_200_OK)

    '''
    delete the add cluster functionality - also update the settings_json
    '''
    def post(self, request, scenario_id):
        try:
            work_load = Scenario.objects.get(id= scenario_id)
        except Scenario.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        cluster_name = request.data.get('cluster_name')
        if(not cluster_name):
            return Response("Cluster name can not be empty",status=status.HTTP_404_NOT_FOUND)
        try:
            if(FixedResults.objects.filter(cluster_name = cluster_name,scenario_id = scenario_id).count() != 0):
                fixed_results = FixedResults.objects.get(cluster_name = cluster_name,scenario_id = scenario_id)
                fixed_results.delete()

                # update the settings_json where name = Fixed_Config
                fix_result_table = Results.objects.get(scenario_id = scenario_id, name = 'Fixed_Config')
                fix_res_setting = fix_result_table.settings_json
                
                index = -1
                for n in range(0,len(fix_res_setting)): 
                    if fix_res_setting[n]['cluster_name'] == cluster_name:
                        index = n
                        break 
                fix_res_setting.pop(index)
                fix_result_table.settings_json = fix_res_setting
                fix_result_table.save()

                if not fix_res_setting:
                    # response = list()
                    # sizingcalc_result = dict()
                    scenario_settings = HomePage.get_fixed_default_settings(work_load)
                    scenario_settings['result_name'] = 'Fixed_Config'
                    # sizingcalc_result['sizing_calculator'] = WorkloadAdder.get_sizing_calculator_result(scenario_settings)
                    # sizingcalc_result['cluster_name'] = scenario_settings['cluster_name']
                    # sizingcalc_result['result_name'] = scenario_settings['result_name']
                    # response.append(sizingcalc_result)
                    ScenarioSolve.save_result('Fixed_Config', list(), [scenario_settings], scenario_id,
                                    error=None)
                    fix_res_setting = [scenario_settings]
                
                # for updating the workload_json -> setting_json
                setting_index = -1
                if 'settings_json' in work_load.workload_json:
                    for n in range(0,len(work_load.workload_json['settings_json'])):
                        if isinstance(work_load.workload_json['settings_json'][n], list):
                            setting_index = n
                            break
                    work_load.workload_json['settings_json'][setting_index] = fix_res_setting
                work_load.save()
                        

        except FixedResults.DoesNotExist:
            logger.info('No data found in the database. May be only one cluster added without worload - ResultDetails. cluster_name:'+ cluster_name)
            return Response("No record found. cluster_name:" + cluster_name ,status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
          

    def delete(self, request, scenario_id, format=None):

        try:
            result = Results.objects.get(id=scenario_id)
        except Results.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            scenario = Scenario.objects.get(id=result.scenario_id)
        except Scenario.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        sScenario = SharedScenario.objects.filter(scenario_id=scenario_id, userid=self.username)
        if not scenario.username == self.username and len(sScenario) == 0:
            return Response({'status': 'error', 'errorMessage': 'Unauthorized Access'},
                            status=status.HTTP_400_BAD_REQUEST)

        if result.name == 'default':
            return Response({'status': 'error', 'errorMessage': 'Cannot delete default result.'},
                            status=status.HTTP_400_BAD_REQUEST)

        result.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ScenarioFetch(BaseView):
    """
    To retrieve scenario details
    """

    def get(self, request):
        scen_id = request.query_params['id']
        scenario = Scenario.objects.get(id=scen_id)
        serializer = WorkloadGetSerializer(scenario)
        scen_result = fetch_scenario(serializer.data)
        return Response(scen_result)


'''
        if 'id' in request.query_params:
            scen_id = request.query_params['id']
            try:
                scenario = Scenario.objects.get(id=scen_id)
            except HXException:
                raise HXException("Scenario not found")
        else:
            return Response()

        scen_result['id'] = scenario.id
        scen_result['name'] = scenario.name
        scen_result['username'] = scenario.username
        scen_result['settings_json'] = scenario.settings_json
        scen_result['sizing_type'] = scenario.sizing_type
        scen_result['scen_label'] = scenario.scen_label
        scen_result['updated_date'] = scenario.updated_date

        if SharedScenario.objects.filter(scenario_id=scen_id).count():
            scen_result['isshared'] = True
        else:
            scen_result['isshared'] = False

        if scenario.workload_json:
            if 'wl_list' in scenario.workload_json.keys():
                scen_result['wl_count'] = len(scenario.workload_json['wl_list'])
        else:
            scen_result['wl_count'] = 0

        if scenario.sizing_type == 'optimal':
            results = Results.objects.filter(name='Lowest_Cost', scenario_id=scenario.id)
        else:
            results = Results.objects.filter(name='Fixed Config', scenario_id=scenario.id)

        if len(results) > 0 and len(results[0].result_json) > 0:
            scen_result['cluster_count'] = sum([len(cluster) for cluster in results[0].result_json[0]['clusters']])
            scen_result['node_count'] = results[0].result_json[0]['summary_info']['num_nodes']
        else:
            scen_result['cluster_count'] = 0
            scen_result['node_count'] = 0
'''

'''
def  get_userdetails_ldap(userid, LDAP_URL, LDAP_BIND_DETAILS):
    user_details = dict()
    try:
        connect = ldap.initialize(LDAP_URL)
        connect.simple_bind_s(LDAP_BIND_DETAILS)
        connect.protocol_version = ldap.VERSION3
    except:
        #raise Exception("Failed to connect the LDAP server.")
        pass
        user_details['emp_number'] = 'NA'
        user_details['emp_email_id'] = 'NA'
        user_details['emp_company'] = 'NA'
        return user_details        


    base_dn = 'uid=' + userid  + ',OU=ccoentities,O=cco.cisco.com'
    search_scope = ldap.SCOPE_SUBTREE
    retrieve_attributes = ['company', 'givenName', 'sn', 'employeeNumber', 'mail', 'lastLogin', 'accessLevel']
    search_filter = "cn=*"

    try:
        ldap_result_id = connect.search(base_dn, search_scope, search_filter, retrieve_attributes)
        while True:
            result_type, result_data = connect.result(ldap_result_id, 0)
            if (result_data == list()):
                break
            else:
                if result_type == ldap.RES_SEARCH_ENTRY:
                    user_details['emp_number'] = result_data[0][1]['employeeNumber']
                    user_details['emp_email_id'] = result_data[0][1]['mail']
                    user_details['emp_company'] = result_data[0][1]['company']
                    #user_details['emp_firstname'] = result_data[0][1]['givenName']
                    #user_details['emp_sername'] = result_data[0][1]['sn']
                    #user_details['emp_last_login']= result_data[0][1]['lastLogin']
                    #user_details['emp_access_level'] = result_data[0][1]['accessLevel']
    except:
            #raise Exception('Not able to find the data in LDAP database')
            pass
            user_details['emp_number'] = 'NA'
            user_details['emp_email_id'] = 'NA'
            user_details['emp_company'] = 'NA'
            return user_details        

    return user_details
'''
