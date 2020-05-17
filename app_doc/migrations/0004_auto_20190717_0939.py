from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_doc', '0003_auto_20190717_0915'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doc',
            name='path',
        ),
        migrations.AddField(
            model_name='doc',
            name='parent_doc',
            field=models.IntegerField(default=0, verbose_name='上级文档'),
        ),
    ]
