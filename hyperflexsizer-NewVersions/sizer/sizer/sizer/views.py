from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.authtoken.models import Token
from rest_framework import status

from hyperconverged.models import User, Scenario, feature_permission, SharedScenario
from .local_settings import LDAP_BIND_DETAILS, LDAP_PASSWORD, LDAP_URL, STAGE_LOGOUT_URL, PROD_LOGOUT_URL
from .local_settings import HX_PREINSTALLER_STAGE_URL, HX_PREINSTALLER_PROD_URL
from .local_settings import STAGE_REDIRECT_TOKEN_URL, PROD_REDIRECT_TOKEN_URL
from utils.baseview import BaseView
from datetime import date

#import ldap
import os
import copy
from hyperconverged.views.utility_views import get_version_configs
from hyperconverged.views.scenario_solve_views import filter_node_and_part_data, validate_nodes_post_filter
from hyperconverged.solver.sizing import HyperConvergedSizer

from hyperconverged.exception import HXException, RXException

from hyperconverged.serializer.WorkloadSerializer import UCSizerSerializer, WorkloadPostSerializer
from hyperconverged.models import SpecIntData

import logging

logger = logging.getLogger(__name__)


LAE_FROM = "donotreply@cisco.com"
LAE_TO = "hx-sizer@external.cisco.com"
LAE_HOST = "outbound.cisco.com"

STAGE_FROM = "maple-noreply@maplelabs.com"
STAGE_TO = "saleem.sheikh@maplelabs.com"
STAGE_HOST = "webmail.xoriant.com"


class EnvInfo(APIView):
    """
    To know lae/non-lae environment
    """
    def get(self, request, format=None):

        resp_data = {}

        if "HTTP_AUTH_USER" in request.META:
            resp_data["lae"] = True
            resp_data["username"] = request.META["HTTP_AUTH_USER"]
            resp_data["email"] = "hx-sizer@external.cisco.com"
            resp_data["profiler_email"] = "hx-profiler@external.cisco.com"
            resp_data["bench_email"] = "hx-bench@external.cisco.com"
        else:
            resp_data["lae"] = False
            resp_data["email"] = "hx-sizer@maplelabs.com"
            resp_data["profiler_email"] = "hx-profiler@maplelabs.com"
            resp_data["bench_email"] = "hx-bench@maplelabs.com"

        return Response(resp_data)


def get_user_details_from_ldap(userid):

    user_details = dict()

    try:
        connect = ldap.initialize(LDAP_URL)
        connect.simple_bind_s(LDAP_BIND_DETAILS, LDAP_PASSWORD)
        connect.protocol_version = ldap.VERSION3
    except:
        return 'error :Failed to connect the LDAP server.'

    base_dn = 'uid=' + userid  + ',OU=ccoentities,O=cco.cisco.com'
    search_scope = ldap.SCOPE_SUBTREE
    retrieve_attributes = ['company', 'givenName', 'sn', 'employeeNumber', 'mail', 'accessLevel']
    search_filter = "cn=*"

    try:
        ldap_result_id = connect.search(base_dn, search_scope, search_filter, retrieve_attributes)
        while True:
            try:
                result_type, result_data = connect.result(ldap_result_id, 0)
            except:
                return 'Not able to find the data in LDAP database'
            if (result_data == []):
                break
            else:
                if result_type == ldap.RES_SEARCH_ENTRY:
                    user_details['emp_number'] = result_data[0][1]['employeeNumber']
                    user_details['emp_email_id'] = result_data[0][1]['mail']
                    user_details['emp_company'] = result_data[0][1]['company']
                    user_details['emp_firstname'] = result_data[0][1]['givenName']
                    user_details['emp_sername'] = result_data[0][1]['sn']
                    # user_details['emp_last_login']= result_data[0][1]['lastLogin']
                    user_details['emp_access_level'] = result_data[0][1]['accessLevel']
    except:
            return 'Not able to find the data in LDAP database'
    return user_details


