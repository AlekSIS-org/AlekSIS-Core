# Generated by Django 2.2.3 on 2019-07-16 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_split_person_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='Long name of group')),
                ('short_name', models.CharField(max_length=8, verbose_name='Short name of group')),
                ('members', models.ManyToManyField(related_name='member_of', to='core.Person')),
                ('owners', models.ManyToManyField(related_name='owner_of', to='core.Person')),
            ],
        ),
    ]
