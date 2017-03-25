import json

from home.models import Light, TransformInstance, Store
from pilight.light.transforms import TRANSFORMS


def active_transforms():
    active_transforms_query = TransformInstance.objects.get_current()
    result = []
    for transform_instance in active_transforms_query:
        transform = TRANSFORMS.get(transform_instance.transform, None)
        if not transform:
            # Invalid transform? Just scrap the existing one
            transform_instance.delete()
            continue

        result.append({
            'id': transform_instance.id,
            'transform': transform_instance.transform,
            'name': transform.name,
            'params': json.loads(transform_instance.params),
            'order': transform_instance.order,
        })
    return result


def available_transforms():
    result = []
    for name, transform in TRANSFORMS.iteritems():
        result.append({
            'transform': name,
            'name': transform.name,
            'description': transform.description,
            'paramsDef': transform.params_def.to_dict(),
            'order': transform.display_order,
        })

    result.sort(key=lambda t: t['order'])
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
