# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-31 21:50
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('things', '0008_remove_notice_optiontrade'),
    ]

    operations = [
        migrations.AddField(
            model_name='notice',
            name='date',
            field=models.DateField(default=datetime.datetime.now),
        ),
    ]