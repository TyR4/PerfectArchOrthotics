# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2016-11-09 21:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0042_auto_20161103_1543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='referred_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='referred_set', to='clients.Person'),
        ),
    ]
