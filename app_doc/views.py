# utf-8
from django.shortcuts import render, redirect
from django.http.response import JsonResponse, Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from app_doc.report_utils import *
from app_admin.decorators import check_headers, allow_report_file
import os.path


def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|\[\]]"
    new_title = re.sub(rstr, "_", title)
    return new_title


@logger.catch()
def project_list(request):
    global role_list, project_list
    kw = request.GET.get('kw', '')
    sort = request.GET.get('sort', 0)
    role = request.GET.get('role', -1)

    if sort in ['', 0, '0']:
        sort_str = ''
    else:
        sort_str = '-'

    if kw == '':
        is_kw = False
    else:
        is_kw = True

    if request.user.is_authenticated:
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
            project_list = Project.objects.filter(role=0) \
                .order_by("{}create_time".format(sort_str))
        elif role in ['1', 1]:
            project_list = Project.objects.filter(create_user=request.user, role=1) \
                .order_by("{}create_time".format(sort_str))
        elif role in ['2', 2]:
            project_list = Project.objects.filter(role=2, role_value__contains=str(
                request.user.username)
                                                  ).order_by("{}create_time".format(sort_str))
        elif role in ['3', 3]:
            project_list = Project.objects.filter(role=3) \
                .order_by("{}create_time".format(sort_str))
        elif role in ['99', 99]:
            colla_list = [i.project.id for i in ProjectCollaborator
                .objects.filter(user=request.user)]
            project_list = Project.objects.filter(id__in=colla_list).order_by(
                "{}create_time".format(sort_str)
            )
        else:
            return render(request, '404.html')

    elif (is_kw is False) and (is_auth is False) and (is_role is False):
        project_list = Project.objects.filter(role__in=[0, 3]) \
            .order_by("{}create_time".format(sort_str))

    elif (is_kw is False) and (is_auth is False) and (is_role):
        if role in ['0', 0]:
            project_list = Project.objects.filter(role=0) \
                .order_by("{}create_time".format(sort_str))
        elif role in ['3', 3]:
            project_list = Project.objects.filter(role=3) \
                .order_by("{}create_time".format(sort_str))
        else:
            return render(request, '404.html')

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
            colla_list = [i.project.id for i in ProjectCollaborator.objects.filter(
                user=request.user
            )]
            project_list = Project.objects.filter(
                Q(name__icontains=kw) | Q(intro__icontains=kw),
                id__in=colla_list
            ).order_by("{}create_time".format(sort_str))
        else:
            return render(request, '404.html')

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
            return render(request, '404.html')

    paginator = Paginator(project_list, 12)
    page = request.GET.get('page', 1)
    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        projects = paginator.page(1)
    except EmptyPage:
        projects = paginator.page(paginator.num_pages)
    return render(request, 'app_doc/pro_list.html', locals())


@login_required()
@require_http_methods(['POST'])
def create_project(request):
    try:
        name = request.POST.get('pname', '')
        name = validateTitle(name)
        desc = request.POST.get('desc', '')
        role = request.POST.get('role', 0)
        role_list = ['0', '1', '2', '3', 0, 1, 2, 3]
        if name != '':
            project = Project.objects.create(
                name=validateTitle(name),
                intro=desc[:100],
                create_user=request.user,
                role=int(role) if role in role_list else 0
            )
            project.save()
            return JsonResponse({'status': True, 'data': {
                'id': project.id, 'name': project.name
            }})
        else:
            return JsonResponse({'status': False, 'data': '文集名称不能为空！'})
    except Exception as e:

        logger.exception("创建文集出错")
        return JsonResponse({'status': False, 'data': '出现异常,请检查输入值！'})


@require_http_methods(['GET'])
@check_headers
def project_index(request, pro_id):
    try:
        project = Project.objects.get(id=int(pro_id))
        if request.user.is_authenticated:
            colla_user = ProjectCollaborator.objects.filter(
                project=project, user=request.user
            ).count()
        else:
            colla_user = 0

        try:
            allow_download = ProjectReport.objects.get(project=project)
        except ObjectDoesNotExist:
            allow_download = False

        if (project.role == 1) and (request.user != project.create_user) and (colla_user == 0):
            return render(request, '404.html')
        elif project.role == 2:
            user_list = project.role_value
            if request.user.is_authenticated:
                if (request.user.username not in user_list) and \
                        (request.user != project.create_user) and \
                        (colla_user == 0):
                    return render(request, '404.html')
            else:
                return render(request, '404.html')
        elif project.role == 3:
            if request.user != project.create_user and colla_user == 0:
                viewcode = project.role_value
                viewcode_name = 'viewcode-{}'.format(project.id)
                r_viewcode = request.COOKIES[
                    viewcode_name] if viewcode_name in request.COOKIES.keys() else 0
                if viewcode != r_viewcode:
                    return redirect('/check_viewcode/?to={}'.format(request.path))

        kw = request.GET.get('kw', '')
        project_docs = Doc.objects.filter(top_doc=int(pro_id), parent_doc=0,
                                          status=1).order_by('sort')
        if kw != '':
            search_result = Doc.objects.filter(top_doc=int(pro_id), pre_content__icontains=kw)
            return render(request, 'app_doc/project_doc_search.html', locals())
        return render(request, 'app_doc/project.html', locals())
    except Exception as e:
        logger.exception("文集页访问异常")
        return render(request, '404.html')


@login_required()
@require_http_methods(['POST'])
def modify_project(request):
    try:
        pro_id = request.POST.get('pro_id', None)
        project = Project.objects.get(id=pro_id)
        if (request.user == project.create_user) or request.user.is_superuser:
            name = request.POST.get('name', None)
            content = request.POST.get('desc', None)
            project.name = validateTitle(name)
            project.intro = content
            project.save()
            return JsonResponse({'status': True, 'data': '修改成功'})
        else:
            return JsonResponse({'status': False, 'data': '非法请求'})
    except Exception as e:
        logger.exception("修改文集出错")
        return JsonResponse({'status': False, 'data': '请求出错'})


