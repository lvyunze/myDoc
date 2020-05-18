# utf-8
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app_admin', '0001_initial'),
    ]
    operations = [
        migrations.RemoveField(
            model_name='syssetting',
            name='id',
        ),
        migrations.AlterField(
            model_name='syssetting',
            name='name',
            field=models.CharField(max_length=50, primary_key=True, serialize=False,
                                   verbose_name='项目'),
        ),
    ]
