import xlrd
import copy
from re import findall, compile, IGNORECASE
from django.core.exceptions import ObjectDoesNotExist

from hyperconverged.models import SpecIntData, Scenario
from base_sizer.solver.wl import WL

NAME = "Workload Name"
DBTYPE = "Database Type"
DBSUBTYPE = "Database SubType"
COUNT = "Number of Databases"
vCPUs = "vCPUs"
CPU_OPRATIO = "vCPU Overprovisioning Ratio"
RAM_SIZE = "RAM"
RAM_SIZE_UNIT = "RAM Size Unit"
DB_SIZE = "Database Size"
DB_SIZE_UNIT = "Database Size Unit"
IOPS_OR_MBPS = "IOPS/MBPS"
DB_OVERHEAD = "Database Overhead (%)"
CLUSTER_TYPE = "Cluster Type"
RF = "Data Replication Factor"
FT = "Performance Headroom (# of nodes)"
COMPRESSION_FACTOR = "Compression Savings (%)"
DEDUPE_FACTOR = "Deduplication Savings (%)"
ENABLE_REPLICATION = "Enable Remote Replication?"
REPLICATION_SITE = "Primary workload placement"
REPLICATION_AMT = "Site failure protection (% workload)"

suffixes = {1: "st", 2: "nd", 3: "rd"}


