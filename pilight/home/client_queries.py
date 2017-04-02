import json

from home.models import Light, TransformInstance, Store, VariableInstance, load_variable_params
from pilight.light.transforms import TRANSFORMS
from pilight.light.variables import VARIABLES


def active_transforms():
    active_transforms_query = TransformInstance.objects.get_current()
    result = []
    for transform_instance in active_transforms_query:
        transform = TRANSFORMS.get(transform_instance.transform, None)
        if not transform:
            # Invalid transform? Just scrap the existing one
            transform_instance.delete()
            continue

        variable_params = load_variable_params(transform_instance)
        variable_params_dict = {key: value.to_dict() for key, value in variable_params.iteritems()}

        result.append({
            'id': transform_instance.id,
            'transform': transform_instance.transform,
            'name': transform.name,
            'params': json.loads(transform_instance.params or '{}'),
            'variableParams': variable_params_dict,
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


def active_variables():
    active_variables_query = VariableInstance.objects.get_current()
    result = []
    for variable_instance in active_variables_query:
        variable = VARIABLES.get(variable_instance.variable, None)
        if not variable:
            # Invalid transform? Just scrap the existing one
            variable_instance.delete()
            continue

        result.append({
            'id': variable_instance.id,
            'variable': variable_instance.variable,
            'name': variable_instance.name,
            'params': json.loads(variable_instance.params or '{}'),
            'type': variable.param_type,
        })
    return result


def available_variables():
    result = []
    for name, variable in VARIABLES.iteritems():
        result.append({
            'variable': name,
            'name': variable.name,
            'description': variable.description,
            'paramsDef': variable.params_def.to_dict(),
            'order': variable.display_order,
            'type': variable.param_type,
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