@login_required()
@require_http_methods(['GET', "POST"])
@logger.catch()
def modify_project_role(request, pro_id):
    try:
        pro = Project.objects.get(id=pro_id)
    except ObjectDoesNotExist:
        return Http404
    if (pro.create_user != request.user) and (request.user.is_superuser is False):
        return render(request, '403.html')
    else:
        if request.method == 'GET':
            return render(request, 'app_doc/manage_project_role.html', locals())
        elif request.method == 'POST':
            role_type = request.POST.get('role', '')
            if role_type != '':
                if int(role_type) in [0, 1]:
                    Project.objects.filter(id=int(pro_id)).update(
                        role=role_type,
                        modify_time=datetime.datetime.now()
                    )
                if int(role_type) == 2:
                    role_value = request.POST.get('tagsinput', '')
                    Project.objects.filter(id=int(pro_id)).update(
                        role=role_type,
                        role_value=role_value,
                        modify_time=datetime.datetime.now()
                    )
                if int(role_type) == 3:
                    role_value = request.POST.get('viewcode', '')
                    Project.objects.filter(id=int(pro_id)).update(
                        role=role_type,
                        role_value=role_value,
                        modify_time=datetime.datetime.now()
                    )
                pro = Project.objects.get(id=int(pro_id))
                return render(request, 'app_doc/manage_project_role.html', locals())
            else:
                return Http404


@require_http_methods(['GET', "POST"])
def check_viewcode(request):
    try:
        if request.method == 'GET':
            project_id = request.GET.get('to', '').split("/")[1].split('-')[1]
            project = Project.objects.get(id=int(project_id))
            return render(request, 'app_doc/check_viewcode.html', locals())
        else:
            viewcode = request.POST.get('viewcode', '')
            project_id = request.POST.get('project_id', '')
            project = Project.objects.get(id=int(project_id))
            if project.role == 3 and project.role_value == viewcode:
                obj = redirect("pro_index", pro_id=project_id)
                obj.set_cookie('viewcode-{}'.format(project_id), viewcode)
                return obj
            else:
                errormsg = "访问码错误"
                return render(request, 'app_doc/check_viewcode.html', locals())
    except Exception as e:
        logger.exception("验证文集访问码出错")
        return render(request, '404.html')


@login_required()
@require_http_methods(["POST"])
def del_project(request):
    try:
        pro_id = request.POST.get('pro_id', '')
        if pro_id != '':
            pro = Project.objects.get(id=pro_id)
            if (request.user == pro.create_user) or request.user.is_superuser:
                pro_doc_list = Doc.objects.filter(top_doc=int(pro_id))
                pro_doc_list.delete()
                pro.delete()
                return JsonResponse({'status': True})
            else:
                return JsonResponse({'status': False, 'data': '非法请求'})
        else:
            return JsonResponse({'status': False, 'data': '参数错误'})
    except Exception as e:
        logger.exception("删除文集出错")
        return JsonResponse({'status': False, 'data': '请求出错'})


@login_required()
@require_http_methods(['GET'])
def manage_project(request):
    try:
        search_kw = request.GET.get('kw', None)
        if search_kw:
            pro_list = Project.objects.filter(
                create_user=request.user, intro__icontains=search_kw
            ).order_by(
                '-create_time')
            paginator = Paginator(pro_list, 15)
            page = request.GET.get('page', 1)
            try:
                pros = paginator.page(page)
            except PageNotAnInteger:
                pros = paginator.page(1)
            except EmptyPage:
                pros = paginator.page(paginator.num_pages)
            pros.kw = search_kw
        else:
            pro_list = Project.objects.filter(create_user=request.user) \
                .order_by('-create_time')
            paginator = Paginator(pro_list, 15)
            page = request.GET.get('page', 1)
            try:
                pros = paginator.page(page)
            except PageNotAnInteger:
                pros = paginator.page(1)
            except EmptyPage:
                pros = paginator.page(paginator.num_pages)
        return render(request, 'app_doc/manage_project.html', locals())
    except Exception as e:
        logger.exception("管理文集出错")
        return render(request, '404.html')


@login_required()
@require_http_methods(['GET', "POST"])
@logger.catch()
def modify_project_download(request, pro_id):
    try:
        pro = Project.objects.get(id=pro_id)
    except ObjectDoesNotExist:
        return Http404
    if (pro.create_user != request.user) and (request.user.is_superuser is False):
        return render(request, '403.html')
    else:
        project_files = ProjectReportFile.objects.filter(project=pro)
        if request.method == 'GET':
            return render(request, 'app_doc/manage_project_download.html', locals())
        elif request.method == 'POST':
            download_epub = request.POST.get('download_epub', None)
            download_pdf = request.POST.get('download_pdf', None)
            if download_epub == 'on':
                epub_status = 1
            else:
                epub_status = 0
            if download_pdf == 'on':
                pdf_status = 1
            else:
                pdf_status = 0
            ProjectReport.objects.update_or_create(
                project=pro, defaults={'allow_epub': epub_status}
            )
            ProjectReport.objects.update_or_create(
                project=pro, defaults={'allow_pdf': pdf_status}
            )
            return render(request, 'app_doc/manage_project_download.html', locals())


