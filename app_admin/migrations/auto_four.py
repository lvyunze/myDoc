# utf-8

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app_admin', '0004_auto_20191121_2103'),
    ]
    operations = [
        migrations.AlterField(
            model_name='emaiverificationcode',
            name='expire_time',
            field=models.DateTimeField(verbose_name='过期时间'),
        ),
    ]
