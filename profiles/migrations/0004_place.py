# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-27 17:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_profile_phone'),
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
                ('pattern', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.Place')),
            ],
        ),
    ]
