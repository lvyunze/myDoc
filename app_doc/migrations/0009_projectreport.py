# utf-8
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('app_doc', '0008_auto_20191221_1055'),
    ]
    operations = [
        migrations.CreateModel(
            name='ProjectReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('allow_epub', models.IntegerField(default=0,
                                                   verbose_name='前台导出EPUB')),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='app_doc.Project', unique=True
                )),
            ],
            options={
                'verbose_name': '文集导出',
                'verbose_name_plural': '文集导出',
            },
        ),
    ]
