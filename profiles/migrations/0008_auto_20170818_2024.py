# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-18 20:24
from __future__ import unicode_literals

from django.db import migrations, models
import profiles.models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0007_auto_20170817_2357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='icon',
            name='image',
            field=models.ImageField(default='Icon/icono.png', upload_to='iconos'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(default='Profile/no-avatar.png', upload_to=profiles.models.File.generatePath),
        ),
    ]
