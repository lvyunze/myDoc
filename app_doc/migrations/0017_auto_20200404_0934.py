# utf-8
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app_doc', '0016_attachment'),
    ]
    operations = [
        migrations.RenameField(
            model_name='attachment',
            old_name='file',
            new_name='file_path',
        ),
        migrations.AddField(
            model_name='attachment',
            name='file_name',
            field=models.CharField(default='mrdoc_附件.zip', max_length=200,
                                   verbose_name='附件名'),
        ),
        migrations.AddField(
            model_name='attachment',
            name='file_size',
            field=models.CharField(blank=True, max_length=100, null=True,
                                   verbose_name='附件大小'),
        ),
    ]
