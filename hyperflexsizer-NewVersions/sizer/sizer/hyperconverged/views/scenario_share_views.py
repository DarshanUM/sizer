import json
import os

# Added for mail
from mailer import Mailer
from mailer import Message

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from utils.baseview import BaseView

from hyperconverged.models import Scenario, SharedScenario, User
from hyperconverged.serializer.WorkloadSerializer import SharedScenarioSerializer

import logging
logger = logging.getLogger(__name__)

# Scenarios are only shared with users having Greater than or equal to SHARE_ACCESSLEVEL  = 3
# Cisco Access Level
# 1 -> Guest
# 2 -> Customer
# 3 -> Partner
# 4 -> Cisco Employee

# Changed Access level to 0 from 3 as per Manish comment, to remove share restriction
SHARE_ACCESSLEVEL = 0


class ShareScenario(BaseView):

    def get(self, request, id, format=None):

        try:
            scenario = Scenario.objects.get(id=id)
        except Scenario.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        sScenario = SharedScenario.objects.filter(scenario_id=id, userid=self.username)
        if not scenario.username == self.username and len(sScenario) == 0:
            return Response({'status': 'error', 'errorMessage': 'Unauthorized Access'},
                            status=status.HTTP_400_BAD_REQUEST)

        suser_list = list()

        sScenarios = SharedScenario.objects.filter(scenario_id=id)
        if len(sScenarios) > 0:
            for scenario in sScenarios:
                user_details = dict()

                # Getting User email id from auth table instead of userid
                try:
                    user_obj = User.objects.get(username=scenario.userid)
                    # user_details['userid'] = scenario.userid
                    user_details['email'] = user_obj.email
                    user_details['acl'] = scenario.acl
                    user_details['is_secure'] = scenario.is_secure
                    suser_list.append(user_details)
                except User.DoesNotExist:
                    pass

        return Response(suser_list, status=status.HTTP_200_OK)

    def validate_shared_users_list(self, users_list):
        users_share_list = list()
        record_not_found = list()
        access_prohibited = list()

        for suser in users_list:
            user_details = dict()
            email = suser['email']

            try:
                user_obj = User.objects.get(email=email)
                user_details['userid'] = user_obj.username
                user_details['acl'] = suser['acl']
                user_details['is_secure'] = suser.get('is_secure', False)
                user_details['isExistingUser'] = True
                user_details['email'] = email

                accesslevel = user_obj.accesslevel
                if accesslevel >= SHARE_ACCESSLEVEL:
                    users_share_list.append(user_details)
                else:
                    access_prohibited.append(email)
            except User.DoesNotExist:
                record_not_found.append(email)
                pass

        return users_share_list, record_not_found, access_prohibited

    def post(self, request, id, format=None):
        """
        To share scenario across other sizer users
        """
        serializer = SharedScenarioSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'status': 'error',
                             'errorMessage': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            scenario = Scenario.objects.get(id=id)
        except Scenario.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        sScenario = SharedScenario.objects.filter(scenario_id=id, userid=self.username)
        if not scenario.username == self.username and len(sScenario) == 0:
            return Response({'status': 'error', 'errorMessage': 'Unauthorized Access'},
                            status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        users_list = data['users_list']
        existing_users = list()
        user_email_id = list()
        scenario_name = Scenario.objects.get(id=id).name

        # Setting mail url for stage and production links
        if 'SIZER_INSTANCE' in os.environ:
            from sizer.views import get_user_details_from_ldap
            from sizer.local_settings import LAE_FROM, LAE_HOST
            from sizer.local_settings import lae_stage_url, lae_prod_url

            sender_email = LAE_FROM
            mailer_host = LAE_HOST

            if os.environ['SIZER_INSTANCE'] == 'STAGE':
                url = lae_stage_url
            else:
                url = lae_prod_url
        else:
            from sizer.views import get_user_details_from_ldap
            from sizer.local_settings import STAGE_FROM, STAGE_HOST
            from sizer.local_settings import local_stage_url

            sender_email = STAGE_FROM
            mailer_host = STAGE_HOST
            url = local_stage_url

        # Validate the users list
        base_error_msg = "Scenarios can only be shared with Cisco Partners & " \
                         "Employees. Unable to share with users: "
        record_err = "User(s) not found in database: "

        users_share_list, record_not_found, access_prohibited = self.validate_shared_users_list(users_list)

        '''
        for suser in users_list:

            user_name = suser['userid']

            if 'OPENSHIFT_REPO_DIR' in os.environ:
                if not suser['isExistingUser']:
                    user_details_from_ldap = get_user_details_from_ldap(user_name)
                    if 'error' in user_details_from_ldap:
                        return Response({'status': 'error',
                                         'errorMessage': 'Failed to connect '
                                                         'to LDAP Server for '
                                                         'validation of user: ' +
                                                         user_name},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    elif isinstance(user_details_from_ldap, str):
                        return Response({'status': 'error',
                                         'errorMessage': "User %s Not exist in database" % suser["userid"]},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    else:
                        user_details_object = User()
                        user_details_object.username = user_name
                        user_details_object.company = user_details_from_ldap['emp_company']
                        user_details_object.last_name = user_details_from_ldap['emp_sername'][0]
                        user_details_object.first_name = user_details_from_ldap['emp_firstname'][0]
                        user_details_object.email = user_details_from_ldap['emp_email_id'][0]
                        user_details_object.emp_id = user_details_from_ldap['emp_number'][0]
                        user_details_object.accesslevel = user_details_from_ldap['emp_access_level'][0]
                        user_details_object.save()
                        user_access_level = user_details_from_ldap['emp_access_level'][0]

                else:
                    try:
                        user_obj = User.objects.get(username=user_name)
                        user_access_level = user_obj.accesslevel
                    except (ObjectDoesNotExist, AttributeError):
                        logger.info('user detail not in DB: %s ', str(user_name))
                        return Response({'status': 'error',
                                         'errorMessage': record_err},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    if user_access_level == -1 or not user_access_level:
                        user_details_from_ldap = get_user_details_from_ldap(user_name)
                        if 'error' in user_details_from_ldap:
                            return Response({'status': 'error',
                                             'errorMessage': "Failed to connect to LDAP server for validation of user: " + user_name},
                                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                        # user record is available in database with accesslevel
                        #  -1 or NULL and not able to find the record in Ldap.
                        if isinstance(user_details_from_ldap, str):
                            user_access_level = -1
                        else:
                            user_access_level = user_details_from_ldap['emp_access_level'][0]
                        user_obj.accesslevel = user_access_level
                        user_obj.save()
            else:
                if suser['isExistingUser']:
                    try:
                        user_access_level = User.objects.get(username=user_name).accesslevel
                    except (AttributeError, ObjectDoesNotExist):
                        return Response({'status': 'error',
                                         'errorMessage': record_err},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return Response({'status': 'error',
                                     'errorMessage': record_err},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            if user_access_level < 3:
                users_non_ss = users_non_ss + user_name + ', '
            else:
                usr_list_ss.append(suser)
                '''

        # Deleting all the existing shared userid for this scenario id
        sScenarios = SharedScenario.objects.filter(scenario_id=id)
        if sScenarios:
            existing_users = [s_obj.userid for s_obj in sScenarios]
            sScenarios.delete()

        users_ss = ''
        for suser in users_share_list:
            if SharedScenario.objects.filter(scenario_id=id,
                                             userid=suser['userid']) or suser['userid'] == self.username:
                continue

            sharescenario = SharedScenario()
            sharescenario.scenario_id = id
            sharescenario.username = scenario.username
            sharescenario.userid = suser['userid']
            sharescenario.acl = suser['acl']
            sharescenario.is_secure = suser['is_secure']
            sharescenario.email = suser['email']
            sharescenario.save()

            if suser['userid'] not in existing_users:
                try:
                    users_ss = users_ss + suser['userid'] + ", "
                    user_email_id.append(User.objects.get(username=suser['userid']).email).encode('ascii', 'ignore')
                except (KeyError, ObjectDoesNotExist, AttributeError, ValueError):
                    logger.info('recipient email id is not found in DB %s. ', str(suser['userid']))

        message = Message(From=sender_email,
                          To=list(),
                          BCC=user_email_id,
                          charset='utf-8')
        message.Subject = 'Hyperflex Sizer: Scenario share notification'
        body_msg = 'Hi,\n   %s has shared %s scenario with you. ' \
                   'This scenario can be access under "shared with me" ' \
                   'tab on HyperFlex Sizer.\n%s'
        message.Body = body_msg % (Scenario.objects.get(id=id).username,
                                   scenario_name, url)
        sender = Mailer(mailer_host)
        try:
            logger.info('recipients email ids : %s ', str(user_email_id))
            logger.info('Message : %s ' % str(message.Body))
            sender.send(message)
        except Exception as err:
            logger.error('Mail has failed : %s' % str(err))

        if record_not_found:
            format_record_not_found = ['(' + record + ')' for record in record_not_found]
            return Response((users_list, record_err + ", ".join(format_record_not_found), record_not_found),
                            status=status.HTTP_200_OK)

        if access_prohibited:
            format_access_prohibited = ['(' + record + ')' for record in access_prohibited]
            return Response((users_list, base_error_msg + ", ".join(format_access_prohibited), access_prohibited),
                            status=status.HTTP_200_OK)

        suser_list = list()
        sScenarios = SharedScenario.objects.filter(scenario_id=id)
        if len(sScenarios) > 0:
            for scenario in sScenarios:
                user_details = dict()
                user_obj = User.objects.get(username=scenario.userid)
                user_details['email'] = user_obj.email
                user_details['userid'] = scenario.userid
                user_details['acl'] = scenario.acl
                user_details['is_secure'] = scenario.is_secure
                suser_list.append(user_details)

        logger.info('scenario %s has been shared with %s users. ' % (scenario_name, users_ss))

        return Response((suser_list, ), status=status.HTTP_200_OK)


    # The PUT and DELETE is not used as Shared Scenarios arent allowed to edit or delete
    def put(self, request, id, format=None):

        data = JSONParser().parse(request)

        users_list = data['users_list']

        for suser in users_list:
            user_obj = User.objects.get(email=suser['email'])
            userid = user_obj.username

            sScenario = SharedScenario.objects.filter(scenario_id=id, userid=userid)

            if len(sScenario) > 0:
                sScenario_result = sScenario[0]
                sScenario_result.acl = suser['acl']
                sScenario_result.is_secure = suser['is_secure']

                sScenario_result.save()

        suser_list = list()

        sScenarios = SharedScenario.objects.filter(scenario_id=id)
        if len(sScenarios) > 0:
            for scenario in sScenarios:
                user_details = dict()
                user_obj = User.objects.get(username=scenario.userid)
                user_details['email'] = user_obj.email
                user_details['userid'] = scenario.userid
                user_details['acl'] = scenario.acl
                user_details['is_secure'] = scenario.is_secure

                suser_list.append(user_details)

        return Response(suser_list, status=status.HTTP_200_OK)

    @staticmethod
    def delete(request, id, format=None):
        """
        To delete shared user name from a scenario
        """
        data = JSONParser().parse(request)

        users_list = data['users_list']
        for user in users_list:
            user_obj = User.objects.get(email=user['email'])
            userid = user_obj.username
            shared_result = SharedScenario.objects.filter(scenario_id=id, userid=userid)
            shared_result.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
