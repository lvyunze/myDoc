# utf-8
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app_doc', '0001_initial'),
    ]
    operations = [
        migrations.AddField(
            model_name='doc',
            name='pre_content',
            field=models.TextField(default=1, verbose_name='编辑内容'),
            preserve_default=False,
        ),
    ]
