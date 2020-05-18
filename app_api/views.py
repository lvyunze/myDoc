# utf-8
from django.shortcuts import render
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from app_api.models import UserToken
from app_doc.models import Project, Doc
import time
import hashlib
import traceback
from django.conf import settings
from app_doc.util_upload_img import base_img_upload
from loguru import logger


@require_http_methods(['POST', 'GET'])
@login_required()
def manage_token(request):
    if request.method == 'GET':
        try:
            token = UserToken.objects.get(user=request.user).token
        except ObjectDoesNotExist:
            token = '你还没有生成过Token！'
        except Exception as e:
            if settings.DEBUG:
                print(traceback.print_exc())
                logger.exception("Token管理页面异常")
        return render(request, 'app_api/manage_token.html', locals())
    elif request.method == 'POST':
        try:
            user = request.user
            now_time = str(time.time())
            string = 'user_{}_time_{}'.format(user, now_time).encode('utf-8')
            token_str = hashlib.sha224(string).hexdigest()
            user_token = UserToken.objects.filter(user=user)
            if user_token.exists():
                UserToken.objects.get(user=user).delete()
            UserToken.objects.create(
                user=user,
                token=token_str
            )
            return JsonResponse({'status': True, 'data': token_str})
        except Exception as e:
            logger.exception("用户Token生成异常")
            return JsonResponse({'status': False, 'data': '生成出错，请重试！'})


@require_GET
def get_projects(request):
    token = request.GET.get('token', '')
    try:
        token = UserToken.objects.get(token=token)
        projects = Project.objects.filter(create_user=token.user)
        project_list = []
        for project in projects:
            item = {
                'id': project.id,
                'name': project.name,
                'type': project.role
            }
            project_list.append(item)
        return JsonResponse({'status': True, 'data': project_list})
    except ObjectDoesNotExist:
        return JsonResponse({'status': False, 'data': 'token无效'})
    except Exception as e:
        logger.exception("token获取文集异常")
        return JsonResponse({'status': False, 'data': '系统异常'})


@require_http_methods(['GET', 'POST'])
@csrf_exempt
def create_doc(request):
    token = request.GET.get('token', '')
    project_id = request.POST.get('pid', '')
    doc_title = request.POST.get('title', '')
    doc_content = request.POST.get('doc', '')
    try:
        token = UserToken.objects.get(token=token)
        is_project = Project.objects.filter(create_user=token.user, id=project_id)
        if is_project.exists():
            Doc.objects.create(
                name=doc_title,
                pre_content=doc_content,
                top_doc=project_id,
                create_user=token.user
            )
            return JsonResponse({'status': True, 'data': 'ok'})
        else:
            return JsonResponse({'status': False, 'data': '非法请求'})
    except ObjectDoesNotExist:
        return JsonResponse({'status': False, 'data': 'token无效'})
    except Exception as e:
        logger.exception("token创建文档异常")
        return JsonResponse({'status': False, 'data': '系统异常'})


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def upload_img(request):
    token = request.GET.get('token', '')
    base64_img = request.POST.get('data', '')
    try:
        token = UserToken.objects.get(token=token)
        result = base_img_upload(base64_img, '', token.user)
        return JsonResponse(result)
    except ObjectDoesNotExist:
        return JsonResponse({'success': 0, 'data': 'token无效'})
    except Exception as e:
        logger.exception("token上传图片异常")
        return JsonResponse({'success': 0, 'data': '上传出错'})
