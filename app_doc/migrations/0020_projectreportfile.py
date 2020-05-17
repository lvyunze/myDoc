from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_doc', '0019_dochistory_create_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectReportFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_type', models.CharField(choices=[('epub', 'epub'), ('pdf', 'pdf'), ('docx', 'docx')], max_length=10, verbose_name='文件类型')),
                ('file_name', models.CharField(max_length=100, verbose_name='文件名称')),
                ('file_path', models.CharField(max_length=250, verbose_name='文件路径')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_doc.Project')),
            ],
            options={
                'verbose_name': '附件管理',
                'verbose_name_plural': '附件管理',
            },
        ),
    ]
