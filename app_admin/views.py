# utf-8
from django.shortcuts import render, redirect
from django.http.response import JsonResponse, HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from app_admin.decorators import superuser_only, open_register
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
import datetime
from app_doc.models import *
from app_admin.models import *
from app_admin.utils import *
from loguru import logger


def check_code(request):
    try:
        import io
        from . import check_code as CheckCode
        stream = io.BytesIO()
        img, code = CheckCode.create_validate_code()
        img.save(stream, "png")
        request.session["CheckCode"] = code
        return HttpResponse(stream.getvalue())
    except Exception as e:
        logger.exception("生成验证码图片异常")
        return HttpResponse("请求异常：{}".format(repr(e)))


def log_in(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/')
        else:
            return render(request, 'login.html', locals())
    elif request.method == 'POST':
        try:
            username = request.POST.get('username', '')
            pwd = request.POST.get('password', '')
            if username != '' and pwd != '':
                user = authenticate(username=username, password=pwd)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return redirect('/')
                    else:
                        errormsg = '用户被禁用！'
                        return render(request, 'login.html', locals())
                else:
                    errormsg = '用户名或密码错误！'
                    return render(request, 'login.html', locals())
            else:
                errormsg = '用户名或密码错误！'
                return render(request, 'login.html', locals())
        except Exception as e:
            logger.exception("登录异常")
            return HttpResponse('请求出错')


@open_register
@logger.catch()
def register(request):
    global register_code_value
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'GET':
            return render(request, 'register.html', locals())
        elif request.method == 'POST':
            username = request.POST.get('username', None)
            email = request.POST.get('email', None)
            password = request.POST.get('password', None)
            checkcode = request.POST.get("check_code", None)
            register_code = request.POST.get("register_code", None)
            is_register_code = SysSetting.objects.filter(
                types='basic', name='enable_register_code', value='on'
            )
            if is_register_code.count() > 0:
                try:
                    register_code_value = RegisterCode.objects.get(code=register_code,
                                                                   status=1)
                except ObjectDoesNotExist:
                    errormsg = '注册码无效!'
                    return render(request, 'register.html', locals())
            if username and email and password:
                if '@' in email:
                    email_exit = User.objects.filter(email=email)
                    username_exit = User.objects.filter(username=username)
                    if email_exit.count() > 0:
                        errormsg = '此电子邮箱已被注册！'
                        return render(request, 'register.html', locals())
                    elif username_exit.count() > 0:
                        errormsg = '用户名已被使用！'
                        return render(request, 'register.html', locals())
                    elif len(password) < 6:
                        errormsg = '密码必须大于等于6位！'
                        return render(request, 'register.html', locals())
                    elif checkcode != request.session['CheckCode'].lower():
                        errormsg = "验证码错误"
                        return render(request, 'register.html', locals())
                    else:
                        user = User.objects.create_user(username=username, email=email,
                                                        password=password)
                        user.save()
                        user = authenticate(username=username, password=password)
                        if is_register_code.count() > 0:
                            r_all_cnt = register_code_value.all_cnt
                            r_used_cnt = register_code_value.used_cnt + 1
                            r_use_user = register_code_value.user_list
                            if r_used_cnt >= r_all_cnt:
                                RegisterCode.objects.filter(code=register_code).update(
                                    status=0,
                                    used_cnt=r_used_cnt,
                                    user_list=r_use_user + email + ',',
                                )
                            else:
                                RegisterCode.objects.filter(code=register_code).update(
                                    used_cnt=r_used_cnt,
                                    user_list=r_use_user + email + ',',
                                )
                        if user.is_active:
                            login(request, user)
                            return redirect('/')
                        else:
                            errormsg = '用户被禁用，请联系管理员！'
                            return render(request, 'register.html', locals())
                else:
                    errormsg = '请输入正确的电子邮箱格式！'
                    return render(request, 'register.html', locals())
            else:
                errormsg = "请检查输入值"
                return render(request, 'register.html', locals())


def log_out(request):
    try:
        logout(request)
    except Exception as e:
        logger.exception("注销异常")
    return redirect(request.META['HTTP_REFERER'])


def forget_pwd(request):
    if request.method == 'GET':
        return render(request, 'forget_pwd.html', locals())
    elif request.method == 'POST':
        email = request.POST.get("email", None)
        vcode = request.POST.get("vcode", None)
        new_pwd = request.POST.get('password', None)
        new_pwd_confirm = request.POST.get('confirm_password')
        try:
            data = EmaiVerificationCode.objects.get(
                email_name=email, verification_code=vcode, verification_type='忘记密码'
            )
            expire_time = data.expire_time
            print(expire_time)
            if expire_time > datetime.datetime.now():
                user = User.objects.get(email=email)
                user.set_password(new_pwd)
                user.save()
                errormsg = "修改密码成功，请返回登录！"
                return render(request, 'forget_pwd.html', locals())
            else:
                errormsg = "验证码已过期"
                return render(request, 'forget_pwd.html', locals())
        except Exception as e:
            logger.exception("修改密码异常")
            errormsg = "验证码错误"
            return render(request, 'forget_pwd.html', locals())


@logger.catch()
def send_email_vcode(request):
    if request.method == 'POST':
        email = request.POST.get('email', None)
        is_email = User.objects.filter(email=email)
        if is_email.count() != 0:
            vcode_str = generate_vcode()
            send_status = send_email(to_email=email, vcode_str=vcode_str)
            if send_status:
                now_time = datetime.datetime.now()
                expire_time = now_time + datetime.timedelta(minutes=30)
                EmaiVerificationCode.objects.create(
                    email_name=email,
                    verification_type='忘记密码',
                    verification_code=vcode_str,
                    expire_time=expire_time
                )
                return JsonResponse({'status': True, 'data': '发送成功'})
            else:
                return JsonResponse({'status': False, 'data': '发送验证码出错，请重试！'})

        else:
            return JsonResponse({'status': False, 'data': '电子邮箱不存在！'})
    else:
        return JsonResponse({'status': False, 'data': '方法错误'})


@superuser_only
@logger.catch()
def admin_user(request):
    if request.method == 'GET':
        return render(request, 'app_admin/admin_user.html', locals())
    elif request.method == 'POST':
        username = request.POST.get('username', '')
        if username == '':
            user_data = User.objects.all().values_list(
                'id', 'last_login', 'is_superuser', 'username',
                'email', 'date_joined', 'is_active'
            )
        else:
            user_data = User.objects.filter(username__icontains=username).values_list(
                'id', 'last_login', 'is_superuser', 'username',
                'email', 'date_joined', 'is_active'
            )
        table_data = []
        for i in list(user_data):
            item = {
                'id': i[0],
                'last_login': i[1],
                'is_superuser': i[2],
                'username': i[3],
                'email': i[4],
                'date_joined': i[5],
                'is_active': i[6]
            }
            table_data.append(item)
        return JsonResponse({'status': True, 'data': table_data})
    else:
        return JsonResponse({'status': False, 'data': '方法错误'})


@superuser_only
@logger.catch()
def admin_create_user(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        if username != '' and password != '' and email != '' and '@' in email:
            try:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email
                )
                user.save()
                return JsonResponse({'status': True})
            except Exception as e:
                return JsonResponse({'status': False})
        else:
            return JsonResponse({'status': False})
    else:
        return HttpResponse('方法不允许')


@superuser_only
@logger.catch()
def admin_change_pwd(request):
    if request.method == 'POST':
        try:
            user_id = request.POST.get('user_id', None)
            password = request.POST.get('password', None)
            password2 = request.POST.get('password2', None)
            if user_id and password:
                if password == password2:
                    user = User.objects.get(id=int(user_id))
                    user.set_password(password)
                    user.save()
                    return JsonResponse({'status': True, 'data': '修改成功'})
                else:
                    return JsonResponse({'status': False, 'data': '两个密码不一致'})
            else:
                return JsonResponse({'status': False, 'data': '参数错误'})
        except Exception as e:
            print(repr(e))
            return JsonResponse({'status': False, 'data': '请求错误'})
    else:
        return JsonResponse({'status': False, 'data': '方法错误'})


@superuser_only
@logger.catch()
def admin_del_user(request):
    if request.method == 'POST':
        try:
            user_id = request.POST.get('user_id', None)
            user = User.objects.get(id=int(user_id))
            user.delete()
            return JsonResponse({'status': True, 'data': '删除成功'})
        except Exception as e:
            return JsonResponse({'status': False, 'data': '删除出错'})
    else:
        return JsonResponse({'status': False, 'data': '方法错误'})


@superuser_only
@logger.catch()
def admin_project(request):
    if request.method == 'GET':
        search_kw = request.GET.get('kw', '')
        if search_kw == '':
            project_list = Project.objects.all()
            paginator = Paginator(project_list, 20)
            page = request.GET.get('page', 1)
            try:
                projects = paginator.page(page)
            except PageNotAnInteger:
                projects = paginator.page(1)
            except EmptyPage:
                projects = paginator.page(paginator.num_pages)
        else:
            project_list = Project.objects.filter(intro__icontains=search_kw)
            paginator = Paginator(project_list, 20)
            page = request.GET.get('page', 1)

            try:
                projects = paginator.page(page)
            except PageNotAnInteger:
                projects = paginator.page(1)
            except EmptyPage:
                projects = paginator.page(paginator.num_pages)
            projects.kw = search_kw
        return render(request, 'app_admin/admin_project.html', locals())
    else:
        return HttpResponse('方法错误')


@superuser_only
@logger.catch()
def admin_project_role(request, pro_id):
    pro = Project.objects.get(id=pro_id)
    if request.method == 'GET':
        return render(request, 'app_admin/admin_project_role.html', locals())
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
            return render(request, 'app_admin/admin_project_role.html', locals())
        else:
            return Http404


@superuser_only
@logger.catch()
def admin_doc(request):
    if request.method == 'GET':
        kw = request.GET.get('kw', '')
        if kw == '':
            doc_list = Doc.objects.all().order_by('-modify_time')
            paginator = Paginator(doc_list, 10)
            page = request.GET.get('page', 1)
            try:
                docs = paginator.page(page)
            except PageNotAnInteger:
                docs = paginator.page(1)
            except EmptyPage:
                docs = paginator.page(paginator.num_pages)
        else:
            doc_list = Doc.objects.filter(
                Q(content__icontains=kw) | Q(name__icontains=kw)
            ).order_by('-modify_time')
            paginator = Paginator(doc_list, 10)
            page = request.GET.get('page', 1)
            try:
                docs = paginator.page(page)
            except PageNotAnInteger:
                docs = paginator.page(1)
            except EmptyPage:
                docs = paginator.page(paginator.num_pages)
            docs.kw = kw
        return render(request, 'app_admin/admin_doc.html', locals())


@superuser_only
@logger.catch()
def admin_doctemp(request):
    if request.method == 'GET':
        kw = request.GET.get('kw', '')
        if kw == '':
            doctemp_list = DocTemp.objects.all()
            paginator = Paginator(doctemp_list, 10)
            page = request.GET.get('page', 1)
            try:
                doctemps = paginator.page(page)
            except PageNotAnInteger:
                doctemps = paginator.page(1)
            except EmptyPage:
                doctemps = paginator.page(paginator.num_pages)
        else:
            doctemp_list = DocTemp.objects.filter(content__icontains=kw)
            paginator = Paginator(doctemp_list, 10)
            page = request.GET.get('page', 1)
            try:
                doctemps = paginator.page(page)
            except PageNotAnInteger:
                doctemps = paginator.page(1)
            except EmptyPage:
                doctemps = paginator.page(paginator.num_pages)
            doctemps.kw = kw
        return render(request, 'app_admin/admin_doctemp.html', locals())


@superuser_only
@logger.catch()
def admin_register_code(request):
    global random_code
    if request.method == 'GET':
        register_codes = RegisterCode.objects.all()
        paginator = Paginator(register_codes, 10)
        page = request.GET.get('page', 1)
        try:
            codes = paginator.page(page)
        except PageNotAnInteger:
            codes = paginator.page(1)
        except EmptyPage:
            codes = paginator.page(paginator.num_pages)
        return render(request, 'app_admin/admin_register_code.html', locals())
    elif request.method == 'POST':
        types = request.POST.get('types', None)
        if types is None:
            return JsonResponse({'status': False, 'data': '参数错误'})
        if int(types) == 1:
            try:
                all_cnt = int(request.POST.get('all_cnt', 1))
                is_code = False
                while is_code is False:
                    code_str = \
                        '0123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
                    random_code = ''.join(random.choices(code_str, k=10))
                    random_code_used = RegisterCode.objects.filter(code=random_code).count()
                    if random_code_used > 0:
                        is_code = False
                    else:
                        is_code = True
                RegisterCode.objects.create(
                    code=random_code,
                    all_cnt=all_cnt,
                    create_user=request.user
                )
                return JsonResponse({'status': True, 'data': '新增成功'})
            except Exception as e:
                return JsonResponse({'status': False, 'data': '系统异常'})
        elif int(types) == 2:
            code_id = request.POST.get('code_id', None)
            try:
                register_code = RegisterCode.objects.get(id=int(code_id))
                register_code.delete()
                return JsonResponse({'status': True, 'data': '删除成功'})
            except ObjectDoesNotExist:
                return JsonResponse({'status': False, 'data': '注册码不存在'})
            except Exception as e:
                return JsonResponse({'status': False, 'data': '系统异常'})
        else:
            return JsonResponse({'status': False, 'data': '类型错误'})
    else:
        return JsonResponse({'status': False, 'data': '方法错误'})


@login_required()
@logger.catch()
def change_pwd(request):
    if request.method == 'POST':
        try:
            password = request.POST.get('password', None)
            password2 = request.POST.get('password2', None)
            print(password, password2)
            if password and password == password2:
                if len(password) >= 6:
                    user = User.objects.get(id=request.user.id)
                    user.set_password(password)
                    user.save()
                    return JsonResponse({'status': True, 'data': '修改成功'})
                else:
                    return JsonResponse({'status': False, 'data': '密码不得少于6位数'})
            else:
                return JsonResponse({'status': False, 'data': '两个密码不一致'})
        except Exception as e:
            return JsonResponse({'status': False, 'data': '修改出错'})
    else:
        return HttpResponse('方法错误')


@superuser_only
@logger.catch()
def admin_setting(request):
    email_settings = SysSetting.objects.filter(types="email")
    if email_settings.count() == 6:
        emailer = email_settings.get(name='send_emailer')
        email_host = email_settings.get(name='smtp_host')
        email_port = email_settings.get(name='smtp_port')
        email_username = email_settings.get(name="username")
        email_ssl = email_settings.get(name="smtp_ssl")
        email_pwd = email_settings.get(name="pwd")
    if request.method == 'GET':
        return render(request, 'app_admin/admin_setting.html', locals())
    elif request.method == 'POST':
        types = request.POST.get('type', None)
        if types == 'basic':
            close_register = request.POST.get('close_register', None)
            require_login = request.POST.get('require_login', None)
            static_code = request.POST.get('static_code', None)
            ad_code = request.POST.get('ad_code', None)
            ad_code_2 = request.POST.get('ad_code_2', None)
            beian_code = request.POST.get('beian_code', None)
            enbale_email = request.POST.get("enable_email", None)
            enable_register_code = request.POST.get('enable_register_code', None)
            enable_project_report = request.POST.get('enable_project_report', None)
            SysSetting.objects.update_or_create(
                name='require_login',
                defaults={'value': require_login, 'types': 'basic'}
            )
            SysSetting.objects.update_or_create(
                name='close_register',
                defaults={'value': close_register, 'types': 'basic'}
            )
            SysSetting.objects.update_or_create(
                name='static_code',
                defaults={'value': static_code, 'types': 'basic'}
            )
            SysSetting.objects.update_or_create(
                name='ad_code',
                defaults={'value': ad_code, 'types': 'basic'}
            )
            SysSetting.objects.update_or_create(
                name='ad_code_2',
                defaults={'value': ad_code_2, 'types': 'basic'}
            )
            SysSetting.objects.update_or_create(
                name='beian_code',
                defaults={'value': beian_code, 'types': 'basic'}
            )
            SysSetting.objects.update_or_create(
                name='enable_email',
                defaults={'value': enbale_email, 'types': 'basic'}
            )
            SysSetting.objects.update_or_create(
                name='enable_register_code',
                defaults={'value': enable_register_code, 'types': 'basic'}
            )
            SysSetting.objects.update_or_create(
                name='enable_project_report',
                defaults={'value': enable_project_report, 'types': 'basic'}
            )

            return render(request, 'app_admin/admin_setting.html', locals())
        elif types == 'email':
            emailer = request.POST.get("send_emailer", None)
            host = request.POST.get("smtp_host", None)
            port = request.POST.get("smtp_port", None)
            username = request.POST.get("smtp_username", None)
            pwd = request.POST.get("smtp_pwd", None)
            ssl = request.POST.get("smtp_ssl", None)
            pwd = enctry(pwd)
            if emailer is not None:
                SysSetting.objects.update_or_create(
                    name='send_emailer',
                    defaults={"value": emailer, "types": 'email'}
                )
            if host is not None:
                SysSetting.objects.update_or_create(
                    name='smtp_host',
                    defaults={"value": host, "types": 'email'}
                )
            if port is not None:
                SysSetting.objects.update_or_create(
                    name='smtp_port',
                    defaults={"value": port, "types": 'email'}
                )
            if username is not None:
                SysSetting.objects.update_or_create(
                    name='username',
                    defaults={"value": username, "types": 'email'}
                )
            if pwd is not None:
                SysSetting.objects.update_or_create(
                    name='pwd',
                    defaults={"value": pwd, "types": 'email'}
                )
            if ssl is not None:
                SysSetting.objects.update_or_create(
                    name='smtp_ssl',
                    defaults={"value": ssl, "types": 'email'}
                )
            email_settings = SysSetting.objects.filter(types="email")
            if email_settings.count() == 6:
                emailer = email_settings.get(name='send_emailer')
                email_host = email_settings.get(name='smtp_host')
                email_port = email_settings.get(name='smtp_port')
                email_username = email_settings.get(name="username")
                email_ssl = email_settings.get(name="smtp_ssl")
                email_pwd = email_settings.get(name="pwd")
            return render(request, 'app_admin/admin_setting.html', locals())
