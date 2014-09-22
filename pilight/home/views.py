from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from models import Transform, Light, TransformInstance, Store
from pilight.classes import Color, PikaConnection
from pilight.driver import LightDriver
from django.conf import settings
import json
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt


# Pika message passing setup
# Helper functions for controlling the light driver
def publish_message(msg):
    channel = PikaConnection.get_channel()
    channel.basic_publish(exchange='', routing_key=settings.PIKA_QUEUE_NAME, body=msg)


def message_start_driver():
    publish_message('start')


def message_stop_driver():
    publish_message('stop')


def message_restart_driver():
    publish_message('restart')


def message_color_channel(channel, color):
    # Make sure we got a color
    if not isinstance(color, Color):
        return

    # Truncate the channel name so we don't have any possibility of
    # messiness with buffer overruns or the like
    channel = str(channel)[0:30]

    publish_message('color_%s_%s' % (channel, color.to_hex()))


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
@user_passes_test(auth_check)
def index(request):
    # Always "reset" the lights - will fill out the correct number if it's wrong
    Light.objects.reset()

    # Get objects that the page needs
    current_lights = Light.objects.get_current()
    current_transforms = TransformInstance.objects.get_current()
    transforms = Transform.objects.all()
    stores = Store.objects.all().order_by('name')

    # Find average light color to use as default for paintbrush
    tool_color = Color(0, 0, 0)
    for light in current_lights:
        tool_color += light.color
    tool_color /= len(current_lights)

    return render_to_response(
        'home/index.html',
        {
            'title': 'Home',
            'current_lights': current_lights,
            'transforms': transforms,
            'current_transforms': current_transforms,
            'tool_color': tool_color.to_hex_web(),
            'stores': stores,
        },
        context_instance=RequestContext(request)
    )


@csrf_exempt
def post_auth(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)

    result = 'Failed'

    if user is not None:
        if user.is_active:
            login(request, user)
            result = 'Authenticated'
        else:
            result = 'Disabled'

    return HttpResponse(json.dumps({'result': result}), content_type='application/json')


@user_passes_test(auth_check)
def render_lights_snippet(request):
    # Always "reset" the lights - will fill out the correct number if it's wrong
    Light.objects.reset()
    current_lights = Light.objects.get_current()

    return render_to_response(
        'home/snippets/lights.html',
        {'current_lights': current_lights},
        context_instance=RequestContext(request)
    )


@user_passes_test(auth_check)
def render_transforms_snippet(request):
    current_transforms = TransformInstance.objects.get_current()

    return render_to_response(
        'home/snippets/transforms.html',
        {'current_transforms': current_transforms},
        context_instance=RequestContext(request)
    )


@user_passes_test(auth_check)
def render_stores_snippet(request):
    stores = Store.objects.all().order_by('name')

    return render_to_response(
        'home/snippets/stores-list.html',
        {'stores': stores},
        context_instance=RequestContext(request)
    )


@user_passes_test(auth_check)
def save_store(request):

    if request.method == 'POST':
        if 'store_name' in request.POST:
            # First see if the store already exists
            store_name = (request.POST['store_name'])[0:29]
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

            result = True
        else:
            result = False
    else:
        result = False

    return HttpResponse(json.dumps({'success': result}), content_type='application/json')


@user_passes_test(auth_check)
def load_store(request):

    if request.method == 'POST':
        if 'store_id' in request.POST:
            stores = Store.objects.filter(id=int(request.POST['store_id']))
            if len(stores) == 1:
                # Found the store - load its lights and transforms
                # First clear out existing "current" items
                Light.objects.get_current().delete()
                TransformInstance.objects.get_current().delete()

                for light in stores[0].light_set.all():
                    # By setting primary key to none, we ensure a copy of
                    # the object is made
                    light.pk = None
                    # Set the store to None so that it's part of the "current"
                    # setup
                    light.store = None
                    light.save()

                for transforminstance in stores[0].transforminstance_set.all():
                    transforminstance.pk = None
                    transforminstance.store = None
                    transforminstance.save()

                result = True
            else:
                result = False
        else:
            result = False
    else:
        result = False

    if result:
        message_restart_driver()

    return HttpResponse(json.dumps({'success': result}), content_type='application/json')


