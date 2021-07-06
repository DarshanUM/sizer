import json

from rest_framework.response import Response
from rest_framework import status
from utils.baseview import BaseView

from hyperconverged.views.RV_tools_calc import RVToolsCalculator
from hyperconverged.views.exchange_workload_calc import ExchangeWorkload
from hyperconverged.views.profiler_calc import process_esx_data
from hyperconverged.views.bulk_wl_calc import BulkWLCalculator
from hyperconverged.views.oracle_awr_calc import OracleAwr


class ProcessEsxStat(BaseView):

    @staticmethod
    def post(request):

        file_name = request.FILES['file'].name

        isbulkworkload = request.data.get('bulkwl', False)

        if isbulkworkload:

            if file_name.endswith(".xls") or file_name.endswith(".xlsx") or file_name.endswith(".XLS") or \
                    file_name.endswith(".XLSX"):

                scenario_id = request.data.get('id', None)
                content = BulkWLCalculator(request.FILES["file"], scenario_id).construct_response()
                error_message = content[1]
                response = content[0]

                if error_message:
                    return Response({"status": "error",
                                     "Msg": error_message,
                                     "data": response})
                else:
                    return Response({"status": "success", "Msg": list(),
                                     "data": response})

            else:
                return Response({'status': 'error',
                                 'errorMessage': 'File is not in xls(x) format.'},
                                status=status.HTTP_400_BAD_REQUEST)

        if file_name.endswith("csv") or file_name.endswith("CSV"):

            file_data = request.FILES['file'].read()

            file_data = str(file_data, 'utf-8')

            if file_data:

                result, error = process_esx_data(file_data)

                if error['Num_of_Errors'] > 0 or error['Error'] != '':
                    return Response({'status': 'error',
                                     'Msg': list(error['Error'].split('\n')[:-1]),
                                     'data': json.loads(json.dumps(result))})

                elif error['Num_of_Errors'] == 0 and error['Warnings'] != '':
                    warning_result = 'The following servers have insufficient historical data. \n' + error['Warnings']
                    return Response({'status': 'warning',
                                     'Msg': list(warning_result.split('\n')),
                                     'data': json.loads(json.dumps(result))})

                else:
                    return Response({'status': 'success',
                                     'Msg': list(),
                                     'data': json.loads(json.dumps(result))})

            else:
                return Response({'status': 'error',
                                 'errorMessage': 'Data is empty.'},
                                status=status.HTTP_400_BAD_REQUEST)

        elif file_name.endswith(".xls") or file_name.endswith(".xlsx") or file_name.endswith(".XLS") or \
                file_name.endswith(".XLSX"):

            content = RVToolsCalculator(request.FILES["file"]).construct_response()
            error_message = content[1]
            response = content[0]

            if error_message:
                return Response({"status": "error",
                                 "Msg": error_message,
                                 "data": response})
            else:
                if 'Unassigned' in response:
                    return Response({"status": "warning",
                                     "Msg": ["We have hosts that don't belong to any cluster."],
                                     "data": response})

                return Response({"status": "success",
                                 "Msg": list(),
                                 "data": response})

        elif file_name.endswith(".xlsm") or file_name.endswith(".XLSM"):

            content = ExchangeWorkload(request.FILES["file"]).construct_response()

            if content['errors']:
                return Response({"status": "error",
                                 "Msg": list(content['errors'].split('\n')),
                                 "data": content['response']})

            elif content['warnings']:
                return Response({"status": "warning",
                                 "Msg": list(content['warnings'].split('\n')),
                                 "data": content['response']})

            else:
                return Response({"status": "success",
                                 "Msg": list(),
                                 "data": content['response']})

        elif file_name.endswith(".txt") or file_name.endswith(".TXT") or file_name.lower().endswith(".html") \
                or file_name.lower().endswith(".htm"):

            if file_name.lower().endswith(".html") or file_name.lower().endswith(".htm"):
                content = OracleAwr(request.FILES["file"]).construct_response(True)
            else:
                content = OracleAwr(request.FILES["file"]).construct_response(False)

            if content.errors:
                return Response({"status": "error",
                                 "Msg": content.errors,
                                 "data": content.response})
            else:
                return Response({"status": "success",
                                 "Msg": list(),
                                 "data": content.response})

        else:
            return Response({'status': 'error',
                             'errorMessage': 'File is not in csv / xls(x) / xls(m) format.'},
                            status=status.HTTP_400_BAD_REQUEST)
