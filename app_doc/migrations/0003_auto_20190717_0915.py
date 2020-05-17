from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_doc', '0002_doc_pre_content'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doc',
            name='parent_doc',
        ),
        migrations.AddField(
            model_name='doc',
            name='path',
            field=models.CharField(default=1, max_length=50, verbose_name='文档路径'),
            preserve_default=False,
        ),
    ]
