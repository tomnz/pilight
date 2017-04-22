import json

from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.middleware import csrf
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_POST

from home import client_queries, driver
from home.models import Config, Light, TransformInstance, VariableInstance, VariableParam, save_variable_params
from pilight.classes import Color
from pilight.driver import LightDriver
from pilight.light import params
from pilight.light.transforms import TRANSFORMS
from pilight.light.variables import VARIABLES


def success_json(data_dict):
    data_dict['success'] = True
    return HttpResponse(json.dumps(data_dict), content_type='application/json')


def fail_json(error):
    return HttpResponse(json.dumps({
        'success': False,
        'error': error,
    }), content_type='application/json')


def auth_check(user):
    # Should we restrict access?
    if not settings.LIGHTS_REQUIRE_AUTH:
        return True

    # Auth is really easy - you just need to be logged in
    if user.is_authenticated():
        return True
    else:
        return False


# Views
@ensure_csrf_cookie
def index(request):
    return render(
        request,
        'home/index.html',
    )


@ensure_csrf_cookie
def bootstrap_client(request):
    if not request.user.is_authenticated() and settings.LIGHTS_REQUIRE_AUTH:
        success_json({
            'loggedIn': False,
            'authRequired': True,
        })

    # Always "reset" the lights - will fill out the correct number if it's wrong
    Light.objects.reset()

    # Get objects that the page needs
    current_lights = Light.objects.get_current()

    # Find average light color to use as default for paintbrush
    tool_color = Color(0.0, 0.0, 0.0)
    base_colors = []
    for light in current_lights:
        tool_color += light.color or Color.get_default()
        base_colors.append(light.color.safe_dict())
    tool_color /= len(current_lights)

    return success_json({
        'numLights': settings.LIGHTS_NUM_LEDS,
        'baseColors': base_colors,
        'activeTransforms': client_queries.active_transforms(),
        'availableTransforms': client_queries.available_transforms(),
        'activeVariables': client_queries.active_variables(),
        'availableVariables': client_queries.available_variables(),
        'configs': client_queries.configs(),
        'toolColor': tool_color.safe_dict(),
        'csrfToken': csrf.get_token(request),
        'loggedIn': request.user.is_authenticated(),
        'authRequired': settings.LIGHTS_REQUIRE_AUTH,
    })


