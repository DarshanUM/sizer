import django
import os
from packaging.version import Version
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from datetime import datetime
from datetime import timedelta
import time
from collections import defaultdict

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sizer.local_settings")

django.setup()

from hyperconverged.models import Scenario, Results

output_array = list()
cpu_array = list()
disk_array = list()
node_occ_details = defaultdict(lambda: defaultdict(int))

print ("Running Export Analytics Script... ")

# Fetching all the Scenarios is commented as there more than 55K scenarios and it takes lotz of time run
# scenario_list = Scenario.objects.all()
# print ("Total number of Scenarios = ", len(scenario_list))


epoch_milli_sec = int(round(time.time() * 1000))
currentdate = datetime.now()
print ("Analytics Script Start time", currentdate)

# last_year_date="2019-09-30T00:00:00Z"
last_year_date = datetime.now() - timedelta(days=1*365)
scenario_list = Scenario.objects.filter(updated_date__gte=last_year_date).order_by('-id')
print ("Total number of Scenarios in a span of year = ", len(scenario_list))


def analysis_sizerversion_below_5point1():

        for result in results.result_json:

            output['cluster_count'] = len(result['clusters'])
            num_nodes = result['summary_info']['num_nodes']

            total_hyperconverged = 0
            total_all_flash = 0
            total_compute = 0

            for cluster in result['clusters']:

                for node in cluster['node_info']:

                    node_bom_name = node['bom_details']['bom_name']
                    node_type = node['model_details']['subtype']
                    cpu_type = node['model_details']['cpu_part'].split('_')[0]
                    disk_type = node['model_details']['hdd_size']
                    num_individual_node = node['num_nodes']

                    if node_type in ['hyperconverged', 'robo', 'lff_12tb', 'veeam']:
                        total_hyperconverged += num_individual_node
                    elif node_type in ['all-flash', 'allnvme', 'robo_allflash', 'epic']:
                        total_all_flash += num_individual_node
                    elif node_type == 'compute':
                        total_compute += num_individual_node

                    node_sku_distribution[node_bom_name] += num_individual_node

                    cpu_array.append({'created_date': output['created_date'],
                                      'cpu_type': cpu_type,
                                      'scen_id': scenario.id})

                    node_occ_details[node_bom_name][num_individual_node] += 1

                    if node_type != 'compute':

                        disk_array.append({'created_date': output['created_date'],
                                           'disk_type': disk_type,
                                           'scen_id': scenario.id})

            output['total_nodes'] = num_nodes
            output['total_hyperconverged'] = total_hyperconverged
            output['total_all_flash'] = total_all_flash
            output['total_compute'] = total_compute
            output['total_node_by_sku'] = node_sku_distribution

            if total_compute > 0: 
                output['result_type'] = 'HX+Compute'
            else:
                if total_all_flash > 0:
                    output['result_type'] = 'All-flash'
                elif total_hyperconverged > 0:
                    output['result_type'] = 'HX'


def analysis_sizerversion_above_5point2():

        for result in results.result_json:

            output['cluster_count'] = sum([len(cluster) for cluster in result['clusters']])
            num_nodes = result['summary_info']['num_nodes']
            total_hyperconverged = 0
            total_all_flash = 0
            total_compute = 0

            for clusterindex in result['clusters']:

                if type(clusterindex) is not list:
                    continue

                for cluster in clusterindex:

                    for node in cluster['node_info']:

                        node_bom_name = node['bom_details']['bom_name']
                        node_type = node['model_details']['subtype']
                        cpu_type = node['model_details']['cpu_part'].split('_')[0]
                        disk_type = node['model_details']['hdd_size']
                        num_individual_node = node['num_nodes']

                        if node_type in ['hyperconverged', 'robo', 'lff_12tb', 'veeam']:
                            total_hyperconverged += num_individual_node
                        elif node_type in ['all-flash', 'allnvme', 'robo_allflash', 'epic']:
                            total_all_flash += num_individual_node
                        elif node_type == 'compute':
                            total_compute += num_individual_node

                        node_sku_distribution[node_bom_name] += num_individual_node

                        cpu_array.append({'created_date': output['created_date'],
                                          'cpu_type': cpu_type,
                                          'scen_id': scenario.id})

                        node_occ_details[node_bom_name][num_individual_node] += 1

                        if node_type != 'compute':
                            disk_array.append({'created_date': output['created_date'],
                                               'disk_type': disk_type,
                                               'scen_id': scenario.id})

            output['total_nodes'] = num_nodes
            output['total_hyperconverged'] = total_hyperconverged
            output['total_all_flash'] = total_all_flash
            output['total_compute'] = total_compute
            output['total_node_by_sku'] = node_sku_distribution

            if total_compute > 0: 
                output['result_type'] = 'HX+Compute'
            else:
                if total_all_flash > 0:
                    output['result_type'] = 'All-flash'
                elif total_hyperconverged > 0:
                    output['result_type'] = 'HX'


