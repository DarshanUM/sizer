import django
import os
from packaging.version import Version
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from datetime import datetime
import time
import xlsxwriter
from collections import defaultdict
from collections import OrderedDict

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sizer.local_settings")

django.setup()

from hyperconverged.models import Scenario, Results

output_array = list()
cpu_array = list()
disk_array = list()
node_occ_details = defaultdict(lambda: defaultdict(int))

analytics_array = list()

# This Script to export the Analytics to Excel file, Update the local database with the latest Production DB backup before running this Script.

# To fetch first 10K records order by id, as script runs for 7-8 hrs divide the records like below 
# scenario_list = Scenario.objects.all().order_by('-id')[10000:20000]

scenario_list = Scenario.objects.all().order_by('-id')[:10000]

# To fetch records based on updated date which are done last one year

# last_year_date="2019-04-28T00:00:00Z"
# scenario_list = Scenario.objects.filter(updated_date__gte=last_year_date).order_by('-id')

print "scenario list len = ", len(scenario_list)

epoch_milli_sec = int(round(time.time() * 1000))
currentdate = datetime.now()
print "Start time", currentdate

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
        if output['scenario_name'] == 'sav_test2333':
            print "Found mine"

        output['cluster_details'] = list()

        for result in results.result_json:

            #For fixed config with no results
            if 'clusters' not in result:
                return

            output['cluster_count'] = sum([len(cluster) for cluster in result['clusters']])
            num_nodes = result['summary_info']['num_nodes']
            num_ft_nodes = result['summary_info']['num_ft_nodes']
            total_hyperconverged = 0
            total_all_flash = 0
            total_compute = 0

            cluster_no = 0

            for clusterindex in result['clusters']:

                if type(clusterindex) is not list:
                    continue

                wl_count = dict()


                for cluster in clusterindex:

                    cluster_no += 1
                    cluster_name = "Cluster " + str(cluster_no)

                    workload_list = cluster['wl_list']
                    for workload in workload_list:
                        wl_type = workload['wl_type']
                        if wl_type not in WL_LIST or wl_type not in wl_count:
                            wl_count[wl_type] = 0

                        wl_count[wl_type] += 1


                    if 'status' in cluster['Utilization'][0]:
                        cpu_without_failure = int(round(cluster['Utilization'][0]['wl_util'])) if cluster['Utilization'][0][
                        'status'] else 0
                        cpu_with_failure = int(round(cluster['Utilization'][0]['ft_util'])) if cluster['Utilization'][0][
                        'status'] else 0
                    else:
                        cpu_without_failure = int(round(cluster['Utilization'][0]['wl_util']))
                        cpu_with_failure = int(round(cluster['Utilization'][0]['ft_util']))

                    if 'status' in cluster['Utilization'][1]:
                        ram_without_failure = int(round(cluster['Utilization'][1]['wl_util'])) if cluster['Utilization'][1][
                        'status'] else 0
                        ram_with_failure = int(round(cluster['Utilization'][1]['ft_util'])) if cluster['Utilization'][1][
                        'status'] else 0
                    else:
                        ram_without_failure = int(round(cluster['Utilization'][1]['wl_util']))
                        ram_with_failure = int(round(cluster['Utilization'][1]['ft_util']))

                    if 'status' in cluster['Utilization'][2]:
                        hdd_without_failure = int(round(cluster['Utilization'][2]['wl_util'])) if cluster['Utilization'][2][
                            'status'] else 0
                        hdd_with_failure = int(round(cluster['Utilization'][2]['ft_util'])) if cluster['Utilization'][2][
                        'status'] else 0
                    else:
                        hdd_without_failure = int(round(cluster['Utilization'][2]['wl_util']))
                        hdd_with_failure = int(round(cluster['Utilization'][2]['ft_util']))

                    if 'status' in cluster['Utilization'][4]:
                        iops_without_failure = int(round(cluster['Utilization'][4]['wl_util'])) if cluster['Utilization'][4][
                            'status'] else 0
                        iops_with_failure = int(round(cluster['Utilization'][4]['ft_util'])) if cluster['Utilization'][4][
                        'status'] else 0
                    else:
                        iops_without_failure = int(round(cluster['Utilization'][4]['wl_util']))
                        iops_with_failure = int(round(cluster['Utilization'][4]['ft_util']))


                    percluster_details = list()

                    percluster_details.append(cluster_name)

                    cluster_wl_list = ""
                    for key, value in wl_count.iteritems():
                        cluster_wl_list += key + '(' + str(value) + ")  "

                    percluster_details.append(cluster_wl_list)
                    percluster_details.append(cpu_without_failure)
                    percluster_details.append(cpu_with_failure)
                    percluster_details.append(ram_without_failure)
                    percluster_details.append(ram_with_failure)
                    percluster_details.append(hdd_without_failure)
                    percluster_details.append(hdd_with_failure)
                    percluster_details.append(iops_without_failure)
                    percluster_details.append(iops_with_failure)

                    hx_cpu_type = cluster['node_info'][0]['model_details']['cpu_part'].split('_')[0]
                    disk_type = cluster['node_info'][0]['bom_details']['hdd_bom_name']
                    num_drives = cluster['node_info'][0]['model_details']['hdd_slots']
                    hdd_desc = cluster['node_info'][0]['bom_details']['hdd_bom_descr']
                    hx_num_nodes = cluster['node_info'][0]['num_nodes']
                    hx_num_ft_nodes = cluster['node_info'][0]['num_ft_nodes']

                    if len(cluster['node_info']) > 1:
                        co_num_nodes = cluster['node_info'][1]['num_nodes']
                    else:
                        co_num_nodes = ""

                    percluster_details.append(hx_num_nodes)
                    percluster_details.append(hx_num_ft_nodes)
                    percluster_details.append(co_num_nodes)
                    percluster_details.append(str(hx_cpu_type))
                    percluster_details.append(str(disk_type))
                    percluster_details.append(num_drives)
                    percluster_details.append(str(hdd_desc))


                    output['cluster_details'].append(percluster_details)

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
            output['ft_nodes'] = num_ft_nodes
            output['total_hyperconverged'] = total_hyperconverged
            output['total_all_flash'] = total_all_flash
            output['total_compute'] = total_compute
            output['total_node_by_sku'] = node_sku_distribution

            # output['cluster_details']['util_details'] = util_array
            # output['cluster_details']['node_details'] = node_array

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

    if output['scenario_name'] == 'sav_test2333':
        print "Found mine"

    if type(scenario.settings_json) == list:
        if 'account' in scenario.settings_json[0]:
            output['account_name'] = scenario.settings_json[0]['account']
            output['scenario_version'] = scenario.settings_json[0]['sizer_version'] \
                if 'sizer_version' in scenario.settings_json[0] else 'N/A'

    elif type(scenario.settings_json) == dict:
        if 'account' in scenario.settings_json:
            output['account_name'] = scenario.settings_json['account']
            output['scenario_version'] = scenario.settings_json['sizer_version'] \
                if 'sizer_version' in scenario.settings_json else 'N/A'

    output['username'] = scenario.username
    output['sizing_type'] = scenario.sizing_type
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

    # WL_LIST = ['VDI', 'VDI_HOME', 'EPIC', 'VDI_INFRA', 'RDSH', 'RDSH_HOME',
    #            'DB', 'OLTP', 'OLAP', 'ORACLE', 'OOLTP', 'OOLAP', 'SPLUNK', 'AWR_FILE',
    #            'VSI', 'EXCHANGE', 'ROBO', 'RAW', 'RAW_FILE', 'VEEAM', 'CONTAINER', 'AIML']

    WL_LIST = ['VDI', 'VDI_HOME', 'EPIC', 'VDI_INFRA', 'RDSH', 'RDSH_HOME',
               'DB', 'ORACLE', 'SPLUNK', 'VSI', 'EXCHANGE', 'ROBO', 'RAW', 'RAW_FILE', 'VEEAM', 'CONTAINER', 'AIML']

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
    if scenario.sizing_type == 'fixed':
        result_list = Results.objects.filter(scenario_id=scenario.id)
    else:
        result_list = Results.objects.filter(scenario_id=scenario.id, name='Lowest_Cost')

    node_sku_distribution = defaultdict(int)

    for results in result_list:
        if 'sizer_version' not in results.settings_json:
            continue
        if Version(results.settings_json['sizer_version']) < 3.1:
            continue
        if Version(results.settings_json['sizer_version']) < 5.1:
            analysis_sizerversion_below_5point1()
        if Version(results.settings_json['sizer_version']) >= 5.2:
            analysis_sizerversion_above_5point2()

    output_array.append(output)

    if output['scenario_name'] == 'sav_test2333':
        analytics_array.append(output)

