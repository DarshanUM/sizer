import requests
import json
from xml.etree import ElementTree
import re
import logging
import os

from utils.baseview import BaseView

from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status

from hyperconverged.models import UploadBomExcelInfo, User, Scenario, EstimateDetails
from hyperconverged.views.bom_excel_report import BomExcelReport
from hyperconverged.views.generatebom_payload import EstimatePayload
from hyperconverged.views.getuser_profile_payload import GET_USER_PROFILE
from hyperconverged.exception import RXException
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class BOMExcelInfo(BaseView):

    """
    get the data from db and create estimates
    """
    def get(self, request, format=None):
        resp_data = {}
        access_key = request.GET.get('access_token')

        # Uncomment below line and add valid access_key for local testing
        # access_key = "2uHX4ZfWqec9DNfkB3YC2z6XCnJ4"

        # should not have more than 1 value unprocessed.
        uploaded_payload = UploadBomExcelInfo.objects.get(username=self.username, is_completed=False)

        if uploaded_payload.bom_input_json:
            bom_excel = BomExcelReport()
            uploaded_payload.bom_input_json['uploadbom'] = True

            selected_estimate = uploaded_payload.bom_input_json['selectedEstimate'].strip()

            res_code, response = bom_excel.generate_bom_file(
                uploaded_payload.bom_input_json["scenarioID"], uploaded_payload.bom_input_json, self.username)

            scen_id = uploaded_payload.bom_input_json["scenarioID"]

            if res_code == "NOT_FOUND":
                return Response(status=status.HTTP_404_NOT_FOUND)
            elif res_code == "BAD_REQUEST":
                return Response({'status': 'error', 'errorMessage': response}, status=status.HTTP_400_BAD_REQUEST)
            if not res_code:
                scen = Scenario.objects.get(id=uploaded_payload.bom_input_json["scenarioID"])
                ccw_status, ccw_res, ccw_res_txt = self.upload_excel_ccw(response, access_key, scen.name, scen_id,
                                                                         selected_estimate)
                if ccw_status == 'error':
                    logger.info(ccw_res)
                    return Response({'status': 'error', 'errorMessage': ccw_res}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    estimate_name = scen.name + "_Sizer_Upload"
                    logger.info("Estimate Details |%s| |%s| %s" % (scen_id, ccw_res, estimate_name))
                    return Response({'status': 'success', 'estimate_id': ccw_res, 'estimate_name': estimate_name,
                                     'response': ccw_res_txt}, status=status.HTTP_200_OK)
        else:
            logger.info("Unable to find the payload for the user:{}".format(self.username))
            return Response({'status': 'error', 'errorMessage': 'Unable to find the payload'},
                            status=status.HTTP_400_BAD_REQUEST)

    """
    save the data to upload_bom_excel DB
    """
    def post(self, request, format=None):
        # old_time = datetime.now(timezone.utc)
        data = JSONParser().parse(request)
        jsonEmpty = {}
        bom_json_data = data.get('bom_json_data', jsonEmpty)
        bom_info = UploadBomExcelInfo()

        # update the table if any unprocessed data
        result = UploadBomExcelInfo.objects.filter(username=self.username, is_completed=False).order_by('-transaction_datetime')
        # new_time = datetime.now(timezone.utc)
        # test_time = new_time -old_time
        # elapsed_time = datetime.now(datetime.timezone.utc) - result[0].transaction_datetime
        if len(result) > 0 and (datetime.now(timezone.utc) - result[0].transaction_datetime).seconds > 5:
            result.update(is_completed=True)
        elif len(result) == 1 and (datetime.now(timezone.utc) - result[0].transaction_datetime).seconds < 5:
            return Response('Previous upload bom is in progress. Please try after previous upload is completed', status=status.HTTP_404_NOT_FOUND)

        bom_info.bom_input_json = bom_json_data
        bom_info.username = self.username
        bom_info.transaction_datetime = datetime.now(timezone.utc)
        bom_info.save()
        return Response({'status': 'success'}, status=status.HTTP_200_OK)

    ''' Upload the payload and generate the estimate ID '''
    def upload_excel_ccw(self, bomfile_path, access_token, scenario_name, scenario_id, selected_estimate):

        # STEP 1 -  GET DEFAULT PRICE LIST
        logger.info("upload_excel_ccw::::username::::" + str(self.username))
        user = User.objects.get(username=self.username)
        default_price_list = user.price_list

        # Default Price List is an one time fetch process. So if already exist then we can skip that fetch process
        if not default_price_list:
            res = GET_USER_PROFILE

            api_url = "https://api.cisco.com/commerce/CONFIG/v1/getUserProfile"

            api_call_headers = {'Authorization': 'Bearer ' + access_token, 'content-type': 'application/xml'}

            api_call_res = requests.post(api_url, headers=api_call_headers, data=res, verify=False)

            logger.info(str(api_call_res.text))
            if api_call_res.status_code != 200:
                logger.info("API call failed. Status Code: {}, Reason: {}".format(api_call_res.status_code,
                                                                                  api_call_res.reason))
                return "error", "API call failed. Status Code: {}, Reason: {}".format(api_call_res.status_code,
                                                                                      api_call_res.reason), ''
            try:
                root = ElementTree.fromstring(api_call_res.text)

                reason = root.find(".//{urn:cisco:b2b:bod:services:1.0}PriceList[@type='DefaultPriceList']")
                if reason is None:
                    # try to get the first price list in the xml response
                    reason = root.find(".//{urn:cisco:b2b:bod:services:1.0}PriceList")
                    logger.info("Unable to find the DefaultPriceList for the user:{}".format(str(self.username)))

                default_price_list = reason.find(".//{urn:cisco:b2b:bod:services:1.0}ShortName").text

            except (ElementTree.ParseError, AttributeError) as ex:
                logging.error(str(ex))
                logger.info("Unable to find the PriceList for the user:{}".format(str(self.username)))
                return "error", "Exception occurred while uploading the BOM. kindly contact the Administrator.", ''

        # STEP 2 -  CREATE ESTIMATE PAYLOAD
        content = EstimatePayload(bomfile_path, scenario_name, selected_estimate, default_price_list).construct_response()
        error_message = content[1]
        response = content[0]

        # Delete the bom excel file from system
        try:
            os.system("rm " + str(bomfile_path))
        except OSError:
            pass

        if error_message:
            return "error", error_message
            # return Response({"status": "error",
            #                  "Msg": error_message,
            #                  "data": response})

        # STEP 3 - Make a CREATE OR UPDATE ESTIMATE API call with access Token
        if 'SIZER_INSTANCE' in os.environ:
            from sizer.local_settings import CREATE_ESTIMATE_URL, UPDATE_ESTIMATE_URL
            if selected_estimate == '' or selected_estimate == 'New':
                api_url = CREATE_ESTIMATE_URL
            else:
                api_url = UPDATE_ESTIMATE_URL
        else:
            # Local testing
            # check for empty string or New
            if selected_estimate == '' or selected_estimate == 'New':
                # create
                api_url = "https://api.cisco.com/commerce/EST/v2/sync/createEstimate"
            else:
                # update
                api_url = "https://api.cisco.com/commerce/EST/v2/sync/updateEstimate"

        # api_url = "https://api.cisco.com/commerce/EST/v2/sync/createEstimate"
        # access_token = "GmK5gPbotV3Um3IBoOrIkTencsJo"
        api_call_headers = {'Authorization': 'Bearer ' + access_token,
                            'content-type': 'application/json'}

        api_call_response = requests.post(api_url, headers=api_call_headers, data=json.dumps(response), verify=False)
        # print(api_call_response.text)
        # logger.info(json.dumps(response))
        logger.info("DefaultPriceList:" + default_price_list)
        logger.info(str(api_call_response.text))
        if api_call_response.status_code != 200:
            logger.info("API call failed. Status Code: {}, Reason: {}".format(api_call_response.status_code,
                                                                              api_call_response.reason))
            return "error", "API call failed. Status Code: {}, Reason: {}".format(api_call_response.status_code,
                                                                                  api_call_response.reason), ''

        # parse the XML response
        try:

            xmlstring = re.sub(r'\sxmlns="[^"]+"', '', api_call_response.text, count=1)
            root = ElementTree.fromstring(xmlstring)
            reason = root.find(".//DataArea/Acknowledge/ResponseCriteria/ChangeStatus/Reason").text

            if reason.lower() == "success":
                estimated_id = root.find(".//DataArea/Quote/QuoteHeader/ID").text
                estimated_name = root.find(".//DataArea/Quote/QuoteHeader/Extension/ValueText[2]").text
                estimate = EstimateDetails()

                estimate_details = EstimateDetails.objects.filter(scenario_id=scenario_id, estimate_id=selected_estimate).first()

                # populate the table with estimate details during create estimate
                if selected_estimate == 'New' or selected_estimate == '' or not estimate_details:
                    estimate.scenario_id = scenario_id
                    estimate.scenario_name = scenario_name
                    estimate.estimate_id = estimated_id
                    estimate.estimate_name = estimated_name
                    estimate.estimate_response = reason.lower()
                    estimate.created_datetime = datetime.now(timezone.utc)
                    estimate.save()
                    response_txt = "BOM Uploaded Successfully!!!"
                    logger.info(response_txt)

                # update the is_updated and current time of estimate row if it is update estimate
                else:
                    estimate_details.is_updated += 1
                    estimate_details.created_datetime = datetime.now(timezone.utc)
                    estimate_details.save()
                    response_txt = "BOM Updated Successfully!!!"
                    logger.info(response_txt)

                # UPDATE DEFAULT PRICE LIST IN THE TABLE
                if not user.price_list:
                    user.price_list = default_price_list
                    user.save()

                return "success", estimated_id, response_txt

            else:
                # get the error reason
                error_description = root.find(".//DataArea/Quote/QuoteHeader/Message/Description").text
                return "error", error_description, ''

        except ElementTree.ParseError as ex:
            logging.error(str(ex))
            return "error", "Exception occured while uploading the BOM. kindly contact the Administrator.", ''


