# Generated by Django 2.2.3 on 2019-07-16 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='short_name',
            field=models.CharField(blank=True, max_length=5, verbose_name='Short name'),
        ),
    ]