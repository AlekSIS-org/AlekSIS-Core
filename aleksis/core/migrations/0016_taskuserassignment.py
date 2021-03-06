# Generated by Django 3.2 on 2021-05-09 10:55

from django.conf import settings
import django.contrib.sites.managers
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('django_celery_results', '0008_chordcounter'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0015_oauth_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskUserAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('extended_data', models.JSONField(default=dict, editable=False)),
                ('site', models.ForeignKey(default=1, editable=False, on_delete=django.db.models.deletion.CASCADE, to='sites.site')),
                ('task_result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_celery_results.taskresult', verbose_name='Task result')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Task user')),
            ],
            options={
                'verbose_name': 'Task user assignment',
                'verbose_name_plural': 'Task user assignments',
            },
            managers=[
                ('objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
    ]
