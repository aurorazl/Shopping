# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-09-22 16:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20180923_0043'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactionrecord',
            name='balance',
            field=models.IntegerField(blank=True, null=True, verbose_name='账户余额'),
        ),
    ]
