from django.db import models
from django.conf import settings
from pilight.classes import Color
from pilight.fields import ColorField


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
            for i in range(settings.LIGHTS_NUM_LEDS):
                light = self.create(index=i)
                light.color = Color.get_default()
                light.save()


class Light(models.Model):

    index = models.IntegerField()
    color = ColorField(blank=True, null=True)
    store = models.ForeignKey(Store, blank=True, null=True)

    objects = LightManager()

    def __unicode__(self):
        if self.store:
            return u'%s - %s - %s' % (self.store.name, unicode(self.index), self.color_hex())
        else:
            return u'%s - %s' % (unicode(self.index), self.color_hex())

    @property
    def color_hex(self):
        return self.color.to_hex()

    @property
    def color_hex_web(self):
        return self.color.to_hex_web()


# Descriptor for different transform types
class Transform(models.Model):

    name = models.CharField(max_length=15)
    long_name = models.CharField(max_length=60)
    description = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.long_name

    @property
    def default_params(self):
        """
        Builds a parameter string based on the fields assigned
        to this transform type, and their defaults
        """

        params = {}

        for transformfield in self.transformfield_set.all():
            if transformfield.field_type == 'boolean':
                default_value = bool(transformfield.default_value)
            elif transformfield.field_type == 'long':
                default_value = long(transformfield.default_value)
            elif transformfield.field_type in ('float', 'percentage'):
                default_value = float(transformfield.default_value)
            else:
                default_value = transformfield.default_value
            params[transformfield.name] = default_value

        return params


# Stores information about a given transform instance
class TransformInstanceManager(models.Manager):
    use_for_related_fields = True

    def get_current(self):
        return self.filter(store=None).order_by('order')


class TransformInstance(models.Model):

    transform = models.ForeignKey(Transform)
    order = models.IntegerField()
    params = models.TextField(blank=True, null=True)
    store = models.ForeignKey(Store, blank=True, null=True)

    objects = TransformInstanceManager()

    def __unicode__(self):
        return self.transform.long_name


FIELD_TYPE_CHOICES = (
    ('boolean', 'True/False'),
    ('long', 'Number'),
    ('float', 'Decimal'),
    ('color', 'Color'),
    ('percentage', 'Percent'),
)


class TransformField(models.Model):

    transform = models.ForeignKey(Transform)
    name = models.CharField(max_length=15)
    long_name = models.CharField(max_length=60)
    description = models.CharField(max_length=255, blank=True, null=True)
    field_type = models.CharField(max_length=10, choices=FIELD_TYPE_CHOICES, default='float')
    default_value = models.TextField(default='')

    def __unicode__(self):
        return u'%s - %s' % (self.transform.long_name, self.long_name)