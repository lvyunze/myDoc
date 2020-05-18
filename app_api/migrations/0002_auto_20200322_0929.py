# utf-8
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app_api', '0001_initial'),
    ]
    operations = [
        migrations.AlterField(
            model_name='usertoken',
            name='token',
            field=models.CharField(max_length=250, unique=True, verbose_name='token值'),
        ),
    ]