import json

#print json.dumps(output_array)

#print json.dumps(analytics_array)

print "Data collection done"

'''
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


'''
# print ES.search(index='sizer_output', doc_type='sizer_output', body={'query':{'match_all':dict()}})
'''


# Cron Job 2
# This Cron job is to update the User details Email and Access level fetched from LDAP to auth_user table to resolve
# permission issues faced by users.

import update_user_details as updateusers
updateusers.update_user_details()
'''




details_table = OrderedDict()
row_index = 0

for data in output_array:

    if 'cluster_details' not in data:
        details_per_row = list()

        if 'scenario_name' in data:
            details_per_row.append(data['scenario_name'])

        if 'username' in data:
            details_per_row.append(data['username'])

        if 'scenario_version' in data:
            details_per_row.append(data['scenario_version'])
        else:
            details_per_row.append('N/A')

        if 'sizing_type' in data:
            details_per_row.append(data['sizing_type'])
        else:
            details_per_row.append('N/A')

        if 'updated_date' in data:
            details_per_row.append(data['updated_date'])

        if 'wl_type_count' in data:
            wl_list = ""
            for key, value in data['wl_type_count'].iteritems():
                if value:
                    wl_list += key + '(' + str(value) + ")  "

            details_per_row.append(wl_list)
        else:
            details_per_row.append("No Workloads")


        if 'wl_type_count' in data:
            wl_list = list()
            for wl_type in WL_LIST:
                wl_list.append(data['wl_type_count'][wl_type])

            details_per_row.extend(wl_list)
        else:
            wl_list = list()
            for wl_type in WL_LIST:
                wl_list.append("")
            details_per_row.extend(wl_list)

        if 'total_nodes' in data:
            node_str = "%s+%s (FT)" % ((data['total_nodes'] - data['ft_nodes']), data['ft_nodes'])
            details_per_row.append(node_str)
            details_per_row.append(data['total_nodes'] - data['ft_nodes'])
            details_per_row.append(data['ft_nodes'])
            details_per_row.append(data['total_compute'])
        else:
            details_per_row.append("No Result")
            details_per_row.append("")
            details_per_row.append("")
            details_per_row.append("")

        row_name = "row" + str(row_index)
        details_table[row_name] = details_per_row
        row_index += 1

    else:

        for cluster in data['cluster_details']:

            details_per_row = list()

            if 'scenario_name' in data:
                details_per_row.append(data['scenario_name'])

            if 'username' in data:
                details_per_row.append(data['username'])

            if 'scenario_version' in data:
                details_per_row.append(data['scenario_version'])
            else:
                details_per_row.append('N/A')

            if 'sizing_type' in data:
                details_per_row.append(data['sizing_type'])
            else:
                details_per_row.append('N/A')

            if 'updated_date' in data:
                details_per_row.append(data['updated_date'])

            if 'wl_type_count' in data:
                wl_list = ''
                for key, value in data['wl_type_count'].iteritems():
                    if value:
                        wl_list += key + '(' + str(value) + ")  "

                details_per_row.append(wl_list)
            else:
                details_per_row.append("No Workloads")

            if 'wl_type_count' in data:
                wl_list = list()
                for wl_type in WL_LIST:
                    wl_list.append(data['wl_type_count'][wl_type])

                details_per_row.extend(wl_list)
            else:
                wl_list = list()
                for wl_type in WL_LIST:
                    wl_list.append("")
                details_per_row.extend(wl_list)

            if 'total_nodes' in data:
                node_str = "%s+%s (FT)" %((data['total_nodes'] - data['ft_nodes']), data['ft_nodes'])
                details_per_row.append(node_str)
                details_per_row.append(data['total_nodes'] - data['ft_nodes'])
                details_per_row.append(data['ft_nodes'])
                details_per_row.append(data['total_compute'])
            else:
                details_per_row.append("No Result")
                details_per_row.append("")
                details_per_row.append("")
                details_per_row.append("")


            details_per_row.extend(cluster)


            row_name = "row" + str(row_index)
            details_table[row_name] = details_per_row
            row_index += 1


