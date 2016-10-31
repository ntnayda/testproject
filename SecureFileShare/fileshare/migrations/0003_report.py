# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fileshare', '0002_user_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('short_desc', models.CharField(max_length=128)),
                ('long_desc', models.TextField()),
                ('file_attached', models.CharField(max_length=128)),
                ('owned_by', models.ForeignKey(to='fileshare.User')),
            ],
        ),
    ]
