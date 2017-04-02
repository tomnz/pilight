from django.db import models
from django.conf import settings
from pilight.classes import Color
from pilight.fields import ColorField
import json


# Stores metadata information about saved configurations
# TODO: Rename to "config"
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

    # TODO: Switch these to a Postgres-specific JSONField
    params = models.TextField(blank=True, null=True)
    variable_params = models.TextField(blank=True, null=True)

    store = models.ForeignKey(Store, blank=True, null=True)

    objects = TransformInstanceManager()

    def __unicode__(self):
        return self.transform


class VariableInstanceManager(models.Manager):
    use_for_related_fields = True

    def get_current(self):
        return self.filter(store=None)


class VariableInstance(models.Model):
    variable = models.TextField(blank=False, null=False)
    name = models.TextField(blank=True, null=True)
    # TODO: Switch to a Postgres-specific JSONField
    params = models.TextField(blank=True, null=True)
    store = models.ForeignKey(Store, blank=True, null=True)

    objects = VariableInstanceManager()

    def __unicode__(self):
        return self.variable
