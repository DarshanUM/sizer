import csv
from hyperconverged.models import SpecIntData
from re import findall, compile, IGNORECASE
from django.core.exceptions import ObjectDoesNotExist
from copy import deepcopy
from base_sizer.solver.wl import WL
from collections import defaultdict
from math import ceil

def get_model_obj(vm_data, model_name, num_cores, cpu_clock):

    def get_cpu_model(spec_objs):

        if spec_objs[0].blended_core_2017:
            spec_objs = spec_objs.order_by('blended_core_2017')
        else:
            spec_objs = spec_objs.order_by('blended_core_2006')

        return spec_objs[0]

    try:

        if vm_data:
            spec_obj = SpecIntData.objects.filter(model=model_name)
            if not spec_obj:
                return "Error: No benchmark data for CPU: %s" % model_name, None

            return get_cpu_model(spec_obj), None

        else:
            return SpecIntData.objects.get(model=model_name, cores=num_cores), None

    except (ObjectDoesNotExist, AttributeError):

        model = findall(r'\d{4}\w?\s?', model_name)

        if model:

            model = model[0].strip()

            if cpu_clock:
                spec_objs = SpecIntData.objects.filter(model__contains=model, speed__contains=cpu_clock)
            else:
                spec_objs = SpecIntData.objects.filter(model__contains=model)

            if spec_objs:

                cpu_model = get_cpu_model(spec_objs) if vm_data else spec_objs[0]

                warning = '%s has been fuzzy matched with %s. Exact match not found' \
                          % (model_name, cpu_model)

                return cpu_model, warning

        return "Error: No benchmark data for CPU: %s" % model_name, None


def get_normalized_cores_used(norm_data, vm_data):

    cores = int(norm_data['num_cores'])

    if float(cores) == 0.0:
        return None, None
        #return 'Error : CPUCores value cannot be : 0', None

    cores_per_socket = cores / int(ceil(norm_data['cpu_packages']))
    if not norm_data['model_name']:
        return None, None

    cpu_model, warning = get_model_obj(vm_data, model_name=norm_data['model_name'], num_cores=cores_per_socket,
                                       cpu_clock=norm_data['cpu_clock'])

    if isinstance(cpu_model, str):
        return cpu_model, warning

    if norm_data['clock_util']:
        cores_used = float(cores) * (norm_data['clock_util'] / (float(cores) * cpu_model.speed))
    else:
        cores_used = float(cores) * (norm_data['cpu_util_pcnt'] / 100.0)

    normalized_core = cores_used * WL.normalise_cpu(cpu_model)

    return normalized_core, warning


