# utf-8
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app_doc', '0015_projectcollaborator'),
    ]
    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='attachment/%Y/%m/',
                                          verbose_name='附件')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': '附件管理',
                'verbose_name_plural': '附件管理',
            },
        ),
    ]
