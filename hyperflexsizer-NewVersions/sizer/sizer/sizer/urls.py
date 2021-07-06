from django.urls import path, include
from django.contrib import admin

from . import local_settings
from .views import EnvInfo, AuthInfo, UserData, UCSizer_SizingResult
from hyperconverged.views.profiler_api_views import ProfilerSizing
from django.http import HttpResponseRedirect
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import re_path
from django.views.static import serve

urlpatterns = [
    path(r'hyperconverged/', include('hyperconverged.urls')),
    path(r'auth/login/', AuthInfo.as_view()),
    path(r'', lambda r: HttpResponseRedirect('ui/index.html')),
    path(r'userdata', UserData.as_view()),
    path(r'envinfo', EnvInfo.as_view()),
    path(r'help/', include('help.urls')),
    re_path(r'ui/(?P<path>.*)', serve, {'document_root': local_settings.UI_ROOT}),

    path(r'api/sizing_result', UCSizer_SizingResult.as_view()),
    path(r'api/profile_upload', ProfilerSizing.as_view()),

    # This is added for refresh issue
    # re_path(r'an/', lambda r: HttpResponseRedirect('ui/index.html'))
    re_path(r'list/$', lambda r: HttpResponseRedirect('/')),
    re_path(r'scenario-details/(?P<id>\w+)/$', lambda r,id: HttpResponseRedirect('/')),
    re_path(r'an/', lambda r: HttpResponseRedirect('/'))
]

urlpatterns = format_suffix_patterns(urlpatterns)

