import xlrd
import copy
from re import findall, compile, IGNORECASE
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response

from .ccw_request_template import CREATE_ESTIMATE_PAYLOAD


from hyperconverged.models import CCWData
#from base_sizer.solver.wl import WL

ITEM_ID = "Part Number"
ITEM_QUANTITY = "Quantity"

PARENT_ID = "ParentID"
PARENT_NAME = "ParentName"
WORKLOADS_LIST = "WorkloadsList"


class EstimatePayload(object):

    def __init__(self, file_path, scenario_name, selected_estimate, default_price_list):

        self.xl_obj = xlrd.open_workbook(file_path)

        self.mandatory_sheets = list()

        self.base_exception = list()
        self.error_message = list()
        self.non_extract = list()

        self.host_headers = [ITEM_ID, ITEM_QUANTITY, PARENT_ID, PARENT_NAME, WORKLOADS_LIST]

        self.create_payload = CREATE_ESTIMATE_PAYLOAD
        self.estimate_name = scenario_name + "_Sizer_Upload"
        self.estimate_id = selected_estimate

        self.price_list = default_price_list

    def construct_response(self):

        self.validate_excel()
        if self.base_exception:
            return list(), self.base_exception

        self.create_payload_request()
        if self.base_exception:
            return self.create_payload, self.base_exception

        return self.create_payload, self.error_message

    def validate_excel(self):

        xl_sheets = [sheet_name for sheet_name in self.xl_obj.sheet_names()]

        wl_sheets = ["BOM for Lowest_Cost", "BOM for All-Flash", "BOM for All NVMe", "BOM for Fixed_Config"]

        for sheet_list in wl_sheets:
            if sheet_list in xl_sheets:
                self.mandatory_sheets.append(sheet_list)
                break

        if not self.mandatory_sheets:
            error = "Mandatory Sheet of any %s is missing from workbook" % (wl_sheets)
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

        workload_sheet = self.mandatory_sheets[0]
        worksheet = self.xl_obj.sheet_by_name(workload_sheet)
        self.host_headers = self.get_header_indices(worksheet, self.host_headers)
        pid_names = list()

        for row in range(1, worksheet.nrows):

            part_name = worksheet.cell(row, self.host_headers[ITEM_ID]).value

            pid_names.append(part_name)

        if not len(pid_names):
            error = "The %s sheet should have minimum of one Part detail." % (workload_sheet)
            self.base_exception.append(error)
            return


    @staticmethod
    def get_header_indices(worksheet, header_list):

        sheet_header = [str(cell.value) for cell in worksheet.row(0)]
        index_dict = dict()

        for header in header_list:
            index_dict[header] = sheet_header.index(header)
        return index_dict

    def create_payload_request(self):

        input_sheet = self.mandatory_sheets[0]
        worksheet = self.xl_obj.sheet_by_name(input_sheet)
        self.host_headers = self.get_header_indices(worksheet, self.host_headers)

        # During Update Estimate, the Estimate ID that needs to be updated, must be passed along with the PayLoad
        if self.estimate_id != 'New' or "":
            ID = {"value": self.estimate_id, "typeCode": "Estimate ID"}
            self.create_payload["ProcessQuote"]["DataArea"]["Quote"][0]["QuoteHeader"]["ID"] = ID

        self.create_payload["ProcessQuote"]["DataArea"]["Quote"][0]["QuoteHeader"]["Extension"][0]["ValueText"][0][
            "value"] = self.estimate_name
        self.create_payload["ProcessQuote"]["DataArea"]["Quote"][0]["QuoteHeader"]["Extension"][0]["ID"][0][
            "value"] = self.price_list
        pid_quote = self.create_payload["ProcessQuote"]["DataArea"]["Quote"][0]["QuoteLine"][0]

        quote_line = list()
        #saved_parentid = ""

        for row in range(1, worksheet.nrows):

            quote_line_item = copy.deepcopy(pid_quote)

            item_id = worksheet.cell(row, self.host_headers[ITEM_ID]).value
            item_quantity = worksheet.cell(row, self.host_headers[ITEM_QUANTITY]).value
            parent_id = worksheet.cell(row, self.host_headers[PARENT_ID]).value
            parent_name = worksheet.cell(row, self.host_headers[PARENT_NAME]).value

            wls_list = ""
            if parent_id == 0:
                wls_list = worksheet.cell(row, self.host_headers[WORKLOADS_LIST]).value

            quote_line_item["LineNumberID"]["value"] = str(row)
            quote_line_item["Note"][0]["value"] = wls_list
            quote_line_item["Item"]["Specification"][0]["Property"][0]["ParentID"]["value"] = int(parent_id)

            quote_line_item["Item"]["ID"]["value"] = item_id
            quote_line_item["Item"]["Extension"][0]["Quantity"][0]["value"] = int(item_quantity)

            product_details = CCWData.objects.filter(product_id=item_id)

            # if parent_id == 0:      # Save Parent Name for further relation with Child PID
            #     saved_parentid = item_id

            if len(product_details) == 1:
                for prod in product_details:
                    quote_line_item["Item"]["Specification"][0]["Property"][0]["Extension"][0]["ValueText"][0][
                        "value"] = prod.product_path
                    quote_line_item["Item"]["Specification"][0]["Property"][0]["Extension"][0]["ValueText"][1][
                        "value"] = prod.product_reference
            elif len(product_details) >= 2:
                for prod in product_details:

                    if parent_name in prod.product_parent:
                        quote_line_item["Item"]["Specification"][0]["Property"][0]["Extension"][0]["ValueText"][0][
                            "value"] = prod.product_path
                        quote_line_item["Item"]["Specification"][0]["Property"][0]["Extension"][0]["ValueText"][1][
                            "value"] = prod.product_reference

                        break

            quote_line.append(quote_line_item)

        self.create_payload["ProcessQuote"]["DataArea"]["Quote"][0]["QuoteLine"] = copy.deepcopy(quote_line)
