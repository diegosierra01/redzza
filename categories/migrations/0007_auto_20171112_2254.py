# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-11-12 22:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0006_wantedcategory_notice'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wantedcategory',
            name='notice',
        ),
        migrations.RemoveField(
            model_name='wantedcategory',
            name='type_category',
        ),
    ]