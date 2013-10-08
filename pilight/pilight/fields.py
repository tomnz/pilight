from django.db import models
from django import forms
from django.utils.text import capfirst
from pilight.widgets import ColorPickerWidget
from south.modelsinspector import add_introspection_rules


class ColorField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 7
        super(ColorField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs['widget'] = ColorPickerWidget
        return super(ColorField, self).formfield(**kwargs)


add_introspection_rules([], ["^pilight\.fields\.ColorField"])