# utf-8
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app_admin', '0002_auto_20191117_0808'),
    ]
    operations = [
        migrations.AlterField(
            model_name='syssetting',
            name='value',
            field=models.TextField(blank=True, null=True, verbose_name='内容'),
        ),
    ]
