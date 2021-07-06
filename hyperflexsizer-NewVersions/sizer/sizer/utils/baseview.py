from rest_framework.views import APIView

from django.contrib.auth import get_user_model
User = get_user_model()

HTTP_AUTH_USER = 'HTTP_AUTH_USER'
HTTP_AUTH = "HTTP_AUTHORIZATION"


class BaseView(APIView):

    def dispatch(self, request, *args, **kwargs):
        self.user_validator(request.META)
        return super(BaseView, self).dispatch(request, *args, **kwargs)

    def user_validator(self, obj):

        if HTTP_AUTH_USER in obj:
           self.username = obj[HTTP_AUTH_USER]

        elif HTTP_AUTH in obj:
            token = obj[HTTP_AUTH]
            try:
                self.username = User.objects.get(auth_token=token).username
            except Exception as e:
                raise Exception("Unauthorized Access")
        else:
            raise Exception("Unauthorized Access")
