#utf-8
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app_doc', '0007_auto_20191221_1035'),
    ]
    operations = [
        migrations.RemoveField(
            model_name='projectrole',
            name='project',
        ),
        migrations.AddField(
            model_name='project',
            name='role_value',
            field=models.TextField(blank=True, null=True, verbose_name='文集权限值'),
        ),
        migrations.AlterField(
            model_name='project',
            name='role',
            field=models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3)],
                                      default=0, verbose_name='文集权限'),
        ),
        migrations.DeleteModel(
            name='ProjectRole',
        ),
    ]
