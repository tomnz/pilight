from django.db import models
from pilight.widgets import ColorPickerWidget
from south.modelsinspector import add_introspection_rules
import pickle


class PickledObject(str):
    """A subclass of string so it can be told whether a string is
       a pickled object or not (if the object is an instance of this class
       then it must [well, should] be a pickled one)."""
    pass


class PickledObjectField(models.Field):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, PickledObject):
            # If the value is a definite pickle; and an error is raised in de-pickling
            # it should be allowed to propagate.
            return pickle.loads(str(value))
        else:
            try:
                return pickle.loads(str(value))
            except:
                # If an error was raised, just return the plain value
                return value

    def get_db_prep_save(self, value, connection):
        if value is not None and not isinstance(value, PickledObject):
            value = PickledObject(pickle.dumps(value))
        return value

    def get_internal_type(self):
        return 'TextField'

    def get_db_prep_lookup(self, lookup_type, value, connection, prepared=False):
        if lookup_type == 'exact':
            value = self.get_db_prep_save(value, connection)
            return super(PickledObjectField, self).get_db_prep_lookup(lookup_type, value)
        elif lookup_type == 'in':
            value = [self.get_db_prep_save(v, connection) for v in value]
            return super(PickledObjectField, self).get_db_prep_lookup(lookup_type, value)
        else:
            raise TypeError('Lookup type %s is not supported.' % lookup_type)


class ColorField(PickledObjectField):
    def __init__(self, *args, **kwargs):
        super(ColorField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs['widget'] = ColorPickerWidget
        return super(ColorField, self).formfield(**kwargs)


add_introspection_rules([], ["^pilight\.fields\.ColorField"])