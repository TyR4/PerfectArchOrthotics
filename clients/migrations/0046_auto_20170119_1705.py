# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-01-20 00:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0045_auto_20161119_2033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='gender',
            field=models.CharField(blank=True, choices=[('wo', "Women's"), ('me', "Men's"), ('un', 'Unisex')], max_length=4, verbose_name='Gender'),
        ),
    ]
