# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-11 20:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advertising', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='advertising',
            name='counter',
            field=models.IntegerField(default=0),
        ),
    ]
