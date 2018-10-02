# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-16 04:51
from __future__ import unicode_literals

from django.db import migrations, models
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0008_auto_20171031_1950'),
    ]

    operations = [
        migrations.CreateModel(
            name='KeyValue',
            fields=[
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('key', models.SlugField(max_length=255, primary_key=True, serialize=False, unique=True)),
                ('value', models.TextField()),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
    ]