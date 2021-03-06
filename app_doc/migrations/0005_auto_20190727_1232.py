# utf-8
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app_doc', '0004_auto_20190717_0939'),
    ]
    operations = [
        migrations.AlterModelOptions(
            name='doc',
            options={'ordering': ['create_time', '-sort'], 'verbose_name': '文档',
                     'verbose_name_plural': '文档'},
        ),
        migrations.AddField(
            model_name='doc',
            name='sort',
            field=models.IntegerField(default=99, verbose_name='排序'),
        ),
    ]
