# Generated by Django 3.0.2 on 2020-01-22 16:49

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_add_verbose_names_meta'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='user',
            new_name='recipient',
        ),
        migrations.RenameField(
            model_name='notification',
            old_name='app',
            new_name='sender',
        ),
        migrations.RenameField(
            model_name='notification',
            old_name='mailed',
            new_name='sent',
        ),
        migrations.AlterField(
            model_name='activity',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created at'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created at'),
        ),
    ]
