from celery import task
from home.models import CurrentLight, CurrentTransform, Transform, TransformField
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from copy import deepcopy
import time
from pilight.classes import Color
from pilight.light.transforms import AVAILABLE_TRANSFORMS


@task
def run_lights():
    # Do locking

    # Setup the output device
    #spidev = file(settings.LIGHTS_DEV_NAME, 'wb')

    # Grab the simulation parameters
    current_lights_db = CurrentLight.objects.all().order_by('index')
    current_lights = dict()

    for i in range(settings.LIGHTS_NUM_LEDS):
        try:
            current_lights[i] = Color.from_hex(current_lights_db.get(index=i).color)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            current_lights[i] = Color(0.5, 1, 1)

    flattened_lights = current_lights.values()

    # Initiate transform objects
    transform_items = CurrentTransform.objects.all().order_by('order')
    current_transforms = []

    for transform_item in transform_items:
        transform_obj = AVAILABLE_TRANSFORMS[transform_item.transform.name](transform_item.params)

        current_transforms[transform_item] = transform_obj

    # Run the simulation
    start_time = time.time()
    for i in range(100):
        current_time = time.time()
        elapsed_time = current_time - start_time

        # Determine the value to print to each LED
        raw_data = bytearray(settings.LIGHTS_NUM_LEDS * 3)
        for i in range(settings.LIGHTS_NUM_LEDS):
            color = deepcopy(current_lights[i])

            for transform_item, transform_obj in current_transforms:
                color = transform_obj.transform(elapsed_time, i, settings.LIGHTS_NUM_LEDS, color, flattened_lights)

            raw_data[i*3:] = color.to_raw()

        # Write the data
        #spidev.write(raw_data)
        #spidev.flush()
        print raw_data.decode('utf-8')