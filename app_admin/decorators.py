# utf-8
from django.core.exceptions import PermissionDenied
from django.http import Http404
from app_admin.models import SysSetting


def superuser_only(function):
    def _inner(request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_superuser:
                raise PermissionDenied
        else:
            raise PermissionDenied
        return function(request, *args, **kwargs)
    return _inner


def open_register(function):
    def _inner(request, *args, **kwargs):
        try:
            status = SysSetting.objects.get(name='close_register')
        except Exception as e:
            return function(request, *args, **kwargs)
        if status.value == 'on':
            raise Http404
        return function(request, *args, **kwargs)
    return _inner


def check_headers(function):
    def _inner(request, *args, **kwargs):
        metas = request.META
        if 'HTTP_USER_AGENT' not in metas:
            raise Http404
        return function(request, *args, **kwargs)
    return _inner


def allow_report_file(function):
    def _inner(request, *args, **kwargs):
        try:
            status = SysSetting.objects.get(name='enable_project_report')
        except Exception as e:
            raise Http404
        if status.value == 'on':
            return function(request, *args, **kwargs)
        else:
            raise Http404
    return _inner