for scenario in scenario_list:

    output = dict()

    # Scenario Level Statistics

    output['scenario_id'] = scenario.id
    output['scenario_name'] = scenario.name

    if type(scenario.settings_json) == list:
        if 'account' in scenario.settings_json[0]:
            output['account_name'] = scenario.settings_json[0]['account']
    elif type(scenario.settings_json) == dict:
        if 'account' in scenario.settings_json:
            output['account_name'] = scenario.settings_json['account']

    output['username'] = scenario.username
    output['created_date'] = scenario.created_date.strftime('%Y-%m-%d %H:%M:%S')
    output['updated_date'] = scenario.updated_date.strftime('%Y-%m-%d %H:%M:%S')

    output['current_timestamp'] = currentdate.strftime('%Y-%m-%d %H:%M:%S')
    output['epoch_time'] = epoch_milli_sec

    try:
        if 'wl_list' not in scenario.workload_json:
            output_array.append(output)
            continue
    except:
        output_array.append(output)
        continue

    # Workload Level Statistics
    wl_type_count = dict()
    wl_instance_count = dict()

    WL_LIST = ['VDI', 'VDI_HOME', 'EPIC', 'VDI_INFRA', 'RDSH', 'RDSH_HOME',
               'DB', 'OLTP', 'OLAP', 'ORACLE', 'OOLTP', 'OOLAP', 'SPLUNK', 'AWR_FILE',
               'VSI', 'EXCHANGE', 'ROBO', 'RAW', 'RAW_FILE', 'VEEAM', 'CONTAINER', 'AIML',
               'ANTHOS', 'ROBO_BACKUP']

    for wl_type in WL_LIST:
        wl_type_count[wl_type] = 0
        wl_instance_count[wl_type] = 0

    workload_list = scenario.workload_json['wl_list']

    for workload in workload_list:

        wl_type = workload['wl_type']
 
        if wl_type not in WL_LIST:
            wl_type_count[wl_type] = 0
            wl_instance_count[wl_type] = 0

        wl_type_count[wl_type] += 1

        if wl_type == 'VDI':
            wl_instance_count[wl_type] += workload['num_desktops']
            # separate condition for this because VDI-HOME workloads aren't created by users.
            # Hence they won't be present in input json
            if workload.get('vdi_directory', 0):
                wl_type_count['VDI_HOME'] += 1
        elif wl_type == 'VSI':
            wl_instance_count[wl_type] += workload['num_vms']
        elif wl_type in ['DB', 'ORACLE', 'OLTP', 'OLAP', 'OOLTP', 'OOLAP']:
            wl_instance_count[wl_type] += workload['num_db_instances']
        elif wl_type == 'RAW':
            wl_instance_count[wl_type] += 1
        elif wl_type == 'ROBO':
            wl_instance_count[wl_type] += workload['num_vms']
        elif wl_type == 'EXCHANGE':
            wl_instance_count[wl_type] += 1
        elif wl_type == 'EPIC':
            wl_instance_count[wl_type] += 1
        elif wl_type == 'VDI_INFRA':
            wl_instance_count[wl_type] += 1
        elif wl_type == 'RDSH':
            wl_instance_count[wl_type] += workload['total_users']
            # separate condition for this because VDI-HOME workloads aren't created by users.
            # Hence they won't be present in input json
            if workload.get('rdsh_directory', 0):
                wl_type_count['RDSH_HOME'] += 1
        elif wl_type == 'SPLUNK':
            wl_instance_count[wl_type] += 1
        elif wl_type == 'VEEAM':
            wl_instance_count[wl_type] += 1

    output['wl_type_count'] = wl_type_count
    output['wl_instance_count'] = wl_instance_count

    if len([x for x in wl_type_count.values() if x]) > 1:
        output['scenario_wl_type'] = 'Mixed'
    else:
        for wl in WL_LIST:
            if wl_type_count[wl] > 0:
                output['scenario_wl_type'] = wl

    # Result Level Statistics
    result_list = Results.objects.filter(scenario_id=scenario.id, name='Lowest_Cost')

    node_sku_distribution = defaultdict(int)

    for results in result_list:
        if 'sizer_version' not in results.settings_json:
            continue
        if Version(results.settings_json['sizer_version']) < Version("3.1"):
            continue
        if Version(results.settings_json['sizer_version']) < Version("5.1"):
            analysis_sizerversion_below_5point1()
        if Version(results.settings_json['sizer_version']) >= Version("5.2"):
            analysis_sizerversion_above_5point2()

    output_array.append(output)

