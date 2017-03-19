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
from home.models import Transform, Light, TransformInstance, Store
from pilight.classes import Color
from pilight.driver import LightDriver


def success_json(data_dict):
    data_dict['success'] = True
    return json.dumps(data_dict)


def fail_json(error):
    return json.dumps({
        'success': False,
        'error': error,
    })


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
        return HttpResponse(success_json({
            'loggedIn': False,
            'authRequired': True,
        }), content_type='application/json')

    # Always "reset" the lights - will fill out the correct number if it's wrong
    Light.objects.reset()

    # Get objects that the page needs
    current_lights = Light.objects.get_current()

    # Find average light color to use as default for paintbrush
    tool_color = Color(0.0, 0.0, 0.0)
    base_colors = []
    for light in current_lights:
        tool_color += light.color or Color(1.0, 1.0, 1.0)
        base_colors.append(light.color.safe_dict())
    tool_color /= len(current_lights)

    return HttpResponse(success_json({
        'baseColors': base_colors,
        'activeTransforms': client_queries.active_transforms(),
        'availableTransforms': client_queries.available_transforms(),
        'configs': client_queries.configs(),
        'toolColor': tool_color.safe_dict(),
        'csrfToken': csrf.get_token(request),
        'loggedIn': request.user.is_authenticated(),
        'authRequired': settings.LIGHTS_REQUIRE_AUTH,
    }), content_type='application/json')


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
        return HttpResponse(fail_json('Must include username and password'))

    return HttpResponse(success_json({
        'loggedIn': logged_in,
    }), content_type='application/json')


@require_POST
@user_passes_test(auth_check)
def logout(request):
    auth_logout(request)
    return HttpResponse(success_json({}), content_type='application/json')


@user_passes_test(auth_check)
def get_base_colors(request):
    # Always "reset" the lights - will fill out the correct number if it's wrong
    Light.objects.reset()

    return HttpResponse(success_json({
        'baseColors': client_queries.base_colors(),
    }), content_type='application/json')


@require_POST
@user_passes_test(auth_check)
def save_config(request):
    req = json.loads(request.body)

    error = None
    if 'configName' in req:
        # First see if the store already exists
        store_name = (req['configName'])[0:29]
        stores = Store.objects.filter(name=store_name)
        if len(stores) >= 1:
            store = stores[0]
            # Remove existing lights/transforms
            store.light_set.all().delete()
            store.transforminstance_set.all().delete()
        else:
            # Create new store
            store = Store()
            store.name = store_name
            store.save()

        # Copy all of the current lights and transforms to the given store
        current_lights = Light.objects.get_current()
        current_transforms = TransformInstance.objects.get_current()

        for light in current_lights:
            # By setting primary key to none, we ensure a copy of
            # the object is made
            light.pk = None
            # Set the store to None so that it's part of the "current"
            # setup
            light.store = store
            light.save()

        for transforminstance in current_transforms:
            transforminstance.pk = None
            transforminstance.store = store
            transforminstance.save()

    else:
        error = 'Must specify a config name'

    if error:
        return HttpResponse(fail_json(error), content_type='application/json')

    return HttpResponse(success_json({
        'configs': client_queries.configs(),
    }), content_type='application/json')


@require_POST
@user_passes_test(auth_check)
def load_config(request):
    req = json.loads(request.body)

    error = None
    if 'id' in req:
        store = Store.objects.get(id=req['id'])
        if store:
            # Found the store - load its lights and transforms
            # First clear out existing "current" items
            Light.objects.get_current().delete()
            TransformInstance.objects.get_current().delete()

            for light in store.light_set.all():
                # By setting primary key to none, we ensure a copy of
                # the object is made
                light.pk = None
                # Set the store to None so that it's part of the "current"
                # setup
                light.store = None
                light.save()

            for transforminstance in store.transforminstance_set.all():
                transforminstance.pk = None
                transforminstance.store = None
                transforminstance.save()

        else:
            error = 'Invalid config specified'
    else:
        error = 'Must specify a config'

    if error:
        return HttpResponse(fail_json(error), content_type='application/json')

    driver.message_restart()
    # Return an empty response - the client will re-bootstrap
    return HttpResponse(success_json({}), content_type='application/json')


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

    return HttpResponse(success_json({
        'frames': frame_dicts
    }), content_type='application/json')


