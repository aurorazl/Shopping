# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-09-18 19:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_coupon_couponrecord'),
    ]

    operations = [
        migrations.AlterField(
            model_name='couponrecord',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.UserInfo', verbose_name='拥有者'),
        ),
    ]
