import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sizer.local_settings")

django.setup()

from hyperconverged.models import Scenario

scenario_list = Scenario.objects.all()

for scenario in scenario_list:
    scenario_json = scenario.scenario_json
    settings_json = scenario.settings_json
    settings_json['account'] = scenario_json['account']
    settings_json['deal_id'] = scenario_json['deal_id']
    if 'sizer_version' in scenario_json.keys():
        settings_json['sizer_version'] = scenario_json['sizer_version']
        settings_json['hx_version'] = scenario_json['hx_version']
    if 'heterogenous' in scenario_json.keys():
        settings_json['heterogenous'] = scenario_json['heterogenous']
        settings_json['threshold'] = scenario_json['threshold']
    else:
        settings_json['heterogenous'] = False
        settings_json['threshold'] = 1
    settings_json['result_name'] = 'Lowest_Cost'
    scenario.settings_json = settings_json

    scenario.save()
