# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-08 21:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discord', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='last_edit',
            field=models.DateTimeField(blank=True, verbose_name='Last Edit Date'),
        ),
    ]
