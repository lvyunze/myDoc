# utf-8
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app_doc', '0014_auto_20200322_1459'),
    ]
    operations = [
        migrations.CreateModel(
            name='ProjectCollaborator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('role', models.IntegerField(choices=[(0, 0), (1, 1)], default=0,
                                             verbose_name='协作模式')),
                ('create_time', models.DateTimeField(auto_now=True,
                                                     verbose_name='添加时间')),
                ('modify_time', models.DateTimeField(auto_now_add=True,
                                                     verbose_name='修改时间')),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='app_doc.Project'
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': '文集协作',
                'verbose_name_plural': '文集协作',
            },
        ),
    ]
