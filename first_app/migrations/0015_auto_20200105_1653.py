# Generated by Django 2.1.3 on 2020-01-05 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('first_app', '0014_auto_20200105_1652'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='fee',
            field=models.CharField(max_length=264),
        ),
    ]