currentdatetime = datetime.now().strftime('%Y-%m-%d_%H-%M')
analytics_report_name = "sizeranalytics" + "_" + str(currentdatetime) + ".xlsx"



wb = xlsxwriter.Workbook(analytics_report_name)

sheetname = "Sizer Analytics"
worksheet = wb.add_worksheet(sheetname)

# Adjust the column width.
#column_width = [15, 15, 15, 15, 15, 15, 15, 20, 20]
tablehdr = wb.add_format({'bold': True, 'font_size': '12'})
nodehdr = wb.add_format({'bold': True, 'font_size': '11'})

# Header
hdr = ["Scenario name", "Owner", "Scenario version", "Sizing type", "Updated date", "All workload(s)"]

hdr.extend(WL_LIST)

hdr.extend(["Total nodes", "Total HX nodes", "Total FT nodes", "Total Compute nodes",
       "Cluster name", "Cluster workload(s)",
       "CPU % (Without failures)", "CPU % (With failures)", "RAM % (Without failures)", "RAM % (With failures)",
       "HDD % (Without failures)", "HDD % (With failures)", "IOPS % (Without failures)", "IOPS % (With failures)",
       "# of HX nodes", "# of FT nodes", "# of Compute nodes", "CPU Type",
       "Disk Type", "# of drives", "Drive description"])


column_width = [15] * len(hdr)

# Fixed Rows and columns for table. Here col=1 means second column.
row = 0

for colindex in range(0, len(hdr)):
    worksheet.set_column(row, colindex, column_width[colindex])
    worksheet.write(row, colindex, hdr[colindex], tablehdr)

row = 1
col = 0

for rowindex in range(0, len(details_table)):
    key_name = "row" + str(rowindex)
    part_data_list = details_table[key_name]

    for item in part_data_list:

        worksheet.set_column(row, col, column_width[col])
        worksheet.write(row, col, item)

        col += 1

    row += 1
    col = 0

wb.close()

currentdate = datetime.now()
print "END time", currentdate

