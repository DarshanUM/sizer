import copy
import json

from packaging.version import Version

import hyperconverged.views.generatebom as bomreport

from hyperconverged.models import Scenario, SharedScenario, Results, FixedResults
from hyperconverged.serializer.WorkloadSerializer import GenerateReportSerializer, WorkloadGetDetailSerializer

class BomExcelReport(object):
    ''' this class is used by Bom upload and Download Class '''
    # def __init__(self):
    #     pass

    def generate_bom_file(self, id, bom_input, username):
        try:
            work_load = Scenario.objects.get(id=id)
        except Scenario.DoesNotExist:
            return "NOT_FOUND", ""
            # return Response(status=status.HTTP_404_NOT_FOUND)

        sScenario = SharedScenario.objects.filter(scenario_id=id, userid=username)
        if not work_load.username == username and len(sScenario) == 0:
            return "BAD_REQUEST", "Unauthorized Access"
            # return Response({'status': 'error', 'errorMessage': 'Unauthorized Access'},
            #                 status=status.HTTP_400_BAD_REQUEST)

        serializer = WorkloadGetDetailSerializer(work_load)

        results = Results.objects.filter(scenario_id=work_load.id).order_by('name')

        fixed_results = FixedResults.objects.filter(scenario_id=work_load.id)

        ReturnData = dict()
        ReturnData['id'] = serializer.data['id']
        ReturnData['name'] = serializer.data['name']
        ReturnData['workload_json'] = serializer.data['workload_json']

        if results:
            result_data = list()
            settings_data = list()
            error_data = list()

            # fixed_result_data = dict()
            fixed_result_data = list()
            fixed_error_data = list()

            for result in results:
                if isinstance(result.settings_json, list):
                    fixed_results = FixedResults.objects.filter(scenario_id=work_load.id)
                    if len(fixed_results):
                        for fixed_res in fixed_results:
                            fixed_result_data.extend(fixed_res.result_json)
                            # fixed_result_data[fixed_res.cluster_name] = fixed_res.result_json
                            if 'message' in fixed_res.error_json and fixed_res.error_json['message']:
                                fixed_error_data.append(fixed_res.error_json)
                    else:
                        fixed_result_data.extend(result.result_json)
                        # fixed_result_data['No_cluster'] = result.result_json
                        if 'message' in result.error_json and result.error_json['message']:
                            fixed_error_data.append(result.error_json)
                    ReturnData['fixed_setting_json'] = result.settings_json
                else:
                    result_data.extend(result.result_json)
                    settings_data.append(result.settings_json)
                    if 'message' in result.error_json and result.error_json['message']:
                        error_data.append(result.error_json)

            ReturnData['workload_result'] = result_data
            ReturnData['settings_json'] = settings_data
            ReturnData['errors'] = error_data

            ReturnData['fixed_workload_result'] = fixed_result_data
            ReturnData['fixed_error_data'] = fixed_error_data

        else:
            ReturnData['workload_result'] = serializer.data['workload_result']
            ReturnData['settings_json'] = [serializer.data['settings_json']]
            ReturnData['fixed_workload_result'] = dict()
            ReturnData['fixed_error_data'] = list()

        scenario_data = ReturnData
        sizing_results = len(scenario_data['workload_result'])

        all_errors = copy.deepcopy(scenario_data['errors'])
        all_errors.extend(scenario_data['fixed_error_data'])

        err_result_name = [error['result_name'] for error in all_errors  if 'result_name' in error]

        # Check for Optimal Sizing
        if not sizing_results and bom_input['nodetype'] != 'Fixed_Config':
            if 'selectedEstimate' in bom_input:
                return "BAD_REQUEST", "Scenario must have Workload/Sizing result to Upload BOM."
            else:
                return "BAD_REQUEST", "Scenario must have Workload/Sizing result to download BOM excel."
            # return Response({'status': 'error',
            #                  'errorMessage': 'Scenario must have Workload/Sizing result to download BOM excel.'},
            #                 status=status.HTTP_400_BAD_REQUEST)

        if bom_input['nodetype'] in ['Lowest_Cost', 'All-Flash', 'All NVMe'] and bom_input['nodetype'] in err_result_name:
            if 'selectedEstimate' in bom_input:
                return "BAD_REQUEST", "Scenario must have Sizing result to Upload BOM."
            else:
                return "BAD_REQUEST", "Scenario must have {} Sizing result to download BOM excel.".format(
                    bom_input['nodetype'])
            # return Response({'status': 'error',
            #                  'errorMessage': 'Scenario must have %s Sizing result to download BOM excel.'
            #                                  % data['nodetype']},
            #                 status=status.HTTP_400_BAD_REQUEST)

        if scenario_data['settings_json'][0]['server_type'] == 'M6':
            group = scenario_data['workload_json']['wl_list']
            if any(wl.get('gpu_users', False) for wl in group):
                return "BAD_REQUEST", 'GPUs are not currently available for ordering in M6 nodes, per Cisco Spec Sheet.'
            else:
                pass

        # Check for Fixed Config Sizing
        if bom_input['nodetype'] == 'Fixed_Config':
            fixed_sizing_results = len(ReturnData['fixed_workload_result'])
            fixed_errors = len(ReturnData['fixed_error_data'])

            if not fixed_sizing_results or fixed_errors:
                if 'selectedEstimate' in bom_input:
                    return "BAD_REQUEST", "Scenario must have Workload/Sizing result to Upload BOM."
                else:
                    return "BAD_REQUEST", "Scenario must have {} Sizing result to download BOM excel.".format(bom_input['nodetype'])
                # return Response({'status': 'error',
                #                  'errorMessage': 'Scenario must have %s Sizing result to download BOM excel.'
                #                                  % data['nodetype']},
                #                 status=status.HTTP_400_BAD_REQUEST)


        std_version = "2.0.0"
        if 'sizer_version' in scenario_data['settings_json'][0]:
            sizer_version = scenario_data['settings_json'][0]['sizer_version']
            if Version(sizer_version) >= Version(std_version):

                s_data = json.dumps(scenario_data)
                file_path = bomreport.generate_bom(s_data, json.dumps(bom_input))
                # data = {"filename": fpath}

                # Estimate option will be available only in UploadBOM, not in DownloadBOM so it is checked
                # for selectedEstimate and returned
                return "", file_path

            else:
                if 'selectedEstimate' in bom_input:
                    return "BAD_REQUEST", 'Upload BOM is not supported for Sizer Version below 2.0'
                else:
                    return "BAD_REQUEST", 'Download BOM is not supported for Sizer Version below 2.0'
                # return Response({'status': 'error',
                #                  'errorMessage': 'Download BOM is not supported for Sizer Version below 2.0'},
                #                 status=status.HTTP_400_BAD_REQUEST)

        else:
            if 'selectedEstimate' in bom_input:
                return "BAD_REQUEST", 'Upload BOM is not supported for Sizer Version below 2.0'
            else:
                return "BAD_REQUEST", 'Download BOM is not supported for Sizer Version below 2.0'
            # return Response({'status': 'error',
            #                  'errorMessage': 'Download BOM is not supported for Sizer Version below 2.0'},
            #                 status=status.HTTP_400_BAD_REQUEST)