@login_required()
@require_http_methods(['GET', "POST"])
@logger.catch()
def manage_project_collaborator(request, pro_id):
    project = Project.objects.filter(id=pro_id, create_user=request.user)
    if project.exists() is False:
        return Http404

    if request.method == 'GET':
        pro = project[0]
        collaborator = ProjectCollaborator.objects.filter(project=pro)
        return render(request, 'app_doc/manage_project_collaborator.html', locals())

    elif request.method == 'POST':
        types = request.POST.get('types', '')
        try:
            types = int(types)
        except:
            return JsonResponse({'status': False, 'data': '参数错误'})
        if int(types) == 0:
            colla_user = request.POST.get('username', '')
            role = request.POST.get('role', 0)
            user = User.objects.filter(username=colla_user)
            if user.exists():
                if user[0] == project[0].create_user:
                    return JsonResponse({'status': False, 'data': '文集创建者无需添加'})
                elif ProjectCollaborator.objects.filter(
                        user=user[0], project=project[0]
                ).exists():
                    return JsonResponse({'status': False, 'data': '用户已存在'})
                else:
                    ProjectCollaborator.objects.create(
                        project=project[0],
                        user=user[0],
                        role=role if role in ['1', 1] else 0
                    )
                    return JsonResponse({'status': True, 'data': '添加成功'})
            else:
                return JsonResponse({'status': False, 'data': '用户不存在'})
        elif int(types) == 1:
            username = request.POST.get('username', '')
            try:
                user = User.objects.get(username=username)
                pro_colla = ProjectCollaborator.objects.get(project=project[0], user=user)
                pro_colla.delete()
                return JsonResponse({'status': True, 'data': '删除成功'})
            except:
                logger.exception("删除协作者出错")
                return JsonResponse({'status': False, 'data': '删除出错'})
        elif int(types) == 2:
            username = request.POST.get('username', '')
            role = request.POST.get('role', '')
            try:
                user = User.objects.get(username=username)
                pro_colla = ProjectCollaborator.objects.filter(project=project[0], user=user)
                pro_colla.update(role=role)
                return JsonResponse({'status': True, 'data': '修改成功'})
            except:
                logger.exception("修改协作权限出错")
                return JsonResponse({'status': False, 'data': '修改失败'})

        else:
            return JsonResponse({'status': False, 'data': '无效的类型'})


@login_required()
@logger.catch()
def manage_pro_colla_self(request):
    colla_pros = ProjectCollaborator.objects.filter(user=request.user)
    return render(request, 'app_doc/manage_project_self_colla.html', locals())


@require_http_methods(['GET'])
def doc(request, pro_id, doc_id):
    try:
        if pro_id != '' and doc_id != '':
            project = Project.objects.get(id=int(pro_id))
            if request.user.is_authenticated:
                colla_user = ProjectCollaborator.objects.filter(
                    project=project, user=request.user
                )
                if colla_user.exists():
                    colla_user_role = colla_user[0].role
                    colla_user = colla_user.count()
                else:
                    colla_user = colla_user.count()
            else:
                colla_user = 0

            if (project.role == 1) and (request.user != project.create_user) and \
                    (colla_user == 0):
                return render(request, '404.html')
            elif project.role == 2:
                user_list = project.role_value
                if request.user.is_authenticated:
                    if (request.user.username not in user_list) and \
                            (request.user != project.create_user) and \
                            (colla_user == 0):
                        return render(request, '404.html')
                else:
                    return render(request, '404.html')
            elif project.role == 3:
                if (request.user != project.create_user) and (colla_user == 0):
                    viewcode = project.role_value
                    viewcode_name = 'viewcode-{}'.format(project.id)
                    r_viewcode = request.COOKIES[
                        viewcode_name] if viewcode_name in request.COOKIES.keys() else 0
                    if viewcode != r_viewcode:
                        return redirect('/check_viewcode/?to={}'.format(request.path))

            try:
                doc = Doc.objects.get(id=int(doc_id), status=1)
            except ObjectDoesNotExist:
                return render(request, '404.html')
            project_docs = Doc.objects.filter(
                top_doc=doc.top_doc, parent_doc=0, status=1
            ).order_by('sort')
            return render(request, 'app_doc/doc.html', locals())
        else:
            return HttpResponse('参数错误')
    except Exception as e:
        logger.exception("文集浏览出错")
        return render(request, '404.html')


@login_required()
@require_http_methods(['GET', "POST"])
@logger.catch()
def create_doc(request):
    if request.method == 'GET':
        try:
            pid = request.GET.get('pid', -999)
            project_list = Project.objects.filter(create_user=request.user)
            colla_project_list = ProjectCollaborator.objects.filter(user=request.user)
            doctemp_list = DocTemp.objects.filter(create_user=request.user) \
                .values('id', 'name', 'create_time')
            return render(request, 'app_doc/create_doc.html', locals())
        except Exception as e:
            logger.exception("访问创建文档页面出错")
            return render(request, '404.html')
    elif request.method == 'POST':
        try:
            project = request.POST.get('project', '')
            parent_doc = request.POST.get('parent_doc', '')
            doc_name = request.POST.get('doc_name', '')
            doc_content = request.POST.get('content', '')
            pre_content = request.POST.get('pre_content', '')
            sort = request.POST.get('sort', '')
            status = request.POST.get('status', 1)
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
                    return JsonResponse({'status': True, 'data': {
                        'pro': project, 'doc': doc.id
                    }})
                else:
                    return JsonResponse({'status': False, 'data': '无权操作此文集'})
            else:
                return JsonResponse({'status': False, 'data': '请确认文档标题、文集正确'})
        except Exception as e:
            logger.exception("创建文档出错")
            return JsonResponse({'status': False, 'data': '请求出错'})
    else:
        return JsonResponse({'status': False, 'data': '方法不允许'})


