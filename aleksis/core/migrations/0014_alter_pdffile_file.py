# Generated by Django 3.2 on 2021-04-17 18:47

from django.db import migrations, models

def _get_upload_path(instance, filename):  # noqa
    return f"pdfs/{instance.secret}.pdf"


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_pdf_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pdffile',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=_get_upload_path, verbose_name='Generated PDF file'),
        ),
    ]
