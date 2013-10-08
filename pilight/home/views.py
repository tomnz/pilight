from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from tasks import run_lights
from celery import current_app


def index(request):
    return render_to_response('home/index.html')


def start(request):
    run_lights.apply_async(task_id='run_lights')
    return HttpResponse()


def stop(request):
    current_app.control.revoke('run_lights')
    return HttpResponse()