class AuthInfo(APIView):

    """
    To authorize the user if exists in DB/Ldap and accessLevel is more than 3
    """
    def post(self, request, format=None):

        if "HTTP_AUTH_USER" not in request.META:

            username = request.data["username"]
            user = User.objects.get(username=username)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"auth_token": str(token),
                             "iops_access": True}, status=status.HTTP_200_OK)

        else:

            username = request.META["HTTP_AUTH_USER"]

            try:
                user_name = User.objects.get(username=username).username
            except ObjectDoesNotExist:
                user_name = 'NA'

            if not user_name == 'NA':

                status_dict = {'status': 'success',
                               'iops_access': User.objects.get(username=username).iops_access}
                return Response(status_dict)

            else:

                user_name = username
                user_details_from_ldap = get_user_details_from_ldap(user_name)

                if 'error' in user_details_from_ldap:
                    return Response({'status': 'error', 'errorMessage': 'Not able to connect the Ldap'})
                elif 'LDAP database' in user_details_from_ldap:
                    return Response({'status': 'error', 'errorMessage': user_details_from_ldap})

                if len(user_details_from_ldap) == 0 or 'NameErr' in user_details_from_ldap:
                    return Response({'status': 'error',
                                     'errorMessage': 'Unauthorized Access to login'})
                else:
                    user_details_object = User()
                    user_details_object.username = user_name

                    company = user_details_from_ldap['emp_company'][0]
                    emp_company = company.decode() if isinstance(company, bytes) else company
                    user_details_object.company = emp_company

                    sername = user_details_from_ldap['emp_sername'][0]
                    emp_sername = sername.decode() if isinstance(sername, bytes) else sername
                    user_details_object.last_name = emp_sername

                    firstname = user_details_from_ldap['emp_firstname'][0]
                    emp_firstname = firstname.decode() if isinstance(firstname, bytes) else firstname
                    user_details_object.first_name = emp_firstname

                    email_id = user_details_from_ldap['emp_email_id'][0]
                    emp_email_id = email_id.decode() if isinstance(email_id, bytes) else email_id
                    user_details_object.email = emp_email_id

                    number = user_details_from_ldap['emp_number'][0]
                    emp_number = number.decode() if isinstance(number, bytes) else number
                    user_details_object.emp_id = emp_number

                    user_details_object.accesslevel = user_details_from_ldap['emp_access_level'][0]
                    user_details_object.iops_access = False
                    user_details_object.save()

                    status_dict = {'status': 'success',
                                   'iops_access': False}

                    return Response(status_dict)


class UserData(BaseView):

    def get(self, _):

        user = User.objects.get(username=self.username)

        logout_url = ""
        hxpreinstaller_url =  HX_PREINSTALLER_PROD_URL
        estimatetokenapi_url = ""
        if 'SIZER_INSTANCE' in os.environ:
            if os.environ['SIZER_INSTANCE'] == 'STAGE':
                logout_url = STAGE_LOGOUT_URL
                hxpreinstaller_url = HX_PREINSTALLER_STAGE_URL
                estimatetokenapi_url = STAGE_REDIRECT_TOKEN_URL

            else:
                logout_url = PROD_LOGOUT_URL
                hxpreinstaller_url = HX_PREINSTALLER_PROD_URL
                estimatetokenapi_url = PROD_REDIRECT_TOKEN_URL

        first_name = ""
        if user.first_name:
            if isinstance(user.first_name, str):
                first_name = user.first_name
            else:
                first_name = user.first_name.decode("utf-8")

        if self.username == 'admin':
            return Response({"home_page_desc": user.home_page_desc,
                             "optimal_sizing_desc": user.optimal_sizing_desc,
                             "fixed_sizing_desc": user.fixed_sizing_desc,
                             "scenario_per_page": user.scenario_per_page,
                             "language": user.language,
                             "theme": user.theme,
                             "banner_version": user.banner_version,
                             "user_firstname": first_name if first_name else "anonymous",
                             "home_disclaimer": True if user.home_disclaimer == date(2001, 1, 1) else False,
                             "logout_url": logout_url,
                             "hxpreinstaller_url": hxpreinstaller_url,
                             "access_token": "Nc1cJMLeWoMSRJHrCYMHBMV3IEqZ",
                             "scenario_count": {"active": Scenario.objects.filter(status=True).exclude(
                                 scen_label='archive').count(),
                                                "favorite": Scenario.objects.filter(scen_label="fav",
                                                                                    status=True).count(),
                                                "archive": Scenario.objects.filter(scen_label="archive",
                                                                                   status=True).count(),
                                                "shared": SharedScenario.objects.filter(userid=self.username).count()}},
                            status=status.HTTP_200_OK)

        return Response({"home_page_desc": user.home_page_desc,
                         "optimal_sizing_desc": user.optimal_sizing_desc,
                         "fixed_sizing_desc": user.fixed_sizing_desc,
                         "scenario_per_page": user.scenario_per_page,
                         "language": user.language,
                         "theme": user.theme,
                         "banner_version": user.banner_version,
                         "user_firstname": first_name if first_name else "anonymous",
                         "home_disclaimer": True if user.home_disclaimer == date(2001, 1, 1) else False,
                         "logout_url" : logout_url,
                         "hxpreinstaller_url": hxpreinstaller_url,
                         "estimatetokenapi_url": estimatetokenapi_url,
                         "scenario_count": {"active": Scenario.objects.filter(status=True,
                                                                              username=self.username).exclude(
                             scen_label='archive').count(),
                                            "favorite": Scenario.objects.filter(scen_label="fav",
                                                                                status=True,
                                                                                username=self.username).count(),
                                            "archive": Scenario.objects.filter(scen_label="archive",
                                                                               status=True,
                                                                               username=self.username).count(),
                                            "shared": SharedScenario.objects.filter(userid=self.username).count()}},
                        status=status.HTTP_200_OK)

    def post(self, request):

        user = User.objects.get(username=self.username)
        data = JSONParser().parse(request)

        if "home_page_desc" in data:
            user.home_page_desc = data['home_page_desc']
        if "scenario_per_page" in data:
            user.scenario_per_page = data['scenario_per_page']
        if "optimal_sizing_desc" in data:
            user.optimal_sizing_desc = data['optimal_sizing_desc']
        if "fixed_sizing_desc" in data:
            user.fixed_sizing_desc = data['fixed_sizing_desc']
        if "language" in data:
            user.language = data['language']
        if "theme" in data:
            user.theme = data['theme']
        if "banner_version" in data:
            user.banner_version = data['banner_version']
        if "home_disclaimer" in data:
            user.home_disclaimer = date.today()

        user.save()

        first_name = ""
        if user.first_name:
            if isinstance(user.first_name, str):
                first_name = user.first_name
            else:
                first_name = user.first_name.decode("utf-8")

        return Response({"home_page_desc": user.home_page_desc,
                         "optimal_sizing_desc": user.optimal_sizing_desc,
                         "fixed_sizing_desc": user.fixed_sizing_desc,
                         "scenario_per_page": user.scenario_per_page,
                         "language": user.language,
                         "theme": user.theme,
                         "banner_version": user.banner_version,
                         "user_firstname": first_name if first_name else "anonymous",
                         "home_disclaimer": True if user.home_disclaimer == date(2001, 1, 1) else False,},
                        status=status.HTTP_200_OK)


