from django.db import models
from pilight.fields import ColorField


class CurrentLight(models.Model):

    index = models.IntegerField()
    color = ColorField(blank=True, null=True)

    def __unicode__(self):
        return self.color


class Transform(models.Model):

    name = models.CharField(max_length=15)
    long_name = models.CharField(max_length=60)
    description = models.TextField(blank=True, null=True)


class TransformInstance(models.Model):

    transform = models.ForeignKey(Transform)
    order = models.IntegerField()
    params = models.TextField(blank=True, null=True)


TRANSFORM_TYPE_CHOICES = (
    ('boolean', 'True/False'),
    ('integer', 'Number'),
    ('color', 'Color'),
    ('percentage', 'Percent'),
)


class TransformField(models.Model):

    transform = models.ForeignKey(Transform)
    name = models.CharField(max_length=10)
    transform_type = models.CharField(max_length=10, choices=TRANSFORM_TYPE_CHOICES)
    default_value = models.TextField()