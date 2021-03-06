# utf-8
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app_admin', '0003_auto_20191117_0816'),
    ]
    operations = [
        migrations.CreateModel(
            name='EmaiVerificationCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('email_name', models.EmailField(max_length=254, verbose_name='电子邮箱')),
                ('verification_type', models.CharField(max_length=50,
                                                       verbose_name='验证码类型')),
                ('verification_code', models.CharField(max_length=10,
                                                       verbose_name='验证码')),
                ('create_time', models.DateTimeField(auto_now_add=True,
                                                     verbose_name='创建时间')),
                ('expire_time', models.DateTimeField(auto_now=True, verbose_name='过期时间')),
            ],
            options={
                'verbose_name': '电子邮件验证码',
                'verbose_name_plural': '电子邮件验证码',
            },
        ),
        migrations.AddField(
            model_name='syssetting',
            name='types',
            field=models.CharField(default='basic', max_length=10, verbose_name='类型'),
        ),
    ]
