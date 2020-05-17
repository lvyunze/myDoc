from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_doc', '0009_projectreport'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectreport',
            name='project',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app_doc.Project'),
        ),
    ]