@login_required()
@require_http_methods(['GET', "POST"])
def modify_doc(request, doc_id):
    if request.method == 'GET':
        try:
            doc = Doc.objects.get(id=doc_id)
            project = Project.objects.get(id=doc.top_doc)
            pro_colla = ProjectCollaborator.objects.filter(
                project=project, user=request.user
            )
            if (request.user == doc.create_user) or (pro_colla[0].role == 1):
                doc_list = Doc.objects.filter(top_doc=project.id)
                doctemp_list = DocTemp.objects.filter(create_user=request.user)
                history_list = DocHistory.objects.filter(doc=doc).order_by('-create_time')
                return render(request, 'app_doc/modify_doc.html', locals())
            else:
                return render(request, '403.html')
        except Exception as e:
            logger.exception("修改文档页面访问出错")
            return render(request, '404.html')
    elif request.method == 'POST':
        try:
            doc_id = request.POST.get('doc_id', '')
            project = request.POST.get('project', '')
            parent_doc = request.POST.get('parent_doc', '')
            doc_name = request.POST.get('doc_name', '')
            doc_content = request.POST.get('content', '')
            pre_content = request.POST.get('pre_content', '')
            sort = request.POST.get('sort', '')
            status = request.POST.get('status', 1)
            if doc_id != '' and project != '' and doc_name != '' and project != '-1':
                doc = Doc.objects.get(id=doc_id)
                pro_colla = ProjectCollaborator.objects.filter(
                    project=project, user=request.user
                )
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
                    return JsonResponse({'status': True, 'data': '修改成功'})
                else:
                    return JsonResponse({'status': False, 'data': '未授权请求'})
            else:
                return JsonResponse({'status': False, 'data': '参数错误'})
        except Exception as e:
            logger.exception("修改文档出错")
            return JsonResponse({'status': False, 'data': '请求出错'})


@login_required()
@require_http_methods(["POST"])
def del_doc(request):
    try:
        doc_id = request.POST.get('doc_id', None)
        if doc_id:
            try:
                doc = Doc.objects.get(id=doc_id)
            except ObjectDoesNotExist:
                return JsonResponse({'status': False, 'data': '文档不存在'})
            if request.user == doc.create_user:
                doc.delete()
                Doc.objects.filter(parent_doc=doc_id).update(parent_doc=0)
                return JsonResponse({'status': True, 'data': '删除完成'})
            else:
                return JsonResponse({'status': False, 'data': '非法请求'})
        else:
            return JsonResponse({'status': False, 'data': '参数错误'})
    except Exception as e:
        logger.exception("删除文档出错")
        return JsonResponse({'status': False, 'data': '请求出错'})


@login_required()
@require_http_methods(['GET'])
@logger.catch()
def manage_doc(request):
    global doc_list
    search_kw = request.GET.get('kw', None)
    if search_kw:
        published_doc_cnt = Doc.objects.filter(
            create_user=request.user, status=1
        ).count()
        draft_doc_cnt = Doc.objects.filter(
            create_user=request.user, status=0
        ).count()
        all_cnt = published_doc_cnt + draft_doc_cnt
        doc_status = request.GET.get('status', 'all')

        if doc_status == 'all':
            doc_list = Doc.objects.filter(
                Q(content__icontains=search_kw) | Q(name__icontains=search_kw),
                create_user=request.user,
            ).order_by('-modify_time')
        elif doc_status == 'published':
            doc_list = Doc.objects.filter(
                create_user=request.user,
                content__icontains=search_kw,
                status=1
            ).order_by('-modify_time')
        elif doc_status == 'draft':
            doc_list = Doc.objects.filter(
                Q(content__icontains=search_kw) | Q(name__icontains=search_kw),
                create_user=request.user,
                status=0
            ).order_by('-modify_time')
        paginator = Paginator(doc_list, 15)
        page = request.GET.get('page', 1)
        try:
            docs = paginator.page(page)
        except PageNotAnInteger:
            docs = paginator.page(1)
        except EmptyPage:
            docs = paginator.page(paginator.num_pages)
        docs.kw = search_kw
        docs.status = doc_status
    else:
        published_doc_cnt = Doc.objects.filter(
            create_user=request.user, status=1
        ).count()
        draft_doc_cnt = Doc.objects.filter(
            create_user=request.user, status=0
        ).count()
        all_cnt = published_doc_cnt + draft_doc_cnt
        doc_status = request.GET.get('status', 'all')
        if len(doc_status) == 0:
            doc_status = 'all'
        if doc_status == 'all':
            doc_list = Doc.objects.filter(create_user=request.user).order_by('-modify_time')
        elif doc_status == 'published':
            doc_list = Doc.objects.filter(
                create_user=request.user, status=1
            ).order_by('-modify_time')
        elif doc_status == 'draft':
            doc_list = Doc.objects.filter(
                create_user=request.user, status=0
            ).order_by('-modify_time')
        else:
            doc_list = Doc.objects.filter(create_user=request.user).order_by('-modify_time')
        paginator = Paginator(doc_list, 15)
        page = request.GET.get('page', 1)
        try:
            docs = paginator.page(page)
        except PageNotAnInteger:
            docs = paginator.page(1)
        except EmptyPage:
            docs = paginator.page(paginator.num_pages)
        docs.status = doc_status
    return render(request, 'app_doc/manage_doc.html', locals())


@login_required()
@require_http_methods(['GET', "POST"])
def diff_doc(request, doc_id, his_id):
    if request.method == 'GET':
        try:
            doc = Doc.objects.get(id=doc_id)
            project = Project.objects.get(id=doc.top_doc)
            pro_colla = ProjectCollaborator.objects.filter(
                project=project, user=request.user
            )
            if (request.user == doc.create_user) or (pro_colla[0].role == 1):
                history = DocHistory.objects.get(id=his_id)
                history_list = DocHistory.objects.filter(doc=doc).order_by('-create_time')
                if history.doc == doc:
                    return render(request, 'app_doc/diff_doc.html', locals())
                else:
                    return render(request, '403.html')
            else:
                return render(request, '403.html')
        except Exception as e:
            logger.exception("文档历史版本页面访问出错")
            return render(request, '404.html')

    elif request.method == 'POST':
        try:
            doc = Doc.objects.get(id=doc_id)
            project = Project.objects.get(id=doc.top_doc)  #
            pro_colla = ProjectCollaborator.objects.filter(
                project=project, user=request.user
            )
            if (request.user == doc.create_user) or (pro_colla[0].role == 1):
                history = DocHistory.objects.get(id=his_id)
                if history.doc == doc:
                    return JsonResponse({'status': True, 'data': history.pre_content})
                else:
                    return JsonResponse({'status': False, 'data': '非法请求'})
            else:
                return JsonResponse({'status': False, 'data': '非法请求'})
        except Exception as e:
            logger.exception("文档历史版本获取出错")
            return JsonResponse({'status': False, 'data': '获取异常'})


