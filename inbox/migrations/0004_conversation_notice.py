# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-02 00:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('things', '0004_auto_20170829_1922'),
        ('inbox', '0003_auto_20170901_2359'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='notice',
            field=models.ManyToManyField(to='things.Notice'),
        ),
    ]
