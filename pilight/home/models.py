from django.db import models
from django.conf import settings

from pilight.classes import Color, scale_colors
from pilight.fields import ColorField
from pilight.light import params


class Config(models.Model):
    """Stores metadata information about saved configurations"""

    name = models.CharField(max_length=30)
    description = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name


class Playlist(models.Model):
    """Stores a set of configs to rotate through"""

    name = models.TextField()
    description = models.TextField(blank=True, null=True)
    base_duration_secs = models.FloatField(default=30)

    def __unicode__(self):
        return self.name


class PlaylistConfig(models.Model):
    config = models.ForeignKey(Config, on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    order = models.IntegerField()
    duration = models.FloatField(default=1.0)


class LastPlayed(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, null=True)


class LightManager(models.Manager):
    use_for_related_fields = True

    def get_current(self):
        return self.filter(config=None).order_by('index')

    def reset(self, config=None):
        current_lights = self.filter(config=config)
        # If we have the wrong number of lights, rescale to the expected number
        if len(current_lights) != settings.LIGHTS_NUM_LEDS:
            old_colors = [light.color for light in current_lights]
            if old_colors:
                current_lights.delete()

                new_colors = scale_colors(old_colors, settings.LIGHTS_NUM_LEDS)
                new_lights = []
                for i, color in enumerate(new_colors):
                    new_lights.append(Light(
                        index=i,
                        color=color,
                        config=config,
                    ))
            else:
                new_lights = [
                    Light(index=i, color=Color.get_default(), config=config)
                    for i in range(settings.LIGHTS_NUM_LEDS)
                ]

            Light.objects.bulk_create(new_lights)


class Light(models.Model):
    """Stores base light values"""

    index = models.IntegerField()
    color = ColorField(blank=True, null=True)
    config = models.ForeignKey(Config, blank=True, null=True)

    objects = LightManager()

    def __unicode__(self):
        if self.config:
            return '%s - %s - %s' % (self.config.name, str(self.index), self.color_hex)
        else:
            return '%s - %s' % (str(self.index), self.color_hex)

    @property
    def color_hex(self):
        return self.color.to_hex()

    @property
    def color_hex_web(self):
        return self.color.to_hex_web()


class TransformInstanceManager(models.Manager):
    use_for_related_fields = True

    def get_current(self):
        return self.filter(config=None).order_by('order')


class TransformInstance(models.Model):
    """Stores information about a given transform instance"""

    transform = models.TextField(blank=False, null=False)
    order = models.IntegerField()
    # TODO: Switch these to a Postgres-specific JSONField
    params = models.TextField(blank=True, null=True)
    config = models.ForeignKey(Config, blank=True, null=True)

    objects = TransformInstanceManager()

    def __unicode__(self):
        return self.transform


class VariableInstanceManager(models.Manager):
    use_for_related_fields = True

    def get_current(self):
        return self.filter(config=None)


class VariableInstance(models.Model):
    """Stores information about a given variable instance"""

    variable = models.TextField(blank=False, null=False)
    name = models.TextField(blank=True, null=True)
    # TODO: Switch to a Postgres-specific JSONField
    params = models.TextField(blank=True, null=True)
    config = models.ForeignKey(Config, blank=True, null=True)

    objects = VariableInstanceManager()

    def __unicode__(self):
        return self.variable


class VariableParam(models.Model):
    transform = models.ForeignKey(TransformInstance, on_delete=models.CASCADE)
    variable = models.ForeignKey(VariableInstance, on_delete=models.CASCADE)
    param = models.TextField()
    multiply = models.FloatField(default=1.0)
    add = models.FloatField(default=0.0)


def save_variable_params(transform_instance, transform_params):
    existing_ids = {
        variable_param.id
        for variable_param
        in VariableParam.objects.filter(transform=transform_instance)
    }

    for name, variable in transform_params.variable_params.items():
        variable_instance = VariableInstance.objects.get_current().get(id=variable.variable_id)
        if not variable_instance:
            # Ignore? Definitely don't need to try to save a bogus ID
            continue

        existing = VariableParam.objects.filter(
            transform=transform_instance,
            variable=variable_instance,
            param=name,
        ).first()

        if existing:
            existing.multiply = variable.multiply
            existing.add = variable.add
            existing.save()

            existing_ids.remove(existing.id)
        else:
            new_variable = VariableParam(
                transform=transform_instance,
                variable=variable_instance,
                param=name,
                add=variable.add,
                multiply=variable.multiply
            )
            new_variable.save()

    # Remove any that don't exist any longer
    VariableParam.objects.filter(id__in=existing_ids).delete()


def load_variable_params(transform_instance, params_def):
    variable_params = {}
    for variable_param in VariableParam.objects.filter(transform=transform_instance):
        param = getattr(params_def, variable_param.param, None)
        if not param:
            # We don't know about this param? Don't load it
            continue

        variable_params[variable_param.param] = params.VariableParam(
            variable_id=variable_param.variable.id,
            multiply=variable_param.multiply,
            add=variable_param.add,
            get_value=lambda: 1.0,
            convert=params.PARAM_CONVERSIONS.get(param.param_type, None),
        )

    return variable_params
