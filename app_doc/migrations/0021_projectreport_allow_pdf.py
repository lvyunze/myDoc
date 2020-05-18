# utf-8
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app_doc', '0020_projectreportfile'),
    ]
    operations = [
        migrations.AddField(
            model_name='projectreport',
            name='allow_pdf',
            field=models.IntegerField(default=0, verbose_name='前台导出PDF'),
        ),
    ]
