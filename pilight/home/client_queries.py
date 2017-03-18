import json

from home.models import Transform, Light, TransformInstance, Store


def active_transforms():
    active_transforms_query = TransformInstance.objects.get_current()
    result = []
    for current_transform in active_transforms_query:
        result.append({
            'id': current_transform.id,
            'transformId': current_transform.transform.id,
            'name': current_transform.transform.name,
            'longName': current_transform.transform.long_name,
            'params': json.loads(current_transform.params),
        })
    return result


def available_transforms():
    transforms_query = Transform.objects.all()
    result = []
    for transform in transforms_query:
        result.append({
            'id': transform.id,
            'name': transform.name,
            'longName': transform.long_name,
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
