# utf-8
from app_admin.models import SysSetting
from django.contrib.auth.decorators import login_required
import re


class RequiredLoginMiddleware():
    def __init__(self, get_response):
        self.get_response = get_response
        compile_tuple = (r'/user/login(.*)$', r'/user/logout(.*)$',
                         r'/user/register(.*)$', r'/user/check_code(.*)$')
        self.exceptions = tuple(re.compile(url) for url in compile_tuple)

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated:
            return None

        try:
            data = SysSetting.objects.get(name='require_login').value
            if data == 'on':
                is_exceptions = False
                for url in self.exceptions:
                    if url.match(request.path):
                        is_exceptions = True
                if is_exceptions:
                    return None
                else:
                    return login_required(view_func)(request, *view_args,
                                                     **view_kwargs)
            else:
                return None
        except Exception as e:
            return None
