# utf-8
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.conf import settings
from rest_framework.views import APIView
from app_api.models import AppUserToken
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from app_api.serializers_app import *
from app_api.auth_app import AppAuth, AppMustAuth
from app_doc.views import validateTitle
from app_doc.util_upload_img import img_upload, base_img_upload
from loguru import logger
import datetime
import os
import time
import hashlib


def get_token_code(username):
    timestamp = str(time.time())
    m = hashlib.md5(username.encode("utf-8"))
    m.update(timestamp.encode("utf-8"))
    return m.hexdigest()


class LoginView(APIView):
    def post(self, request):
        res = {"code": 0}
        username = request.data.get("username")
        password = request.data.get("password")
        user_obj = authenticate(username=username, password=password)
        if user_obj:
            if user_obj.is_active:
                token = get_token_code(username)
                AppUserToken.objects.update_or_create(defaults={"token": token},
                                                      user=user_obj)
                res["token"] = token
            else:
                res["error"] = '账号被禁用'

        else:
            res["code"] = 1
            res["error"] = "用户名或密码错误"
        return Response(res)


class ProjectView(APIView):
    authentication_classes = (AppAuth,)

    def get(self, request):
        global role_list, project_list
        pro_id = request.query_params.get('id', None)
        if pro_id:
            resp = dict()
            project = Project.objects.get(id=int(pro_id))
            if request.auth:
                colla_user = ProjectCollaborator.objects.filter(project=project,
                                                                user=request.user).count()
            else:
                colla_user = 0

            try:
                allow_download = ProjectReport.objects.get(project=project)
            except:
                allow_download = False
            if (project.role == 1) and (request.user != project.create_user) and (colla_user == 0):
                resp['code'] = 2
            elif project.role == 2:
                user_list = project.role_value
                if request.auth:
                    if (request.user.username not in user_list) and \
                            (request.user != project.create_user) and \
                            (colla_user == 0):
                        resp['code'] = 2
                else:
                    resp['code'] = 2
            elif project.role == 3:
                if request.user != project.create_user and colla_user == 0:
                    viewcode = project.role_value
                    viewcode_name = 'viewcode-{}'.format(project.id)
                    r_viewcode = request.data.get(viewcode_name, 0)
                    if viewcode != r_viewcode:
                        resp['code'] = 3
            else:
                serializer = ProjectSerializer(project)
                resp = {'code': 0, 'data': serializer.data}
            return Response(resp)

        else:
            kw = request.query_params.get('kw', '')
            sort = request.query_params.get('sort', 0)
            role = request.query_params.get('role', -1)
            if sort in ['', 0, '0']:
                sort_str = ''
            else:
                sort_str = '-'

            if kw == '':
                is_kw = False
            else:
                is_kw = True

            if request.auth:
                is_auth = True
            else:
                is_auth = False

            if role in ['', -1, '-1']:
                is_role = False
                role_list = [0, 3]
            else:
                is_role = True

            if (is_kw is False) and (is_auth) and (is_role is False):
                colla_list = [i.project.id for i in ProjectCollaborator.objects.filter(
                    user=request.user
                )]
                project_list = Project.objects.filter(
                    Q(role__in=role_list) | \
                    Q(role=2, role_value__contains=str(request.user.username)) | \
                    Q(create_user=request.user) | \
                    Q(id__in=colla_list)
                ).order_by("{}create_time".format(sort_str))

            elif (is_kw is False) and (is_auth) and (is_role):
                if role in ['0', 0]:
                    project_list = Project.objects.filter(role=0).order_by(
                        "{}create_time".format(sort_str
                                               ))
                elif role in ['1', 1]:
                    project_list = Project.objects.filter(create_user=request.user, role=1).order_by(
                        "{}create_time".format(sort_str))
                elif role in ['2', 2]:
                    project_list = Project.objects.filter(
                        role=2, role_value__contains=str(request.user.username)
                    ).order_by(
                        "{}create_time".format(sort_str))
                elif role in ['3', 3]:
                    project_list = Project.objects.filter(role=3).order_by(
                        "{}create_time".format(sort_str)
                    )
                elif role in ['99', 99]:
                    colla_list = [i.project.id for i in
                                  ProjectCollaborator.objects.filter(user=request.user)]
                    project_list = Project.objects.filter(id__in=colla_list).order_by(
                        "{}create_time".format(sort_str)
                    )
                else:
                    return Response({'code': 2, 'data': []})

            elif (is_kw is False) and (is_auth is False) and (is_role is False):
                project_list = Project.objects.filter(role__in=[0, 3]).order_by(
                    "{}create_time".format(sort_str)
                )

            elif (is_kw is False) and (is_auth is False) and (is_role):
                if role in ['0', 0]:
                    project_list = Project.objects.filter(role=0).order_by(
                        "{}create_time".format(sort_str)
                    )
                elif role in ['3', 3]:
                    project_list = Project.objects.filter(role=3).order_by(
                        "{}create_time".format(sort_str)
                    )
                else:
                    return Response({'code': 2, 'data': []})

            elif (is_kw) and (is_auth) and (is_role is False):
                colla_list = [i.project.id for i in ProjectCollaborator.objects.filter(
                    user=request.user
                )]
                project_list = Project.objects.filter(
                    Q(role__in=[0, 3]) | \
                    Q(role=2, role_value__contains=str(request.user.username)) | \
                    Q(create_user=request.user) | \
                    Q(id__in=colla_list),
                    Q(name__icontains=kw) | Q(intro__icontains=kw)
                ).order_by('{}create_time'.format(sort_str))

            elif (is_kw) and (is_auth) and (is_role):
                if role in ['0', 0]:
                    project_list = Project.objects.filter(
                        Q(name__icontains=kw) | Q(intro__icontains=kw),
                        role=0
                    ).order_by("{}create_time".format(sort_str))
                elif role in ['1', 1]:
                    project_list = Project.objects.filter(
                        Q(name__icontains=kw) | Q(intro__icontains=kw),
                        create_user=request.user
                    ).order_by("{}create_time".format(sort_str))
                elif role in ['2', 2]:
                    project_list = Project.objects.filter(
                        Q(name__icontains=kw) | Q(intro__icontains=kw),
                        role=2,
                        role_value__contains=str(request.user.username)
                    ).order_by("{}create_time".format(sort_str))
                elif role in ['3', 3]:
                    project_list = Project.objects.filter(
                        Q(name__icontains=kw) | Q(intro__icontains=kw),
                        role=3
                    ).order_by("{}create_time".format(sort_str))
                elif role in ['99', 99]:
                    colla_list = [i.project.id for i in
                                  ProjectCollaborator.objects.filter(user=request.user)]
                    project_list = Project.objects.filter(
                        Q(name__icontains=kw) | Q(intro__icontains=kw),
                        id__in=colla_list
                    ).order_by("{}create_time".format(sort_str))
                else:
                    return Response({'code': 1, 'data': []})

            elif (is_kw) and (is_auth is False) and (is_role is False):
                project_list = Project.objects.filter(
                    Q(name__icontains=kw) | Q(intro__icontains=kw),
                    role__in=[0, 3]
                ).order_by("{}create_time".format(sort_str))

            elif (is_kw) and (is_auth is False) and (is_role):
                if role in ['0', 0]:
                    project_list = Project.objects.filter(
                        Q(name__icontains=kw) | Q(intro__icontains=kw),
                        role=0
                    ).order_by("{}create_time".format(sort_str))
                elif role in ['3', 3]:
                    project_list = Project.objects.filter(
                        Q(name__icontains=kw) | Q(intro__icontains=kw),
                        role=3
                    ).order_by("{}create_time".format(sort_str))
                else:
                    return Response({'code': 1, 'data': []})

            page = PageNumberPagination()
            page_projects = page.paginate_queryset(project_list, request, view=self)
            serializer = ProjectSerializer(page_projects, many=True)
            resp = {
                'code': 0,
                'data': serializer.data,
                'count': project_list.count()
            }
            return Response(resp)

    def post(self, request):
        resp = dict()
        if request.auth:
            try:
                name = request.data.get('pname', '')
                name = validateTitle(name)
                desc = request.data.get('desc', '')
                role = request.data.get('role', 0)
                role_list = ['0', '1', '2', '3', 0, 1, 2, 3]
                if name != '':
                    project = Project.objects.create(
                        name=validateTitle(name),
                        intro=desc[:100],
                        create_user=request.user,
                        role=int(role) if role in role_list else 0
                    )
                    project.save()
                    resp = {'code': 0, 'data': {'id': project.id, 'name': project.name}}
                    return Response(resp)
                else:
                    resp['code'] = 5
                    resp['data'] = '参数不正确'
                    return Response(resp)
            except Exception as e:
                logger.exception("创建文集出错")
                resp['code'] = 4
                resp['data'] = '系统异常请稍后再试'
                return Response(resp)
        else:
            resp['code'] = 6
            resp['data'] = '请登录后操作'
            return Response(resp)

    def put(self, request):
        resp = dict()
        if request.auth:
            try:
                pro_id = request.query_params.get('id', None)
                project = Project.objects.get(id=pro_id)
                if (request.user == project.create_user) or request.user.is_superuser:
                    name = request.data.get('name', None)
                    content = request.data.get('desc', None)
                    role = request.data.get('role', None)
                    role_value = request.data.get('role_value', None)
                    project.name = validateTitle(name)
                    project.intro = content
                    project.role = role
                    project.role_value = role_value
                    project.save()
                    resp['code'] = 0
                    resp['data'] = 'ok'
                else:
                    resp['code'] = 2
                    resp['data'] = '非法请求'
            except ObjectDoesNotExist:
                resp['code'] = 1
                resp['data'] = '资源未找到'
            except Exception as e:
                logger.exception("修改文集出错")
                resp['code'] = 4
        else:
            resp['code'] = 6

        return Response(resp)

    def delete(self, request):
        resp = dict()
        if request.auth:
            try:
                pro_id = request.query_params.get('id', '')
                if pro_id != '':
                    pro = Project.objects.get(id=pro_id)
                    if (request.user == pro.create_user) or request.user.is_superuser:
                        pro_doc_list = Doc.objects.filter(top_doc=int(pro_id))
                        pro_doc_list.delete()
                        pro.delete()
                        resp['code'] = 0
                        resp['data'] = 'ok'
                    else:
                        resp['code'] = 2
                else:
                    resp['code'] = 5
                    resp['data'] = '参数错误'
            except ObjectDoesNotExist:
                resp['code'] = 1
                resp['data'] = '资源未找到'
            except Exception as e:
                logger.exception("API文集删除异常")
                resp['code'] = 4
        else:
            resp['code'] = 6

        return Response(resp)


