#
# # Create your views here.
# from node_db.models import *
# from sizing import VendorSizer
# import json
#
# parts_json = Part.objects.all()
# part_list = []
# for pat in parts_json:
#     part_list.append(json.loads(pat.part_json))
#
# node_list = []
#
# nodes_json = Node.objects.filter(status=True)
# for nd in nodes_json:
#     node_list.append(json.loads(nd.model_json))
#
# PART_FILE = 'parts_dell.json'
# NODE_FILE = 'nodes_dell_conf.json'
# WL_FILE = 'workload2.json'
#
# parts_file_obj = open(PART_FILE)
# part_js = json.load(parts_file_obj)
# parts_file_obj.close()
#
# node_file_obj = open(NODE_FILE)
# node_js = json.load(node_file_obj)
# node_file_obj.close()
#
# work_load_file_obj = open(WL_FILE)
# wl_js = json.load(work_load_file_obj)
# work_load_file_obj.close()
#
# holi = VendorSizer()
#
# pd = {'parts': part_list}
# nds = {'models': node_list}
#
# parts = json.dumps(pd)
# nodes = json.dumps(nds)
#
# parts_json = json.dumps(part_js)
# node_json = json.dumps(node_js)
# workload_json = json.dumps(wl_js)
#
# holi.load_data(parts_json, node_json, workload_json)
# holi.print_data()
# result = holi.solve()
