from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from models import Transform, Light, TransformInstance
from pilight.classes import Color, PikaConnection
import json
from django.views.decorators.csrf import ensure_csrf_cookie


# Pika message passing setup
# Helper functions for controlling the light driver
def publish_message(msg):
    connection = PikaConnection.get_connection()
    channel = connection.channel()
    channel.queue_declare(queue='pilight-queue', auto_delete=False, durable=True)
    channel.basic_publish(exchange='', routing_key='pilight_queue', body=msg)


def message_start_driver():
    publish_message('start')


def message_stop_driver():
    publish_message('stop')


def message_restart_driver():
    publish_message('restart')


# Views
@ensure_csrf_cookie
def index(request):
    # Always "reset" the lights - will fill out the correct number if it's wrong
    Light.objects.reset()

    # Get objects that the page needs
    current_lights = Light.objects.get_current()
    current_transforms = TransformInstance.objects.get_current()
    transforms = Transform.objects.all()

    return render_to_response(
        'home/index.html',
        {
            'title': 'Home',
            'current_lights': current_lights,
            'transforms': transforms,
            'current_transforms': current_transforms,
        },
        context_instance=RequestContext(request)
    )


def render_lights_snippet(request):
    # Always "reset" the lights - will fill out the correct number if it's wrong
    Light.objects.reset()
    current_lights = Light.objects.get_current()

    return render_to_response(
        'home/snippets/lights.html',
        {'current_lights': current_lights},
        context_instance=RequestContext(request)
    )


def render_transforms_snippet(request):
    current_transforms = TransformInstance.objects.get_current()

    return render_to_response(
        'home/snippets/transforms.html',
        {'current_transforms': current_transforms},
        context_instance=RequestContext(request)
    )


def apply_light_tool(request):
    """
    Complex function that applies a "tool" across several lights
    """

    result = False

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
                max_idx = min(len(current_lights), index + radius)

                for i in range(min_idx, max_idx):
                    light = current_lights[i]
                    light.color = (light.color * (1.0 - opacity)) + (color * opacity)
                    light.save()

                result = True
            elif tool == 'smooth':
                # Apply the color at the given opacity and radius, with falloff
                min_idx = max(0, index - radius)
                max_idx = min(len(current_lights), index + radius)

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


def delete_transform(request):
    result = False

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


def update_transform_params(request):
    result = False

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


def add_transform(request):
    result = False

    if request.method == 'POST':
        if 'transform_id' in request.POST:
            transform = Transform.objects.filter(id=int(request.POST['transform_id']))
            if len(transform) == 1:
                transform_instance = TransformInstance()
                transform_instance.transform = transform[0]
                transform_instance.params = ''
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


def start_driver(request):
    message_start_driver()
    return HttpResponse()


def stop_driver(request):
    message_stop_driver()
    return HttpResponse()


def restart_driver(request):
    message_restart_driver()
    return HttpResponse()