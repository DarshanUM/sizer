import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sizer.local_settings")

django.setup()

from hyperconverged.models import Scenario, Results, User
from sizer.views import get_user_details_from_ldap

def update_user_details():
    users_list = User.objects.all()
    print ("Total Number of Users = ", len(users_list))

    emailcount = 0
    accesscount = 0
    inactiveusers = 0

    for user in users_list:
        username = user.username

        user_details_from_ldap = get_user_details_from_ldap(username)

        if 'error' in user_details_from_ldap:
            continue

        elif 'LDAP database' in user_details_from_ldap:
            inactiveusers += 1
            continue

        if len(user_details_from_ldap) == 0 or 'NameErr' in user_details_from_ldap:
            continue

        email_id = user_details_from_ldap['emp_email_id'][0]
        ldap_email_id = email_id.decode() if isinstance(email_id, bytes) else email_id

        if user.email != ldap_email_id:
            print ('%s Email: Database entry = %s -- LDAP entry = %s' % \
                  (username, user.email, ldap_email_id))
            user.email = ldap_email_id
            emailcount += 1
            user.save()

        # Retain David - dfoerster@geico.com access level at 3 based on Manish's feedback
        if username == 'davidfoerster':
            continue

        if user.accesslevel != int(user_details_from_ldap['emp_access_level'][0]):
            print ('%s AccessLevel: Database entry = %s -- LDAP entry = %s' % (username, user.accesslevel,
                                                                           user_details_from_ldap['emp_access_level'][0]))
            user.accesslevel = user_details_from_ldap['emp_access_level'][0]
            accesscount += 1
            user.save()

    print ("Updated mismatch email count %d" % emailcount)
    print ("Updated mismatch access level count %d" % accesscount)
    print ("Inactive/disabled users count %d" % inactiveusers)

