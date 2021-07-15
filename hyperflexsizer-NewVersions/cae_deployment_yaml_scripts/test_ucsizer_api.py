
import requests
import json

# # Local UCSizer API Test
# api_url = "http://localhost:9000/api/sizing_result"
# api_call_headers = {'Authorization': '03011f56614a48b7e76642149b9e1e7ecad55fa2', "content-type": "application/json"}
# data = {"vcpus": 2, "ram_size_unit": "GiB", "ram_size": 128, "hdd_size_unit": "GB", "hdd_size": 1000}
#
# api_call_response = requests.post(api_url, headers=api_call_headers, data=json.dumps(data), verify=False)
#
# print ("Sizing result: ")
# print (api_call_response.text)
# exit()


# # To Test UCSizer API Access on CAE STAGE # #
# STEP 1:  To get the bearer token from Stage token URL
token_url = "https://cloudsso-test.cisco.com/as/token.oauth2"

# client credentials for non-prod env
client_id = 'cae_stage_oauth_api'
client_secret = 'interstellar'
data = {'grant_type': 'client_credentials'}

access_token_response = requests.post(token_url, data=data, verify=False, allow_redirects=False, auth=(client_id, client_secret))

print (access_token_response.text)

# STEP 2 - Make a API call to get Sizer Result with Token
api_url = "https://hyperflexsizer-stage.cloudapps.cisco.com/api/sizing_result"
tokens = json.loads(access_token_response.text)
#print "Bearer token: " + tokens['access_token']

api_call_headers = {'Authorization': 'Bearer ' + tokens['access_token'],
                    'content-type': 'application/json'}
data = {
        "cpu_attribute": "vcpus",
        "cpu_clock": 35,
        "vcpus": 2,
        "ram_size_unit": "GiB",
        "ram_size": 128,
        "hdd_size_unit": "GB",
        "hdd_size": 1000,
        "fault_tolerance": 1,
        "nodetype": "cto"
    }

api_call_response = requests.post(api_url, headers=api_call_headers, data=json.dumps(data), verify=False)

print ("Sizing result: ")
print (api_call_response.text)
