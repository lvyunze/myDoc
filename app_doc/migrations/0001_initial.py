# utf-8
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='Doc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='文档标题')),
                ('content', models.TextField(verbose_name='文档内容')),
                ('parent_doc', models.IntegerField(default=0, verbose_name='上级文档')),
                ('top_doc', models.IntegerField(default=0, verbose_name='所属项目')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('modify_time', models.DateTimeField(auto_now=True)),
                ('create_user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': '文档',
                'verbose_name_plural': '文档',
            },
        ),
        migrations.CreateModel(
            name='DocTemp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='模板名称')),
                ('content', models.TextField(verbose_name='文档模板')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('modify_time', models.DateTimeField(auto_now=True)),
                ('create_user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': '文档模板',
                'verbose_name_plural': '文档模板',
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='文档名称')),
                ('intro', models.TextField(verbose_name='介绍')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('modify_time', models.DateTimeField(auto_now=True)),
                ('create_user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': '文集',
                'verbose_name_plural': '文集',
            },
        ),
    ]
