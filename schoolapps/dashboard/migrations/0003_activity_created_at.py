# Generated by Django 2.0 on 2017-12-22 11:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ('dashboard', '0002_activity_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
