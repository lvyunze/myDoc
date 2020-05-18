# utf-8
from django.db import models
from django.contrib.auth.models import User


class SysSetting(models.Model):
    objects = None
    name = models.CharField(verbose_name="项目", max_length=50, primary_key=True)
    value = models.TextField(verbose_name="内容", null=True, blank=True)
    types = models.CharField(verbose_name="类型", max_length=10, default="basic")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '系统设置'
        verbose_name_plural = verbose_name


class EmaiVerificationCode(models.Model):
    objects = None
    email_name = models.EmailField(verbose_name="电子邮箱")
    verification_type = models.CharField(verbose_name="验证码类型", max_length=50)
    verification_code = models.CharField(verbose_name="验证码", max_length=10)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    expire_time = models.DateTimeField(verbose_name="过期时间")

    def __str__(self):
        return "{}:{}".format(self.verification_type, self.email_name)

    class Meta:
        verbose_name = '电子邮件验证码'
        verbose_name_plural = verbose_name


class RegisterCode(models.Model):
    objects = None
    code = models.CharField(verbose_name="注册邀请码", max_length=10, unique=True)
    all_cnt = models.IntegerField(verbose_name="有效注册数量", default=1)
    used_cnt = models.IntegerField(verbose_name='已使用数量', default=0)
    status = models.IntegerField(verbose_name="注册码状态", default=1)
    user_list = models.CharField(verbose_name="使用此注册码的用户", default='', 
                                 max_length=500, blank=True, null=True)
    create_user = models.ForeignKey(User, on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now=True, verbose_name='创建时间')

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = '注册邀请码'
        verbose_name_plural = verbose_name
