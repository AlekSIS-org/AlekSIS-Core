# Generated by Django 2.2.1 on 2019-08-18 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('debug', '0002_auto_20190523_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='debuglog',
            name='filename',
            field=models.FilePathField(blank=True, match='.*.log', path='/home/p-h/git/school-apps/schoolapps/latex', verbose_name='Dateiname zur Logdatei (falls nicht Log-Text)'),
        ),
    ]
