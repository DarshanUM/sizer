import os
import configparser
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from hyperconverged.models import LaeUsers


class SizerAccessNew(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    @staticmethod
    def process_request(self, request): 
        
        if "HTTP_AUTH_USER" in request.META:
    
            white_list_status = False
            if 'SIZER_INSTANCE' in os.environ:
                if os.environ['SIZER_INSTANCE'] == 'STAGE':
                    white_list_status = True
                else:
                    white_list_status = False

            if white_list_status:
                user = request.META["HTTP_AUTH_USER"]
                try:
                    LaeUsers.objects.get(username=user)
                except ObjectDoesNotExist:
                    return HttpResponse('<h3><b>This user does not have access to this Sizer instance<br>'
                                        'Please reach out to the HX team to request access</b></h3>')


class SizerAccess(object):

    @staticmethod
    def process_request(request):

        if "HTTP_AUTH_USER" in request.META:

            white_list_status = False
            if 'SIZER_INSTANCE' in os.environ:
                if os.environ['SIZER_INSTANCE'] == 'STAGE':
                    white_list_status = True
                else:
                    white_list_status = False

            if white_list_status:
                user = request.META["HTTP_AUTH_USER"]
                try:
                    LaeUsers.objects.get(username=user)
                except ObjectDoesNotExist:
                    return HttpResponse('<h3><b>This user does not have access to this Sizer instance<br>'
                                        'Please reach out to the HX team to request access</b></h3>')
