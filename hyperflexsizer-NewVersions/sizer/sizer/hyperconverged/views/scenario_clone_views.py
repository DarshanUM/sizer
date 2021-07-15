from utils.baseview import BaseView
from rest_framework.response import Response
from rest_framework import status

from hyperconverged.models import Scenario, Results, FixedResults

class ScenarioClone(BaseView):

    def post(self, request, id):

        old_scenario = Scenario.objects.get(id=id)
        new_scenario = Scenario()
        new_name = request.data["name"]
        
        if Scenario.objects.filter(name=new_name):
            er_msg = "Scenario with name '" + new_name + "' already existed"
            return Response({'status': 'error', 'errorMessage': er_msg}, status=status.HTTP_400_BAD_REQUEST)

        new_scenario.name = new_name
        new_scenario.workload_json = old_scenario.workload_json
        new_scenario.workload_result = old_scenario.workload_result
        new_scenario.status = old_scenario.status
        new_scenario.settings_json = old_scenario.settings_json
        new_scenario.sizing_type = old_scenario.sizing_type
        new_scenario.username = self.username
        new_scenario.save()

        old_results = Results.objects.filter(scenario_id=id)

        for result in old_results:
            new_result = Results()
            new_result.scenario_id = new_scenario.id
            new_result.name = result.name
            new_result.result_json = result.result_json
            new_result.settings_json = result.settings_json
            new_result.error_json = result.error_json

            if result.name != 'Fixed_Config':
                new_result.settings_json['account'] = request.data['settings_json'][0]['account'] \
                    if 'account' in request.data['settings_json'][0] else ""

            new_result.save()

        
        if old_scenario.sizing_type == "hybrid":
            old_fixed_result = FixedResults.objects.filter(scenario_id=id)
        
            for fixed_result in old_fixed_result:
                new_fix_result = FixedResults()
                new_fix_result.result_json = fixed_result.result_json
                new_fix_result.cluster_name = fixed_result.cluster_name
                new_fix_result.scenario_id = new_scenario.id
                new_fix_result.settings_json = fixed_result.settings_json
                new_fix_result.error_json = fixed_result.error_json
                new_fix_result.save()

        return Response({'status': 'success'}, status=status.HTTP_200_OK)
