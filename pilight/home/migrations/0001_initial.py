# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pilight.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Light',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('index', models.IntegerField()),
                ('color', pilight.fields.ColorField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Transform',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=15)),
                ('long_name', models.CharField(max_length=60)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TransformField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=15)),
                ('long_name', models.CharField(max_length=60)),
                ('description', models.CharField(max_length=255, null=True, blank=True)),
                ('field_type', models.CharField(default=b'float', max_length=10, choices=[(b'boolean', b'True/False'), (b'long', b'Number'), (b'float', b'Decimal'), (b'color', b'Color'), (b'percentage', b'Percent')])),
                ('default_value', models.TextField(default=b'')),
                ('transform', models.ForeignKey(to='home.Transform')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TransformInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField()),
                ('params', models.TextField(null=True, blank=True)),
                ('store', models.ForeignKey(blank=True, to='home.Store', null=True)),
                ('transform', models.ForeignKey(to='home.Transform')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='light',
            name='store',
            field=models.ForeignKey(blank=True, to='home.Store', null=True),
            preserve_default=True,
        ),
    ]