class DocView(APIView):
    authentication_classes = (AppAuth,)

    def get(self, request):
        pro_id = request.query_params.get('pid', '')
        doc_id = request.query_params.get('did', '')

        if pro_id != '' and doc_id != '':
            project = Project.objects.get(id=int(pro_id))
            if request.auth:
                colla_user = ProjectCollaborator.objects.filter(project=project, user=request.user)
                if colla_user.exists():
                    colla_user_role = colla_user[0].role
                    colla_user = colla_user.count()
                else:
                    colla_user = colla_user.count()
            else:
                colla_user = 0

            if (project.role == 1) and (request.user != project.create_user) and (colla_user == 0):
                return Response({'code': 2})
            elif project.role == 2:
                user_list = project.role_value
                if request.user.is_authenticated:
                    if (request.user.username not in user_list) and \
                            (request.user != project.create_user) and \
                            (colla_user == 0):
                        return Response({'code': 2})
                else:
                    return Response({'code': 2})
            elif project.role == 3:
                if (request.user != project.create_user) and (colla_user == 0):
                    viewcode = project.role_value
                    viewcode_name = 'viewcode-{}'.format(project.id)
                    r_viewcode = request.data.get(viewcode_name, 0)
                    if viewcode != r_viewcode:
                        return Response({'code': 3})

            try:
                doc = Doc.objects.get(id=int(doc_id), status=1)
                serializer = DocSerializer(doc)
                resp = {'code': 0, 'data': serializer.data}
                return Response(resp)
            except ObjectDoesNotExist:
                return Response({'code': 4})
        else:
            return Response({'code': 4})

    def post(self, request):
        try:
            project = request.data.get('project', '')
            parent_doc = request.data.get('parent_doc', '')
            doc_name = request.data.get('doc_name', '')
            doc_content = request.data.get('content', '')
            pre_content = request.data.get('pre_content', '')
            sort = request.data.get('sort', '')
            status = request.data.get('status', 1)
            if project != '' and doc_name != '' and project != '-1':
                check_project = Project.objects.filter(id=project, create_user=request.user)
                colla_project = ProjectCollaborator.objects.filter(project=project,
                                                                   user=request.user)
                if check_project.count() > 0 or colla_project.count() > 0:
                    doc = Doc.objects.create(
                        name=doc_name,
                        content=doc_content,
                        pre_content=pre_content,
                        parent_doc=int(parent_doc) if parent_doc != '' else 0,
                        top_doc=int(project),
                        sort=sort if sort != '' else 99,
                        create_user=request.user,
                        status=status
                    )
                    return Response({'code': 0, 'data': {'pro': project, 'doc': doc.id}})
                else:
                    return Response({'code': 2, 'data': '无权操作此文集'})
            else:
                return Response({'code': 5, 'data': '请确认文档标题、文集正确'})
        except Exception as e:
            logger.exception("api新建文档异常")
            return Response({'status': 4, 'data': '请求出错'})

    def put(self, request):
        try:
            doc_id = request.data.get('doc_id', '')
            project = request.data.get('project', '')
            parent_doc = request.data.get('parent_doc', '')
            doc_name = request.data.get('doc_name', '')
            doc_content = request.data.get('content', '')
            pre_content = request.data.get('pre_content', '')
            sort = request.data.get('sort', '')
            status = request.data.get('status', 1)

            if doc_id != '' and project != '' and doc_name != '' and project != '-1':
                doc = Doc.objects.get(id=doc_id)
                pro_colla = ProjectCollaborator.objects.filter(project=project, user=request.user)
                if (request.user == doc.create_user) or (pro_colla[0].role == 1):
                    DocHistory.objects.create(
                        doc=doc,
                        pre_content=doc.pre_content,
                        create_user=request.user
                    )
                    Doc.objects.filter(id=int(doc_id)).update(
                        name=doc_name,
                        content=doc_content,
                        pre_content=pre_content,
                        parent_doc=int(parent_doc) if parent_doc != '' else 0,
                        sort=sort if sort != '' else 99,
                        modify_time=datetime.datetime.now(),
                        status=status
                    )
                    return Response({'code': 0, 'data': '修改成功'})
                else:
                    return Response({'code': 2, 'data': '未授权请求'})
            else:
                return Response({'code': 5, 'data': '参数错误'})
        except Exception as e:
            logger.exception("api修改文档出错")
            return Response({'code': 4, 'data': '请求出错'})

    def delete(self, request):
        try:
            doc_id = request.data.get('doc_id', None)
            if doc_id:
                try:
                    doc = Doc.objects.get(id=doc_id)
                except ObjectDoesNotExist:
                    return Response({'code': 1, 'data': '文档不存在'})
                if request.user == doc.create_user:
                    doc.delete()
                    Doc.objects.filter(parent_doc=doc_id).update(parent_doc=0)
                    return Response({'code': 0, 'data': '删除完成'})
                else:
                    return Response({'code': 2, 'data': '非法请求'})
            else:
                return Response({'code': 5, 'data': '参数错误'})
        except Exception as e:
            logger.exception("api删除文档出错")
            return Response({'code': 4, 'data': '请求出错'})


