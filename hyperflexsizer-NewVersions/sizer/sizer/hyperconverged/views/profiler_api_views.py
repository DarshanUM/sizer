import copy
import json
import random
import string
import time
#import shortuuid
import math

from hyperconverged.views.profiler_calc import process_esx_data
from hyperconverged.models import Results, Scenario, SharedScenario, ApiDetails

# from hyperconverged.serializer.WorkloadSerializer import WorkloadSerializer, WorkloadGetSerializer, \
#     ScenarioGetSerializer, WorkloadPostSerializer, WorkloadGetDetailSerializer, ScenarioCloneSerializer, \
#     ResultsSerializer, GenerateReportSerializer, GenerateBOMexcelSerializer, SharedScenarioSerializer, FixedResultsSerializer


from hyperconverged.exception import HXException, RXException
from hyperconverged.solver.attrib import HyperConstants
from base_sizer.solver.attrib import BaseConstants
from hyperconverged.views.home_page_views import HomePage
from hyperconverged.views.scenario_solve_views import ScenarioSolve

from utils.utility import *
from utils.baseview import BaseView
from rest_framework.views import APIView

from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status

import logging

logger = logging.getLogger(__name__)


class ProfilerSizing(APIView):

    def dispatch(self, request, *args, **kwargs):
        self.username = "profiler_user"
        return super().dispatch(request, *args, **kwargs)
   
    """
    This is just a testing the API
    """
    def get(self, request, format=None):
        
        try:
            logger.info("Profiler API, username is:: " + self.username)
        except Exception as error:
            logger.info("Profiler API, exception is::::"+ str(error))

        return Response(status=status.HTTP_200_OK)

    """
    This API will be used to create HX-Profile scenario and add workload
    """
    def post(self, request, format=None):

        if 'file' not in request.data:
            return Response("File is missing.",status=status.HTTP_404_NOT_FOUND)
        
        file_name = request.FILES['file'].name

        if file_name.endswith("csv") or file_name.endswith("CSV"):
    
            file_data = request.FILES['file'].read()

            file_data = str(file_data, 'utf-8')

            if file_data:

                # Process the file
                csv_result, error = process_esx_data(file_data)

                if error['Num_of_Errors'] > 0 or error['Error'] != '':
                    logger.error("Profiler API, data has Num_of_Errors::::" + error['Error'])
                    # return Response({'status': 'error',
                    #                  'Msg': list(error['Error'].split('\n')[:-1]),
                    #                  'data': json.loads(json.dumps(csv_result))})

                elif error['Num_of_Errors'] == 0 and error['Warnings'] != '':
                    warning_result = 'The following servers have insufficient historical data. \n' + error['Warnings']
                    logger.error("Profiler API, data has warnigs::::" + warning_result)
                    # return Response({'status': 'warning',
                    #                  'Msg': list(warning_result.split('\n')),
                    #                  'data': json.loads(json.dumps(csv_result))})

            else:
                return Response({'status': 'error',
                                 'errorMessage': 'Data is empty.'},
                                status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'status': 'error',
                             'errorMessage': 'File is not in csv format.'},
                            status=status.HTTP_400_BAD_REQUEST)
        
        
        
        scenarion_name = 'profiler_' + self.random_char() + '_' + self.generate_current_timestamp()

        # Step 1: create scenario and save in the DB
        create_setting_json = dict()
        create_scenario_data = dict()

        create_setting_json['account'] = ''
        create_setting_json['deal_id'] = ''

        create_scenario_data['name'] = scenarion_name
        create_scenario_data['username'] = self.username
        create_scenario_data['settings_json'] = create_setting_json
        create_scenario_data['sizing_type'] = 'hybrid'
        create_scenario_data['sizing_for'] = 'optimal'

        scenario_res , isCreated = HomePage.create_scenario(self.username, create_scenario_data)
        if not isCreated:
            return Response({'status': 'error',
                         'errorMessage': scenario_res},
                        status=status.HTTP_400_BAD_REQUEST)
        
        # Step 2: fetch the created id from response and ready the json string for sizing
        scenario_id = scenario_res['id']

        # Trying to fetch the sceanrio from DB
        try:
            scenario_detail = Scenario.objects.get(id= scenario_id)
            # save the data in APIdetails DB and get the token for reponse
            api_id = self.save_api_details(scenario_id)
        except Scenario.DoesNotExist:
            return Response({'status': 'error',
                         'errorMessage': 'Unable to find the scenario id: '+ scenario_id}, status=status.HTTP_404_NOT_FOUND)

        # Step 3: Prepare the json data for sizing.
        wl_template = self.process_csv_result(csv_result)
        profiler_json_data = self.generate_profiler_json(self.username, scenarion_name, wl_template)

        scenario_detail.workload_json = profiler_json_data
        scenario_detail.save()

        # Step 4: Send the data for sizing. while claiming data        
        return Response({'status': 'success', 'message': 'File is uploaded. Reference number is: '+ str(api_id)}, status=status.HTTP_201_CREATED)

    """
    workload json will be created
    """
    def generate_profiler_json(self, username, scenario_name, profie_wl):

        json_data = dict()
        settings_json = list()
        wl = Scenario()
        result_list = ['Lowest_Cost', 'All-Flash', 'All NVMe']
        
        optimal_setting = HomePage.get_default_settings(wl) 
        optimal_setting['free_disk_slots'] = 0
        fixed_setting = HomePage.get_fixed_default_settings(wl)
        fixed_setting['result_name'] = 'Fixed_Config'
        
        for result_name in result_list:
            copy_setting = copy.deepcopy(optimal_setting)
            copy_setting['result_name'] = result_name
            settings_json.append(copy_setting)
        settings_json.append([fixed_setting])

        json_data['username'] = username
        json_data['model_list'] = []
        json_data['name'] = scenario_name
        json_data['sizing_for'] = 'optimal'
        json_data['sizing_type'] = 'hybrid'
        json_data['model_choice'] = 'None'
        json_data['settings_json'] = settings_json
        json_data['overwrite'] = True
        # json_data['ddl_sizing_res_arr'] = ['All-Flash', 'Lowest_Cost', 'All NVMe', 'Fixed_Config']
        # Do sizing only for Lowest_Cost
        json_data['ddl_sizing_res_arr'] = ['Lowest_Cost']
        json_data['wl_list'] = [profie_wl]

        return json_data

    """
    Generate random string which will be used to create sceanrio name
    """
    def random_char(self, y = 5):
           return ''.join(random.choice(string.ascii_letters) for x in range(y))

    """
    Get the current timstamp which will be used to create scenario name
    """
    def generate_current_timestamp(self):
        # stores the time in seconds
        curent_timestamp = time.time()
        return str(curent_timestamp).replace('.','')

    """
    Save the data in ApiDetail Table
    """
    def save_api_details(self, scenario_id):
        api_detail = ApiDetails()
        api_detail.api_token = shortuuid.uuid()
        api_detail.scenario_id = scenario_id
        api_detail.save()
        # api_id = id to Django ORM behaviour during insert
        return api_detail.api_token

    """
    process the csv result. fetch the necessary information which will be used in workload json
    """
    def process_csv_result(self, csv_res):
        
        wl_template = self.get_profile_workload_json()

        sum_cpu_clock = 0
        sum_hdd_size = 0
        sum_ram_size = 0
        sum_vcpus = 0

        for server_key, server_value in csv_res.items():
            for cluster, cluster_data in server_value.items():
                host_details = cluster_data['host']['provisioned']
                sum_cpu_clock += host_details['cpu_clock']
                sum_hdd_size += host_details['hdd_size']
                sum_ram_size += host_details['ram_size']
                sum_vcpus += host_details['vcpus']

        wl_template['cpu_clock'] = round(sum_cpu_clock,1)

        if (sum_hdd_size > 1000):
            wl_template['hdd_size'] = round(sum_hdd_size/1000,1)
            wl_template['hdd_size_unit'] = 'TB'
        else:
            wl_template['hdd_size_unit'] = 'GB'
        if (sum_ram_size > 1024):
            wl_template['ram_size'] = round(sum_ram_size/1024,1)
            wl_template['ram_size_unit'] = 'TiB'
        else:
            wl_template['ram_size_unit'] = 'GiB'
        wl_template['vcpus'] = math.ceil(sum_vcpus)
        return wl_template

    """
    Get the default fileupload workload for profiler with default data
    """
    def get_profile_workload_json(self):
        profile_workload_template = { 
            'wl_type':'RAW_FILE',
            'wl_name':'RAW_FILE-1',
            'wl_cluster_name':'',
            'input_type':'HX Profiler CSV',
            'provisioned':True,
            'cpu_attribute':'vcpus',
            'isFileInput':True,
            'vcpus': 0,
            'cpu_clock': 0,
            'vcpus_per_core':1,
            'ram_size': 0,
            'ram_size_unit':'TiB',
            'ram_opratio':1,
            'hdd_size': 0,
            'hdd_size_unit':'TB',
            'overhead_percentage':10,
            'iops_value':0,
            'io_block_size':'VSI',
            'cpu_model':'Intel Platinum 8164',
            'working_set':10,
            'gpu_users':0,
            'iops':0,
            'ssd_size':0,
            'ssd_size_unit':'GB',
            'cluster_type':'normal',
            'replication_factor':3,
            'fault_tolerance':1,
            'compression_factor':0,
            'dedupe_factor':0,
            'compression_saved':100,
            'dedupe_saved':100,
            'isDirty':True
        }
        return profile_workload_template



