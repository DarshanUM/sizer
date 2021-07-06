import django
import os
import ldap
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sizer.local_settings")
 
django.setup()
 
from hyperconverged.models import *
 
output_array = []
 
output = {}

scenario_list = Scenario.objects.values_list('username', flat=True).distinct()

LDAP_URL = 'ldap://dsx.cisco.com:389'
LDAP_BIND_DETAILS = 'uid=hxsizerad.gen,OU=Generics,O=cco.cisco.com'
LDAP_PASSWORD = 'Agile@123'

def  get_user_details_from_ldap(userid):

    user_details = dict()
    try:
        connect = ldap.initialize(LDAP_URL)
        connect.simple_bind_s(LDAP_BIND_DETAILS, LDAP_PASSWORD)
        connect.protocol_version = ldap.VERSION3
    except:
        return 'error : not able to connect the LDAP  '

    base_dn = 'uid=' + userid  + ',OU=ccoentities,O=cco.cisco.com'
    search_scope = ldap.SCOPE_SUBTREE
    retrieve_attributes = ['company', 'givenName', 'sn', 'employeeNumber', 'mail', 'lastLogin', 'accessLevel']
    search_filter = "cn=*"

    try:
        ldap_result_id = connect.search(base_dn, search_scope, search_filter, retrieve_attributes)
        while True:
            result_type, result_data = connect.result(ldap_result_id, 0)
            if (result_data == []):
                break
            else:
                if result_type == ldap.RES_SEARCH_ENTRY:
                    user_details['emp_number'] = result_data[0][1]['employeeNumber']
                    user_details['emp_email_id'] = result_data[0][1]['mail']
                    user_details['emp_company'] = result_data[0][1]['company'][0]
                    user_details['emp_firstname'] = result_data[0][1]['givenName']
                    user_details['emp_sername'] = result_data[0][1]['sn']
                    user_details['emp_last_login']= result_data[0][1]['lastLogin']
                    user_details['emp_access_level'] = result_data[0][1]['accessLevel']
    except:
            return 'error : Not able to find the data in LDAP database'
    return user_details



if __name__ == '__main__':
    scenarios_user_list = Scenario.objects.values_list('username', flat=True).distinct()
    for userid in scenarios_user_list:
        user_details_from_ldap = dict()
        user_details_object = User()
        if User.objects.filter(username=userid).exists():
            continue
        try:
            user_details_from_ldap = get_user_details_from_ldap(userid) 
        except:
            pass
        if not user_details_from_ldap:
            continue
        else:
            # user_details_object = User()
            user_details_object.username = userid
            user_details_object.company = user_details_from_ldap['emp_company']
            user_details_object.last_name = user_details_from_ldap['emp_sername'][0]
            user_details_object.first_name = user_details_from_ldap['emp_firstname'][0]
            user_details_object.email = user_details_from_ldap['emp_email_id'][0]
            user_details_object.emp_id = user_details_from_ldap['emp_number'][0]
            user_details_object.save()
  

