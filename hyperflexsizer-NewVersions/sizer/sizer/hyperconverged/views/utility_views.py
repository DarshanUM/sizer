import os
import configparser

from rest_framework.response import Response
from rest_framework import status
from functools import wraps
from utils.baseview import BaseView

from hyperconverged.models import User, feature_permission, SharedScenario, Scenario, Results, Part, SpecIntData, \
    HxPerfNumbers
from hyperconverged.serializer.WorkloadSerializer import WorkloadGetSerializer
from hyperconverged.serializer.perf_serializer import HxGetSerializer
from hyperconverged.solver.attrib import HyperConstants

import logging
logger = logging.getLogger(__name__)

def get_version_configs():

    config = configparser.ConfigParser()
    if 'OPENSHIFT_REPO_DIR' in os.environ:
        from local_settings import BASE_DIR
        config.read(os.path.join(BASE_DIR, 'sizer/sizing_config.cfg'))
    else:
        from sizer.local_settings import BASE_DIR
        config.read(os.path.join(BASE_DIR, 'sizer/sizing_config.cfg'))

    items = config.items('Versions')

    versions = dict()
    versions['sizer_version'] = items[0][1]
    versions['hx_version'] = items[1][1]
    versions['hxbench_version'] = items[2][1]

    return versions


def get_configs(config_item):

    config = configparser.ConfigParser()

    if 'OPENSHIFT_REPO_DIR' in os.environ:
        from local_settings import BASE_DIR
        config.read(os.path.join(BASE_DIR, 'sizer/sizing_config.cfg'))
    else:
        from sizer.local_settings import BASE_DIR
        config.read(os.path.join(BASE_DIR, 'sizer/sizing_config.cfg'))

    items = config.items(config_item)

    url = dict()
    file_url = config_item.lower() + '_url'
    url[file_url] = items[0][1]

    return url


def fetch_scenario(scenario):

    add_scen = dict()
    add_scen['id'] = scenario['id']
    add_scen['name'] = scenario['name']

    if isinstance(scenario['settings_json'], list):
        add_scen['settings_json'] = scenario['settings_json']
    else:
        add_scen['settings_json'] = [scenario['settings_json']]

    add_scen['updated_date'] = scenario['updated_date']
    add_scen['isshared'] = False
    add_scen['sharedcount'] = 0
    add_scen['username'] = scenario['username']
    add_scen['sizing_type'] = scenario['sizing_type']

    sScenarios = SharedScenario.objects.filter(scenario_id=scenario['id'])
    # sScenarios = SharedScenario.objects.filter(scenario_id=scenario['id']).values_list('email',flat=True)
    if len(sScenarios) > 0:
        add_scen['isshared'] = True
        add_scen['sharedcount'] = len(sScenarios)
        #add_scen['shared_email_id'] = list(sScenarios)
        add_scen['shared_email_id'] = [scen.email for scen in sScenarios]
        add_scen['secure_enabled'] = any(scen.is_secure for scen in sScenarios)


    wl_type_count = dict()
    if scenario['workload_json']:
        if 'wl_list' in scenario['workload_json'].keys():
            add_scen['wl_count'] = len(scenario['workload_json']['wl_list'])

            for workload in scenario['workload_json']['wl_list']:

                wl_type = workload['wl_type']
                if wl_type not in HyperConstants.WORKLOAD_TYPES or wl_type not in wl_type_count:
                    wl_type_count[wl_type] = 0

                wl_type_count[wl_type] += 1

            add_scen['wl_type_count'] = wl_type_count
    else:
        add_scen['wl_count'] = 0
        add_scen['wl_type_count'] = wl_type_count

    if scenario['sizing_type'] == 'optimal':
        default_result = Results.objects.filter(name='Lowest_Cost', scenario_id=scenario['id'])
    elif scenario['sizing_type'] == 'fixed':
        default_result = Results.objects.filter(name='Fixed Config', scenario_id=scenario['id'])
    else:
        default_result = Results.objects.filter(name='Lowest_Cost', scenario_id=scenario['id'])

    # Commented the code as its not adding all scenarios, till we find root cause
    # # Weird issue seen twice..!  Unable to reproduce
    # # The default_result doesn't have result entry itself for scenario.
    # if not len(default_result):
    #     logger.error('ERROR: The Scenario %s(%s) has default_result for Lowest Cost/Fixed Config as empty..!'
    #                  % (str(scenario['id']), scenario['name']))
    #     return dict()

    if scenario['workload_json'] and len(default_result) > 0 and len(default_result[0].result_json) > 0 and \
            'clusters' in default_result[0].result_json[0]:
        add_scen['cluster_count'] = sum([len(cluster) for cluster in default_result[0].result_json[0]['clusters']])
        add_scen['node_count'] = default_result[0].result_json[0]['summary_info']['num_nodes']
    else:
        add_scen['cluster_count'] = 0
        add_scen['node_count'] = 0

    add_scen['scen_label'] = scenario['scen_label']

    if scenario['sizing_type'] == 'hybrid':
        add_scen['settings_json'] = [default_result[0].settings_json]

    return add_scen


