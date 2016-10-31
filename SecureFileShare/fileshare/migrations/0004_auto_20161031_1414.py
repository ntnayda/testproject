# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fileshare', '0003_report'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='reports_owned',
            field=models.ManyToManyField(to='fileshare.Report', blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='group',
            field=models.CharField(default=None, max_length=128, blank=True),
        ),
    ]