class DocTempView(APIView):
    authentication_classes = (AppAuth,)

    def get(self, request):
        if request.auth:
            temp_id = request.query_params.get('id', '')
            if temp_id != '':
                doctemp = DocTemp.objects.get(id=int(temp_id))
                if request.user == doctemp.create_user:
                    serializer = DocTempSerializer(doctemp)
                    resp = {'code': 0, 'data': serializer.data}
                else:
                    resp = {'code': 2, 'data': '无权操作'}
            else:
                doctemps = DocTemp.objects.filter(create_user=request.user)
                page = PageNumberPagination()
                page_doctemps = page.paginate_queryset(doctemps, request, view=self)
                serializer = DocTempSerializer(page_doctemps, many=True)
                resp = {'code': 0, 'data': serializer.data, 'count': doctemps.count()}
            return Response(resp)
        else:
            return Response({'code': 6, 'data': '请登录'})

    def post(self, request):
        try:
            if request.auth:
                name = request.data.get('name', '')
                content = request.data.get('content', '')
                if name != '':
                    doctemp = DocTemp.objects.create(
                        name=name,
                        content=content,
                        create_user=request.user
                    )
                    doctemp.save()
                    return Response({'code': 0, 'data': '创建成功'})
                else:
                    return Response({'code': 5, 'data': '模板标题不能为空'})
            else:
                return Response({'code': 6, 'data': '请登录'})
        except Exception as e:
            logger.exception("api创建文档模板出错")
            return Response({'code': 4, 'data': '请求出错'})

    def put(self, request):
        try:
            doctemp_id = request.data.get('doctemp_id', '')
            name = request.data.get('name', '')
            content = request.data.get('content', '')
            if doctemp_id != '' and name != '':
                doctemp = DocTemp.objects.get(id=doctemp_id)
                if request.user == doctemp.create_user:
                    doctemp.name = name
                    doctemp.content = content
                    doctemp.save()
                    return Response({'code': 0, 'data': '修改成功'})
                else:
                    return Response({'code': 2, 'data': '非法操作'})
            else:
                return Response({'code': 5, 'data': '参数错误'})
        except Exception as e:
            logger.exception("api修改文档模板出错")
            return Response({'code': 4, 'data': '请求出错'})

    def delete(self, request):
        try:
            doctemp_id = request.data.get('doctemp_id', '')
            if doctemp_id != '':
                doctemp = DocTemp.objects.get(id=doctemp_id)
                if request.user == doctemp.create_user:
                    doctemp.delete()
                    return Response({'code': 0, 'data': '删除完成'})
                else:
                    return Response({'code': 2, 'data': '非法请求'})
            else:
                return Response({'code': 5, 'data': '参数错误'})
        except Exception as e:
            logger.exception("api删除文档模板出错")
            return Response({'code': 4, 'data': '请求出错'})


