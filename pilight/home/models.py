from django.db import models
from django.conf import settings
from pilight.classes import Color
from pilight.fields import ColorField
import json


# Stores metadata information about saved configurations
class Store(models.Model):

    name = models.CharField(max_length=30)
    description = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name


# Store base light values
class LightManager(models.Manager):
    use_for_related_fields = True

    def get_current(self):
        return self.filter(store=None).order_by('index')

    def reset(self):
        current_lights = self.get_current()
        # If we have the wrong number of lights, just delete the existing and replace with defaults
        if len(current_lights) != settings.LIGHTS_NUM_LEDS:
            current_lights.delete()
            new_lights = []
            for i in range(settings.LIGHTS_NUM_LEDS):
                new_lights.append(Light(
                    index=i,
                    color=Color.get_default(),
                ))

            Light.objects.bulk_create(new_lights)


class Light(models.Model):

    index = models.IntegerField()
    color = ColorField(blank=True, null=True)
    store = models.ForeignKey(Store, blank=True, null=True)

    objects = LightManager()

    def __unicode__(self):
        if self.store:
            return u'%s - %s - %s' % (self.store.name, unicode(self.index), self.color_hex)
        else:
            return u'%s - %s' % (unicode(self.index), self.color_hex)

    @property
    def color_hex(self):
        return self.color.to_hex()

    @property
    def color_hex_web(self):
        return self.color.to_hex_web()


# Stores information about a given transform instance
class TransformInstanceManager(models.Manager):
    use_for_related_fields = True

    def get_current(self):
        return self.filter(store=None).order_by('order')


class TransformInstance(models.Model):

    transform = models.TextField(blank=False, null=False)
    order = models.IntegerField()
    params = models.TextField(blank=True, null=True)
    store = models.ForeignKey(Store, blank=True, null=True)

    objects = TransformInstanceManager()

    def __unicode__(self):
        return self.transform

    @property
    def decoded_params(self):
        """
        Decodes the params field and returns an object
        containing any values that are set
        """

        try:
            params = json.loads(self.params)
        except ValueError:
            params = {}

        return params
#
#
# FIELD_TYPE_CHOICES = (
#     ('boolean', 'True/False'),
#     ('long', 'Number'),
#     ('float', 'Decimal'),
#     ('color', 'Color'),
#     ('percentage', 'Percent'),
#     ('string', 'String'),
# )
#
#
# class TransformField(models.Model):
#
#     transform = models.ForeignKey(Transform)
#     name = models.CharField(max_length=15)
#     long_name = models.CharField(max_length=60)
#     description = models.CharField(max_length=255, blank=True, null=True)
#     field_type = models.CharField(max_length=10, choices=FIELD_TYPE_CHOICES, default='float')
#     default_value = models.TextField(default='')
#
#     def __unicode__(self):
#         return u'%s - %s' % (self.transform.long_name, self.long_name)
#
#     def format_value(self, value):
#         if self.field_type == 'boolean':
#             if str(value).lower() == 'false':
#                 return False
#             else:
#                 return bool(value)
#         elif self.field_type == 'long':
#             return long(value)
#         elif self.field_type in ('float', 'percentage'):
#             return float(value)
#         elif self.field_type == 'string':
#             return str(value)
#         else:
#             return value