@login_required()
@require_http_methods(['GET', "POST"])
def manage_doc_history(request, doc_id):
    if request.method == 'GET':
        try:
            doc = Doc.objects.get(id=doc_id, create_user=request.user)
            history_list = DocHistory.objects.filter(
                create_user=request.user, doc=doc_id
            ).order_by('-create_time')
            paginator = Paginator(history_list, 15)
            page = request.GET.get('page', 1)
            try:
                historys = paginator.page(page)
            except PageNotAnInteger:
                historys = paginator.page(1)
            except EmptyPage:
                historys = paginator.page(paginator.num_pages)
            return render(request, 'app_doc/manage_doc_history.html', locals())
        except Exception as e:
            logger.exception("管理文档历史版本页面访问出错")
            return render(request, '404.html')
    elif request.method == 'POST':
        try:
            history_id = request.POST.get('history_id', '')
            DocHistory.objects.filter(
                id=history_id, doc=doc_id, create_user=request.user
            ).delete()
            return JsonResponse({'status': True, 'data': '删除成功'})
        except:
            logger.exception("操作文档历史版本出错")
            return JsonResponse({'status': False, 'data': '出现异常'})


@login_required()
@require_http_methods(['GET', "POST"])
def create_doctemp(request):
    if request.method == 'GET':
        doctemps = DocTemp.objects.filter(create_user=request.user)
        return render(request, 'app_doc/create_doctemp.html', locals())
    elif request.method == 'POST':
        try:
            name = request.POST.get('name', '')
            content = request.POST.get('content', '')
            if name != '':
                doctemp = DocTemp.objects.create(
                    name=name,
                    content=content,
                    create_user=request.user
                )
                doctemp.save()
                return JsonResponse({'status': True, 'data': '创建成功'})
            else:
                return JsonResponse({'status': False, 'data': '模板标题不能为空'})
        except Exception as e:
            logger.exception("创建文档模板出错")
            return JsonResponse({'status': False, 'data': '请求出错'})


@login_required()
@require_http_methods(['GET', "POST"])
def modify_doctemp(request, doctemp_id):
    if request.method == 'GET':
        try:
            doctemp = DocTemp.objects.get(id=doctemp_id)
            if request.user.id == doctemp.create_user.id:
                doctemps = DocTemp.objects.filter(create_user=request.user)
                return render(request, 'app_doc/modify_doctemp.html', locals())
            else:
                return HttpResponse('非法请求')
        except Exception as e:
            logger.exception("访问文档模板修改页面出错")
            return render(request, '404.html')
    elif request.method == 'POST':
        try:
            doctemp_id = request.POST.get('doctemp_id', '')
            name = request.POST.get('name', '')
            content = request.POST.get('content', '')
            if doctemp_id != '' and name != '':
                doctemp = DocTemp.objects.get(id=doctemp_id)
                if request.user.id == doctemp.create_user.id:
                    doctemp.name = name
                    doctemp.content = content
                    doctemp.save()
                    return JsonResponse({'status': True, 'data': '修改成功'})
                else:
                    return JsonResponse({'status': False, 'data': '非法操作'})
            else:
                return JsonResponse({'status': False, 'data': '参数错误'})
        except Exception as e:
            logger.exception("修改文档模板出错")
            return JsonResponse({'status': False, 'data': '请求出错'})


@login_required()
def del_doctemp(request):
    try:
        doctemp_id = request.POST.get('doctemp_id', '')
        if doctemp_id != '':
            doctemp = DocTemp.objects.get(id=doctemp_id)
            if request.user.id == doctemp.create_user.id:
                doctemp.delete()
                return JsonResponse({'status': True, 'data': '删除完成'})
            else:
                return JsonResponse({'status': False, 'data': '非法请求'})
        else:
            return JsonResponse({'status': False, 'data': '参数错误'})
    except Exception as e:
        logger.exception("删除文档模板出错")
        return JsonResponse({'status': False, 'data': '请求出错'})


@login_required()
@require_http_methods(['GET'])
def manage_doctemp(request):
    try:
        search_kw = request.GET.get('kw', None)
        if search_kw:
            doctemp_list = DocTemp.objects.filter(
                create_user=request.user,
                content__icontains=search_kw
            ).order_by('-modify_time')
            paginator = Paginator(doctemp_list, 10)
            page = request.GET.get('page', 1)
            try:
                doctemps = paginator.page(page)
            except PageNotAnInteger:
                doctemps = paginator.page(1)
            except EmptyPage:
                doctemps = paginator.page(paginator.num_pages)
            doctemps.kw = search_kw
        else:
            doctemp_list = DocTemp.objects.filter(create_user=request.user) \
                .order_by('-modify_time')
            paginator = Paginator(doctemp_list, 10)
            page = request.GET.get('page', 1)
            try:
                doctemps = paginator.page(page)
            except PageNotAnInteger:
                doctemps = paginator.page(1)
            except EmptyPage:
                doctemps = paginator.page(paginator.num_pages)
        return render(request, 'app_doc/manage_doctemp.html', locals())
    except Exception as e:
        logger.exception("管理文档模板页面访问出错")
        return render(request, '404.html')


@login_required()
@require_http_methods(["POST"])
def get_doctemp(request):
    try:
        doctemp_id = request.POST.get('doctemp_id', '')
        if doctemp_id != '':
            content = DocTemp.objects.get(id=int(doctemp_id)).serializable_value('content')
            return JsonResponse({'status': True, 'data': content})
        else:
            return JsonResponse({'status': False, 'data': '参数错误'})
    except Exception as e:
        logger.exception("获取指定文档模板出错")
        return JsonResponse({'status': False, 'data': '请求出错'})


