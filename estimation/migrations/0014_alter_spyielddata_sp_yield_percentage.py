# Generated by Django 5.0 on 2024-04-22 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estimation', '0013_rename_time_period_wtfmethod_precipitation_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spyielddata',
            name='sp_yield_percentage',
            field=models.FloatField(),
        ),
    ]