@user_passes_test(auth_check)
def run_simulation(request):
    # To do this, we call into the driver class to simulate running
    # the actual driver
    driver = LightDriver()
    colors = driver.run_simulation(0.1, 100)
    hex_colors = []

    for color in colors:
        hex_colors.append([x.to_hex_web() for x in color])

    return HttpResponse(json.dumps(hex_colors), content_type='application/json')


@user_passes_test(auth_check)
def apply_light_tool(request):
    """
    Complex function that applies a "tool" across several lights
    """

    if request.method == 'POST':
        if 'tool' in request.POST and \
                'index' in request.POST and \
                'radius' in request.POST and \
                'opacity' in request.POST and \
                'color' in request.POST:
            # Always "reset" the lights - will fill out the correct number if it's wrong
            Light.objects.reset()
            current_lights = list(Light.objects.get_current())

            tool = request.POST['tool']
            index = int(request.POST['index'])
            radius = int(request.POST['radius'])
            opacity = float(request.POST['opacity']) / 100
            color = Color.from_hex(request.POST['color'])

            if tool == 'solid':
                # Apply the color at the given opacity and radius
                min_idx = max(0, index - radius)
                max_idx = min(len(current_lights), index + radius + 1)

                for i in range(min_idx, max_idx):
                    light = current_lights[i]
                    light.color = (light.color * (1.0 - opacity)) + (color * opacity)
                    light.save()

                result = True
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

                result = True
            else:
                result = False
        else:
            result = False
    else:
        result = False

    if result:
        message_restart_driver()

    return HttpResponse(json.dumps({'success': result}), content_type='application/json')


@user_passes_test(auth_check)
def fill_color(request):

    if request.method == 'POST':
        if 'color' in request.POST:
            color = Color.from_hex(request.POST['color'])

            for light in Light.objects.get_current():
                light.color = color
                light.save()

            result = True
        else:
            result = False
    else:
        result = False

    if result:
        message_restart_driver()

    return HttpResponse(json.dumps({'success': result}), content_type='application/json')


@csrf_exempt
def update_color_channel(request):

    if request.method == 'POST':
        if 'color' in request.POST and 'channel' in request.POST:
            color = Color.from_hex(request.POST['color'])
            channel = request.POST['channel']

            message_color_channel(channel, color)

            result = True
        else:
            result = False
    else:
        result = False

    return HttpResponse(json.dumps({'success': result}), content_type='application/json')


@user_passes_test(auth_check)
def delete_transform(request):

    if request.method == 'POST':
        if 'transform_id' in request.POST:
            transforms = TransformInstance.objects.filter(id=int(request.POST['transform_id'])).filter(store=None)
            if len(transforms) == 1:
                transforms.delete()
                result = True
            else:
                result = False
        else:
            result = False
    else:
        result = False

    if result:
        message_restart_driver()

    return HttpResponse(json.dumps({'success': result}), content_type='application/json')


@user_passes_test(auth_check)
def update_transform_params(request):

    if request.method == 'POST':
        if 'transform_id' in request.POST and\
                'params' in request.POST:
            transforms = TransformInstance.objects.filter(id=int(request.POST['transform_id'])).filter(store=None)
            if len(transforms) == 1:
                transforms[0].params = request.POST['params']
                transforms[0].save()
                result = True
            else:
                result = False
        else:
            result = False
    else:
        result = False

    if result:
        message_restart_driver()

    return HttpResponse(json.dumps({'success': result}), content_type='application/json')


@user_passes_test(auth_check)
def add_transform(request):

    if request.method == 'POST':
        if 'transform_id' in request.POST:
            transform = Transform.objects.filter(id=int(request.POST['transform_id']))
            if len(transform) == 1:
                transform_instance = TransformInstance()
                transform_instance.transform = transform[0]
                transform_instance.params = json.dumps(transform[0].default_params)
                transform_instance.order = 0
                transform_instance.save()
                result = True
            else:
                result = False
        else:
            result = False
    else:
        result = False

    if result:
        message_restart_driver()

    return HttpResponse(json.dumps({'success': result}), content_type='application/json')


@user_passes_test(auth_check)
def start_driver(request):
    message_start_driver()
    return HttpResponse()


@user_passes_test(auth_check)
def stop_driver(request):
    message_stop_driver()
    return HttpResponse()


@user_passes_test(auth_check)
def restart_driver(request):
    message_restart_driver()
    return HttpResponse()