class ClaimProfileData(BaseView):

    """
    This method is used to claim the profile data
    """
    def post(self, request):

        data = JSONParser().parse(request)
        try:
            api_detail = ApiDetails.objects.get(api_token = data['profile_token'])
        except ApiDetails.DoesNotExist:
            return Response({'status': 'error',
                         'errorMessage': 'Supplied token is either invalid or it is expired. Please enter a valid token.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            work_load = Scenario.objects.get(id=api_detail.scenario_id)
        except Scenario.DoesNotExist:
            return Response({'status': 'error',
                         'errorMessage': 'No scenario is not found against the token'}, status = status.HTTP_404_NOT_FOUND)

        if(api_detail.is_claimed):
            return Response({'status': 'error', 'errorMessage': 'Scenario is already claimed'}, status = status.HTTP_410_GONE)
        
        # Save username in the scenario
        work_load.username = self.username
        work_load.save()

        # Complete the sizing
        profiler_json_data = work_load.workload_json
        profiler_json_data['username'] = self.username
        scenario_solve_obj = ScenarioSolve()
        error_msg, isValidate = scenario_solve_obj.process_scenario_sizing(profiler_json_data, work_load)
        if isValidate:
            return error_msg 
        if error_msg:
            return Response({'status': 'error', 'errorMessage': error_msg}, status=status.HTTP_403_FORBIDDEN)

        # Set the claim as True
        api_detail.is_claimed = True
        api_detail.save()
        return Response({'status': 'success', 'message': 'Scenario is claimed successfully'}, status=status.HTTP_200_OK)