@require_http_methods(["POST"])
@logger.catch()
def get_pro_doc(request):
    pro_id = request.POST.get('pro_id', '')
    if pro_id != '':
        doc_list = Doc.objects.filter(top_doc=int(pro_id)).values_list(
            'id', 'name', 'parent_doc'
        ).order_by(
            'parent_doc')
        item_list = []
        for doc in doc_list:
            if doc[2] == 0:
                item = [
                    doc[0], doc[1], doc[2], ''
                ]
                item_list.append(item)
            else:
                try:
                    parent = Doc.objects.get(id=doc[2])
                except ObjectDoesNotExist:
                    return JsonResponse({'status': False, 'data': '文档id不存在'})
                if parent.parent_doc == 0:
                    item = [
                        doc[0], doc[1], doc[2], parent.name + ' --> '
                    ]
                    item_list.append(item)
        return JsonResponse({'status': True, 'data': list(item_list)})
    else:
        return JsonResponse({'status': False, 'data': '参数错误'})


@login_required()
@require_http_methods(['POST'])
@logger.catch()
def get_pro_doc_tree(request):
    pro_id = request.POST.get('pro_id', None)
    if pro_id:
        doc_list = []
        top_docs = Doc.objects.filter(top_doc=pro_id, parent_doc=0, status=1).order_by('sort')
        for doc in top_docs:
            top_item = {
                'id': doc.id,
                'field': doc.name,
                'title': doc.name,
                'spread': True,
                'level': 1
            }
            sec_docs = Doc.objects.filter(
                top_doc=pro_id, parent_doc=doc.id, status=1
            ).order_by('sort')
            if sec_docs.exists():
                top_item['children'] = []
                for doc in sec_docs:
                    sec_item = {
                        'id': doc.id,
                        'field': doc.name,
                        'title': doc.name,
                        'level': 2
                    }
                    thr_docs = Doc.objects.filter(
                        top_doc=pro_id, parent_doc=doc.id, status=1
                    ).order_by('sort')
                    if thr_docs.exists():
                        sec_item['children'] = []
                        for doc in thr_docs:
                            item = {
                                'id': doc.id,
                                'field': doc.name,
                                'title': doc.name,
                                'level': 3
                            }
                            sec_item['children'].append(item)
                        top_item['children'].append(sec_item)
                    else:
                        top_item['children'].append(sec_item)
                doc_list.append(top_item)
            else:
                doc_list.append(top_item)
        return JsonResponse({'status': True, 'data': doc_list})
    else:
        return JsonResponse({'status': False, 'data': '参数错误'})


def handle_404(request):
    return render(request, '404.html')


@login_required()
@require_http_methods(["POST"])
def report_md(request):
    pro_id = request.POST.get('project_id', '')
    user = request.user
    try:
        project = Project.objects.get(id=int(pro_id))
        if project.create_user == user:
            project_md = ReportMD(
                project_id=int(pro_id)
            )
            md_file_path = project_md.work()
            md_file_filename = os.path.split(md_file_path)[-1]
            md_file = "/media/reportmd_temp/" + md_file_filename
            return JsonResponse({'status': True, 'data': md_file})
        else:
            return JsonResponse({'status': False, 'data': '无权限'})
    except Exception as e:
        logger.exception("导出文集MD文件出错")
        return JsonResponse({'status': False, 'data': '文集不存在'})


@login_required()
@require_http_methods(["POST"])
def genera_project_file(request):
    report_type = request.POST.get('types', None)

    pro_id = request.POST.get('pro_id')
    try:
        project = Project.objects.get(id=int(pro_id))
        if request.user.is_authenticated:
            colla_user = ProjectCollaborator.objects.filter(project=project, user=request.user)
            if colla_user.exists():
                colla_user_role = colla_user[0].role
                colla_user = colla_user.count()
            else:
                colla_user = colla_user.count()
        else:
            colla_user = 0

        if project.role == 0:
            allow_export = True

        elif (project.role == 1):
            if (request.user != project.create_user) and (colla_user == 0):
                allow_export = False
            else:
                allow_export = True

        elif project.role == 2:
            user_list = project.role_value
            if request.user.is_authenticated:
                if (request.user.username not in user_list) and \
                        (request.user != project.create_user) and \
                        (colla_user == 0):
                    allow_export = False
                else:
                    allow_export = True
            else:
                allow_export = False

        elif project.role == 3:
            if (request.user != project.create_user) and (colla_user == 0):
                viewcode = project.role_value
                viewcode_name = 'viewcode-{}'.format(project.id)
                r_viewcode = request.COOKIES[
                    viewcode_name] if viewcode_name in request.COOKIES.keys() else 0
                if viewcode != r_viewcode:
                    allow_export = False
                else:
                    allow_export = True
            else:
                allow_export = True
        else:
            allow_export = False

        if allow_export:
            if report_type in ['epub']:
                try:
                    report_project = ReportEPUB(
                        project_id=project.id
                    ).work()
                    report_file_path = report_project.split('media', maxsplit=1)[-1]
                    epub_file = '/media' + report_file_path + '.epub'
                    report_cnt = ProjectReportFile.objects.filter(
                        project=project, file_type='epub'
                    )
                    if report_cnt.count() != 0:
                        for r in report_cnt:
                            is_exist = os.path.exists(settings.BASE_DIR + r.file_path)
                            if is_exist:
                                os.remove(settings.BASE_DIR + r.file_path)
                        report_cnt.delete()

                    ProjectReportFile.objects.create(
                        project=project,
                        file_type='epub',
                        file_name=epub_file,
                        file_path=epub_file
                    )

                    return JsonResponse({'status': True, 'data': epub_file})
                except Exception as e:
                    return JsonResponse({'status': False, 'data': '生成出错'})
            elif report_type in ['pdf']:
                try:
                    report_project = ReportPDF(
                        project_id=project.id
                    ).work()
                    if report_project is False:
                        return JsonResponse({'status': False, 'data': '生成出错'})
                    report_file_path = report_project.split('media', maxsplit=1)[-1]
                    pdf_file = '/media' + report_file_path
                    report_cnt = ProjectReportFile.objects.filter(
                        project=project, file_type='pdf'
                    )
                    if report_cnt.count() != 0:
                        for r in report_cnt:
                            is_exist = os.path.exists(settings.BASE_DIR + r.file_path)
                            if is_exist:
                                os.remove(settings.BASE_DIR + r.file_path)
                        report_cnt.delete()

                    ProjectReportFile.objects.create(
                        project=project,
                        file_type='pdf',
                        file_name=pdf_file,
                        file_path=pdf_file
                    )

                    return JsonResponse({'status': True, 'data': pdf_file})

                except Exception as e:
                    return JsonResponse({'status': False, 'data': '生成出错'})
            else:
                return JsonResponse({'status': False, 'data': '不支持的类型'})
        else:
            return JsonResponse({'status': False, 'data': '无权限导出'})

    except ObjectDoesNotExist:
        return JsonResponse({'status': False, 'data': '文集不存在'})

    except Exception as e:
        logger.exception("生成文集文件出错")
        return JsonResponse({'status': False, 'data': '系统异常'})