def get_scenario_list(username, scen_tab, scen_offset, scen_limit):

    if username == 'admin':
        if scen_tab == "ACTIVE":
            scenarios = Scenario.objects.filter(status=True).exclude(scen_label='archive').order_by(
                '-updated_date')[scen_offset:scen_limit]
        elif scen_tab == "FAVORITE":
            scenarios = Scenario.objects.filter(status=True, scen_label='fav').order_by(
                '-updated_date')[scen_offset:scen_limit]
        elif scen_tab == "ARCHIVE":
            scenarios = Scenario.objects.filter(status=True, scen_label='archive').order_by(
                '-updated_date')[scen_offset:scen_limit]

    else:

        if scen_tab == "ACTIVE":
            scenarios = Scenario.objects.filter(status=True, username=username).exclude(
                scen_label='archive').order_by('-updated_date')[scen_offset:scen_limit]
        elif scen_tab == "FAVORITE":
            scenarios = Scenario.objects.filter(status=True, username=username, scen_label='fav').order_by(
                '-updated_date')[scen_offset:scen_limit]
        elif scen_tab == "ARCHIVE":
            scenarios = Scenario.objects.filter(status=True, username=username, scen_label='archive').order_by(
                '-updated_date')[scen_offset:scen_limit]

    serializer = WorkloadGetSerializer(scenarios, many=True)

    scenario_data = list()
    for scenario in serializer.data:

        add_scen = fetch_scenario(scenario)

        if add_scen:
            scenario_data.append(add_scen)

    return Response(scenario_data, status=status.HTTP_200_OK)


def get_shared_scenario_list(username, scen_offset, scen_limit):

    shared_scenarios = SharedScenario.objects.filter(userid=username)

    scenarios = Scenario.objects.filter(status=True,
                                        id__in=[scenario.scenario_id for scenario in shared_scenarios]).order_by(
        '-updated_date')[scen_offset:scen_limit]

    serializer = WorkloadGetSerializer(scenarios, many=True)

    scenario_data = list()

    for scenario in serializer.data:

        add_scen = fetch_scenario(scenario)

        if add_scen:
            share_scen = SharedScenario.objects.get(userid=username, scenario_id=scenario['id'])
            add_scen['edit_enabled'] = share_scen.acl
            if share_scen.is_secure:
                owner_mail = list()
                owner_mail.append(User.objects.get(username=scenario['username']).email)
                add_scen['shared_email_id'] = owner_mail
                add_scen['sharedcount'] = 1

            scenario_data.append(add_scen)

    return Response(scenario_data, status=status.HTTP_200_OK)


def search_scenarios(username, search_string, scen_tab, scen_offset, scen_limit):

    if username == 'admin':

        if scen_tab == "ACTIVE":
            scenarios = Scenario.objects.filter(status=True, name__icontains=search_string).exclude(
                scen_label='archive').order_by('-updated_date')
        elif scen_tab =="ARCHIVE":
            scenarios = Scenario.objects.filter(status=True, name__icontains=search_string,
                                                scen_label='archive').order_by('-updated_date')
        elif scen_tab == "FAVORITE":
            scenarios = Scenario.objects.filter(status=True, name__icontains=search_string,
                                                scen_label='fav').order_by('-updated_date')

    else:

        if scen_tab == "ACTIVE":
            scenarios = Scenario.objects.filter(status=True, username=username, name__icontains=search_string
                                                ).exclude(scen_label='archive').order_by('-updated_date')
        elif scen_tab=="ARCHIVE":
            scenarios = Scenario.objects.filter(status=True, username=username, name__icontains=search_string,
                                                scen_label='archive').order_by('-updated_date')
        elif scen_tab == "FAVORITE":
            scenarios = Scenario.objects.filter(status=True, username=username, name__icontains=search_string,
                                                scen_label='fav').order_by('-updated_date')

    scenario_count = scenarios.count()
    scenarios = scenarios[scen_offset:scen_limit]
    serializer = WorkloadGetSerializer(scenarios, many=True)
    search_response = dict()
    scenario_data = list()
    for scenario in serializer.data:
        add_scen = fetch_scenario(scenario)

        if add_scen:
            scenario_data.append(add_scen)
    
    search_response = {'total_count': scenario_count, 'result': scenario_data}
    return Response(search_response, status=status.HTTP_200_OK)


