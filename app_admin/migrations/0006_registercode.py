# utf-8
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app_admin', '0005_auto_20191125_2155'),
    ]
    operations = [
        migrations.CreateModel(
            name='RegisterCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True,
                                          verbose_name='注册邀请码')),
                ('all_cnt', models.IntegerField(default=1, verbose_name='有效注册数量')),
                ('used_cnt', models.IntegerField(default=0, verbose_name='已使用数量')),
                ('status', models.IntegerField(default=1, verbose_name='注册码状态')),
                ('user_list', models.CharField(blank=True, max_length=500,
                                               null=True, verbose_name='使用此注册码的用户')),
                ('create_time', models.DateTimeField(auto_now=True, verbose_name='创建时间')),
                ('create_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                                  to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '注册邀请码',
                'verbose_name_plural': '注册邀请码',
            },
        ),
    ]
