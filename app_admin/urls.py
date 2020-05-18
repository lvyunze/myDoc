# utf-8
from django.urls import path
from app_admin import views

urlpatterns = [
    path('login/', views.log_in, name='login'),
    path('logout/', views.log_out, name='logout'),
    path('register/', views.register, name="register"),
    path('user_manage/', views.admin_user, name="user_manage"),
    path('create_user/', views.admin_create_user, name="create_user"),
    path('del_user/', views.admin_del_user, name='del_user'),
    path('change_pwd', views.admin_change_pwd, name="change_pwd"),
    path('modify_pwd', views.change_pwd, name="modify_pwd"),
    path('project_manage/', views.admin_project, name='project_manage'),
    path('project_role_manage/<int:pro_id>/', views.admin_project_role,
         name="admin_project_role"),
    path('doc_manage/', views.admin_doc, name='doc_manage'),
    path('doctemp_manage/', views.admin_doctemp, name='doctemp_manage'),
    path('setting/', views.admin_setting, name="sys_setting"),
    path('check_code/', views.check_code, name='check_code'),
    path('forget_pwd/', views.forget_pwd, name='forget_pwd'),
    path('send_email_vcode/', views.send_email_vcode, name='send_email_vcode'),
    path('admin_register_code/', views.admin_register_code, name='register_code_manage'),
]
