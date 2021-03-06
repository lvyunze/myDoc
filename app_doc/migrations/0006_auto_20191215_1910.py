# utf-8
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app_doc', '0005_auto_20190727_1232'),
    ]
    operations = [
        migrations.AlterModelOptions(
            name='doc',
            options={'verbose_name': '文档', 'verbose_name_plural': '文档'},
        ),
        migrations.AddField(
            model_name='doc',
            name='status',
            field=models.IntegerField(choices=[(0, 0), (1, 1)], default=1,
                                      verbose_name='文档状态'),
        ),
    ]
