from copy import deepcopy
from utils.baseview import BaseView
from django.core.exceptions import ObjectDoesNotExist

from base_sizer.solver.attrib import BaseConstants
from hyperconverged.solver.attrib import HyperConstants
from hyperconverged.models import Scenario, SharedScenario, Results, SpecIntData, Part, FixedResults
from hyperconverged.views.utility_views import get_version_configs
from hyperconverged.views.scenario_solve_views import filter_node_and_part_data, validate_nodes_post_filter, ScenarioSolve
from hyperconverged.views.home_page_views import HomePage
from hyperconverged.solver.sizing import HyperConvergedSizer
from hyperconverged.solver.reverse_sizing import WorkloadAdder
from hyperconverged.exception import HXException, RXException
from hyperconverged.serializer.WorkloadSerializer import WorkloadGetDetailSerializer
from hyperconverged.utilities.get_serializer import get_wl_serializer_details

from rest_framework.response import Response
from rest_framework import status


class ReSizeScenario(BaseView):

    # TODO: Need to check if this method is required any more.?
    @staticmethod
    def convert_merge_json_object(input_json):

        indexs = [idx for idx, val in enumerate(input_json) if not isinstance(val, list) ]
        
        all_flash_dict = input_json[indexs[0]]
        lower_cost_dict = input_json[indexs[1]]
        all_nvme_dict = input_json[indexs[2]]
        for key, value in all_flash_dict.items():
            if key not in HyperConstants.base_list:
                continue
            if key == "filters":
                for filter_key, filter_value in all_flash_dict[key].items():

                    value = list(set(filter_value + lower_cost_dict[key][filter_key] + all_nvme_dict[key][filter_key]))
                    all_flash_dict[key][filter_key] = value
                    lower_cost_dict[key][filter_key] = value
                    all_nvme_dict[key][filter_key] = value
            else:
                if key == "heterogenous" or key == "includeSoftwareCost":
                    value = value | lower_cost_dict[key] | all_nvme_dict[key]
                elif key == "bundle_only":
                    # value = value & lower_cost_dict[key] & all_nvme_dict[key]
                    if value != lower_cost_dict[key]:
                        value = "ALL"
                elif key == "threshold":
                    value = max(value, lower_cost_dict[key])
                    value = max(value, all_nvme_dict[key])
                elif key == "modular_lan" or key == "disk_option":
                    if value != lower_cost_dict[key] or value != all_nvme_dict[key]:
                        value = "ALL"
                all_flash_dict[key] = value
                lower_cost_dict[key] = value
                all_nvme_dict[key] = value

    """
    As per New UI - reverse sizing for Fixed_config is not required
    """
    def handle_fixed_resize(self, scenario_object):

        # modification of settings_json
        versions = get_version_configs()
        settings = scenario_object.settings_json
        settings['hypervisor'] = settings.get('hypervisor', 'esxi')

        if '[Hercules]' in settings['node_properties']['node']:
            settings['hercules_conf'] = HyperConstants.FORCED
            settings['node_properties']['node'] = settings['node_properties']['node'].replace('[Hercules]', '').strip()
        else:
            settings['hercules_conf'] = HyperConstants.DISABLED

        settings['hx_boost_conf'] = settings.get('hx_boost_conf', HyperConstants.DISABLED)

        if 'cluster_properties' not in settings:
            settings['cluster_properties'] = dict()
            settings['cluster_properties']['rf'] = 3
            settings['cluster_properties']['ft'] = 0
            settings['cluster_properties']['dedupe_factor'] = 10
            settings['cluster_properties']['compression_factor'] = 20

        if '[Cascade]' in settings['node_properties']['node']:
            cpu_ram_part = '[Cascade]'
        else:
            cpu_ram_part = '[Sky]'

        if settings['node_properties']['cpu'] and type(settings['node_properties']['cpu']) is not list:
            if ' (' not in settings['node_properties']['cpu']:
                cpu_name = "%s %s" %(settings['node_properties']['cpu'], cpu_ram_part)
            else:
                cpu_name = "%s %s" %(settings['node_properties']['cpu'].split(' ')[0], cpu_ram_part)

            try:
                cpu_obj = Part.objects.get(name=cpu_name)
            except ObjectDoesNotExist:
                cpu_obj = Part.objects.get(name='8164 [Sky]')

            settings['node_properties']['cpu'] = [cpu_obj.name,
                                                  cpu_obj.part_json[BaseConstants.CAPACITY],
                                                  cpu_obj.part_json[HyperConstants.FREQUENCY],
                                                  cpu_obj.part_json[HyperConstants.RAM_LIMIT],
                                                  cpu_obj.part_json[HyperConstants.SPECLNT]
                                                  ]

        if type(settings['node_properties']['ram']) is not list:

            string = settings['node_properties']['ram']
            firstDelPos = string.find("[")  # get the position of delimiter [
            secondDelPos = string.find("]")  # get the position of delimiter ]
            ramString = string[firstDelPos + 1:secondDelPos]  # get the string between two dels

            ram_slot = ramString.split('x')[0]
            ram_size = ramString.split('x')[1]

            ram_name = "%sGiB [DDR4]%s[1]" %(ram_size, cpu_ram_part)
            settings['node_properties']['ram'] = [ram_name,
                                                  int(ram_slot),
                                                  [int(ram_size)]
                                                  ]

        #handle skylake deprecated CPU and RAM part 
        if 'sky' in (settings['node_properties']['cpu'][0]).lower() or 'sky' in (settings['node_properties']['ram'][0]).lower():
            return 'Resizing failed. One of the cluster in Fixed_Result contain Skylake CPU which are deprecated. Version is updated to the latest.'

        # Changing the node name here to avoid validate_node error for 9.4 fixed resize
        if '[M&L Processor]' in settings['node_properties']['node'] or \
                '[General]' in settings['node_properties']['node'] or \
                '[128 GB]' in settings['node_properties']['node']:

            node_name = settings['node_properties']['node']
            node_name = node_name.replace('[M&L Processor]','').replace('[General]','').replace('[128 GB]','').replace('[Cascade]','')

            settings['node_properties']['node'] = deepcopy(node_name)

        #to support new UI and fixed and optimal merge
        if not ('cluster_name' in settings):
            settings['cluster_name'] = 'cluster_1'
        if not('workloads' in settings):
            settings['workloads'] = []

        cluster_name = settings['cluster_name']
        wl_names = []
        try:
            wl_names = [wl['wl_name'] for wl in scenario_object.workload_json['wl_list']]
        except:
            pass
        settings['workloads'] = wl_names

        settings['result_name'] = 'Fixed_Config'
        settings['sizer_version'] = versions['sizer_version']
        settings['hx_version'] = versions['hx_version']

        
        # since workload json also has settings, it is copied from outside after modifications
        scenario_object.workload_json['settings_json'] = settings
        scenario_object.settings_json = settings

        error = None
        response = list()

        wls_list = scenario_object.workload_json['wl_list'] \
            if 'wl_list' in scenario_object.workload_json else list()

        if wls_list:
            try:
                workload_adder = WorkloadAdder(settings_json=deepcopy([settings]),
                                               workload_list=scenario_object.workload_json['wl_list'])
                response = workload_adder.get_util()
                cluster_utilizations = response[0]['clusters'][0][0]['Utilization']
                cluster_wl_type = response[0]['clusters'][0][0]['wl_list'][0][HyperConstants.INTERNAL_TYPE]
                workload_adder.validate_utilizations(cluster_utilizations, cluster_wl_type)

            except RXException as fixederror:
                error = str(fixederror)

        # Sizing calculator result irrespective of Sizing failure
        try:
            sizingcalc_response = WorkloadAdder.get_sizing_calculator_result(settings)
            if response:
                response[0]['sizing_calculator'] = sizingcalc_response
                response[0]['cluster_name'] = cluster_name
            else:
                sizingcalc_result = dict()
                sizingcalc_result['cluster_name'] = cluster_name
                sizingcalc_result['result_name'] = settings['result_name']
                sizingcalc_result['sizing_calculator'] = sizingcalc_response
                # versions = get_version_configs()
                sizingcalc_result['sizer_version'] = versions['sizer_version']
                sizingcalc_result['hx_version'] = versions['hx_version']
                response.append(sizingcalc_result)
        except RXException as calcerror:
            calcerror = str(calcerror)

        scenario_object.status = True
        scenario_object.workload_result = response
        # versions = get_version_configs()
        scenario_object.settings_json['sizer_version'] = versions['sizer_version']
        scenario_object.settings_json['hx_version'] = versions['hx_version']
        scenario_object.save()

        if not error:
            error = list()
        self.save_result('Fixed_Config', response, [settings], scenario_object.id, error)
        self.save_fixed_result(cluster_name, response , scenario_object.id, settings, error)


    def post(self, request, id):

        try:
            scenario = Scenario.objects.get(id=id)
        except Scenario.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        sScenario = SharedScenario.objects.filter(scenario_id=id, userid=self.username)
        if not scenario.username == self.username and len(sScenario) == 0:
            return Response({'status': 'error', 'errorMessage': 'Unauthorized Access'},
                            status=status.HTTP_400_BAD_REQUEST)

        wl_list = list()

        if 'wl_list' in scenario.workload_json:
            wl_list = scenario.workload_json['wl_list']
            get_wl_serializer_details(wl_list)

        versions = get_version_configs()
        results = Results.objects.filter(scenario_id=id)
        # TODO: Not sure why it has to go default as Fixed_config, if wl_list is empty.
        # As per v10.0 - this if condition must change
        if not wl_list:
            if scenario.sizing_type == "optimal":
                return Response({'status': 'error', "errorMessage": "Resizing for optimal scenario without workload is not supported from v10.0.0 onwards"},status=status.HTTP_404_NOT_FOUND )
            if scenario.sizing_type == "fixed":
                fixed_error_msg = self.handle_fixed_resize(scenario)
                if fixed_error_msg:
                    return Response({'status': 'error', 'errorCode': 4, 'errorMessage': fixed_error_msg}, status=status.HTTP_403_FORBIDDEN) 
                result_list = ['Lowest_Cost', 'All-Flash', 'All NVMe']
                optimal_settings = HomePage.get_default_settings(scenario)
                for result_name in result_list:
                    result = Results()
                    result.name = result_name
                    result.result_json = list()
                    optimal_settings['result_name'] = result_name
                    result.settings_json = optimal_settings
                    result.error_json = dict()
                    result.scenario_id = scenario.id
                    result.save()
            else:

                for scen_res in results:
                    if scen_res.name == "Fixed_Config":
                        for fix_setting in scen_res.settings_json:
                            fix_setting['sizer_version'] = versions['sizer_version']
                            fix_setting['hx_version'] = versions['hx_version']
                        # Version will get updated here
                        # fixed_settings_json= HomePage.get_fixed_default_settings(scenario)
                        # fixed_settings_json['result_name'] = 'Fixed_Config'
                        # scen_res.settings_json = [fixed_settings_json]
                        # fixed_wl_res = self.generate_fixed_wl_result(scen_res.settings_json)
                        # scen_res.result_json = fixed_wl_res
                    else:
                        scen_res.settings_json['sizer_version'] = versions['sizer_version']
                        scen_res.settings_json['hx_version'] = versions['hx_version']
                    scen_res.save()

            scenario.workload_json = dict()
            # scenario.workload_json['sizing_type'] = 'fixed'
            scenario.sizing_type = "hybrid"
            scenario.save()
            # self.handle_fixed_resize(scenario)
            return Response(list(), status=status.HTTP_200_OK)

        for wl in wl_list:

            
            if not (HyperConstants.WL_CLUSTER_NAME in wl):
                wl[HyperConstants.WL_CLUSTER_NAME] = ""
            
            if not (HyperConstants.IS_DIRTY in wl):
                wl[HyperConstants.IS_DIRTY] = False

            if 'storage_protocol' not in wl:
                wl['storage_protocol'] = 'NFS'

            wl[HyperConstants.CLUSTER_TYPE] = wl.get(HyperConstants.CLUSTER_TYPE, HyperConstants.NORMAL)

            if wl[BaseConstants.WL_TYPE] in [HyperConstants.VDI, HyperConstants.VSI, HyperConstants.ORACLE,
                                             HyperConstants.DB, HyperConstants.RAW, HyperConstants.EXCHANGE,
                                             HyperConstants.ROBO, HyperConstants.RDSH, HyperConstants.EPIC,
                                             HyperConstants.CONTAINER, HyperConstants.AIML]:

                if wl[BaseConstants.WL_TYPE] in [HyperConstants.VSI, HyperConstants.ORACLE, HyperConstants.DB]:

                    remote_flag = wl.get("remote_replication_enabled", False)

                    if not remote_flag:
                        wl["replication_amt"] = 0
                        wl["remote_replication_enabled"] = remote_flag

                elif wl[BaseConstants.WL_TYPE] in [HyperConstants.RAW, HyperConstants.EXCHANGE]:

                    if wl[BaseConstants.WL_TYPE] == HyperConstants.RAW and 'isFileInput' in wl and wl['isFileInput']:
                        wl[BaseConstants.WL_TYPE] = HyperConstants.RAW_FILE

                    if HyperConstants.VCPUS not in wl:

                        wl[HyperConstants.VCPUS] = wl[HyperConstants.CPU_CORES]

                        del wl[HyperConstants.CPU_CORES]

                        wl[HyperConstants.VCPUS_PER_CORE] = 1

                elif wl[BaseConstants.WL_TYPE] in [HyperConstants.VDI]:

                    if HyperConstants.USER_DATA_IOPS not in wl:

                        wl[HyperConstants.USER_DATA_IOPS] = 0

                    if HyperConstants.VDI_DIRECTORY not in wl:

                        wl[HyperConstants.VDI_DIRECTORY] = 0

                elif wl[BaseConstants.WL_TYPE] in [HyperConstants.EPIC]:
                    if wl['cpu'] == 'Intel Gold 6150':
                        wl['cpu'] = 'Intel Gold 6254'
                    elif wl['cpu'] == 'Intel Platinum 8168':
                        wl['cpu'] = 'Intel Platinum 8268'

                if wl.get(HyperConstants.VIDEO_RAM, None) == '512':

                     wl[HyperConstants.VIDEO_RAM] = '1024'

                unit_dict = {HyperConstants.VDI: {HyperConstants.HDD_PER_DT_UNIT: "GB",
                                                  HyperConstants.GOLD_IMG_SIZE_UNIT: "GB",
                                                  HyperConstants.RAM_PER_DT_UNIT: "GiB"},
                             HyperConstants.VSI: {HyperConstants.HDD_PER_VM_UNIT: "GB",
                                                  HyperConstants.VM_BASE_IMG_SIZE_UNIT: "GB",
                                                  HyperConstants.RAM_PER_VM_UNIT: "GiB"},
                             HyperConstants.RAW: {BaseConstants.HDD_SIZE_UNIT: "GB",
                                                  HyperConstants.SSD_SIZE_UNIT: "GB",
                                                  BaseConstants.RAM_SIZE_UNIT: "GiB",
                                                  HyperConstants.CPU_CLOCK: 35,
                                                  HyperConstants.CPU_ATTRIBUTE: HyperConstants.VCPUS},
                             HyperConstants.RAW_FILE: {BaseConstants.HDD_SIZE_UNIT: "GB",
                                                  HyperConstants.SSD_SIZE_UNIT: "GB",
                                                  BaseConstants.RAM_SIZE_UNIT: "GiB",
                                                  HyperConstants.CPU_CLOCK: 35,
                                                  HyperConstants.CPU_ATTRIBUTE: HyperConstants.VCPUS},
                             HyperConstants.EXCHANGE: {HyperConstants.CPU_CLOCK: 35,
                                                       HyperConstants.CPU_ATTRIBUTE: HyperConstants.VCPUS,
                                                       BaseConstants.RAM_SIZE_UNIT: "GiB"},
                             HyperConstants.ORACLE: {HyperConstants.DB_SIZE_UNIT: "GB",
                                                     HyperConstants.RAM_PER_DB_UNIT: "GiB"},
                             HyperConstants.DB: {HyperConstants.DB_SIZE_UNIT: "GB",
                                                 HyperConstants.RAM_PER_DB_UNIT: "GiB"},
                             HyperConstants.ROBO: {HyperConstants.HDD_PER_VM_UNIT: "GB",
                                                   HyperConstants.VM_BASE_IMG_SIZE_UNIT: "GB",
                                                   HyperConstants.MOD_LAN: 'ANY',
                                                   HyperConstants.RAM_PER_VM_UNIT: "GiB"},
                             HyperConstants.RDSH: {HyperConstants.RAM_PER_VM_UNIT: "GiB"},
                             HyperConstants.EPIC: {HyperConstants.RAM_PER_GUEST_UNIT: "GiB"},
                             HyperConstants.CONTAINER: {HyperConstants.RAM_PER_CONTAINER_UNIT: "GiB"},
                             HyperConstants.AIML: {HyperConstants.RAM_PER_DS_UNIT: "GiB"},
                             }

                for key, value in unit_dict[wl[BaseConstants.WL_TYPE]].items():
                    if key not in wl:
                        wl[key] = value
                    if key == HyperConstants.CPU_ATTRIBUTE and wl[key] == 'cpu_cores':
                        wl[key] = HyperConstants.VCPUS

        if scenario.sizing_type == 'fixed':
            fixed_error_msg = self.handle_fixed_resize(scenario)
            if fixed_error_msg:
                return Response({'status': 'error', 'errorCode': 4, 'errorMessage': fixed_error_msg}, status=status.HTTP_403_FORBIDDEN) 

            #add optimal default result
            result_list = ['Lowest_Cost', 'All-Flash', 'All NVMe']
            optimal_settings = HomePage.get_default_settings(scenario)
            for result_name in result_list:
                result = Results()
                result.name = result_name
                result.result_json = list()
                optimal_settings['result_name'] = result_name
                result.settings_json = optimal_settings
                result.error_json = dict()
                result.scenario_id = scenario.id
                result.save()

        # results = Results.objects.filter(scenario_id=id)

        settings_json_array = list()

        account_name = ''

        deal_id = ''

        # iterate each result in a particular scenario and append all the settings_json under settings_json_array
        for result in results:

            if result.name == 'Lowest_Cost':

                if 'account' in result.settings_json.keys():
                    account_name = result.settings_json['account']
                else:
                    result.settings_json['account'] = account_name

                if 'deal_id' in result.settings_json.keys():
                    deal_id = result.settings_json['deal_id']
                else:
                    result.settings_json['deal_id'] = deal_id

                if 'filters' not in result.settings_json:
                    result.settings_json['filters'] = dict()
                    result.settings_json['filters']['Node_Type'] = list()
                    result.settings_json['filters']['RAM_Slots'] = list()
                    result.settings_json['filters']['RAM_Options'] = list()
                    result.settings_json['filters']['CPU_Type'] = list()
                    result.settings_json['filters']['Compute_Type'] = list()

                if 'threshold' not in result.settings_json:
                    result.settings_json['threshold'] = 1

                if 'heterogenous' not in result.settings_json:
                    result.settings_json['heterogenous'] = True

                if 'result_name' not in result.settings_json:
                    result.result_name = 'Lowest_Cost'

                if result.settings_json['bundle_only'] not in [HyperConstants.BUNDLE_ONLY, HyperConstants.CTO_ONLY,
                                                               HyperConstants.BUNDLE_AND_CTO]:
                    result.settings_json['bundle_only'] = HyperConstants.BUNDLE_AND_CTO

            if 'filters' in result.settings_json:
                if "Riser_options" in result.settings_json['filters']:
                    result.settings_json['filters']["Riser_options"] = 'Storage'

                result.save()

            settings_json_array.append(result.settings_json)

        if len(settings_json_array) < 2:

            all_flash_settings_json = dict()
            result = Results()
            result.name = 'All-Flash'
            result.result_json = list()

            filters = dict()
            filters["Node_Type"] = ['HXAF-SP-220', 'HXAF-SP-240']
            filters["RAM_Slots"] = list()
            filters["RAM_Options"] = list()
            filters["CPU_Type"] = list()
            filters["Compute_Type"] = list()
            filters["Riser_options"] = 'Storage'
            all_flash_settings_json['account'] = account_name
            all_flash_settings_json['deal_id'] = deal_id
            all_flash_settings_json["filters"] = filters
            all_flash_settings_json["result_name"] = 'All-Flash'
            all_flash_settings_json["threshold"] = 1
            all_flash_settings_json["heterogenous"] = True

            result.settings_json = all_flash_settings_json
            result.scenario_id = id
            result.save()

            settings_json_array.append(all_flash_settings_json)

        if len(settings_json_array) < 3:

            all_nvme_settings_json = dict()
            result = Results()
            result.name = 'All NVMe'
            result.result_json = list()

            filters = dict()
            #filters["Node_Type"] = ['HXAF-220 [NVME]', 'HXAF-220 [NVME 8TB]']
            filters["Node_Type"] = list()
            filters["Compute_Type"] = list()
            filters["CPU_Type"] = list()
            filters["Clock"] = list()
            filters["RAM_Slots"] = list()
            filters["RAM_Options"] = list()
            filters["Disk_Options"] = list()
            filters["Cache_Options"] = list()
            filters["GPU_Type"] = list()
            filters["Riser_options"] = 'Storage'
            all_nvme_settings_json['account'] = account_name
            all_nvme_settings_json['deal_id'] = deal_id
            all_nvme_settings_json["filters"] = filters
            all_nvme_settings_json["result_name"] = 'All NVMe'
            all_nvme_settings_json["threshold"] = 1
            all_nvme_settings_json["heterogenous"] = True
            all_nvme_settings_json["bundle_only"] = "ALL"
            all_nvme_settings_json["includeSoftwareCost"] = True
            all_nvme_settings_json["disk_option"] = "ALL"
            all_nvme_settings_json["cache_option"] = "ALL"
            all_nvme_settings_json["modular_lan"] = "ALL"
            all_nvme_settings_json["cpu_generation"] = "recommended"

            result.settings_json = all_nvme_settings_json
            result.scenario_id = id
            result.save()

            settings_json_array.append(all_nvme_settings_json)
        
        # Add 4th result as Fixed_config - fixed config merge in a single page.
        if len(results) < 4:
            result = Results()
            result.name = 'Fixed_Config'
            result.result_json = list()
            # version will get updated here
            fixed_settings_json= HomePage.get_fixed_default_settings(scenario)
            fixed_settings_json['result_name'] = 'Fixed_Config'
            result.settings_json = [fixed_settings_json]
            result.scenario_id = id
            result.save()

            settings_json_array.append([fixed_settings_json])



        self.convert_merge_json_object(settings_json_array)

        for settings_json in settings_json_array:

            # fixed_merge
            if isinstance(settings_json, list):
                #yet to add code
                # if(scenario.sizing_type == "optimal"):
                #     # fixed_wl_result = list()
                #     # response = dict()
                #     # fixed_settings = settings_json[0]
                #     fixed_wl_result = self.generate_fixed_wl_result(settings_json)
                #     # response['sizing_calculator'] = WorkloadAdder.get_sizing_calculator_result(fixed_settings)
                #     # response['sizer_version'] = fixed_settings['sizer_version']
                #     # response['hx_version'] = fixed_settings['hx_version']
                #     # response['result_name'] = fixed_settings['result_name']
                #     # response['cluster_name'] = fixed_settings['cluster_name']
                #     # fixed_wl_result.append(response)
                #     ScenarioSolve.save_result('Fixed_Config', fixed_wl_result, settings_json, id, error=None)
                if (scenario.sizing_type == "hybrid"):
                    # When sizing type is hybrid. mutliple settings will be there 
                    fixed_error_msg = self.handle_hybrid_fixed_resize(settings_json, versions, wl_list, scenario)
                    if fixed_error_msg:
                        return Response({'status': 'error', 'errorCode': 4, 'errorMessage': fixed_error_msg}, status=status.HTTP_403_FORBIDDEN) 
                continue

            settings_json['bundle_only'] = settings_json.get('bundle_only', "ALL")
            bundle_only = settings_json['bundle_only']

            # Always setting the filters to HX nodes to drag attention to new defaults
            settings_json['filters']['Compute_Type'] = ["HX-B200", "HX-C220", "HX-C240", "HX-C480"]
            if bundle_only == HyperConstants.BUNDLE_ONLY:
                settings_json['filters']['Compute_Type'] = []

            if 'Clock' not in settings_json['filters']:
                settings_json['filters']['Clock'] = list()

            if 'CPU_Type' not in settings_json['filters']:
                settings_json['filters']['CPU_Type'] = list()

            elif settings_json['filters']['CPU_Type']:

                if ' (' not in settings_json['filters']['CPU_Type'][0]:

                    new_cpu_rep = list()

                    for cpu_str in settings_json['filters']['CPU_Type']:

                        cpu_objs = Part.objects.filter(name=cpu_str)
                        for cpu_obj in cpu_objs:
                            new_cpu_str = '%s (%s, %s)' % (cpu_str,
                                                           cpu_obj.part_json['capacity'],
                                                           cpu_obj.part_json['frequency'])

                            new_cpu_rep.append(new_cpu_str)

                    settings_json['filters']['CPU_Type'] = new_cpu_rep

            if 'Disk_Options' not in settings_json['filters'] or 'Cache_Options' not in settings_json['filters']:
                settings_json['filters']['Disk_Options'] = list()
                settings_json['filters']['Cache_Options'] = list()

            if 'GPU_Type' not in settings_json['filters']:
                settings_json['filters']['GPU_Type'] = list()

            filters = settings_json['filters']
            result_name = settings_json['result_name']

            if "disk_option" not in settings_json or (settings_json["disk_option"] in ['NVME', 'COLDSTREAM']):
                settings_json['disk_option'] = "ALL"
            disk_option = settings_json["disk_option"]

            settings_json['cache_option'] = settings_json.get("cache_option", "ALL")
            cache_option = settings_json["cache_option"]

            settings_json[HyperConstants.SINGLE_CLUSTER] = settings_json.get(HyperConstants.SINGLE_CLUSTER, False)

            settings_json['modular_lan'] = "ALL"

            if HyperConstants.LICENSE_YEARS not in settings_json:
                settings_json[HyperConstants.LICENSE_YEARS] = 1 if settings_json.get("includeSoftwareCost", True) else 0

            settings_json['bundle_discount_percentage'] = settings_json.get("bundle_discount_percentage", 0)
            settings_json['cto_discount_percentage'] = settings_json.get("cto_discount_percentage", 0)

            settings_json["server_type"] = "M5"
            server_type = settings_json["server_type"]

            settings_json["hypervisor"] = settings_json.get('hypervisor', 'esxi')
            hypervisor = settings_json["hypervisor"]

            settings_json['hercules_conf'] = settings_json.get('hercules_conf', 'enabled')
            hercules = settings_json['hercules_conf']

            settings_json['hx_boost_conf'] = settings_json.get('hx_boost_conf', 'enabled')
            hx_boost = settings_json['hx_boost_conf']

            if 'cpu_generation' not in settings_json:
                if bundle_only == HyperConstants.BUNDLE_ONLY:
                    settings_json['cpu_generation'] = 'ALL'
                else:
                    settings_json['cpu_generation'] = 'recommended'

            # cpu_ram_gen = settings_json['cpu_generation']

            if not settings_json.get("dr_enabled", False):
                settings_json["dr_enabled"] = False

            settings_json['free_disk_slots'] = settings_json.get('free_disk_slots', 0)
            free_disk_slots = settings_json['free_disk_slots']

            # Remove deprecate Skylake CPU and RAM from filters
            settings_json['filters']['CPU_Type'] = list(filter(lambda cpu_type: cpu_type[1] == 2 , settings_json['filters']['CPU_Type']))
            settings_json['cpu_generation'] = 'recommended' if 'sky' in settings_json['cpu_generation'] else settings_json['cpu_generation']
            cpu_ram_gen = settings_json['cpu_generation']

            settings_json['sizer_version'] = versions['sizer_version']
            nodes, parts, parts_qry = filter_node_and_part_data(filters, result_name, disk_option, cache_option,
                                                                server_type, hypervisor, hercules, cpu_ram_gen,
                                                                hx_boost, free_disk_slots)

            error = validate_nodes_post_filter(nodes, parts_qry, settings_json, wl_list)

            resp = list()
            try:
                if not error:
                    solver = HyperConvergedSizer(parts, nodes, wl_list, settings_json, id)
                    resp = solver.solve(bundle_only)
            except HXException as e:
                error = str(e)

            result_name = settings_json["result_name"]

            self.save_result(result_name, resp, settings_json, id, error)

        wl = scenario
        wl.status = True
        wl.workload_json['settings_json'] = settings_json_array
        wl.workload_json['sizing_type'] = scenario.sizing_type
        wl.sizing_type = "hybrid"
        wl.save()

        return Response(list(), status=status.HTTP_200_OK)
    
    '''
    This code is required to resize the hybrid type Fixed Config from V-10.0.0
    '''
    def handle_hybrid_fixed_resize(self, settings_json, versions, wl_list, scenario_object):
        
        error_msg = None
        for fix_settings in settings_json:
            fix_settings['sizer_version'] = versions['sizer_version']
            fix_settings['hx_version'] = versions['hx_version']

            setting_name = fix_settings['cluster_name']
            # wl_isDirty = False
            
            if fix_settings['hercules_conf'] == 'enabled':
                fix_settings['hercules_conf'] = 'disabled'

            if fix_settings['hx_boost_conf'] == 'enabled':
                fix_settings['hx_boost_conf'] = 'disabled'

            if not ("io_block_size" in fix_settings['node_properties']):
                fix_settings['node_properties']['io_block_size'] = 'VSI'

            # Handle skylake deprecated CPU and RAM part
            if fix_settings['cluster_name'] != 'cluster_default':
                if 'sky' in (fix_settings['node_properties']['cpu'][0]).lower() or \
                        'sky' in (fix_settings['node_properties']['ram'][0]).lower():
                    return 'Resizing failed. One of the cluster in Fixed Result contain Skylake CPU which are deprecated. Version is updated to the latest.'

            size_wl_list = list()
            req_len = len(wl_list)
            input_from_ui = fix_settings['workloads']
            
            for n in range(0,req_len):
                if(wl_list[n]['wl_name']  in  input_from_ui):
                    size_wl_list.append(wl_list[n])
                

            response = list()
            try:
                if len(size_wl_list) > 0:
                    workload_adder = WorkloadAdder(settings_json= [fix_settings],
                                                workload_list=size_wl_list)
                    response = workload_adder.get_util()
                    cluster_utilizations = response[0]['clusters'][0][0]['Utilization']
                    cluster_wl_type = response[0]['clusters'][0][0]['wl_list'][0][HyperConstants.INTERNAL_TYPE]
                    workload_adder.validate_utilizations(cluster_utilizations, cluster_wl_type)

            except RXException as error:
                error_msg = str(error)

            # Sizing calculator result irrespective of Sizing failure
            try:
                sizingcalc_response = WorkloadAdder.get_sizing_calculator_result(fix_settings)
                if response:
                    response[0]['sizing_calculator'] = sizingcalc_response
                    response[0]['cluster_name'] = setting_name
                else:
                    sizingcalc_result = dict()
                    sizingcalc_result['cluster_name'] = setting_name
                    sizingcalc_result['result_name'] = fix_settings['result_name']
                    sizingcalc_result['sizing_calculator'] = sizingcalc_response
                    response.append(sizingcalc_result)

            except RXException as calcerror:
                calcerror = str(calcerror)

            self.save_fixed_result(setting_name, response , scenario_object.id, fix_settings, error_msg)

        self.save_result('Fixed_Config', response, settings_json , scenario_object.id, error_msg)


    @staticmethod
    def save_result(result_name, result, settings, id, error):
        results = Results.objects.filter(scenario_id=id, name=result_name)

        if len(results) == 0:
            new_result = Results()
            new_result.scenario_id = id
            new_result.result_json = result
            new_result.settings_json = settings
            new_result.error_json = {'message': error, 'result_name': result_name}
            new_result.name = result_name
            new_result.save()
        else:
            saved_result = results[0]
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
    
    @staticmethod
    def generate_fixed_wl_result(settings_json):
        fixed_wl_result = list()
        response = dict()
        fixed_settings = settings_json[0]
        response['sizing_calculator'] = WorkloadAdder.get_sizing_calculator_result(fixed_settings)
        response['sizer_version'] = fixed_settings['sizer_version']
        response['hx_version'] = fixed_settings['hx_version']
        response['result_name'] = fixed_settings['result_name']
        response['cluster_name'] = fixed_settings['cluster_name']
        fixed_wl_result.append(response)
        return fixed_wl_result
        
