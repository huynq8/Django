# Generated by Django 2.1.3 on 2020-01-05 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('first_app', '0017_auto_20200105_1812'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='fee',
            field=models.TextField(),
        ),
    ]
