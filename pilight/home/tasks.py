from celery import task
from home.models import Light, TransformInstance, Transform, TransformField
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import time
from pilight.classes import Color
from pilight.light.transforms import AVAILABLE_TRANSFORMS


@task
def run_lights():
    # Do locking

    # Setup the output device
    #spidev = file(settings.LIGHTS_DEV_NAME, 'wb')

    # Grab the simulation parameters
    current_lights_db = Light.objects.get_current()
    current_lights = []

    for i in range(settings.LIGHTS_NUM_LEDS):
        try:
            current_lights.append(Color.from_hex(current_lights_db.get(index=i).color))
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            current_lights.append(Color(0.5, 1, 1))

    # Initiate transform objects
    transform_items = TransformInstance.objects.get_current()
    current_transforms = []

    for transform_item in transform_items:
        transform_obj = AVAILABLE_TRANSFORMS[transform_item.transform.name](transform_item.params)

        current_transforms.append(transform_obj)

    # Run the simulation
    start_time = time.time()
    for i in range(20):
        # Setup the current iteration
        current_time = time.time()
        elapsed_time = current_time - start_time

        # Note that we always start from the same base lights on each iteration
        # The previous iteration has no effect on the current iteration
        lights = current_lights
        next_lights = []

        # Perform each transform step
        for transform in current_transforms:
            # Transform each light
            for i in range(settings.LIGHTS_NUM_LEDS):
                color = transform.transform(elapsed_time, i, settings.LIGHTS_NUM_LEDS, lights[i], lights)
                next_lights.append(color)

            # Save lights for next transform
            lights = next_lights
            next_lights = []

        # Prepare the final data
        raw_data = bytearray(settings.LIGHTS_NUM_LEDS * 3)
        for light in lights:
            raw_data[i*3:] = light.to_raw()

        # Write the data
        #spidev.write(raw_data)
        #spidev.flush()
        time.sleep(1)
        print raw_data.decode('utf-8')