class ImageView(APIView):
    authentication_classes = (AppAuth,)

    def get(self, request):
        if request.auth:
            g_id = int(request.query_params.get('group', 0))
            if int(g_id) == 0:
                image_list = Image.objects.filter(user=request.user)
            elif int(g_id) == -1:
                image_list = Image.objects.filter(user=request.user, group_id=None)
            else:
                image_list = Image.objects.filter(user=request.user, group_id=g_id)
            page = PageNumberPagination()
            page_images = page.paginate_queryset(image_list, request, view=self)
            serializer = ImageSerializer(page_images, many=True)
            resp = {'code': 0, 'data': serializer.data, 'count': image_list.count()}
            return Response(resp)
        else:
            return Response({'code': 6, 'data': '请登录'})

    def post(self, request):
        img = request.data.get("api_img_upload", None)
        dir_name = request.data.get('dirname', '')
        base_img = request.data.get('base', None)
        if img:
            result = img_upload(img, dir_name, request.user)
            resp = {'code': 0, 'data': result['url']}
        elif base_img:
            result = base_img_upload(base_img, dir_name, request.user)
            resp = {'code': 0, 'data': result['url']}
        else:
            resp = {"code": 5, "message": "出错信息"}
        return Response(resp)

    def delete(self, request):
        img_id = request.data.get('id', '')
        img = Image.objects.get(id=img_id)
        if img.user != request.user:
            return Response({'code': 2, 'data': '未授权请求'})
        file_path = settings.BASE_DIR + img.file_path
        is_exist = os.path.exists(file_path)
        if is_exist:
            os.remove(file_path)
        img.delete()
        return Response({'code': 0, 'data': 'ok'})