def process_esx_data(data):

    esxdata = csv.reader(data.split('\n'))

    #row = esxdata.next()
    row = next(esxdata)

    #To Support Older and Current Profiler files

    #has_vm_data = True if 'VMName' in row else False
    if 'VMName' in row or 'VM_summary' in row:
        has_vm_data = True
    else:
        has_vm_data = False

    base_cols_dict = {"CPUType": {"ind": None},
                      "CPUMaxAvgGHz": {"ind": None},
                      "MemMaxAvgGB": {"ind": None},
                      "CPUCores": {"ind": None},
                      "CPUMaxAvgPcnt": {"ind": None},
                      "StorageUsedGB": {"ind": None},
                      "HostName": {"ind": None},
                      "CPUPackages": {"ind": None},
                      "DaysCollected": {"ind": None},
                      "StorageProvisionedGB": {"ind": None},
                      "MemoryGB": {"ind": None},
                      "HostCluster": {"ind": None}}

    if has_vm_data:
        base_cols_dict['VMName'] = {"ind": None}
        base_cols_dict['VMRunState'] = {"ind": None}

    # Getting index of columns'
    while 'HostName' not in row:
        #row = esxdata.next()
        row = next(esxdata)

    for ind, value in enumerate(row):

        if value.rstrip() in base_cols_dict:
            base_cols_dict[value.rstrip()]['ind'] = ind

    total_columns = ind + 1  # Total column in row

    cluster_dict = dict()

    base_dict = {'ram_size': 0,
                 'vcpus': 0,
                 'hdd_size': 0,
                 'cpu_clock': 0}

    sizing_basis = {'utilized': deepcopy(base_dict),
                    'provisioned': deepcopy(base_dict)}

    error_data = {'Error': '', 'Num_of_Errors': 0, 'Warnings': ''}

    # Checking the columns(CPUMaxAvgGHz, MemMaxAvgGB, CPUType, CPUCores, CPUMaxAvgPcnt)
    # and raising exception if any is not present.
    base_error = " %s column is not present in line 1. \n"

    for key, value in base_cols_dict.items():

        '''the reason for below condition being written in this way is to handle the case
        of mandatory columns coming under index 0'''

        if value['ind'] == None:
            error_data['Error'] += base_error % key
            error_data['Num_of_Errors'] += 1

    if error_data['Num_of_Errors'] > 0:
        return sizing_basis, error_data
        # raise Exception("Number of Errors %d \n Errors: %s" % (error_data['Num_of_Errors'], error_data['Error']))

    # initializing the variables
    num_of_row = 0

    # Reading the complete csv file's content from line 2 and computing
    for fields in esxdata:

        if num_of_row == 0 and fields == list():

            error_data['Error'] += 'Error : CSV format | Data is not available in file \n'
            error_data['Num_of_Errors'] = error_data['Num_of_Errors'] + 1
            return sizing_basis, error_data

        if total_columns != len(fields):

            if num_of_row == 0:
                error_data['Error'] += 'For host %s, at line %d, number of columns are not equal \n' % \
                                       (fields[int(base_cols_dict["HostName"]["ind"])], num_of_row + 2)
            continue

        hostname = fields[int(base_cols_dict["HostName"]["ind"])]
        clustername = fields[int(base_cols_dict["HostCluster"]["ind"])]

        if has_vm_data:
            vm_data = True if fields[int(base_cols_dict["VMName"]["ind"])] != 'N/A' else False
            vmname = fields[int(base_cols_dict["VMName"]["ind"])]
        else:
            vm_data = False

        if clustername in ['--', '']:
            clustername = 'Unassigned'

        if hostname in ['--', '', '""']:
            hostname = prevhostname
        else:
            prevhostname = hostname

        sizing_basis, num_of_row, error_data = \
            get_esx_result(fields, num_of_row, sizing_basis, error_data, base_cols_dict, hostname, vm_data)

        if not sizing_basis:
            continue

        if clustername not in cluster_dict:
            cluster_dict[clustername] = defaultdict(dict)

        if hostname not in cluster_dict[clustername]:
            cluster_dict[clustername][hostname] = defaultdict(dict)
            cluster_dict[clustername][hostname]['host'] = {'utilized': deepcopy(base_dict),
                    'provisioned': deepcopy(base_dict)}

            if has_vm_data:
                cluster_dict[clustername][hostname]['vm'] = {'utilized': deepcopy(base_dict),
                                                             'provisioned': deepcopy(base_dict)}

        if vm_data:
            # if vmname not in cluster_dict[clustername][hostname]['vm']:
            #     cluster_dict[clustername][hostname]['vm'][vmname] = deepcopy(sizing_basis)
            if 'vm' not in cluster_dict[clustername][hostname]:
                cluster_dict[clustername][hostname]['vm'] = deepcopy(sizing_basis)
            else:
                vm_sizing_basis = deepcopy(sizing_basis)
                for sizing_type in sizing_basis:
                    for key in sizing_basis[sizing_type]:
                        cluster_dict[clustername][hostname]['vm'][sizing_type][key] += vm_sizing_basis[sizing_type][key]
        else:
            cluster_dict[clustername][hostname]['host'] = deepcopy(sizing_basis)

    return cluster_dict, error_data


