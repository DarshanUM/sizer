# from django.http import HttpResponse
# import json
# import httplib
# from django.contrib.auth.decorators import login_required
# from django.template import RequestContext
# from django.core.urlresolvers import reverse
# from django.http import HttpResponseRedirect
# from hyperconverged.models import Part,Node
# #import hyperconverged.models as  models
# from rest_framework.decorators import api_view
# from django.shortcuts import render_to_response
# from django.views.decorators.csrf import csrf_exempt
# from rest_framework.renderers import JSONRenderer
# from rest_framework.parsers import JSONParser
# from hyperconverged.serializer.PartSerializer import PartSerializer, \
# PartGetSerializer,PartPutSerializer
# import hyperconverged.serializer.NodeSerializer  as node_serializer
# from hyperconverged.strings import FIXED
# from utils.utility import JSONResponse
# from rest_framework.authtoken.models import Token
# from base_sizer.token_generate import token_expire
# from utils.baseview import BaseView
#
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
#
# def user_verification(tkn):
#     token_obj = Token
#     sa = token_obj.objects.filter( ).order_by("user_id")
#     status = False
#     for i in sa:
#         j = "Token "+str(i)
#         if str(tkn) == j:
#             status =  True
#     return status
#
# class parts(BaseView):
#     """
#     List all parts, or create a part.
#     """
#     def get(self,request,format=None):
#         parts = Part.objects.all().order_by('id')
#         serializer = PartGetSerializer(parts, many=True)
#         return Response(serializer.data)
#
#     def post(self,request,format=None):
#         data = JSONParser().parse(request)
#         serializer = PartSerializer(data=data)
#         if serializer.is_valid():
#             pt  = Part()
#             pt.name = serializer.data['name']
#             pt.part_json = serializer.data
#             pt.save()
#             resp = serializer.data
#             resp['id'] = pt.id
#             return Response(resp, status=status.HTTP_201_CREATED)
#         return Response({'status' : 'error' ,'errorMessage':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
#
#
#
# class part_detail(BaseView):
#     """
#     Retrieve, update or delete specific part .
#     """
#     def get(self, request, part_id, format=None):
#         try:
#             part = Part.objects.get(id = part_id,status = True)
#         except Part.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#
#         serializer = PartGetSerializer(part)
#         return Response(serializer.data)
#
#     def put(self, request, part_id, format=None):
#         try:
#             part = Part.objects.get(id = part_id,status = True)
#         except Part.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#         data = JSONParser().parse(request)
#         serializer = PartPutSerializer(part, data=data)
#         if serializer.is_valid():
#             if part.status:
#                 wl = part
#                 wl.part_json = data
#                 wl.save()
#                 data['id'] = wl.id
#                 return Response(data)
#             else:
#                 return Response({'status' : 'error' ,'errorMessage':'This node is deprecated.'})
#
#         return Response({'status' : 'error' ,'errorMessage':serializer.errors}, status=status.HTTP_404_NOT_FOUND)
#
#     def delete(self, request, part_id, format=None):
#         try:
#             part = Part.objects.get(id = part_id,status = True)
#         except Part.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#         part.status = False
#         part.save()
#         return Response(status=status.HTTP_204_NO_CONTENT)
#