class ImageGroupView(APIView):
    authentication_classes = (AppMustAuth,)

    def get(self, request):
        try:
            group_list = []
            all_cnt = Image.objects.filter(user=request.user).count()
            non_group_cnt = Image.objects.filter(group_id=None, user=request.user).count()
            group_list.append({'group_name': '全部图片', 'group_cnt': all_cnt, 'group_id': 0})
            group_list.append({'group_name': '未分组', 'group_cnt': non_group_cnt, 'group_id': -1})
            groups = ImageGroup.objects.filter(user=request.user)
            for group in groups:
                group_cnt = Image.objects.filter(group_id=group).count()
                item = {
                    'group_id': group.id,
                    'group_name': group.group_name,
                    'group_cnt': group_cnt
                }
                group_list.append(item)
            return Response({'code': 0, 'data': group_list})
        except:
            return Response({'code': 4, 'data': '出现错误'})

    def post(self, request):
        group_name = request.data.get('group_name', '')
        if group_name not in ['', '默认分组', '未分组']:
            ImageGroup.objects.create(
                user=request.user,
                group_name=group_name
            )
            return Response({'code': 0, 'data': 'ok'})
        else:
            return Response({'code': 5, 'data': '名称无效'})

    def put(self, request):
        group_name = request.data.get("group_name", '')
        if group_name not in ['', '默认分组', '未分组']:
            group_id = request.POST.get('group_id', '')
            ImageGroup.objects.filter(id=group_id, user=request.user).update(group_name=group_name)
            return Response({'code': 0, 'data': 'ok'})
        else:
            return Response({'code': 5, 'data': '名称无效'})

    def delete(self, request):
        try:
            group_id = request.data.get('group_id', '')
            group = ImageGroup.objects.get(id=group_id, user=request.user)
            images = Image.objects.filter(group_id=group_id).update(group_id=None)
            group.delete()
            return Response({'code': 0, 'data': 'ok'})
        except:
            return Response({'code': 4, 'data': '删除错误'})


