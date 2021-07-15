import xlrd
from math import ceil
from hyperconverged.models import SpecIntData


class ExchangeWorkload(object):

    def __init__(self, file_object):
        self.file_object = file_object
        self.errors = ''
        self.warnings = ''
        self.year = None
        self.excel_base_model = "Intel E5-2650"

    def validation_fields_check(self, sheet):
        """
        this method verifies if all the validation checks that the excel does are False i.e.
        They should be False. the functions returns error string if any of them is True
        """
        # Below value indicates column I in excel
        column_no = 8
        error = ''

        if self.year == '2019':
            # each element in below indicates range of cell addresses i.e. 154, 164 indicates all cells from 155 to 165.
            # Cell addresses in this module start at 0. hence we are referring to I155, I156 etc. here
            row_list = [(180, 180, 'Too Many DAG Members Validation Check'),
                        (182, 182, 'DB Copy Count Validation Check'),
                        (184, 184, 'Calculated Max DB Size Not Zero Check'),
                        (185, 185, 'Mailbox Size Limit Not Zero Check'),
                        (187, 187, 'Disk Count Validation Check'),
                        (188, 188, 'Invalid Active/Active DAG'),
                        (193, 193, 'Calculator Validation Check')]
        else:
            row_list = [(155, 157, 'Too Many DAG Members Validation Check & DB Copy Count Validation Check & '
                                   'Mailbox Size Limit Not Zero Check'),
                        (160, 163, 'Calculator Validation Check & Calculated Max DB Size Not Zero Check & '
                                   'Disk Count Validation Check & Invalid Active/Active DAG'),
                        (181, 188, 'JBOD Validation checks section')]

        for item in row_list:

            for i in range(item[0], item[1]+1):

                if sheet.cell(i, column_no).value:
                    error += "\"%s\" in \"%s\" sheet has failed.\n" % (sheet.cell(i, column_no-1).value, sheet.name)

        self.errors = error

    def construct_cell_map(self):
        """
        this method creates a dictionary which is used to store data, position of the cell
        i.e. the row and column number. it also includes a data_type which is later used for validation
        """

        # Below tuple is indicating (name of key in dictionary, row, column, section name in excel sheet, row header,
        # column header). Only the first three keys will be used. Rest are for reference
        row_col_tuple_list = [("cycles",
                               {'2019': (204, 4), '2013|2016': (200, 4)},
                               'Megacycle calculations',
                               ('Active Mailbox CPU Requirements (Mcycles) / Pri-DC Server', 'Double Failure')),

                              ("num_servers_per_dag",
                               {'2019': (227, 2), '2013|2016': (228, 2)},
                               'Environment Configuration',
                               ('Total Number of Servers / DAG', '/ Primary Datacentre')),

                              ("num_dag",
                               {'2019': (97, 2), '2013|2016': (95, 2)},
                               'Server Calculations',
                               ('Total DAGs in the Environment', 'Value')),

                              ("read_percentage",
                               {'2019': (285, 2), '2013|2016': (284, 2)},
                               'Host IO and Throughput Requirements',
                               ('Database Read I/O Percentage', '/ Database')),

                              ("iops_server_DB",
                               {'2019': (283, 3), '2013|2016': (282, 3)},
                               'Host IO and Throughput Requirements',
                               ('Total Database Required IOPS', '/ Server')),

                              ("iops_required_Log",
                               {'2019': (284, 3), '2013|2016': (283, 3)},
                               'Host IO and Throughput Requirements',
                               ('Total Log Required IOPS', '/ Server')),

                              ("maintenance_throughput",
                               {'2019': (286, 3), '2013|2016': (285, 3)},
                               'Host IO and Throughput Requirements',
                               ('Background Database Maintenance Throughput Requirements', '/ Server')),

                              ("ram_per_server",
                               {'2019': (143, 2), '2013|2016': (141, 2)},
                               'Memory Calculations (Primary Datacenter)',
                               ('Calculated Amount of Server RAM (Total)', 'Value')),

                              ("min_GC_cores",
                               {'2019': (220, 2), '2013|2016': (216, 2)},
                               'Processor Core Ratio Requirements',
                               ('Recommended Minimum Number of Global Catalog Cores', '/ Primary Datacentre')),

                              ("transport_DB_space",
                               {'2019': (273, 3), '2013|2016': (274, 3)},
                               'Disk Space Requirements',
                               ('Transport Database Space Required', '/ Server')),

                              ("DB_space",
                               {'2019': (274, 3), '2013|2016': (275, 3)},
                               'Disk Space Requirements',
                               ('Database Space Required', '/ Server')),

                              ("log_space",
                               {'2019': (275, 3), '2013|2016': (276, 3)},
                               'Disk Space Requirements',
                               ('Log Space Required', '/ Server'))
                              ]

        if self.year == '2019':

            # This is spec rate for N #cores required by system
            row_col_tuple_list.append(("spec_2017",
                                       {'2019': (136, 2)},
                                       'Processor Configuration',
                                       ('Mailbox Servers', 'Server SPECint2017 Rate Value')))

        map_data_dict = dict()
        for item in row_col_tuple_list:

            map_data_dict[item[0]] = \
                {"position": {
                    "row": item[1][self.year][0],
                    "col": item[1][self.year][1]
                },
                    "data_type": float,
                    "data": None}

        return map_data_dict

    @staticmethod
    def result_correction(required_data_dict):
        """
        this function ensures that for very small workloads, number of cores and ram etc that sometimes
        round off to zero are not sent to UI as it is
        """
        min_required_values = {"ram_size": 2,
                               "hdd_size": 10,
                               "vcpus": 1,
                               "EXCHANGE_16KB": 10,
                               "EXCHANGE_32KB": 10,
                               "EXCHANGE_64KB": 10}
        for key in min_required_values:
            if not required_data_dict[key]:
                required_data_dict[key] = min_required_values[key]

    def required_calculations(self, map_data_dict):
        """
        this method performs the manual calculations using the data fetched from the excel file.
        the calculations are as follows:
        No. of servers = total no. of servers/DAG * no. DAGs
        Memory = memory per server * no. servers
        Capacity = (transport DB space + log space + DB space) * no. servers
        Cores = total MHz/2000 (the sheet assumes that E5-2650 as the base core which has 2000MHz per core)
        The above value is multiplied by (SpecInt of 2650/ SpecInt of Sizer base core).
        The maintenance throughput is normalised to 32Kb/s IO/s profile
        """
        required_data_dict = dict()
        num_servers = int(map_data_dict["num_servers_per_dag"]["data"]) * int(map_data_dict["num_dag"]["data"])

        required_data_dict["ram_size"] = int(ceil(map_data_dict["ram_per_server"]["data"]))

        required_data_dict["EXCHANGE_16KB"] = int(map_data_dict["iops_server_DB"]["data"])
        required_data_dict["EXCHANGE_32KB"] = int(map_data_dict["iops_required_Log"]["data"])
        required_data_dict["EXCHANGE_64KB"] = int(map_data_dict["maintenance_throughput"]["data"] / 0.064)

        required_data_dict["hdd_size"] = \
            int(ceil(map_data_dict["transport_DB_space"]["data"] + map_data_dict["DB_space"]["data"] +
                     map_data_dict["log_space"]["data"]))

        required_data_dict["min_GC_cores"] = int(map_data_dict["min_GC_cores"]["data"])

        required_data_dict["vcpus_per_core"] = 1

        if self.year == '2019':

            # 2019 excel uses SpecINT vale for N #cores required by system
            required_data_dict["vcpus"] = int(ceil(map_data_dict["spec_2017"]["data"] /
                                                   SpecIntData.objects.get(is_base_model=True).blended_core_2017))

        else:

            total_cycles = int(ceil(map_data_dict["cycles"]["data"] * num_servers))

            '''
            the excel sheet assumes that E5-2650 is the base cpu. hence no. of E5-2650 cores is total
            cycles/cycles_per_core ie.2000
            '''
            excel_base_cores = int(ceil(total_cycles / 2000.0))

            required_data_dict["vcpus"] = \
                int(ceil(excel_base_cores * (SpecIntData.objects.get(model=self.excel_base_model).blended_core_2006 /
                                             SpecIntData.objects.get(is_base_model=True).blended_core_2006)))

        # the below list fields were calculated for per server basis. hence the multiplication
        for key in ["EXCHANGE_16KB", "EXCHANGE_32KB", "EXCHANGE_64KB", "hdd_size", "ram_size"]:
            required_data_dict[key] *= num_servers

        self.result_correction(required_data_dict)
        return required_data_dict, None

    def handle_fallback_case(self, key, map_data_dict, role_req_sheet):
        """
        this method handles the CPU cycles fallback condition. when double failure is not of type float, we check
        for single failure and normal runtime columns. we use the whichever value comes first and is valid
        :param key:
        :param map_data_dict:
        :param role_req_sheet:
        :return:
        """
        row = map_data_dict[key]["position"]["row"]
        col = map_data_dict[key]["position"]["col"]
        '''
        the range below spans to 2 columns in the left direction and checks for values. if both these columns also
        are invalid then error message is produced.
        '''
        for difference in range(1, 3):
            col -= 1
            value_to_check = role_req_sheet.cell(row, col).value
            if value_to_check and value_to_check != '--':
                map_data_dict[key]["data"] = value_to_check
                return
        self.errors += "the field %s in sheet %s has invalid data.\n" % (role_req_sheet.cell(row, col-1).value,
                                                                         role_req_sheet.name)

    def get_cell_data(self, map_data_dict, role_req_sheet, input_sheet):

        for key in map_data_dict:

            if key in ['num_cores_per_server', 'spec_2017']:
                sheet = input_sheet
            else:
                sheet = role_req_sheet

            value = sheet.cell(map_data_dict[key]["position"]["row"], map_data_dict[key]["position"]["col"]).value

            if type(value) == map_data_dict[key]["data_type"] and value:

                map_data_dict[key]["data"] = value

                if key == "read_percentage":

                    if value > 0.66:
                        self.warnings += "Database read IO is greater than 66%\n"
                    elif value < 0.5:
                        self.errors += "Database read IO is less than 50%\n"
                    else:
                        continue

            elif key in ["cycles"]:

                # the below function is to handle fallback case that is required presently for cpu cycles only.
                self.handle_fallback_case(key, map_data_dict, role_req_sheet)

            elif key in ["min_GC_cores"]:

                self.errors += "GC Cores field is not currently populated. " \
                               "Please apply a SPECint value to cell D130 in the input parameters, " \
                               "and click on Automatically Calculate DAG Solution. " \
                               "SPECint values can be found at Spec.org\n"

            else:

                error_row = map_data_dict[key]["position"]["row"]

                for i in range(1, 10):

                    error_col = map_data_dict[key]["position"]["col"] - i
                    value_to_check = role_req_sheet.cell(error_row, error_col).value

                    if type(value_to_check) == unicode and value_to_check != '--':
                        break

                self.errors += "the field %s in sheet %s has invalid data.\n" % (value_to_check, role_req_sheet.name)

    def construct_response(self):
        """
        this method creates a excel workbook and is kind of the main function of this file.
        it opens up the Role Requirements sheet and collects values from the excel sheet into map_data_dict.
        it performs data_validation check using the data_type field. if incompatible it send an error string
        which is then sent to final_calculations function.
        """
        exchange = xlrd.open_workbook(file_contents=self.file_object.read())

        role_req_sheet = exchange.sheet_by_name('Role Requirements')
        input_sheet = exchange.sheet_by_name('Input')

        self.year = int(input_sheet.cell(21, 2).value)

        if self.year not in [2013, 2016, 2019]:
            self.errors = "%s's Exchange calculator file isn't supported." % self.year
        elif self.year in [2013, 2016]:
            self.year = '2013|2016'
        else:
            self.year = '2019'

        self.validation_fields_check(role_req_sheet)

        if self.errors:
            return {"response": dict(),
                    "errors": self.errors,
                    "warnings": self.warnings}

        map_data_dict = self.construct_cell_map()

        self.get_cell_data(map_data_dict, role_req_sheet, input_sheet)

        if self.errors:
            return {"response": dict(),
                    "errors": self.errors,
                    "warnings": self.warnings}

        result, self.errors = self.required_calculations(map_data_dict)

        return {"response": result,
                "errors": self.errors,
                "warnings": self.warnings}
