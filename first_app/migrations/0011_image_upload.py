# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-12 12:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('first_app', '0010_remove_file_upload_namefile'),
    ]

    operations = [
        migrations.CreateModel(
            name='image_upload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=264, unique=True)),
                ('image', models.ImageField(upload_to='images')),
            ],
        ),
    ]
