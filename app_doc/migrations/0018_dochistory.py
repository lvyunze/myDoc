# utf-8
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('app_doc', '0017_auto_20200404_0934'),
    ]
    operations = [
        migrations.CreateModel(
            name='DocHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('pre_content', models.TextField(blank=True, null=True,
                                                 verbose_name='文档历史编辑内容')),
                ('create_time', models.DateTimeField(auto_now=True)),
                ('doc', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='app_doc.Doc'
                )),
            ],
            options={
                'verbose_name': '文档历史',
                'verbose_name_plural': '文档历史',
            },
        ),
    ]
