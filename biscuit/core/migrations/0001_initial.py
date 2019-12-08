# Generated by Django 2.2.5 on 2019-09-03 18:30

import biscuit.core.util.core_helpers
from django.conf import settings
from django.db import migrations, models
from django.utils.translation import ugettext_lazy as _
import django.db.models.deletion
import image_cropping.fields
import phonenumber_field.modelfields


def create_default_school(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    School = apps.get_model('core', 'School')  # noqa
    School.objects.using(db_alias).create(name=_('Default school'))


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='Name')),
                ('name_official', models.CharField(help_text='Official name of the school, e.g. as given by supervisory authority', max_length=200, verbose_name='Official name')),
            ],
            options={
                'ordering': ['name', 'name_official'],
            },
        ),
        migrations.RunPython(create_default_school),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60, verbose_name='Long name of group')),
                ('short_name', models.CharField(max_length=16, verbose_name='Short name of group')),
            ],
            options={
                'ordering': ['short_name', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is person active?')),
                ('first_name', models.CharField(max_length=30, verbose_name='First name')),
                ('last_name', models.CharField(max_length=30, verbose_name='Last name')),
                ('additional_name', models.CharField(blank=True, max_length=30, verbose_name='Additional name(s)')),
                ('short_name', models.CharField(blank=True, max_length=5, null=True, verbose_name='Short name')),
                ('street', models.CharField(blank=True, max_length=30, verbose_name='Street')),
                ('housenumber', models.CharField(blank=True, max_length=10, verbose_name='Street number')),
                ('postal_code', models.CharField(blank=True, max_length=5, verbose_name='Postal code')),
                ('place', models.CharField(blank=True, max_length=30, verbose_name='Place')),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None, verbose_name='Home phone')),
                ('mobile_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None, verbose_name='Mobile phone')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='E-mail address')),
                ('date_of_birth', models.DateField(blank=True, null=True, verbose_name='Date of birth')),
                ('sex', models.CharField(blank=True, choices=[('f', 'female'), ('m', 'male')], max_length=1, verbose_name='Sex')),
                ('photo', image_cropping.fields.ImageCropField(blank=True, null=True, upload_to='', verbose_name='Photo')),
                ('photo_cropping', image_cropping.fields.ImageRatioField('photo', '600x800', adapt_rotation=False, allow_fullsize=False, free_crop=False, help_text=None, hide_image_field=False, size_warning=True, verbose_name='photo cropping')),
                ('import_ref', models.CharField(blank=True, editable=False, max_length=64, null=True, verbose_name='Reference ID of import source')),
                ('guardians', models.ManyToManyField(related_name='children', to='core.Person', verbose_name='Guardians / Parents')),
                ('primary_group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Group')),
                ('school', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.School')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='person', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['last_name', 'first_name'],
                'unique_together': {('school', 'import_ref'), ('school', 'short_name')},
            },
        ),
        migrations.AddField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(related_name='member_of', to='core.Person'),
        ),
        migrations.AddField(
            model_name='group',
            name='owners',
            field=models.ManyToManyField(related_name='owner_of', to='core.Person'),
        ),
        migrations.AddField(
            model_name='group',
            name='parent_groups',
            field=models.ManyToManyField(related_name='child_groups', to='core.Group', verbose_name='Parent groups', blank=True),
        ),
        migrations.AddField(
            model_name='group',
            name='school',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.School'),
        ),
        migrations.AlterUniqueTogether(
            name='group',
            unique_together={('school', 'name'), ('school', 'short_name')},
        ),
    ]
