# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-27 17:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0005_auto_20170327_1722'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='pattern',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='profiles.Place'),
        ),
    ]
