import json

from home.models import Light, TransformInstance, Store
from pilight.light.transforms import TRANSFORMS


def active_transforms():
    active_transforms_query = TransformInstance.objects.get_current()
    result = []
    for current_transform in active_transforms_query:
        transform = TRANSFORMS.get(current_transform.transform, default=None)
        if not transform:
            # Invalid transform? Just scrap the existing one
            current_transform.delete()
            continue

        result.append({
            'transform': current_transform.transform,
            'name': transform.name,
            'params': json.loads(current_transform.params),
        })
    return result


def available_transforms():
    result = []
    for name, transform in TRANSFORMS.iteritems():
        result.append({
            'transform': name,
            'name': transform.name,
            'description': transform.description,
        })
    return result


def base_colors():
    current_lights = Light.objects.get_current()
    result = []
    for light in current_lights:
        result.append(light.color.safe_dict())
    return result


def configs():
    configs_query = Store.objects.all().order_by('name')
    result = []
    for config in configs_query:
        result.append({
            'id': config.id,
            'name': config.name,
        })
    return result
