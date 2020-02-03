# Generated by Django 3.0.2 on 2020-02-03 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_dashboard_widget'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='sender',
            field=models.CharField(max_length=100, verbose_name='Sender'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='sent',
            field=models.BooleanField(default=False, verbose_name='Sent'),
        ),
    ]
