from celery import task
import time


@task
def run_lights():
    while True:
        print 'Working...'
        time.sleep(2)