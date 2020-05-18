# utf-8
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import datetime
import time
import json
import base64
import os
from app_doc.models import Image


@login_required()
@csrf_exempt
def upload_img(request):
    img = request.FILES.get("editormd-image-file", None)
    manage_upload = request.FILES.get('manage_upload', None)
    dir_name = request.POST.get('dirname', '')
    base_img = request.POST.get('base', None)
    if img:
        result = img_upload(img, dir_name, request.user)
    elif manage_upload:
        result = img_upload(manage_upload, dir_name, request.user)
    elif base_img:
        result = base_img_upload(base_img, dir_name, request.user)
    else:
        result = {"success": 0, "message": "出错信息"}
    return HttpResponse(json.dumps(result), content_type="application/json")


def upload_generation_dir(dir_name=''):
    today = datetime.datetime.today()
    dir_name = dir_name + '/%d%02d/' % (today.year, today.month)
    if not os.path.exists(settings.MEDIA_ROOT + dir_name):
        os.makedirs(settings.MEDIA_ROOT + dir_name)
    return dir_name


def img_upload(files, dir_name, user):
    allow_suffix = ["jpg", "jpeg", "gif", "png", "bmp", "webp"]
    file_suffix = files.name.split(".")[-1]
    if file_suffix not in allow_suffix:
        return {"success": 0, "message": "图片格式不正确"}

    relative_path = upload_generation_dir(dir_name)
    file_name = files.name.replace(file_suffix, '').replace('.', '') + '_' + str(int(time.time())) + '.' + file_suffix
    path_file = os.path.join(relative_path, file_name)
    path_file = settings.MEDIA_ROOT + path_file
    file_url = settings.MEDIA_URL + relative_path + file_name
    with open(path_file, 'wb') as f:
        for chunk in files.chunks():
            f.write(chunk)
    Image.objects.create(
        user=user,
        file_path=file_url,
        file_name=file_name,
        remark='本地上传',
    )
    return {"success": 1, "url": file_url, 'message': '上传图片成功'}


def base_img_upload(files, dir_name, user):
    files_str = files.split(';base64,')[-1]
    files_base = base64.b64decode(files_str)
    relative_path = upload_generation_dir(dir_name)
    file_name = str(datetime.datetime.today()).replace(':', '').replace(' ', '_').split('.')[0] + '.png'
    path_file = os.path.join(relative_path, file_name)
    path_file = settings.MEDIA_ROOT + path_file
    file_url = settings.MEDIA_URL + relative_path + file_name
    with open(path_file, 'wb') as f:
        f.write(files_base)
    Image.objects.create(
        user=user,
        file_path=file_url,
        file_name=file_name,
        remark='粘贴上传',
    )
    return {"success": 1, "url": file_url, 'message': '上传图片成功'}