@allow_report_file
@require_http_methods(["POST"])
def report_file(request):
    report_type = request.POST.get('types', None)

    pro_id = request.POST.get('pro_id')
    try:
        project = Project.objects.get(id=int(pro_id))

        if request.user.is_authenticated:
            colla_user = ProjectCollaborator.objects.filter(project=project, user=request.user)
            if colla_user.exists():
                colla_user_role = colla_user[0].role
                colla_user = colla_user.count()
            else:
                colla_user = colla_user.count()
        else:
            colla_user = 0

        if project.role == 0:
            allow_export = True

        elif (project.role == 1):
            if (request.user != project.create_user) and (colla_user == 0):
                allow_export = False
            else:
                allow_export = True

        elif project.role == 2:
            user_list = project.role_value
            if request.user.is_authenticated:
                if (request.user.username not in user_list) and \
                        (request.user != project.create_user) and \
                        (colla_user == 0):
                    allow_export = False
                else:
                    allow_export = True
            else:
                allow_export = False
        elif project.role == 3:
            if (request.user != project.create_user) and (colla_user == 0):
                viewcode = project.role_value
                viewcode_name = 'viewcode-{}'.format(project.id)
                r_viewcode = request.COOKIES[
                    viewcode_name] if viewcode_name in request.COOKIES.keys() else 0
                if viewcode != r_viewcode:
                    allow_export = False
                else:
                    allow_export = True
            else:
                allow_export = True
        else:
            allow_export = False
        if allow_export:
            if report_type in ['epub']:
                try:
                    try:
                        report_project = ProjectReportFile.objects.get(
                            project=project, file_type='epub'
                        )
                    except ObjectDoesNotExist:
                        return JsonResponse(
                            {'status': False, 'data': '无可用文件,请联系文集创建者'}
                        )
                    return JsonResponse({'status': True, 'data': report_project.file_path})
                except Exception as e:
                    return JsonResponse({'status': False, 'data': '导出出错'})
            elif report_type in ['pdf']:
                try:
                    try:
                        report_project = ProjectReportFile.objects.get(
                            project=project, file_type='pdf'
                        )
                    except ObjectDoesNotExist:
                        return JsonResponse(
                            {'status': False, 'data': '无可用文件,请联系文集创建者'}
                        )
                    return JsonResponse({'status': True, 'data': report_project.file_path})
                except Exception as e:
                    return JsonResponse({'status': False, 'data': '导出出错'})
            else:
                return JsonResponse({'status': False, 'data': '不支持的类型'})
        else:
            return JsonResponse({'status': False, 'data': '无权限导出'})
    except ObjectDoesNotExist:
        return JsonResponse({'status': False, 'data': '文集不存在'})
    except Exception as e:
        logger.exception("获取文集前台导出文件出错")
        return JsonResponse({'status': False, 'data': '系统异常'})


@login_required()
@require_http_methods(['GET', "POST"])
def manage_image(request):
    if request.method == 'GET':
        try:
            groups = ImageGroup.objects.filter(user=request.user)
            all_img_cnt = Image.objects.filter(user=request.user).count()
            no_group_cnt = Image.objects.filter(user=request.user, group_id=None).count()
            g_id = int(request.GET.get('group', 0))
            if int(g_id) == 0:
                image_list = Image.objects.filter(user=request.user).order_by('-create_time')
            elif int(g_id) == -1:
                image_list = Image.objects.filter(user=request.user, group_id=None).order_by(
                    '-create_time')
            else:
                image_list = Image.objects.filter(user=request.user, group_id=g_id).order_by(
                    '-create_time')
            paginator = Paginator(image_list, 18)
            page = request.GET.get('page', 1)
            try:
                images = paginator.page(page)
            except PageNotAnInteger:
                images = paginator.page(1)
            except EmptyPage:
                images = paginator.page(paginator.num_pages)
            images.group = g_id
            return render(request, 'app_doc/manage_image.html', locals())
        except:
            logger.exception("图片素材管理出错")
            return render(request, '404.html')
    elif request.method == 'POST':
        try:
            img_id = request.POST.get('img_id', '')
            types = request.POST.get('types', '')
            if int(types) == 0:
                img = Image.objects.get(id=img_id)
                if img.user != request.user:
                    return JsonResponse({'status': False, 'data': '未授权请求'})
                file_path = settings.BASE_DIR + img.file_path
                is_exist = os.path.exists(file_path)
                if is_exist:
                    os.remove(file_path)
                img.delete()
                return JsonResponse({'status': True, 'data': '删除完成'})
            elif int(types) == 1:
                group_id = request.POST.get('group_id', None)
                if group_id is None:
                    Image.objects.filter(id=img_id, user=request.user).update(group_id=None)
                else:
                    group = ImageGroup.objects.get(id=group_id, user=request.user)
                    Image.objects.filter(id=img_id, user=request.user).update(group_id=group)
                return JsonResponse({'status': True, 'data': '移动完成'})
            elif int(types) == 2:
                group_id = request.POST.get('group_id', None)
                if group_id is None:
                    return JsonResponse({'status': False, 'data': '参数错误'})
                elif int(group_id) == 0:
                    imgs = Image.objects.filter(user=request.user).order_by('-create_time')
                elif int(group_id) == -1:
                    imgs = Image.objects.filter(user=request.user, group_id=None) \
                        .order_by('-create_time')
                else:
                    imgs = Image.objects.filter(user=request.user,
                                                group_id=group_id).order_by('-create_time')
                img_list = []
                for img in imgs:
                    item = {
                        'path': img.file_path,
                        'name': img.file_name,
                    }
                    img_list.append(item)
                return JsonResponse({'status': True, 'data': img_list})
            else:
                return JsonResponse({'status': False, 'data': '非法参数'})
        except ObjectDoesNotExist:
            return JsonResponse({'status': False, 'data': '图片不存在'})
        except:
            logger.exception("操作图片素材出错")
            return JsonResponse({'status': False, 'data': '程序异常'})


