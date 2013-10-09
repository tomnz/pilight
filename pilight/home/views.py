from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from tasks import run_lights
from celery import current_app
from models import Transform, Light, TransformInstance
from pilight.classes import Color
import json
from django.views.decorators.csrf import ensure_csrf_cookie


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


def apply_light_tool(request):
    """
    Complex function that applies a "tool" across several lights
    """

    # Always "reset" the lights - will fill out the correct number if it's wrong
    Light.objects.reset()
    current_lights = list(Light.objects.get_current())

    result = {}

    if request.method == 'POST':
        if 'tool' in request.POST and \
                'index' in request.POST and \
                'radius' in request.POST and \
                'opacity' in request.POST and \
                'color' in request.POST:
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

                result['success'] = True
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

                result['success'] = True
            else:
                result['success'] = False
        else:
            result['success'] = False
    else:
        result['success'] = False

    return HttpResponse(json.dumps(result), content_type='application/json')


def start(request):
    run_lights.apply_async(task_id='run_lights')
    return HttpResponse()


def stop(request):
    current_app.control.revoke('run_lights', terminate=True)
    return HttpResponse()