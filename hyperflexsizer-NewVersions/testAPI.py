import json
import os
import requests
import sys

	
BASE_DIR = os.path.join(os.getcwd(), "..")
sys.path.append(os.path.join(BASE_DIR))
	
	
	
API_SCENARIO = "/hyperconverged/Scenario/scenarios/"
API_WL_DETAIL = "/hyperconverged/Scenario/scenariodetail/69"
API_AUTH = "/auth/login/"
URL = "http://10.11.0.173:9090"
URL_SCEN = URL + API_SCENARIO
URL_WL = URL + API_WL_DETAIL
URL_AUTH = URL + API_AUTH
AUTH_HEADER = {"content_type": "application/json"}
AUTH_DATA = {"username": "admin", "password": "admin"}
	
	
auth = requests.post(url=URL_AUTH, data=AUTH_DATA, headers=AUTH_HEADER)
token = json.loads(auth.text)["auth_token"]

	
def get_Scenarios():

#	headers_post = {'Authorization': token, 'content-type': 'application/json'}
	
#	        response = requests.post(URL_CONF, data=data, headers=headers_post)
	
#	headers_put = {'Authorization': token}
#		response = requests.put(url, headers=headers_put, files=files)

	'''	
	headers_get = {'Authorization': 'Token ' + token, 'content-type': 'application/json'}
	url = URL_SCEN
	response = requests.get(url, headers=headers_get)


	headers_get = {'Authorization': 'Token ' + token, 'content-type': 'application/json'}
	url = URL_WL
	response = requests.get(url, headers=headers_get)

	'''
#	wl_data = {"wl_list":[{"avg_iops_per_desktop":30,"gold_image_size":20,"profile_type":"Task Worker","wl_name":"VDI_1","wl_type":"VDI","vcpus_per_core":10,"disk_per_desktop":5,"num_desktops":1,"ram_per_desktop":2,"replication_factor":2,"provisioning_type":"View Linked Clones","vcpus_per_desktop":1,"compression_factor":0}],"model_list":[],"name":"vdi","model_choice":"None"}

	wl_data = {"model_list":[],"model_choice":"None","wl_list":[{"wl_name":"VDI_1","wl_type":"VDI","profile_type":"Task Worker","provisioning_type":"View Linked Clones","avg_iops_per_desktop":30,"gold_image_size":20,"vcpus_per_desktop":1,"vcpus_per_core":10,"disk_per_desktop":5,"num_desktops":1,"ram_per_desktop":2,"replication_factor":2,"compression_factor":0}],"name":"vdi"}

#	data = JSONViewer()
	
	headers_put = {'Authorization': 'Token ' + token, 'content-type': 'application/json'}
	url = URL_WL
	response = requests.put(url, headers=headers_put, data=wl_data)


get_Scenarios()
