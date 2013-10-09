# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'CurrentLight'
        db.delete_table(u'home_currentlight')

        # Deleting model 'CurrentTransform'
        db.delete_table(u'home_currenttransform')

        # Adding model 'TransformInstance'
        db.create_table(u'home_transforminstance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('transform', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['home.Transform'])),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('params', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('store', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['home.Store'], null=True, blank=True)),
        ))
        db.send_create_signal(u'home', ['TransformInstance'])

        # Adding model 'Light'
        db.create_table(u'home_light', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('index', self.gf('django.db.models.fields.IntegerField')()),
            ('color', self.gf('pilight.fields.ColorField')(max_length=7, null=True, blank=True)),
            ('store', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['home.Store'], null=True, blank=True)),
        ))
        db.send_create_signal(u'home', ['Light'])

        # Adding model 'Store'
        db.create_table(u'home_store', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'home', ['Store'])

        # Deleting field 'TransformField.transform_type'
        db.delete_column(u'home_transformfield', 'transform_type')

        # Adding field 'TransformField.field_type'
        db.add_column(u'home_transformfield', 'field_type',
                      self.gf('django.db.models.fields.CharField')(default='float', max_length=10),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'CurrentLight'
        db.create_table(u'home_currentlight', (
            ('color', self.gf('pilight.fields.ColorField')(max_length=7, null=True, blank=True)),
            ('index', self.gf('django.db.models.fields.IntegerField')()),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'home', ['CurrentLight'])

        # Adding model 'CurrentTransform'
        db.create_table(u'home_currenttransform', (
            ('params', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('transform', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['home.Transform'])),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'home', ['CurrentTransform'])

        # Deleting model 'TransformInstance'
        db.delete_table(u'home_transforminstance')

        # Deleting model 'Light'
        db.delete_table(u'home_light')

        # Deleting model 'Store'
        db.delete_table(u'home_store')

        # Adding field 'TransformField.transform_type'
        db.add_column(u'home_transformfield', 'transform_type',
                      self.gf('django.db.models.fields.CharField')(default='int', max_length=10),
                      keep_default=False)

        # Deleting field 'TransformField.field_type'
        db.delete_column(u'home_transformfield', 'field_type')


    models = {
        u'home.light': {
            'Meta': {'object_name': 'Light'},
            'color': ('pilight.fields.ColorField', [], {'max_length': '7', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['home.Store']", 'null': 'True', 'blank': 'True'})
        },
        u'home.store': {
            'Meta': {'object_name': 'Store'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
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
            'default_value': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'field_type': ('django.db.models.fields.CharField', [], {'default': "'float'", 'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'transform': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['home.Transform']"})
        },
        u'home.transforminstance': {
            'Meta': {'object_name': 'TransformInstance'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'params': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['home.Store']", 'null': 'True', 'blank': 'True'}),
            'transform': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['home.Transform']"})
        }
    }

    complete_apps = ['home']