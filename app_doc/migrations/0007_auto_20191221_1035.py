#utf-8
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('app_doc', '0006_auto_20191215_1910'),
    ]
    operations = [
        migrations.CreateModel(
            name='ProjectRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('role_type', models.IntegerField(choices=[(0, 0), (1, 1)],
                                                  verbose_name='私密文集类型')),
                ('role_value', models.TextField(blank=True, null=True,
                                                verbose_name='文集受限值')),
                ('create_time', models.DateField(auto_now_add=True,
                                                 verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '私密文集权限',
                'verbose_name_plural': '私密文集权限',
            },
        ),
        migrations.AddField(
            model_name='project',
            name='role',
            field=models.IntegerField(choices=[(0, 0), (1, 1)], default=0,
                                      verbose_name='文集权限'),
        ),
        migrations.AddField(
            model_name='projectrole',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    to='app_doc.Project', unique=True),
        ),
    ]
