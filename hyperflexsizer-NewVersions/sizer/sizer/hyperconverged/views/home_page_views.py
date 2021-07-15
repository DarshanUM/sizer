from utils.baseview import BaseView

from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status

from hyperconverged.serializer.WorkloadSerializer import WorkloadSerializer
from hyperconverged.models import Scenario, Results, SharedScenario, User
from hyperconverged.views.utility_views import get_version_configs, get_scenario_list, get_shared_scenario_list, \
    search_scenarios
from hyperconverged.solver.reverse_sizing import WorkloadAdder
from hyperconverged.exception import RXException


class HomePage(BaseView):

    @staticmethod
    def get_default_settings(scenario_object):

        """filters and default settings for new scenarios of optimal type"""
        filters = dict()
        settings_json = dict()

        filters["Node_Type"] = list()
        filters["RAM_Slots"] = list()
        filters["RAM_Options"] = list()
        filters["CPU_Type"] = list()
        filters["Compute_Type"] = ["HX-B200", "HX-C220", "HX-C240", "HX-C480"]
        filters["Disk_Options"] = list()
        filters["Cache_Options"] = list()
        filters["GPU_Type"] = list()
        filters["Clock"] = list()
        versions = get_version_configs()
        settings_json["filters"] = filters
        settings_json['sizer_version'] = versions['sizer_version']
        settings_json['hx_version'] = versions['hx_version']
        settings_json['heterogenous'] = True
        settings_json['threshold'] = 1
        settings_json['bundle_only'] = 'ALL'
        settings_json['disk_option'] = "NON-SED"
        settings_json['cache_option'] = "ALL"
        settings_json['modular_lan'] = "ALL"
        settings_json['server_type'] = "M5"
        settings_json['includeSoftwareCost'] = True
        settings_json['dr_enabled'] = False
        settings_json['hypervisor'] = 'esxi'
        settings_json['hercules_conf'] = 'enabled'
        settings_json['hx_boost_conf'] = 'enabled'
        settings_json['license_yrs'] = 3
        settings_json['cpu_generation'] = "recommended"
        return settings_json

    @staticmethod
    def get_fixed_default_settings(scenario_object):

        """node and cluster properties settings for new scenarios of fixed type"""
        node_properties = dict()
        settings_json = dict()
        node_properties["nodeType"] = "cto"
        node_properties["node"] = "HXAF-220M5SX"
        node_properties["no_of_nodes"] = 3
        node_properties["compute_node"] = "HX-B200-M5-U"
        node_properties["no_of_computes"] = 0
        node_properties["cpu"] = ["3206R [Cascade]", 8, "1.9", 1024, 0.94050343249]
        node_properties["ram"] = ["16GiB [DDR4][Cascade][1]", 8, [16]]
        node_properties["disks_per_node"] = 6
        node_properties["disk_capacity"] = [960, "960GB [CAP][SSD][M5][1]"]
        node_properties["cache_size"] = ["375 [NVMe]", "375GB [SSD-NVMe-Optane][M5-AF][1]"]
        node_properties["workload_options"] = ["DB", "ORACLE", "AWR_FILE", "VDI", "VSI", "RAW", "RAW_FILE",
                                               "EXCHANGE", "VDI_INFRA", "SPLUNK", "RDSH", "CONTAINER"]
        node_properties["io_block_size"] = "VSI"

        cluster_properties = dict()
        cluster_properties['rf'] = 3
        cluster_properties['ft'] = 0
        cluster_properties['dedupe_factor'] = 10
        cluster_properties['compression_factor'] = 20

        versions = get_version_configs()

        settings_json["node_properties"] = node_properties
        settings_json["ram_label"] = "128 [8 x 16GiB]"
        settings_json["cpu_label"] = "3206R (8, 1.9)"
        
        settings_json["cluster_properties"] = cluster_properties

        settings_json['sizer_version'] = versions['sizer_version']
        settings_json['hx_version'] = versions['hx_version']
        settings_json['hypervisor'] = 'esxi'
        settings_json['threshold'] = 1
        settings_json['hercules_conf'] = 'disabled'
        settings_json['hx_boost_conf'] = 'disabled'

        # to support multicluster for fixed_config
        settings_json['cluster_name'] = 'cluster_default'
        settings_json['isDirty'] = False
        settings_json['workloads'] = [] #['VDI']
        return settings_json

    """
    this method is used to fetch all the scenario's to display in the Home page
    """
    def get(self, request):

        scen_tab = request.GET.get('scen_tab', "ACTIVE")
        if scen_tab not in ["ACTIVE", "FAVORITE", "ARCHIVE", "SHARED"]:
            scen_tab = "ACTIVE"

        scen_offset = (int(request.GET.get('scen_page_offset', 1)) - 1) * \
                      User.objects.get(username=self.username).scenario_per_page

        scen_limit = (int(request.GET.get('scen_page_limit', 5))) * \
                     User.objects.get(username=self.username).scenario_per_page
        scen_limit += scen_offset

        search_string = request.GET.get('search', None)
        if search_string:
            return search_scenarios(self.username, search_string, scen_tab, scen_offset, scen_limit)

        if scen_tab != "SHARED":
            return get_scenario_list(self.username, scen_tab, scen_offset, scen_limit)
        else:
            return get_shared_scenario_list(self.username, scen_offset, scen_limit)

    """
    this method is used to save the scenario for the first time.
    """
    def post(self, request):

        data = JSONParser().parse(request)

        resp, isSuccess = self.create_scenario(self.username, data)

        if isSuccess:
            return Response({'resp': resp}, status=status.HTTP_201_CREATED)
        else:
            return Response({'status': 'error',
                         'errorMessage': resp},
                        status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):

        data = JSONParser().parse(request)
        scen_id_list = data['scen_id_list']
        scen_set = Scenario.objects.filter(status=True, id__in=scen_id_list, username=self.username)

        for scen in scen_set:
            scen.scen_label = data['move_to']
            scen.save()

        return Response({'status': 'success'}, status=status.HTTP_200_OK)

    def delete(self, request):

        data = JSONParser().parse(request)
        scen_id_list = data['scen_id_list']

        for id in scen_id_list:
            try:
                work_load = Scenario.objects.get(id=id)
            except Scenario.DoesNotExist:
                continue

            if not work_load.username == self.username:
                return Response({'status': 'error', 'errorMessage': 'Unauthorized Access'},
                                status=status.HTTP_400_BAD_REQUEST)

            workload_results = Results.objects.filter(scenario_id=work_load.id)

            for result in workload_results:
                result.delete()

            work_load.delete()

            # Deleting entries from shared scenario table
            shared_result = SharedScenario.objects.filter(scenario_id=id)
            shared_result.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def create_scenario(username, data):

        if username == 'admin':
            workloads = Scenario.objects.filter(status=True, name=data['name'])
        else:
            workloads = Scenario.objects.filter(status=True, username= username, name=data['name'])

        if len(workloads) > 0:
            return 'Scenario name must be unique to the user.', False

        serializer = WorkloadSerializer(data=data)
        

        if serializer.is_valid():
            
            resp = dict()
            resp['resp'] = "Scenario Created "
            wl = Scenario()
            wl.initialize_scenario(serializer)
            # wl.settings_json = data['settings_json']
            wl.username = username
            wl.sizing_type = data['sizing_type']

            optimal_settings = HomePage.get_default_settings(wl) 
            fixed_settings= HomePage.get_fixed_default_settings(wl)

            # wl.settingss_json = [optimal_settings, fixed_settings]
            wl.save()

            result_list = ['Lowest_Cost', 'All-Flash', 'All NVMe','Fixed_Config']
            #with transaction.atomic():
            for result_name in result_list:
                result = Results()
                result.name = result_name
                result.result_json = list()

                if result_name == 'Fixed_Config':
                    fixed_settings['result_name'] = result_name
                    result.settings_json = [fixed_settings]
                else:
                    optimal_settings['result_name'] = result_name
                    result.settings_json = optimal_settings
                    result.settings_json['account'] = data['settings_json']['account']
                result.error_json = dict()
                result.scenario_id = wl.id
                result.save()
            
            resp['id'] = wl.id

            return resp, True
        else:
            return serializer.errors,False



class AutoArchive(BaseView):

    def patch(self, request):

        data = JSONParser().parse(request)
        input_date = data['input_date']

        scen_set = Scenario.objects.filter(status=True, username=self.username, updated_date__lte=input_date)

        for scen in scen_set:
            scen.scen_label = data['move_to']
            scen.save()

        return Response({'status': 'success'}, status=status.HTTP_200_OK)
