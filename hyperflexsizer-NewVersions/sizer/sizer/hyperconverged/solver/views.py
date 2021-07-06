# # Create your views here.
# from node_db.models import *
# from sizing import HyperConvergedVendorSizer
# import json
#
# parts_j = Part.objects.all()
# part_s = []
# for pat in parts_j:
#     part_s.append(json.loads(pat.part_json))
#
# node_s = []
#
# nodes_j = Node.objects.filter(status=True)
# for nd in nodes_j:
#     node_s.append(json.loads(nd.model_json))
#
# PART_FILE = 'parts_dell.json'
# NODE_FILE = 'nodes_dell_conf.json'
# WL_FILE = 'workload2.json'
#
# fh = open(PART_FILE)
# part_js = json.load(fh)
# fh.close()
#
# fh = open(NODE_FILE)
# node_js = json.load(fh)
# fh.close()
#
# fh = open(WL_FILE)
# wl_js = json.load(fh)
# fh.close()
#
# holi = VendorSizer()
#
# pd = {'parts':part_s}
# nds = {'models':node_s}
#
# x = json.dumps(pd)
# y = json.dumps(nds)
#
# x =json.dumps(part_js)
# y = json.dumps(node_js)
# z = json.dumps(wl_js)
#
# holi.load_data(x,y,z)
# holi.print_data()
# result = holi.solve()
