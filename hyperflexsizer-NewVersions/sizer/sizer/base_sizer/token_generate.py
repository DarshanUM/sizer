from rest_framework.authtoken.models import Token
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.renderers import JSONRenderer
import datetime

from base_sizer.solver.attrib import BaseConstants


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)
        
@csrf_exempt
def token_expire(view_func ):
    def inner_func(request, *args, **kwargs):

        try:
            tkn = request.META["HTTP_AUTHORIZATION"]
        except (AttributeError, KeyError):
            er = JSONResponse({'status': 'error',
                               'errorCode': '101',
                               'errorMessage': BaseConstants.MSG_101})
            return er

        try:
            usrname = User.objects.get(auth_token=tkn[6:])
        except ObjectDoesNotExist:
            er = JSONResponse({'status': 'error',
                               'errorCode': '102',
                               'errorMessage': BaseConstants.MSG_102})
            return er

        token_object = Token.objects.get(key = tkn[6:])
        created = timezone.make_aware(token_object.created,timezone.utc)
        now = datetime.datetime.now(timezone.utc)
        diff = now - created

        if settings.TOKEN_LIFE_SPAN > diff:
            return view_func(request, *args, **kwargs)
        else:
            token_object.delete()
            er = JSONResponse({'status': 'error',
                               'errorCode': '102',
                               'errorMessage': "Token is expired"})
            return er

    return inner_func
