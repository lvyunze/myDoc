# utf-8
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app_doc', '0012_auto_20200313_2204'),
    ]
    operations = [
        migrations.AddField(
            model_name='image',
            name='file_name',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='图片名称'),
        ),
    ]
