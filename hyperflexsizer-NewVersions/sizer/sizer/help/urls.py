from django.urls import path
from .helppage import GetHelpDetails

urlpatterns = [
    path(r'videos', GetHelpDetails.as_view())
]