@require_POST
@csrf_exempt
def login(request):
    req = json.loads(request.body)

    logged_in = False
    if 'username' in req and 'password' in req:
        username = req['username']
        password = req['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                auth_login(request, user)
                logged_in = True
    else:
        return fail_json('Must include username and password')

    return success_json({'loggedIn': logged_in})


@require_POST
@user_passes_test(auth_check)
def logout(request):
    auth_logout(request)
    return success_json({})


@user_passes_test(auth_check)
def get_base_colors(request):
    # Always "reset" the lights - will fill out the correct number if it's wrong
    Light.objects.reset()

    return success_json({'baseColors': client_queries.base_colors()})


@require_POST
@user_passes_test(auth_check)
def save_config(request):
    req = json.loads(request.body)

    if 'configName' in req:
        # First see if the config already exists
        config_name = (req['configName'])[0:29]
        configs = Config.objects.filter(name=config_name)
        if len(configs) >= 1:
            config = configs[0]
            # Remove existing lights/transforms
            config.light_set.all().delete()
            config.transforminstance_set.all().delete()
        else:
            # Create new config
            config = Config()
            config.name = config_name
            config.save()

        # Copy all of the current lights and transforms to the given config
        current_lights = Light.objects.get_current()
        config_lights = []
        for light in current_lights:
            # By setting primary key to none, we ensure a copy of
            # the object is made
            light.pk = None
            # Set the config to None so that it's part of the "current"
            # setup
            light.config = config
            config_lights.append(light)
        Light.objects.bulk_create(config_lights)

        current_transforms = TransformInstance.objects.get_current()
        for transform_instance in current_transforms:
            variable_params = transform_instance.variableparam_set.all()

            transform_instance.pk = None
            transform_instance.config = config
            transform_instance.save()

            for variable_param in variable_params:
                variable_param.pk = None
                variable_param.transform = transform_instance
                variable_param.save()

    else:
        return fail_json('Must specify a config name')

    return success_json({'configs': client_queries.configs()})


@require_POST
@user_passes_test(auth_check)
def delete_config(request):
    req = json.loads(request.body)

    if 'id' in req:
        config = Config.objects.filter(id=req['id']).first()
        if config:
            # Found the config - delete its associated objects
            Light.objects.filter(config=config).delete()
            TransformInstance.objects.filter(config=config).delete()

            # Finally, delete the config itself
            config.delete()

        else:
            return fail_json('Invalid config specified')
    else:
        return fail_json('Must specify a config')

    return success_json({'configs': client_queries.configs()})


@require_POST
@user_passes_test(auth_check)
def load_config(request):
    req = json.loads(request.body)

    if 'id' in req:
        config = Config.objects.filter(id=req['id']).first()
        if config:
            # Found the config - load its lights and transforms
            # First clear out existing "current" items
            Light.objects.get_current().delete()
            TransformInstance.objects.get_current().delete()

            new_lights = []
            for light in config.light_set.all():
                # By setting primary key to none, we ensure a copy of
                # the object is made
                light.pk = None
                # Set the config to None so that it's part of the "current"
                # setup
                light.config = None
                new_lights.append(light)

            Light.objects.bulk_create(new_lights)

            for transform_instance in config.transforminstance_set.all():
                variable_params = transform_instance.variableparam_set.all()

                transform_instance.pk = None
                transform_instance.config = None
                transform_instance.save()

                for variable_param in variable_params:
                    variable_param.pk = None
                    variable_param.transform = transform_instance
                    variable_param.save()

        else:
            return fail_json('Invalid config specified')
    else:
        return fail_json('Must specify a config')

    driver.message_restart()
    # Return an empty response - the client will re-bootstrap
    return success_json({})


@require_POST
@user_passes_test(auth_check)
def preview(request):
    # To do this, we call into the driver class to simulate running
    # the actual driver
    driver = LightDriver(simulation=True)
    frames = driver.run_simulation(0.05, 100)
    frame_dicts = []

    for frame in frames:
        frame_dicts.append([color.safe_dict() for color in frame])

    return success_json({'frames': frame_dicts})


@require_POST
@user_passes_test(auth_check)
def apply_light_tool(request):
    """
    Complex function that applies a "tool" across several lights
    """
    req = json.loads(request.body)

    if 'tool' in req and \
                    'index' in req and \
                    'radius' in req and \
                    'opacity' in req and \
                    'color' in req:

        # Always "reset" the lights - will fill out the correct number if it's wrong
        Light.objects.reset()
        current_lights = list(Light.objects.get_current())

        tool = req['tool']
        index = req['index']
        radius = req['radius']
        opacity = float(req['opacity']) / 100
        color = Color.from_dict(req['color'])

        if tool == 'solid':
            # Apply the color at the given opacity and radius
            min_idx = max(0, index - radius)
            max_idx = min(len(current_lights), index + radius + 1)

            for i in range(min_idx, max_idx):
                light = current_lights[i]
                light.color = (light.color * (1.0 - opacity)) + (color * opacity)
                light.save()

        elif tool == 'smooth':
            # Apply the color at the given opacity and radius, with falloff
            min_idx = max(0, index - radius)
            max_idx = min(len(current_lights), index + radius + 1)

            for i in range(min_idx, max_idx):
                distance = abs(index - i)
                # TODO: Better falloff function
                strength = (1.0 - (float(distance) / radius)) * opacity

                light = current_lights[i]
                light.color = (light.color * (1.0 - strength)) + (color * strength)
                light.save()

        else:
            return fail_json('Unknown tool %s' % tool)
    else:
        return fail_json('No tool specified')

    driver.message_restart()
    return success_json({'baseColors': client_queries.base_colors()})


@require_POST
@user_passes_test(auth_check)
def fill_color(request):
    req = json.loads(request.body)

    if 'color' in req:
        color = Color.from_dict(req['color'])

        Light.objects.get_current().update(color=color)

    else:
        return fail_json('Must specify color')

    driver.message_restart()
    return success_json({'baseColors': client_queries.base_colors()})


@require_POST
@csrf_exempt
def update_color_channel(request):
    req = json.loads(request.body)

    if 'color' in req and 'channel' in req:
        color = Color.from_hex(req['color'])
        channel = req['channel']

        driver.message_color_channel(channel, color)

    else:
        return fail_json('Must specify color and channel')

    return success_json({})


@require_POST
@user_passes_test(auth_check)
def delete_transform(request):
    req = json.loads(request.body)

    if 'id' in req:
        transform = TransformInstance.objects.get(id=req['id'])
        if transform:
            transform.delete()
        else:
            return fail_json('Invalid transform specified')

        # Reorder existing transform
        transforms = TransformInstance.objects.get_current()
        for order, transform in enumerate(transforms):
            transform.order = order
            transform.save()

    else:
        return fail_json('No transform specified')

    driver.message_restart()
    return success_json({'activeTransforms': client_queries.active_transforms()})


@require_POST
@user_passes_test(auth_check)
def update_transform(request):
    req = json.loads(request.body)

    if 'id' in req and 'params' in req:
        transform_instance = TransformInstance.objects.get(id=req['id'])
        if transform_instance:
            transform = TRANSFORMS.get(transform_instance.transform, None)
            if transform:
                variable_params = params.transform_variable_params_from_dict(
                    req.get('variableParams', {}),
                    transform.params_def,
                )
                transform_params = params.transform_params_from_dict(
                    req['params'],
                    variable_params,
                    transform.params_def
                )

                transform_instance.params = json.dumps(transform_params.to_dict())
                save_variable_params(transform_instance, transform_params)
                variable_params_dict = {key: value.to_dict() for key, value in variable_params.iteritems()}

                transform_instance.save()
                result = {
                    'id': transform_instance.id,
                    'transform': transform_instance.transform,
                    'name': transform.name,
                    'params': json.loads(transform_instance.params),
                    'variableParams': variable_params_dict,
                    'order': transform_instance.order,
                }
            else:
                # Invalid transform? Scrap the existing one
                transform_instance.delete()
                return fail_json('Invalid transform')
        else:
            return fail_json('Invalid transform specified')
    else:
        return fail_json('Must supply transform and params')

    driver.message_restart()
    return success_json({'transform': result})


@require_POST
@user_passes_test(auth_check)
def add_transform(request):
    req = json.loads(request.body)

    if 'transform' in req:
        transform_name = req['transform']
        transform = TRANSFORMS.get(transform_name, None)
        if transform:
            # Get the number of current transforms, so we can order the new
            # one at the end
            num_transforms = TransformInstance.objects.get_current().count()

            params_dict = params.transform_params_from_dict(
                {}, {}, transform.params_def
            ).to_dict()

            transform_instance = TransformInstance()
            transform_instance.transform = transform_name
            transform_instance.params = json.dumps(params_dict)
            transform_instance.order = num_transforms
            transform_instance.save()
        else:
            return fail_json('Invalid transform specified: %s' % transform_name)
    else:
        return fail_json('No transform specified')

    driver.message_restart()
    return success_json({'activeTransforms': client_queries.active_transforms()})


@require_POST
@user_passes_test(auth_check)
def reorder_transforms(request):
    req = json.loads(request.body)

    if 'order' in req:
        for order, transform_id in enumerate(req['order']):
            transform_instance = TransformInstance.objects.get(id=transform_id)
            if transform_instance:
                transform_instance.order = order
                transform_instance.save()
    else:
        return fail_json('No order specified')

    driver.message_restart()
    return success_json({'activeTransforms': client_queries.active_transforms()})


@require_POST
@user_passes_test(auth_check)
def add_variable(request):
    req = json.loads(request.body)

    if 'variable' in req:
        variable_name = req['variable']
        variable = VARIABLES.get(variable_name, None)
        if variable:
            # If this is a singleton, make sure there aren't any others
            if variable.singleton:
                num_existing = VariableInstance.objects.get_current().filter(variable=variable_name).count()
                if num_existing >= 1:
                    return fail_json('Can only add one %s variable at once' % variable.name)

            params_dict = params.variable_params_from_dict({}, variable.params_def).to_dict()

            variable_instance = VariableInstance()
            variable_instance.variable = variable_name
            # TODO: Automatically differentiate names with an ordinal?
            variable_instance.name = variable.name
            variable_instance.params = json.dumps(params_dict)
            variable_instance.save()
        else:
            return fail_json('Invalid variable specified: %s' % variable_name)
    else:
        return fail_json('No variable specified')

    driver.message_restart()
    return success_json({'activeVariables': client_queries.active_variables()})


@require_POST
@user_passes_test(auth_check)
def delete_variable(request):
    req = json.loads(request.body)

    if 'id' in req:
        variable = VariableInstance.objects.get(id=req['id'])
        if variable:
            variable.delete()
        else:
            return fail_json('Invalid variable specified')

    else:
        return fail_json('No variable specified')

    driver.message_restart()
    return success_json({
        'activeVariables': client_queries.active_variables(),
        # If we deleted a variable in use, it can impact active transforms
        'activeTransforms': client_queries.active_transforms(),
    })


@require_POST
@user_passes_test(auth_check)
def update_variable(request):
    req = json.loads(request.body)

    if 'id' in req and 'params' in req:
        variable_instance = VariableInstance.objects.get(id=req['id'])
        if variable_instance:
            variable = VARIABLES.get(variable_instance.variable, None)
            if variable:
                params_dict = params.variable_params_from_dict(
                    req['params'],
                    variable.params_def
                ).to_dict()

                variable_instance.params = json.dumps(params_dict)

                if 'name' in req:
                    variable_instance.name = req['name']

                variable_instance.save()
                result = {
                    'id': variable_instance.id,
                    'variable': variable_instance.variable,
                    'name': variable_instance.name,
                    'params': json.loads(variable_instance.params),
                }
            else:
                # Invalid variable? Scrap the existing one
                variable_instance.delete()
                return fail_json('Invalid variable')
        else:
            return fail_json('Invalid variable specified')
    else:
        return fail_json('Must supply variable and params')

    driver.message_restart()
    return success_json({'variable': result})


@require_POST
@user_passes_test(auth_check)
def start_driver(request):
    driver.message_start()
    return success_json({})


@require_POST
@user_passes_test(auth_check)
def stop_driver(request):
    driver.message_stop()
    return success_json({})


@require_POST
@user_passes_test(auth_check)
def restart_driver(request):
    driver.message_restart()
    return success_json({})
