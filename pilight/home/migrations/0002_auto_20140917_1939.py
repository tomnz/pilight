# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transformfield',
            name='field_type',
            field=models.CharField(default=b'float', max_length=10, choices=[(b'boolean', b'True/False'), (b'long', b'Number'), (b'float', b'Decimal'), (b'color', b'Color'), (b'percentage', b'Percent'), (b'string', b'String')]),
        ),
    ]
