# from copy import deepcopy
# from collections import defaultdict
#
# from django.http import HttpResponse
#
# from utils.utility import JSONResponse
# from utils.baseview import BaseView
#
# from rest_framework.authtoken.models import Token
# from rest_framework.parsers import JSONParser
#
# from rest_framework.response import Response
# from rest_framework import status
#
# from hyperconverged.models import Node
#
# from hyperconverged.models import Part
# from hyperconverged.strings import FIXED
# import hyperconverged.serializer.NodeSerializer as node_serializer


# def user_verification(tkn):
#     token_obj = Token
#     sa = token_obj.objects.filter().order_by("user_id")
#     status = False
#     for i in sa:
#         j = "Token " + str(i)
#         if str(tkn) == j:
#             status =  True
#     return status


# class nodes(BaseView):
#     """
#     List all nodes, or create a node.
#     """
#     def get(self, request, format=None):
#         nodes = Node.objects.filter(status=True).order_by('name')
#
#         serializer = node_serializer.NodeGetSerializer(nodes, many=True)
#         return Response(serializer.data)
#
#     def post(self, request, format=None):
#         data = JSONParser().parse(request)
#         type = data.get('type',None)
#         if type:
#             if data['type'] == FIXED:
#                 serializer = node_serializer.FixedNodeSerializer(data=data)
#             else:
#                 serializer = node_serializer.ConfNodeSerializer(data=data)
#             if serializer.is_valid():
#                 nd = Node()
#                 nd.name = serializer.data['name']
#                 nd.node_json = serializer.data
#                 nd.save()
#                 dt = serializer.data
#                 dt['id'] = nd.id
#                 return Response(dt, status=status.HTTP_201_CREATED)
#         else:
#             return Response({'status':'error', 'errorMessage':'Json not defined properly'}, status=status.HTTP_400_BAD_REQUEST)
#
#         return JSONResponse({'status':'error','errorMessage':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# class node_detail(BaseView):
#     """
#     Retrieve, update or delete specific node .
#     """
#     def get(self, request, id, format=None):
#         try:
#             node = Node.objects.get(id=id, status=True)
#         except Node.DoesNotExist:
#             return HttpResponse(status=status.HTTP_404_NOT_FOUND)
#         serializer = node_serializer.NodeGetSerializer(node)
#         return Response(serializer.data)
#
#     def put(self, request, id, format=None):
#         try:
#             node = Node.objects.get(id=id,status=True)
#         except Node.DoesNotExist:
#             return HttpResponse(status=status.HTTP_404_NOT_FOUND)
#
#         data = JSONParser().parse(request)
#         node_model_json = node.node_json
#         if node_model_json['type'] == FIXED:
#             serializer = node_serializer.FixedNodePutSerializer(node, data=data)
#         else:
#             serializer = node_serializer.ConfPutNodeSerializer(node, data=data)
#         if serializer.is_valid():
#             if node.status:
#                 node.node_json = data
#                 node.save()
#                 return Response(data)
#             else:
#                 return Response({'status':'error', 'errorMessage':'This node is deprecated.'})
#         return Response({'status':'error', 'errorMessage':serializer.errors}, status=status.HTTP_404_NOT_FOUND)
#
#     def delete(self,request,id,format=None):
#         try:
#             node = Node.objects.get(id=id, status=True)
#         except Node.DoesNotExist:
#             return HttpResponse(status=status.HTTP_404_NOT_FOUND)
#         node.status = False
#         node.save()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# class get_all_nodes(BaseView):
#
#     """
#     Retrieve all  nodes .
#     """
#     def get(self,request,format=None):
#         try:
#             nodes = Node.objects.filter(status=True).defer('status', 'created_date').order_by('name')
#         except Node.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#         node_list = []
#         for nod in nodes:
#             onenode = {}
#             onenode['model'] = nod.name
#             node_db_desc =  nod.node_json
#             subtype = str(node_db_desc['subtype'])
#
#             cpu_desc = []
#             ram_desc = []
#             hdd_desc = []
#             ssd_desc = []
#
#             for slot in node_db_desc['cpu_socket_count']:
#                 if slot == 0:
#                     continue
#                 for option in node_db_desc['cpu_options']:
#                     cpu_desc.append(str(slot) + "x" + option)
#
#             for slot in node_db_desc['ram_slots']:
#                 if slot == 0:
#                     continue
#                 for option in node_db_desc['ram_options']:
#                     ram_desc.append(str(slot) + "x" + option)
#
#             for slot in node_db_desc['hdd_slots']:
#                 if slot == 0:
#                     continue
#                 for option in node_db_desc['hdd_options']:
#                     hdd_desc.append(str(slot) + "x" + option)
#
#             for slot in node_db_desc['ssd_slots']:
#                 if slot == 0:
#                     continue
#                 for option in node_db_desc['ssd_options']:
#                     ssd_desc.append(str(slot) + "x" + option)
#
#             description = {
#              'CPU_Type': cpu_desc,
#              'subtype' : subtype,
#              'RAM_Options': ram_desc,
#              'HDD_Options': hdd_desc,
#              'SSD_Options': ssd_desc
#             }
#             onenode['description'] = description
#             node_list.append(onenode)
#         resp = {"node_list":node_list}
#         return Response(resp, status=status.HTTP_200_OK)