@login_required()
@require_http_methods(['GET', "POST"])
@logger.catch()
def manage_img_group(request):
    if request.method == 'GET':
        groups = ImageGroup.objects.filter(user=request.user)
        return render(request, 'app_doc/manage_image_group.html', locals())
    elif request.method == 'POST':
        types = request.POST.get('types', None)
        if int(types) == 0:
            group_name = request.POST.get('group_name', '')
            if group_name not in ['', '默认分组', '未分组']:
                ImageGroup.objects.create(
                    user=request.user,
                    group_name=group_name
                )
                return JsonResponse({'status': True, 'data': 'ok'})
            else:
                return JsonResponse({'status': False, 'data': '名称无效'})
        elif int(types) == 1:
            group_name = request.POST.get("group_name", '')
            if group_name not in ['', '默认分组', '未分组']:
                group_id = request.POST.get('group_id', '')
                ImageGroup.objects.filter(id=group_id, user=request.user) \
                    .update(group_name=group_name)
                return JsonResponse({'status': True, 'data': '修改成功'})
            else:
                return JsonResponse({'status': False, 'data': '名称无效'})

        elif int(types) == 2:
            try:
                group_id = request.POST.get('group_id', '')
                group = ImageGroup.objects.get(id=group_id, user=request.user)
                images = Image.objects.filter(group_id=group_id, user=request.user) \
                    .update(group_id=None)
                group.delete()
                return JsonResponse({'status': True, 'data': '删除完成'})
            except Exception as e:
                logger.exception("删除图片分组出错")
                return JsonResponse({'status': False, 'data': '删除错误'})
        elif int(types) == 3:
            try:
                group_list = []
                all_cnt = Image.objects.filter(user=request.user).count()
                non_group_cnt = Image.objects.filter(group_id=None, user=request.user).count()
                group_list.append({'group_name': '全部图片', 'group_cnt': all_cnt,
                                   'group_id': 0})
                group_list.append({'group_name': '未分组', 'group_cnt': non_group_cnt,
                                   'group_id': -1})
                groups = ImageGroup.objects.filter(user=request.user)
                for group in groups:
                    group_cnt = Image.objects.filter(group_id=group).count()
                    item = {
                        'group_id': group.id,
                        'group_name': group.group_name,
                        'group_cnt': group_cnt
                    }
                    group_list.append(item)
                return JsonResponse({'status': True, 'data': group_list})
            except:
                logger.exception("获取图片分组出错")
                return JsonResponse({'status': False, 'data': '出现错误'})


@login_required()
@require_http_methods(['GET', "POST"])
def manage_attachment(request):
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

    if request.method == 'GET':
        try:
            search_kw = request.GET.get('kw', None)
            if search_kw:
                attachment_list = Attachment.objects.filter(
                    user=request.user,
                    file_name__icontains=search_kw
                ).order_by('-create_time')
                paginator = Paginator(attachment_list, 15)
                page = request.GET.get('page', 1)
                try:
                    attachments = paginator.page(page)
                except PageNotAnInteger:
                    attachments = paginator.page(1)
                except EmptyPage:
                    attachments = paginator.page(paginator.num_pages)
                attachments.kw = search_kw
            else:
                attachment_list = Attachment.objects.filter(user=request.user) \
                    .order_by('-create_time')
                paginator = Paginator(attachment_list, 15)
                page = request.GET.get('page', 1)
                try:
                    attachments = paginator.page(page)
                except PageNotAnInteger:
                    attachments = paginator.page(1)
                except EmptyPage:
                    attachments = paginator.page(paginator.num_pages)
            return render(request, 'app_doc/manage_attachment.html', locals())
        except Exception as e:
            logger.exception("附件管理访问出错")
            return render(request, '404.html')
    elif request.method == 'POST':
        types = request.POST.get('types', '')
        if types in ['0', 0]:
            attachment = request.FILES.get('attachment_upload', None)
            if attachment:
                attachment_name = attachment.name
                attachment_size = sizeFormat(attachment.size)
                if attachment.size > 52428800:
                    return JsonResponse({'status': False, 'data': '文件大小超出限制'})
                if attachment_name.endswith('.zip'):
                    a = Attachment.objects.create(
                        file_name=attachment_name,
                        file_size=attachment_size,
                        file_path=attachment,
                        user=request.user
                    )
                    return JsonResponse({'status': True, 'data': {
                        'name': attachment_name, 'url': a.file_path.name
                    }})
                else:
                    return JsonResponse({'status': False, 'data': '不支持的格式'})
            else:
                return JsonResponse({'status': False, 'data': '无效文件'})
        elif types in ['1', 1]:
            attach_id = request.POST.get('attach_id', '')
            attachment = Attachment.objects.filter(id=attach_id, user=request.user)
            for a in attachment:
                a.file_path.delete()
            attachment.delete()
            return JsonResponse({'status': True, 'data': '删除成功'})
        elif types in [2, '2']:
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
            return JsonResponse({'status': True, 'data': attachment_list})
        else:
            return JsonResponse({'status': False, 'data': '无效参数'})