def feature_decorator(feature_name):
    def restrict_feature(post_func):
        """
        Getting access level of user and permitting to use the sizing features.
        """
        @wraps(post_func)
        def core_func(request, *args, **kwargs):
            usrname = request.username  # logged-in username
            if usrname == 'admin':
                return post_func(request, *args, **kwargs)

            # get the acces level from db if user record is available
            user_obj = User.objects.get(username=usrname)

            if feature_name == 'iops_access':
                if user_obj.iops_access:
                    return post_func(request, *args, **kwargs)
                else:
                    error_msg = "You're not authorised to view this page"
                    return Response({'status': 'error', 'errorMessage': error_msg},
                                    status=status.HTTP_400_BAD_REQUEST)

            user_access_level = user_obj.accesslevel

            # Getting accesslevel for existing users .
            if user_access_level == -1 or not user_access_level:
                if 'OPENSHIFT_REPO_DIR' in os.environ:
                    from sizer.sizer.views import get_user_details_from_ldap
                else:
                    from sizer.views import get_user_details_from_ldap

                # Updating accesslevel for existing users in DB.
                user_details_from_ldap = get_user_details_from_ldap(usrname)  # need to uncomment
                user_access_level = user_details_from_ldap['emp_access_level'][0]
                user_obj.accesslevel = user_access_level  # updating the accesslevel if it's not available in DB
                user_obj.save()

            error_msg = "This feature is restricted to Cisco employees and " \
                        "partners only. Please login using your Cisco credentials."

            if user_access_level < feature_permission.objects.get(feature=feature_name).access_level:
                return Response({'status': 'error', 'errorMessage': error_msg},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                return post_func(request, *args, **kwargs)

        return core_func

    return restrict_feature


class SizerUsers(BaseView):

    def get(self, request, format=None):

        if self.username == 'admin':
            sizerusers = User.objects.all().order_by('username')
        else:
            sizerusers = User.objects.all().order_by('username').exclude(username='admin')

        user_data = list()

        for user in sizerusers:
            added_user = dict()
            added_user['userid'] = user.username
            added_user['fname'] = user.first_name
            added_user['lname'] = user.last_name
            added_user['email'] = user.email

            user_data.append(added_user)

        return Response(user_data, status=status.HTTP_200_OK)


class VersionDetails(BaseView):
    """
    Get the version number
    """
    @staticmethod
    def get(request, format=None):

        versions = get_version_configs()
        return Response(versions)


class GetFIOptions(BaseView):

    """Get FI options for the output."""

    @staticmethod
    def get(request, format=None):

        qry_object = Part.objects.filter(part_json__contains="-FI-").\
            exclude(name__contains="_CTO").exclude(name__contains="_M5").order_by("name")
        fi_list = [fi_name.name for fi_name in qry_object]

        return Response(fi_list)


# class ThresholdDetails(BaseView):
#     """
#     Get the threshold details
#     """
#
#     @staticmethod
#     def get(request, format=None):
#
#         config = configparser.ConfigParser()
#
#         if 'OPENSHIFT_REPO_DIR' in os.environ:
#             from local_settings import BASE_DIR
#             config.read(os.path.join(BASE_DIR, 'sizer/sizing_config.cfg'))
#         else:
#             from sizer.local_settings import BASE_DIR
#             config.read(os.path.join(BASE_DIR, 'sizer/sizing_config.cfg'))
#
#         data = dict()
#         for section in config.sections():
#             resp_key = ""
#             if section == "Threshold_Conservative":
#                 resp_key = "CONSERVATIVE"
#             elif section == "Threshold_Normal":
#                 resp_key = "STANDARD"
#             elif section == "Threshold_Aggressive":
#                 resp_key = "AGGRESSIVE"
#
#             data[resp_key] = list()
#             value_list = config.items(section)
#             for (name, val) in value_list:
#                 if name == "gpu_users":
#                     continue
#                 data[resp_key].append({"name":name, "value":val})
#
#         return Response(data)


# class DefaultDetails(BaseView):
#     """
#     Get the threshold details
#     """
#
#     def get(self, request, format=None):
#         config = ConfigParser.ConfigParser()
#         if 'OPENSHIFT_REPO_DIR' in os.environ:
#             from local_settings import BASE_DIR
#             config.read(os.path.join(BASE_DIR, 'sizer/ui_defaults.cfg'))
#         else:
#             from sizer.local_settings import BASE_DIR
#             config.read(os.path.join(BASE_DIR, 'sizer/ui_defaults.cfg'))
#
#         data = dict()
#         for section in config.sections():
#             resp_key = section
#
#             value_list = config.items(section)
#             configs = dict()
#             for (name, val) in value_list:
#                 if name in ['wl_type', 'user_type', 'vm_type', 'provisioning_type', 'desktop_os']:
#                     configs[name] = val
#                 else:
#                     configs[name] = int(val)
#
#             data[resp_key] = configs
#
#         return Response(data)


class GetCpuModels(BaseView):

    def get(self, request, format=None):

        cpumodels = SpecIntData.objects.values_list('model', flat=True).distinct()

        return Response(cpumodels, status=status.HTTP_200_OK)


class GetHxPerfNumbers(BaseView):

    @feature_decorator('iops_access')
    def get(self, request, format=None):

        hx_obj_list = list()
        query_data = HxPerfNumbers.objects.all()

        for hx_obj in query_data:
            serializer = HxGetSerializer(hx_obj, many=False)
            hx_obj_list.append(serializer.data)

        return Response(hx_obj_list, status=status.HTTP_200_OK)
