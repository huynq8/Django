# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-11 10:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('first_app', '0008_auto_20171111_1644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file_upload',
            name='contentfile',
            field=models.FileField(upload_to='media'),
        ),
    ]