class AttachmentView(APIView):
    authentication_classes = (AppAuth,)

    def sizeFormat(size, is_disk=False, precision=2):
        formats = ['KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
        unit = 1000.0 if is_disk else 1024.0
        if not (isinstance(size, float) or isinstance(size, int)):
            raise TypeError('a float number or an integer number is required!')
        if size < 0:
            raise ValueError('number must be non-negative')
        for i in formats:
            size /= unit
            if size < unit:
                r = '{}{}'.format(round(size, precision), i)
                return r

    def get(self, request):
        attachment_list = []
        attachments = Attachment.objects.filter(user=request.user)
        for a in attachments:
            item = {
                'filename': a.file_name,
                'filesize': a.file_size,
                'filepath': a.file_path.name,
                'filetime': a.create_time
            }
            attachment_list.append(item)
        return Response({'code': 0, 'data': attachment_list})

    def post(self, request):
        attachment = request.data.get('attachment_upload', None)
        if attachment:
            attachment_name = attachment.name
            attachment_size = self.sizeFormat(attachment.size)
            if attachment.size > 52428800:
                return Response({'code': False, 'data': '文件大小超出限制'})
            if attachment_name.endswith('.zip'):
                a = Attachment.objects.create(
                    file_name=attachment_name,
                    file_size=attachment_size,
                    file_path=attachment,
                    user=request.user
                )
                return Response({'code': 0, 'data': {
                    'name': attachment_name, 'url': a.file_path.name}
                                 })
            else:
                return Response({'code': 5, 'data': '不支持的格式'})
        else:
            return Response({'code': 5, 'data': '无效文件'})

    def delete(self, request):
        attach_id = request.data.get('attach_id', '')
        attachment = Attachment.objects.filter(id=attach_id, user=request.user)
        for a in attachment:
            a.file_path.delete()
        attachment.delete()
        return Response({'code': 0, 'data': 'ok'})
