# Generated by Django 3.0.4 on 2020-03-31 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_drop_import_refs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Long name of group'),
        ),
        migrations.AlterField(
            model_name='group',
            name='short_name',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True, verbose_name='Short name of group'),
        ),
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
        migrations.AlterField(
            model_name='person',
            name='additional_name',
            field=models.CharField(blank=True, max_length=255, verbose_name='Additional name(s)'),
        ),
        migrations.AlterField(
            model_name='person',
            name='first_name',
            field=models.CharField(max_length=255, verbose_name='First name'),
        ),
        migrations.AlterField(
            model_name='person',
            name='housenumber',
            field=models.CharField(blank=True, max_length=255, verbose_name='Street number'),
        ),
        migrations.AlterField(
            model_name='person',
            name='last_name',
            field=models.CharField(max_length=255, verbose_name='Last name'),
        ),
        migrations.AlterField(
            model_name='person',
            name='place',
            field=models.CharField(blank=True, max_length=255, verbose_name='Place'),
        ),
        migrations.AlterField(
            model_name='person',
            name='postal_code',
            field=models.CharField(blank=True, max_length=255, verbose_name='Postal code'),
        ),
        migrations.AlterField(
            model_name='person',
            name='short_name',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True, verbose_name='Short name'),
        ),
        migrations.AlterField(
            model_name='person',
            name='street',
            field=models.CharField(blank=True, max_length=255, verbose_name='Street'),
        ),
        migrations.AlterField(
            model_name='school',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='school',
            name='name_official',
            field=models.CharField(help_text='Official name of the school, e.g. as given by supervisory authority', max_length=255, verbose_name='Official name'),
        ),
        migrations.AlterField(
            model_name='schoolterm',
            name='caption',
            field=models.CharField(max_length=255, verbose_name='Visible caption of the term'),
        ),
    ]
