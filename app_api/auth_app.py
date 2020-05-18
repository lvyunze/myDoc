# utf-8
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from app_api.models import *


class AppAuth(BaseAuthentication):
    def authenticate(self, request):
        token = request.query_params.get('token')
        if token:
            user_obj = AppUserToken.objects.filter(token=token).first()
            if user_obj:
                return user_obj.user, token
            else:
                return None
        else:
            return None


class AppMustAuth(BaseAuthentication):
    def authenticate(self, request):
        token = request.query_params.get('token')
        if token:
            user_obj = AppUserToken.objects.filter(token=token).first()
            if user_obj:
                return user_obj.user, token
            else:
                raise AuthenticationFailed('无效的token')
        else:
            raise AuthenticationFailed('请求的URL中必须携带token参数')
