# Generated by Django 5.1.4 on 2025-01-14 18:12

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('predictor', '0007_cropdetails_photo_alter_cropdetails_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cropdetails',
            name='photo',
            field=models.ImageField(default='', upload_to='C:\\Users\\niran\\Desktop\\My Files\\Crop Prediction\\media_root/images'),
        ),
        migrations.AlterField(
            model_name='cropdetails',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2025, 1, 14, 23, 42, 23, 353937)),
        ),
    ]
