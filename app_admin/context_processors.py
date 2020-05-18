# utf-8
from app_admin.models import SysSetting
from django.conf import settings


def sys_setting(request):
    setting_dict = dict()
    setting_dict['mrdoc_version'] = settings.VERSIONS
    setting_dict['debug'] = settings.DEBUG
    datas = SysSetting.objects.filter(types="basic")
    for data in datas:
        setting_dict[data.name] = data.value
    return setting_dict