def get_esx_result(fields, num_of_row, sizing_basis, error_data, base_cols_dict, hostname, vm_data):

    data_error = 'For host %s, at line %d, %s Column has no value\n'
    data_warning = 'For host %s, at line %d, historical data is less than 30 days.\n'

    data_cols_dict = {"CPUType": "",
                      "CPUMaxAvgGHz": "",
                      "MemMaxAvgGB": "",
                      "CPUCores": "",
                      "CPUMaxAvgPcnt": "",
                      "StorageUsedGB": "",
                      "HostName": "",
                      "CPUPackages": "",
                      "DaysCollected": "",
                      "StorageProvisionedGB": "",
                      "MemoryGB": ""
                      }

    if vm_data:
        data_cols_dict['VMName'] = ""
        data_cols_dict['VMRunState'] = ""

    for col_name, col_ind in base_cols_dict.items():

        flag = False

        try:
            if col_name not in ['HostName', 'HostCluster', 'VMName']:

                if any(c.isalpha() for c in fields[col_ind['ind']]):
                    data_cols_dict[col_name] = fields[col_ind['ind']]
                else:
                    if '%' not in fields[int(col_ind['ind'])]:
                        data_cols_dict[col_name] = float(fields[col_ind['ind']])
                    else:
                        data_cols_dict[col_name] = float(fields[col_ind['ind']][:-1])

                if col_name == 'DaysCollected':

                    if vm_data and fields[int(base_cols_dict["VMRunState"]["ind"])] == 'poweredOff':
                        continue

                    if vm_data and fields[int(base_cols_dict["VMRunState"]["ind"])] == 'suspended':
                        continue

                    elif int(fields[col_ind['ind']]) < 30:
                        error_data['Warnings'] += data_warning % (hostname, num_of_row + 2)
            else:

                data_cols_dict[col_name] = fields[col_ind['ind']]

        except (AttributeError, KeyError, ValueError):

            if col_name in ['CPUMaxAvgGHz', 'CPUPackages']:
                continue

            if vm_data and (fields[int(base_cols_dict["VMRunState"]["ind"])] == 'poweredOff' or
                            fields[int(base_cols_dict["VMRunState"]["ind"])] == 'suspended' ) and col_name in\
                    ['MemMaxAvgGB', 'CPUMaxAvgPcnt', 'CPUMaxAvgGHz', 'DaysCollected']:
                continue

            error_data['Error'] += data_error % (hostname, num_of_row + 2, col_name)
            error_data['Num_of_Errors'] += 1
            flag = True

        if flag:
            break

    cpu_clock = findall(r'\d{1,2}\.\d{1,2}GHz\s?', data_cols_dict['CPUType'])
    cpu_clock = float(cpu_clock[0].strip()[:-3]) if cpu_clock else None

    '''it is assumed that for M5 nodes the HX_Profiler produces CPUType and CPUTypeLong fields
    similarly as Intel(R) Xeon(R) Gold 6126 CPU @ 2.60GHz. hence the below regex uses this property
    to extract the model 'Intel 6126' from the above string'''
    m5_regex = None
    for element in ["Gold", "Silver", "Platinum", "Bronze"]:
        if element in data_cols_dict['CPUType'] and 'Intel(R) Xeon(R)' in data_cols_dict['CPUType']:
            m5_regex = compile("%s(.*)(?=CPU)" % element, IGNORECASE)
            break
    if m5_regex:
        cpu_model = 'Intel ' + element + ' ' + findall(m5_regex, data_cols_dict['CPUType'])[0].strip()
        data_cols_dict['CPUType'] = cpu_model

    amd_regex = None
    if 'Quad-Core AMD Opteron' in data_cols_dict['CPUType']:
        amd_regex = compile("%s(.*)" % 'Processor', IGNORECASE)

    if amd_regex:
        cpu_model = 'AMD ' + findall(amd_regex, data_cols_dict['CPUType'])[0].replace(" ", "")
        data_cols_dict['CPUType'] = cpu_model

    for sizing_type in sizing_basis:

        if vm_data and (data_cols_dict['VMRunState'] == 'poweredOff' or
                        data_cols_dict['VMRunState'] == 'suspended') and sizing_type == 'utilized':
            sizing_basis[sizing_type] = {'ram_size': 0, 'vcpus': 0, 'hdd_size': 0}
            continue

        normalisation_data = {
            'model_name': data_cols_dict['CPUType'],
            'num_cores': data_cols_dict['CPUCores'],
            'cpu_packages': 2 if not data_cols_dict['CPUPackages'] else data_cols_dict['CPUPackages'],
            'cpu_clock': cpu_clock
        }

        if sizing_type == 'provisioned':

            normalisation_data['cpu_util_pcnt'] = 100.0
            normalisation_data['clock_util'] = 0.0

        else:

            normalisation_data['cpu_util_pcnt'] = data_cols_dict['CPUMaxAvgPcnt']
            normalisation_data['clock_util'] = \
                0.0 if not data_cols_dict['CPUMaxAvgGHz'] else data_cols_dict['CPUMaxAvgGHz']

        normalized_result, warning = get_normalized_cores_used(normalisation_data, vm_data)
        if not normalisation_data:
            print(num_of_row)
            return None, None, None

        if isinstance(normalized_result, float):
            sizing_basis[sizing_type]['vcpus'] = normalized_result

            if sizing_type == 'provisioned':
                ram_column = 'MemoryGB'
                hdd_column = 'StorageProvisionedGB'
            else:
                ram_column = 'MemMaxAvgGB'
                hdd_column = 'StorageUsedGB'

            sizing_basis[sizing_type]['ram_size'] = data_cols_dict[ram_column]
            sizing_basis[sizing_type]['hdd_size'] = data_cols_dict[hdd_column]

        elif isinstance(normalized_result, str):
            error_data['Error'] += 'For host %s, at line %d, ' % \
                                   (hostname, num_of_row + 2) + normalized_result + '\n'
            error_data['Num_of_Errors'] += 1
            num_of_row += 1
            break

    if warning:
        error_data['Warnings'] += warning

    for sizing_type, data_dict in sizing_basis.items():
        data_dict['cpu_clock'] = data_dict['vcpus'] * SpecIntData.objects.get(is_base_model=True).speed

    num_of_row += 1

    return sizing_basis, num_of_row, error_data
