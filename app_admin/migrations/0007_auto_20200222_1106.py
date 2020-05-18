# utf-8
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app_admin', '0006_registercode'),
    ]
    operations = [
        migrations.AlterField(
            model_name='registercode',
            name='user_list',
            field=models.CharField(blank=True, default='', max_length=500, null=True,
                                   verbose_name='使用此注册码的用户'),
        ),
    ]
