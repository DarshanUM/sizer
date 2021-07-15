import xlrd
import copy
from re import findall, compile, IGNORECASE
from django.core.exceptions import ObjectDoesNotExist

from hyperconverged.models import SpecIntData
from base_sizer.solver.wl import WL

HOST = "Host"
CLUSTER = "Cluster"

# CPU data
MODEL = "CPU Model"
SOCKETS = "# CPU"
CORES = "# Cores"
CPU_USAGE = "CPU usage %"

# RAM data
RAM_SIZE = "# Memory"
RAM_USAGE = "Memory usage %"

# HDD Data
CAPACITY = "Provisioned MB"
UTILISED = "In Use MB"
CAPACITY_NEW = "Provisioned MiB"
UTILISED_NEW = "In Use MiB"

# Process Maker Constants
AMD = "AMD"
INTEL = "Intel"

# CPU base constants
CPU_UTIL = "cpu_util"
CORE_BASE = "core_base"
CPU_DETAILS = "cpu_details"
CPU_SOCKET = "cpu_socket"


class RVToolsCalculator(object):

    def __init__(self, file_obj):

        self.mandatory_sheets = None

        self.base_exception = list()
        self.error_message = list()
        self.non_extract = list()

        try:
            self.xl_obj = xlrd.open_workbook(file_contents=file_obj.read())
        except:
            error = "File upload failed due to bad metadata"
            self.base_exception.append(error)

        self.host_headers = [CLUSTER, HOST, MODEL, SOCKETS, CORES, CPU_USAGE, RAM_SIZE, RAM_USAGE]
        self.disk_headers = [CLUSTER, HOST, CAPACITY, UTILISED]
        self.disk_headers_new = [CLUSTER, HOST, CAPACITY_NEW, UTILISED_NEW]

        self.ref_clock = float(SpecIntData.objects.get(is_base_model=True).speed)

        base_dict = {'ram_size': 0,
                     'vcpus': 0,
                     'cpu_clock': 0,
                     'hdd_size': 0}
        self.host_struct = {'utilized': copy.deepcopy(base_dict),
                            'provisioned': copy.deepcopy(base_dict)}

        self.cluster_struct = dict()

    def construct_response(self):

        if self.base_exception:
            return dict(), self.base_exception

        self.validate_excel()
        if self.base_exception:
            return dict(), self.base_exception

        self.cpu_ram_capacity_details()

        if self.non_extract:
            self.error_message.append('Following CPUs are not available: %s' % list(set(self.non_extract)))
            return dict(), self.error_message

        self.storage_capacity_details()

        return self.cluster_struct, self.error_message

    def validate_excel(self):

        xl_sheets = [sheet_name for sheet_name in self.xl_obj.sheet_names()]

        old_rv_sheets = ["tabvInfo", "tabvHost"]
        new_rv_sheets = ["vInfo", "vHost"]

        for sheet_list in (old_rv_sheets, new_rv_sheets):
            if sheet_list[0] in xl_sheets and sheet_list[1] in xl_sheets:
                self.mandatory_sheets = sheet_list
                break

        if not self.mandatory_sheets:
            error = "Mandatory Sheets %s or %s are missing from workbook. Kindly update RVTools to the latest version "\
                    "and try again" % (old_rv_sheets, new_rv_sheets)
            self.base_exception.append(error)
        else:
            for sheet_name in self.mandatory_sheets:

                worksheet = self.xl_obj.sheet_by_name(sheet_name)
                sheet_headers = [str(cell.value) for cell in worksheet.row(0)]
                if set([CAPACITY_NEW, UTILISED_NEW]).issubset(set(sheet_headers)):
                    self.disk_headers = self.disk_headers_new
                
                if 'Host' in sheet_name:
                    req_headers = self.host_headers
                else:
                    req_headers = self.disk_headers

                missing_headers = set(req_headers) - set(sheet_headers)
                if missing_headers:
                    error = "%s columns couldn't be found in %s sheet. Kindly update RVTools to the latest version and"\
                            " try again" % (list(missing_headers), sheet_name)
                    self.base_exception.append(error)

    @staticmethod
    def get_header_indices(worksheet, header_list):

        sheet_header = [str(cell.value) for cell in worksheet.row(0)]
        index_dict = dict()

        for header in header_list:
            index_dict[header] = sheet_header.index(header)
        return index_dict

    def cpu_ram_capacity_details(self):

        host_sheet = self.mandatory_sheets[1]
        worksheet = self.xl_obj.sheet_by_name(host_sheet)
        self.host_headers = self.get_header_indices(worksheet, self.host_headers)

        cpu_key_lst = [CPU_UTIL, CORE_BASE, CPU_DETAILS, CPU_SOCKET]

        for row in range(1, worksheet.nrows):

            cluster = worksheet.cell(row, self.host_headers[CLUSTER]).value

            if not cluster:
                cluster = 'Unassigned'

            if cluster not in self.cluster_struct:
                self.cluster_struct[cluster] = dict()

            cluster_dict = self.cluster_struct[cluster]

            host = worksheet.cell(row, self.host_headers[HOST]).value

            if host not in cluster_dict:
                cluster_dict[host] = copy.deepcopy(self.host_struct)

            for sizing_type, sizing_values in cluster_dict[host].items():

                if sizing_type == 'provisioned':
                    ram_util = 1.0
                else:
                    ram_util = worksheet.cell(row, self.host_headers[RAM_USAGE]).value / 100.0

                sizing_values['ram_size'] = worksheet.cell(row, self.host_headers[RAM_SIZE]).value * ram_util / 1024.0

            # CPU Part
            cpu_util = worksheet.cell(row, self.host_headers[CPU_USAGE]).value
            core_base = worksheet.cell(row, self.host_headers[CORES]).value
            cpu_details = worksheet.cell(row, self.host_headers[MODEL]).value
            cpu_socket = worksheet.cell(row, self.host_headers[SOCKETS]).value

            # Construct CPU details
            cpu_val_lst = [cpu_util, core_base, cpu_details, cpu_socket]
            tmp = dict(zip(cpu_key_lst, cpu_val_lst))
            self.calculate_core(tmp, cluster_dict[host])
            if self.non_extract:
                return

    def calculate_core(self, cpu_details, host_dict):

        #cpu_model = cpu_details[CPU_DETAILS].encode("UTF8")
        cpu_model = cpu_details[CPU_DETAILS]
        sockets = cpu_details[CPU_SOCKET]
        core_per_socket = cpu_details[CORE_BASE] / sockets
        cpu_model = self.extract_cpu_model(cpu_model)

        try:
            cpu_obj = SpecIntData.objects.get(model=cpu_model, cores=int(core_per_socket))
        except ObjectDoesNotExist:
            self.non_extract.append(cpu_details[CPU_DETAILS])
            return

        for sizing_type, sizing_values in host_dict.items():

            if sizing_type == 'provisioned':
                cpu_util = 100.0
            else:
                cpu_util = cpu_details[CPU_UTIL]

            cpu_normalised = (cpu_util / 100.0) * core_per_socket * sockets * WL.normalise_cpu(cpu_obj)
            sizing_values['vcpus'] = cpu_normalised
            sizing_values['cpu_clock'] = cpu_normalised * self.ref_clock

    def extract_cpu_model(self, cpu_details):

        if AMD in cpu_details:

            company = AMD
            amd_regex = "(?<=Processor)(.*)"
            cpu_model = findall(amd_regex, cpu_details)

        else:

            company = INTEL
            intel_regex = "(?<=CPU)(.*)(?=@)"
            m5_regex = None

            for element in ["Gold", "Silver", "Platinum", "Bronze"]:
                if element in cpu_details:
                    m5_regex = compile("%s(.*)(?=CPU)" % element, IGNORECASE)
                    break

            if m5_regex:
                cpu_model = findall(m5_regex, cpu_details)
            else:
                cpu_model = findall(intel_regex, cpu_details)

        if cpu_model:

            if company == AMD:

                cpu_model = cpu_model[0].replace(" ", "")
                return company + " " + cpu_model

            else:

                # requires refactoring
                base = cpu_model[0].strip()

                # Removing spaces after "-". this is for cases such as 'E5- 2630'
                if "- " in base:
                    base = base.replace("- ", "-")

                if " " in base:

                    tmp = base.split(" ")

                    try:
                        # this is for cases such as 'E5-2620 0'
                        int(tmp[1][0])
                        cpu_model = tmp[0]
                    except ValueError:
                        # this is for cases such as 'E5-2620 v2'
                        cpu_model = tmp[0] + " " + tmp[1]

                else:

                    cpu_model = base

                if m5_regex:
                    return company + " " + element + " " + cpu_model
                else:
                    return company + " " + cpu_model

        else:

            self.non_extract.append(cpu_details)
            return False

    def storage_capacity_details(self):

        partition_sheet = self.mandatory_sheets[0]
        worksheet = self.xl_obj.sheet_by_name(partition_sheet)
        self.disk_headers = self.get_header_indices(worksheet, self.disk_headers)

        for row in range(1, worksheet.nrows):

            cluster = worksheet.cell(row, self.disk_headers[CLUSTER]).value
            if not cluster:
                cluster = 'Unassigned'

            host = worksheet.cell(row, self.disk_headers[HOST]).value

            if cluster in self.cluster_struct and host in self.cluster_struct[cluster]:

                for sizing_type, sizing_values in self.cluster_struct[cluster][host].items():

                    if sizing_type == 'provisioned':
                        sizing_values['hdd_size'] += worksheet.cell(row, self.disk_headers[CAPACITY] if (CAPACITY in self.disk_headers) else self.disk_headers[CAPACITY_NEW]).value / 1024.0
                    else:
                        sizing_values['hdd_size'] += worksheet.cell(row, self.disk_headers[UTILISED] if (UTILISED in self.disk_headers) else self.disk_headers[UTILISED_NEW]).value / 1024.0
