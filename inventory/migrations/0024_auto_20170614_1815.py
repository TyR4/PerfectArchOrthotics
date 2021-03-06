# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-06-15 00:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0023_shoeorder_returned_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_type',
            field=models.CharField(choices=[('o', 'Orthotics'), ('cs', 'Compression Stockings'), ('os', 'Orthopedic Shoes'), ('bs', 'Back Support'), ('kb', 'Knee Brace'), ('wb', 'Wrist Brace'), ('ab', 'Ankle Brace'), ('s', 'Shoe'), ('a', 'Adjustment')], max_length=4, verbose_name='Order Type'),
        ),
    ]
