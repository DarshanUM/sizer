import json
import copy

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser

from utils.baseview import BaseView
from packaging.version import Version

import hyperconverged.views.generatereport as report
import hyperconverged.views.generatebom as bomreport
import hyperconverged.views.sizing_calc_report as calcreport
from hyperconverged.views.bom_excel_report import BomExcelReport

from hyperconverged.solver.attrib import HyperConstants

from hyperconverged.utilities.report_views_functionality import get_bom_ppt_reports, get_excel_template
from hyperconverged.views.utility_views import feature_decorator
from hyperconverged.models import Scenario, SharedScenario, Results, FixedResults
from hyperconverged.serializer.WorkloadSerializer import GenerateReportSerializer, WorkloadGetDetailSerializer, \
    GenerateBOMexcelSerializer

class GenerateReport(BaseView):

    @feature_decorator('Download PPT')
    def post(self, request, id, format=None):
        """
        To generate report
        """
        serializer = GenerateReportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'status': 'error',
                             'errorMessage': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        req_data = json.dumps(data)
        try:
            work_load = Scenario.objects.get(id=id)
        except Scenario.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        sScenario = SharedScenario.objects.filter(scenario_id=id, userid=self.username)
        if not work_load.username == self.username and len(sScenario) == 0:
            return Response({'status': 'error', 'errorMessage': 'Unauthorized Access'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = WorkloadGetDetailSerializer(work_load)

        results = Results.objects.filter(scenario_id=work_load.id).order_by('name').reverse()

        fixed_results = FixedResults.objects.filter(scenario_id=work_load.id)

        ReturnData = dict()
        ReturnData['id'] = serializer.data['id']
        ReturnData['name'] = serializer.data['name']
        wl_list = serializer.data['workload_json']['wl_list'] if 'wl_list' in serializer.data['workload_json']  else list()
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

        if len(results) or len(fixed_results):
            result_data = list()
            settings_data = list()
            error_data = list()

            fixed_result_data = dict()
            fixed_error_data = list()

            for result in results:
                if isinstance(result.settings_json, list):
                    fixed_results = FixedResults.objects.filter(scenario_id=work_load.id)
                    if len(fixed_results):
                        for fixed_res in fixed_results:
                            # fixed_result_data.extend(fixed_res.result_json)
                            fixed_result_data[fixed_res.cluster_name] = fixed_res.result_json
                            if 'message' in fixed_res.error_json and fixed_res.error_json['message']:
                                fixed_error_data.append(fixed_res.error_json)
                                fixed_res.result_json[0]['fixed_error_data'] = fixed_res.error_json
                    else:
                        #fixed_result_data['No_cluster'] = result.result_json
                        if 'message' in result.error_json and result.error_json['message']:
                            fixed_error_data.append(result.error_json)
                            result.result_json[0]['fixed_error_data'] = result.error_json

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
            #TODO
            ReturnData['workload_result'] = serializer.data['workload_result']
            ReturnData['settings_json'] = [serializer.data['settings_json']]

            ReturnData['fixed_workload_result'] = dict()
            ReturnData['fixed_error_data'] = list()

        scenario_data = ReturnData

        sizing_results = len(scenario_data['workload_result'])
        fixed_sizing_results = len(scenario_data['fixed_workload_result'])
        errors = len(scenario_data['errors'])
        # fixed_error = len(scenario_data['fixed_error_data'])
        if not sizing_results and not fixed_sizing_results:
            return Response({'status': 'error',
                             'errorMessage': 'Scenario must have Workload/Sizing result to download report.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # sizing_type = serializer.data.get('sizing_type', 'optimal')
        # if sizing_type == 'fixed' and errors:
        # if "Fixed Config Sizing Report" in data['slides'] and scenario_data['fixed_error_data']:
        #     return Response({'status': 'error',
        #                      'errorMessage': 'Scenario must have Workload/Sizing result to download report.'},
        #                     status=status.HTTP_400_BAD_REQUEST)

        # if not sizing_results or (errors and fixed_error):
        #     return Response({'status': 'error',
        #                      'errorMessage': 'Scenario must have Workload/Sizing result to download report.'},
        #                     status=status.HTTP_400_BAD_REQUEST)

        # Case to Download only Sizing Calculator Report after merging it into Fixed Config
        # Case where No Workloads are added.

        # wls = scenario_data['workload_json']['wl_list'] if 'wl_list' in scenario_data['workload_json'] else list()
        # if not wls:
        #     calc_result = dict()
        #     calc_result['node_properties'] = scenario_data['settings_json'][0]['node_properties']
        #     calc_result['scenario_settings'] = scenario_data['settings_json'][0]['cluster_properties']
        #     calc_result['scenario_settings']['threshold'] = scenario_data['settings_json'][0]['threshold']
        #     calc_result['scenario_settings']['hypervisor'] = scenario_data['settings_json'][0]['hypervisor']
        #     calc_result['results'] = scenario_data['workload_result'][0]['sizing_calculator']
        #     calc_result['username'] = self.username
        #
        #     calc_scenario_data = json.dumps(calc_result)
        #     fpath = calcreport.GenerateSizingCalculatorReport(calc_scenario_data, req_data)
        #     data = {"filename": fpath}
        #     return Response(data)

        std_version = "2.0.0"
        if 'sizer_version' in scenario_data['settings_json'][0]:
            sizer_version = scenario_data['settings_json'][0]['sizer_version']
            if Version(sizer_version) >= Version(std_version):

                s_data = json.dumps(scenario_data)
                fpath = report.generate_report(s_data, req_data)
                data = {"filename": fpath}
                return Response(data)
            else:
                return Response({'status': 'error',
                                 'errorMessage': 'Download report is not supported for Sizer Version below 2.0'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status': 'error',
                             'errorMessage': 'Download report is not supported for Sizer Version below 2.0'},
                            status=status.HTTP_400_BAD_REQUEST)


class SizingCalcReport(BaseView):

    @staticmethod
    def post(request):
        """
        To generate report
        """
        data = JSONParser().parse(request)
        req_data = json.dumps(data)
        fpath = calcreport.GenerateSizingCalculatorReport(req_data)
        data = {"filename": fpath}
        return Response(data)


class DownloadReport(APIView):

    @staticmethod
    def get(request, format=None):
        """
        To download report
        """
        return get_bom_ppt_reports(request)


class GenerateBOMExcel(BaseView):

    @feature_decorator('Download BOM')
    def post(self, request, id, format=None):
        """
        To generate bom excel
        """
        serializer = GenerateBOMexcelSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'status' : 'error', 'errorMessage' : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        req_data = json.dumps(data)

        bom_excel = BomExcelReport()
        res_code, response = bom_excel.generate_bom_file(id, data, self.username)
        if res_code == "NOT_FOUND":
            return Response(status=status.HTTP_404_NOT_FOUND)
        elif res_code == "BAD_REQUEST":
            return Response({'status': 'error', 'errorMessage': response}, status=status.HTTP_400_BAD_REQUEST)
        if not res_code:
            data = {"filename": response}
            return Response(data)


class DownloadBOMExcel(APIView):

    @staticmethod
    def get(request, format=None):
        """
        To download bom excel
        """
        return get_bom_ppt_reports(request)

class DownloadExcelTemplate(APIView):

    @staticmethod
    def get(request, format=None):
        """
        To download bom excel
        """
        return get_excel_template(request)