@require_POST
@user_passes_test(auth_check)
def apply_light_tool(request):
    """
    Complex function that applies a "tool" across several lights
    """
    req = json.loads(request.body)

    error = None
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
            error = 'Unknown tool %s' % tool
    else:
        error = 'No tool specified'

    if error:
        return HttpResponse(fail_json(error), content_type='application/json')

    driver.message_restart()
    return HttpResponse(success_json({
        'baseColors': client_queries.base_colors(),
    }), content_type='application/json')


@require_POST
@user_passes_test(auth_check)
def fill_color(request):
    req = json.loads(request.body)

    if 'color' in req:
        color = Color.from_dict(req['color'])

        for light in Light.objects.get_current():
            light.color = color
            light.save()

    else:
        return HttpResponse(fail_json('Must specify color'))

    driver.message_restart()
    return HttpResponse(success_json({
        'baseColors': client_queries.base_colors(),
    }), content_type='application/json')


@require_POST
@csrf_exempt
def update_color_channel(request):
    req = json.loads(request.body)

    if 'color' in req and 'channel' in req:
        color = Color.from_hex(req['color'])
        channel = req['channel']

        driver.message_color_channel(channel, color)

    else:
        return HttpResponse(fail_json('Must specify color and channel'))

    return HttpResponse(success_json({}), content_type='application/json')


@require_POST
@user_passes_test(auth_check)
def delete_transform(request):
    req = json.loads(request.body)

    error = None
    if 'id' in req:
        transform = TransformInstance.objects.get(id=req['id'])
        if transform:
            transform.delete()
        else:
            error = 'Invalid transform specified'
    else:
        error = 'No transform specified'

    if error:
        return HttpResponse(fail_json(error), content_type='application/json')

    driver.message_restart()
    return HttpResponse(success_json({
        'activeTransforms': client_queries.active_transforms(),
    }), content_type='application/json')


@require_POST
@user_passes_test(auth_check)
def update_transform(request):
    req = json.loads(request.body)

    error = None
    result = None
    if 'id' in req and 'params' in req:
        transform = TransformInstance.objects.get(id=req['id'])
        if transform:
            transform.params = json.dumps(req['params'])
            transform.save()
            result = {
                'id': transform.id,
                'transformId': transform.transform.id,
                'name': transform.transform.name,
                'longName': transform.transform.long_name,
                'params': json.loads(transform.params),
            }
        else:
            error = 'Invalid transform specified'
    else:
        error = 'Must supply transform and params'

    print result
    if error:
        return HttpResponse(fail_json(error), content_type='application/json')

    driver.message_restart()
    return HttpResponse(success_json({
        'transform': result,
    }), content_type='application/json')


@require_POST
@user_passes_test(auth_check)
def add_transform(request):
    req = json.loads(request.body)

    error = None
    if 'id' in req:
        transform = Transform.objects.get(id=req['id'])
        if transform:
            transform_instance = TransformInstance()
            transform_instance.transform = transform
            transform_instance.params = json.dumps(transform.default_params)
            transform_instance.order = 0
            transform_instance.save()
        else:
            error = 'Invalid transform specified'
    else:
        error = 'No transform specified'

    if error:
        return HttpResponse(fail_json(error), content_type='application/json')

    driver.message_restart()
    return HttpResponse(success_json({
        'activeTransforms': client_queries.active_transforms(),
    }), content_type='application/json')


@require_POST
@user_passes_test(auth_check)
def start_driver(request):
    driver.message_start()
    return HttpResponse(success_json({}), content_type='application/json')


@require_POST
@user_passes_test(auth_check)
def stop_driver(request):
    driver.message_stop()
    return HttpResponse(success_json({}), content_type='application/json')


@require_POST
@user_passes_test(auth_check)
def restart_driver(request):
    driver.message_restart()
    return HttpResponse(success_json({}), content_type='application/json')