class BulkWLCalculator(object):

    def __init__(self, file_obj, scenario_id):

        self.scenario_id = scenario_id
        self.xl_obj = xlrd.open_workbook(file_contents=file_obj.read())

        self.mandatory_sheets = list()

        self.base_exception = list()
        self.error_message = list()
        self.non_extract = list()

        self.host_headers = [NAME, DBTYPE, DBSUBTYPE, COUNT, vCPUs, CPU_OPRATIO, RAM_SIZE, RAM_SIZE_UNIT, DB_SIZE,
                             DB_SIZE_UNIT, IOPS_OR_MBPS, DB_OVERHEAD, RF, FT, COMPRESSION_FACTOR, DEDUPE_FACTOR]

        self.ref_clock = float(SpecIntData.objects.get(is_base_model=True).speed)

        self.workload_list = list()

    def construct_response(self):

        self.validate_excel()
        if self.base_exception:
            return list(), self.base_exception

        self.create_workloadlist()
        if self.base_exception:
            return self.workload_list, self.base_exception

        return self.workload_list, self.error_message

    def validate_excel(self):

        xl_sheets = [sheet_name for sheet_name in self.xl_obj.sheet_names()]

        wl_sheets = ["Input"]

        for sheet_list in wl_sheets:
            if sheet_list in xl_sheets:
                self.mandatory_sheets.append(sheet_list)
                break

        if not self.mandatory_sheets:
            error = "Mandatory Sheets %s is missing from workbook" % (wl_sheets)
            self.base_exception.append(error)
            return
        else:
            for sheet_name in self.mandatory_sheets:

                worksheet = self.xl_obj.sheet_by_name(sheet_name)
                sheet_headers = [str(cell.value) for cell in worksheet.row(0)]

                missing_headers = set(self.host_headers) - set(sheet_headers)
                if missing_headers:
                    error = "Unable to find %s columns in %s sheet" % (list(missing_headers), sheet_name)
                    self.base_exception.append(error)
                    return

        #Get the list of workloads in Scenarios
        try:
            scenario = Scenario.objects.get(id=self.scenario_id)
        except Scenario.DoesNotExist:
            error = "Invalid Scenario ID"
            self.base_exception.append(error)
            return

        scenario_wl_names = list()
        if 'wl_list' in scenario.workload_json:
            scenario_wl_names = [workload['wl_name'] for workload in scenario.workload_json['wl_list']]

        workload_sheet = self.mandatory_sheets[0]
        worksheet = self.xl_obj.sheet_by_name(workload_sheet)
        self.host_headers = self.get_header_indices(worksheet, self.host_headers)
        bulk_wl_names = list()

        for row in range(1, worksheet.nrows):

            wl_name = worksheet.cell(row, self.host_headers[NAME]).value

            bulk_wl_names.append(wl_name)

        if not len(bulk_wl_names):
            error = "The %s sheet should have minimum of one workload." % (workload_sheet)
            self.base_exception.append(error)
            return

        if len(bulk_wl_names) != len(set(bulk_wl_names)):
            dup_wl = list(set([name for name in bulk_wl_names if bulk_wl_names.count(name) > 1]))
            error = "The %s sheet has duplicate workload names: %s" % (workload_sheet, dup_wl)
            self.base_exception.append(error)
            #return

        if len(set(scenario_wl_names).intersection(bulk_wl_names)):
            dup_wl = list(set(scenario_wl_names).intersection(bulk_wl_names))
            error = "The %s sheet has duplicate workload names which is already created in Scenario: %s" % (workload_sheet, dup_wl)
            self.base_exception.append(error)
            return

    @staticmethod
    def get_header_indices(worksheet, header_list):

        sheet_header = [str(cell.value) for cell in worksheet.row(0)]
        index_dict = dict()

        for header in header_list:
            index_dict[header] = sheet_header.index(header)
        return index_dict

    def create_workloadlist(self):

        input_sheet = self.mandatory_sheets[0]
        worksheet = self.xl_obj.sheet_by_name(input_sheet)
        self.host_headers = self.get_header_indices(worksheet, self.host_headers)

        for row in range(1, worksheet.nrows):

            wl_name = worksheet.cell(row, self.host_headers[NAME]).value
            wl_type = worksheet.cell(row, self.host_headers[DBTYPE]).value
            db_type = worksheet.cell(row, self.host_headers[DBSUBTYPE]).value
            num_db_instances = worksheet.cell(row, self.host_headers[COUNT]).value
            vcpus_per_db = worksheet.cell(row, self.host_headers[vCPUs]).value
            vcpus_per_core = worksheet.cell(row, self.host_headers[CPU_OPRATIO]).value
            ram_per_db = worksheet.cell(row, self.host_headers[RAM_SIZE]).value
            ram_per_db_unit = worksheet.cell(row, self.host_headers[RAM_SIZE_UNIT]).value
            db_size = worksheet.cell(row, self.host_headers[DB_SIZE]).value
            db_size_unit = worksheet.cell(row, self.host_headers[DB_SIZE_UNIT]).value
            avg_iops_per_db = worksheet.cell(row, self.host_headers[IOPS_OR_MBPS]).value
            metadata_size = worksheet.cell(row, self.host_headers[DB_OVERHEAD]).value
            #cluster_type = worksheet.cell(row, self.host_headers[CLUSTER_TYPE]).value
            rep_factor = worksheet.cell(row, self.host_headers[RF]).value
            fault_tolerance = worksheet.cell(row, self.host_headers[FT]).value
            compression_factor = worksheet.cell(row, self.host_headers[COMPRESSION_FACTOR]).value
            dedupe_factor = worksheet.cell(row, self.host_headers[DEDUPE_FACTOR]).value
            # replication_enabled = worksheet.cell(row, self.host_headers[ENABLE_REPLICATION]).value
            # site = worksheet.cell(row, self.host_headers[REPLICATION_SITE]).value
            # replication_amt = worksheet.cell(row, self.host_headers[REPLICATION_AMT]).value

            base_dict = {'wl_name': wl_name,
                         'wl_type': wl_type,
                         'db_type': db_type,
                         'num_db_instances': num_db_instances,
                         'profile_type': 'Custom',
                         'vcpus_per_db': vcpus_per_db,
                         'vcpus_per_core': vcpus_per_core,
                         'ram_per_db': ram_per_db,
                         'ram_per_db_unit': ram_per_db_unit,
                         'db_size': db_size,
                         'db_size_unit': db_size_unit,
                         'metadata_size': metadata_size,
                         'fault_tolerance': fault_tolerance,
                         'compression_factor': compression_factor,
                         'dedupe_factor': dedupe_factor
                         }

            if db_type == 'OLTP':
                base_dict['avg_iops_per_db'] = avg_iops_per_db
            else:
                base_dict['avg_mbps_per_db'] = avg_iops_per_db

            if rep_factor == 'RF 2':
                base_dict['replication_factor'] = 2
            else:
                base_dict['replication_factor'] = 3

            base_dict['cluster_type'] = 'normal'
            base_dict['remote_replication_enabled'] = False
            base_dict['remote'] = False
            base_dict['replication_amt'] = 100

            blankEntry = True if '' in base_dict.values() else False

            if blankEntry:
                if 0 < row+1 <= 3:
                    suffix = suffixes[row+1]
                else:
                    suffix = 'th'
                error = "The %s%s row has incomplete entries." % (row+1, suffix)
                self.base_exception.append(error)
            else:
                self.workload_list.append(base_dict)
