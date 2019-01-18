# Generated by Django 2.0.4 on 2018-12-19 10:07

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aub', '0005_auto_20181128_1709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aub',
            name='created_by',
            field=models.ForeignKey(default=1, on_delete=models.SET(1), related_name='aubs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='aub',
            name='status',
            field=models.ForeignKey(default=7, on_delete=models.SET(7), related_name='aubs', to='aub.Status'),
        ),
    ]