## This part of code is for UCSizer Tool to get the Sizing result
RAW_WL_TEMPLATE = {"wl_name":"RAW-1",
                   "isFileInput":False,
                   "cpu_attribute":"vcpus",
                   "cpu_model":"Intel Platinum 8164",
                   "vcpus":2,
                   "cpu_clock":35,
                   "vcpus_per_core":1,
                   "ram_size_unit":"GiB",
                   "ram_size":128,
                   "ram_opratio":1,
                   "hdd_size_unit":"GB",
                   "hdd_size":1000,
                   "ssd_size_unit":"GB",
                   "ssd_size":0,
                   "iops":0,
                   "gpu_users":0,
                   "working_set":10,
                   "overhead_percentage":0,
                   "cluster_type":"normal",
                   "replication_factor":3,
                   "fault_tolerance":1,
                   "compression_factor":0,
                   "dedupe_factor":0,
                   "wl_type":"RAW",
                   "internal_type": "RAW",
                   "input_type":"Manual",
                   "storage_protocol": "NFS"}


class UCSizer_SizingResult(APIView):

    @staticmethod
    def get_sizer_default_settings():

        """filters and default settings for new scenarios of optimal type"""
        filters = dict()
        filters["Node_Type"] = list()
        filters["RAM_Slots"] = list()
        filters["RAM_Options"] = list()
        filters["CPU_Type"] = list()
        filters["Compute_Type"] = ["HX-B200", "HX-C220", "HX-C240", "HX-C480"]
        filters["Disk_Options"] = list()
        filters["Cache_Options"] = list()
        filters["GPU_Type"] = list()
        filters["Clock"] = list()

        #settings_json = dict()
        settings_json = {"account": "", "deal_id": ""}
        settings_json["filters"] = filters
        versions = get_version_configs()
        settings_json['sizer_version'] = versions['sizer_version']
        settings_json['hx_version'] = versions['hx_version']
        settings_json['heterogenous'] = True
        settings_json['threshold'] = 1
        settings_json['bundle_only'] = "ALL"
        settings_json['disk_option'] = "NON-SED"
        settings_json['cache_option'] = "ALL"
        settings_json['modular_lan'] = "ALL"
        settings_json['server_type'] = "M5"
        settings_json['includeSoftwareCost'] = True
        settings_json['dr_enabled'] = False
        settings_json['hypervisor'] = 'esxi'
        settings_json['hercules_conf'] = 'enabled'
        settings_json['hx_boost_conf'] = 'enabled'
        settings_json['license_yrs'] = 3
        settings_json['cpu_generation'] = "recommended"
        settings_json['free_disk_slots'] = 0

        return settings_json

    def post(self, request):

        serializer = UCSizerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'status': 'error',
                             'errorMessage': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        wl_list = list()
        workload = copy.deepcopy(RAW_WL_TEMPLATE)

        workload['cpu_attribute'] = data['cpu_attribute']

        if data['cpu_attribute'] == 'vcpus':
            if 'vcpus' in data:
                workload['vcpus'] = data['vcpus']
            else:
                return Response({'status': 'error',
                                 'errorMessage': 'Please give value for vcpus key if cpu_attribute is vcpus'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            if 'cpu_clock' in data:
                workload['cpu_clock'] = data['cpu_clock']
            else:
                return Response({'status': 'error',
                                 'errorMessage': 'Please give value for cpu_clock key if cpu_attribute is cpu_clock'},
                                status=status.HTTP_400_BAD_REQUEST)

        cpu_model = data.get('cpu_model', None)

        try:
            if not cpu_model:
                cpu_model = 'Intel Platinum 8164'
            else:
                input_cpu = SpecIntData.objects.get(model=cpu_model)
        except ObjectDoesNotExist:
            return Response({'status': 'error',
                             'errorMessage': "Input CPU model doesn't exist"},
                            status=status.HTTP_400_BAD_REQUEST)

        workload['ram_size'] = data['ram_size']
        workload['ram_size_unit'] = data['ram_size_unit']
        workload['hdd_size'] = data['hdd_size']
        workload['hdd_size_unit'] = data['hdd_size_unit']
        workload['fault_tolerance'] = data['fault_tolerance']
        workload['cpu_model'] = cpu_model

        wl_list.append(workload)

        ReturnData = dict()
        ReturnData['id'] = None
        ReturnData['name'] = "UCSizerScenario"
        ReturnData['sizing_type'] = "hybrid"
        ReturnData['workload_list'] = wl_list
        ReturnData['workload_result'] = list()
        ReturnData['errors'] = list()
        ReturnData['settings_json'] = list()

        # result_type = ["Lowest_Cost", "All-Flash", "All NVMe"]
        # They requested only for Lowest_Cost result to be included as part of result
        result_type = ["Lowest_Cost"]
        for index, result_name in enumerate(result_type):
            settings_json = UCSizer_SizingResult.get_sizer_default_settings()
            ReturnData['settings_json'].append(settings_json)
            ReturnData['settings_json'][index]['result_name'] = result_name

        replication_enabled = False

        serializer_data = dict()
        serializer_data['RAW'] = wl_list
        serializer_data['sizing_type'] = 'optimal'

        settings_json_array = ReturnData['settings_json']
        for settings_json in settings_json_array:

            serializer_data['settings_json'] = settings_json

            filters = settings_json['filters']

            if replication_enabled:
                settings_json['dr_enabled'] = True
            else:
                settings_json['dr_enabled'] = False

            bundle_only = data['nodetype'] if 'nodetype' in data else settings_json["bundle_only"]
            disk_option = settings_json["disk_option"]
            cache_option = settings_json["cache_option"]
            #modular_lan = settings_json["modular_lan"]
            server_type = settings_json["server_type"]
            cpu_ram_gen = settings_json["cpu_generation"]
            hypervisor = settings_json["hypervisor"]
            hercules = settings_json["hercules_conf"]
            hx_boost = settings_json["hx_boost_conf"]
            free_disk_slots = settings_json["free_disk_slots"]

            serializer = WorkloadPostSerializer(data=serializer_data)
            if not serializer.is_valid():
                error = serializer.errors
                return Response({'status': 'error', 'errorCode': 4, 'errorMessage': error},
                                status=status.HTTP_403_FORBIDDEN)

            errors = None
            resp = list()

            if wl_list:

                nodes, parts, parts_qry = filter_node_and_part_data(filters, settings_json['result_name'], disk_option,
                                                                    cache_option, server_type, hypervisor,
                                                                    hercules, cpu_ram_gen, hx_boost, free_disk_slots)

                errors = validate_nodes_post_filter(nodes, parts_qry, settings_json, wl_list)

                try:
                    if not errors:
                        solver = HyperConvergedSizer(parts, nodes, wl_list, settings_json, None)
                        resp = solver.solve(bundle_only)

                        solver.logger.info('UCSizer Sizing requirement: %s ' % data)
                        solver.logger.info('UCSizer Sizing workload: %s ' % wl_list)

                except HXException as e:
                    errors = str(e)

            if resp:
                ReturnData['workload_result'].append(resp)

            if errors:
                error_dict = {'message': errors, 'result_name': settings_json['result_name']}
                ReturnData['errors'].append(error_dict)

        return Response(ReturnData, status=status.HTTP_201_CREATED)
