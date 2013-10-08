# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CurrentLight'
        db.create_table(u'home_currentlight', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('index', self.gf('django.db.models.fields.IntegerField')()),
            ('color', self.gf('pilight.fields.ColorField')(max_length=7, null=True, blank=True)),
        ))
        db.send_create_signal(u'home', ['CurrentLight'])

        # Adding model 'CurrentTransform'
        db.create_table(u'home_currenttransform', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('transform', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['home.Transform'])),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('params', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'home', ['CurrentTransform'])

        # Adding model 'TransformField'
        db.create_table(u'home_transformfield', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('transform', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['home.Transform'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('transform_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('default_value', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'home', ['TransformField'])

        # Adding model 'Transform'
        db.create_table(u'home_transform', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('long_name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'home', ['Transform'])


    def backwards(self, orm):
        # Deleting model 'CurrentLight'
        db.delete_table(u'home_currentlight')

        # Deleting model 'CurrentTransform'
        db.delete_table(u'home_currenttransform')

        # Deleting model 'TransformField'
        db.delete_table(u'home_transformfield')

        # Deleting model 'Transform'
        db.delete_table(u'home_transform')


    models = {
        u'home.currentlight': {
            'Meta': {'object_name': 'CurrentLight'},
            'color': ('pilight.fields.ColorField', [], {'max_length': '7', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {})
        },
        u'home.currenttransform': {
            'Meta': {'object_name': 'CurrentTransform'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'params': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'transform': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['home.Transform']"})
        },
        u'home.transform': {
            'Meta': {'object_name': 'Transform'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        },
        u'home.transformfield': {
            'Meta': {'object_name': 'TransformField'},
            'default_value': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'transform': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['home.Transform']"}),
            'transform_type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }

    complete_apps = ['home']