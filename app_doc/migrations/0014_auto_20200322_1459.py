# utf-8
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app_doc', '0013_image_file_name'),
    ]
    operations = [
        migrations.AlterField(
            model_name='doc',
            name='content',
            field=models.TextField(blank=True, null=True, verbose_name='文档内容'),
        ),
        migrations.AlterField(
            model_name='doc',
            name='pre_content',
            field=models.TextField(blank=True, null=True, verbose_name='编辑内容'),
        ),
    ]
