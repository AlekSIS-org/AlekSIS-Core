# Generated by Django 2.2.3 on 2019-07-15 11:27

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='is_student',
        ),
        migrations.RemoveField(
            model_name='person',
            name='is_teacher',
        ),
        migrations.AddField(
            model_name='person',
            name='additional_name',
            field=models.CharField(blank=True, max_length=30, verbose_name='Additional name(s)'),
        ),
        migrations.AddField(
            model_name='person',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True, verbose_name='Date of birth'),
        ),
        migrations.AddField(
            model_name='person',
            name='guardians',
            field=models.ManyToManyField(related_name='children', to=settings.AUTH_USER_MODEL, verbose_name='Guardians / Parents'),
        ),
        migrations.AddField(
            model_name='person',
            name='housenumber',
            field=models.CharField(blank=True, max_length=10, verbose_name='Street number'),
        ),
        migrations.AddField(
            model_name='person',
            name='import_ref',
            field=models.CharField(blank=True, editable=False, max_length=64, verbose_name='Reference ID of import source'),
        ),
        migrations.AddField(
            model_name='person',
            name='mobile_number',
            field=models.CharField(blank=True, max_length=30, verbose_name='Mobile phone'),
        ),
        migrations.AddField(
            model_name='person',
            name='phone_number',
            field=models.CharField(blank=True, max_length=30, verbose_name='Home phone'),
        ),
        migrations.AddField(
            model_name='person',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='Photo'),
        ),
        migrations.AddField(
            model_name='person',
            name='place',
            field=models.CharField(blank=True, max_length=30, verbose_name='Place'),
        ),
        migrations.AddField(
            model_name='person',
            name='postal_code',
            field=models.CharField(blank=True, max_length=5, verbose_name='Postal code'),
        ),
        migrations.AddField(
            model_name='person',
            name='sex',
            field=models.CharField(blank=True, choices=[('f', 'female'), ('m', 'male')], max_length=1, verbose_name='Sex'),
        ),
        migrations.AddField(
            model_name='person',
            name='street',
            field=models.CharField(blank=True, max_length=30, verbose_name='Street'),
        ),
    ]