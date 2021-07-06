from django.http import JsonResponse
from rest_framework import status

import logging
import traceback
import logging.config
logger = logging.getLogger(__name__)

class ExceptionMiddlewareNew(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception): 
        
        message = "Oops, An unusual error has occurred. Please contact the Sizer team with the scenario details " \
                  "using the feedback button in the right top corner."

        stack = traceback.format_exc()
        url = request.path
        logger.error('\nURL: %s,\n'
                     'DEATILS: %s\n' % (url, str(stack)))

        return JsonResponse({'status': 'error',
                             'errorMessage': message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExceptionMiddleware(object):

    @staticmethod
    def process_exception(request, exception):

        message = "Oops, An unusual error has occurred. Please contact the Sizer team with the scenario details " \
                  "using the feedback button in the right top corner."

        stack = traceback.format_exc()
        url = request.path
        logger.error('\nURL: %s,\n'
                     'DEATILS: %s\n' % (url, str(stack)))

        return JsonResponse({'status': 'error',
                             'errorMessage': message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def process_exception(self, request, exception):
    #     msg = exception.message
    #     code = status.HTTP_500_INTERNAL_SERVER_ERROR
    #
    #     parsed_exception = exception.message.split('|')
    #     if len(parsed_exception) > 3:
    #         result_name = parsed_exception[3]
    #     else:
    #         result_name = ''
    #
    #     if 'unsupported operand' in exception.message:
    #         msg = 'Invalid input data. Data of wrong datatype.'
    #         errorCode = 1
    #     elif 'Unfeasible' in exception.message:
    #         msg = 'No valid sizing possible. Split workloads into new cluster.'
    #         errorCode = 2
    #     elif 'WL_Too_Large' in exception.message:
    #
    #         workloads = parsed_exception[1][1:-1]
    #         workload = workloads.split(",")
    #         for index in range(0,len(workload)):
    #             workload[index] = workload[index][3:-1]
    #
    #         msg = 'A workload is too large to fit into one cluster. Split the following workloads into smaller workloads.'
    #         msg += '<br />Workloads: ' + str(workload)
    #         msg += '<br />Result Name: ' + str(result_name)
    #
    #         errorCode = 3
    #     elif 'No_HC_Nodes' in exception.message:
    #         msg = 'No hyperconverged nodes have been chosen, due to filters. Please change the filters.'
    #         msg += '<br />Result Name: ' + str(result_name)
    #         errorCode = 6
    #     elif 'No_Compute_Nodes' in exception.message:
    #         msg = 'No compute nodes have been chosen, for Hyperflex + Compute, due to filters. Please change the filters.'
    #         msg += '<br />Result Name: ' + str(result_name)
    #         errorCode = 7
    #     elif 'Invalid Database' in exception.message:
    #         scen_id = 0
    #         msg = exception.message
    #         errorCode = 8
    #     elif 'No_Settings_Json' in exception.message:
    #         msg = 'No settings json provided.'
    #         errorCode = 9
    #     elif 'No_GPU_Nodes' in exception.message:
    #         msg = 'No GPU nodes found, with a GPU workload added.'
    #         msg += '<br />Result Name: ' + str(result_name)
    #         errorCode = 10
    #     elif 'No_DB_Nodes' in exception.message:
    #         msg = 'No All-Flash nodes found, with a DB workload added.'
    #         msg += '<br />Result Name: ' + str(result_name)
    #         errorCode = 11
    #     elif 'No_Compute_Node_Combinations' in exception.message:
    #         msg = 'No compute nodes available due to filters.'
    #         msg += '<br />Result Name: ' + str(result_name)
    #         errorCode = 12
    #     elif 'Missing_Threshold_Value' in exception.message:
    #         msg = 'A threshold value is missing in the database.'
    #         errorCode = 13
    #     elif 'No_ROBO_Nodes' in exception.message:
    #         msg = 'No Edge nodes have been chosen, with a Edge workload, due to filters. Please change the filters.'
    #         msg += '<br />Result Name: ' + str(result_name)
    #         errorCode = 14
    #     elif 'No_CTO_HC_Nodes' in exception.message:
    #         msg = 'No CTO hyperconverged nodes have been chosen, due to filters. Please change the filters.'
    #         msg += '<br />Result Name: ' + str(result_name)
    #         errorCode = 15
    #     elif 'Unauthorized Access' in exception.message:
    #         scen_id = 0
    #         msg = 'Unauthorized Access'
    #         errorCode = 0
    #         code = status.HTTP_403_FORBIDDEN
    #     elif 'CSV format' in exception.message or 'CPU model' in exception.message:
    #         msg = exception.message
    #         errorCode = 16
    #     elif 'Column ' in exception.message or 'Columns' in  exception.message or 'Specint data' or \
    #                     'SPECint ' in exception.message:
    #         msg = exception.message
    #         errorCode = 17
    #     elif 'LDAP' in exception.message:
    #         msg = exception.message
    #         errorCode = 18
    #     else:
    #         scen_id = 0
    #         logger.error(exception.message)
    #         msg = 'Unknown Error. Check Server Logs.'
    #         errorCode = 0
    #
    #     if msg:
    #         scen_id = ""
    #         if len(exception.message.split('|')) > 1:
    #             scen_id = exception.message.split('|')[-2]
    #         logger.error('|%s| %s' %(scen_id,msg))
    #         logger.info('|%s| Finish Sizing' %(scen_id))
    #         return JsonResponse({'status':'error','errorCode': errorCode,'errorMessage': msg}, status=code)
    #
    #     return None