# import json
# print (json.dumps(output_array))

endtime = datetime.now()
print("Analytics Script End time", endtime)

print("Time taken to run Script: ", endtime-currentdate)

# ES = Elasticsearch(['http://10.131.35.61:9200'])
ES = Elasticsearch(['http://analytics-elasticsearch-svc:9200'])

query = {'query': {'match_all': dict()}}

ES.delete_by_query(index='temp_sizer_output', doc_type='sizer_output', body=query, ignore=[400, 404])
for output in output_array:
    ES.index(index='temp_sizer_output', doc_type='sizer_output', body=output, refresh=True)

ES.delete_by_query(index='sizer_output', doc_type='sizer_output', body=query, ignore=[400, 404])
helpers.reindex(ES, 'temp_sizer_output', 'sizer_output')

ES.delete_by_query(index='temp_sizer_output_stats', doc_type='sizer_output_stats', body=query, ignore=[400, 404])
for cpu_output in cpu_array:
    ES.index(index='temp_sizer_output_stats', doc_type='sizer_output_stats', body=cpu_output, refresh=True)

for disk_output in disk_array:
    ES.index(index='temp_sizer_output_stats', doc_type='sizer_output_stats', body=disk_output, refresh=True)

ES.delete_by_query(index='sizer_output_stats', doc_type='sizer_output_stats', body=query, ignore=[400, 404])
helpers.reindex(ES, 'temp_sizer_output_stats', 'sizer_output_stats')

ES.delete_by_query(index='temp_sizer_node_stats', doc_type='sizer_node_stats', body=query, ignore=[400, 404])
for node_sku in node_occ_details:
    for cluster_size in node_occ_details[node_sku]:
        ES.index(index='temp_sizer_node_stats',
                 doc_type='sizer_node_stats',
                 body={'node_sku': node_sku,
                       'cluster_size': cluster_size,
                       'occurrence': node_occ_details[node_sku][cluster_size],
                       'current_timestamp': currentdate.strftime('%Y-%m-%d %H:%M:%S')},
                 refresh=True)

ES.delete_by_query(index='sizer_node_stats', doc_type='sizer_node_stats', body=query, ignore=[400, 404])
helpers.reindex(ES, 'temp_sizer_node_stats', 'sizer_node_stats')


# Cron Job 2
# This Cron job is to update the User details Email and Access level fetched from LDAP to auth_user table to resolve
# permission issues faced by users.

import update_user_details as updateusers
updateusers.update_user_details()
