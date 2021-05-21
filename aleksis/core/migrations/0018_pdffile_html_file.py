# Generated by Django 3.2.3 on 2021-05-20 14:25

from django.db import migrations, models
from django.core.files.base import ContentFile

def _get_default():
    return ContentFile("")

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_dashboardwidget_broken'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pdffile',
            name='html',
        ),
        migrations.AddField(
            model_name='pdffile',
            name='html_file',
            field=models.FileField(default=_get_default, upload_to='pdfs/', verbose_name='Generated HTML file'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='pdffile',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='pdfs/', verbose_name='Generated PDF file'),
        ),
    ]