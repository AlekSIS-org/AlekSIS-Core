# Generated by Django 2.2.3 on 2019-07-28 20:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_school'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='school',
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, to='core.School'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='person',
            name='school',
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, to='core.School'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='person',
            name='import_ref',
            field=models.CharField(blank=True, editable=False, max_length=64,
                                   verbose_name='Reference ID of import source'),
        ),
        migrations.AlterField(
            model_name='person',
            name='short_name',
            field=models.CharField(blank=True, max_length=5, verbose_name='Short name'),
        ),
        migrations.AlterUniqueTogether(
            name='group',
            unique_together={('school', 'short_name'), ('school', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='person',
            unique_together={('school', 'short_name'), ('school', 'import_ref')},
        ),
    ]
