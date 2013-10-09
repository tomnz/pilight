from home.models import Light, TransformInstance, Transform, TransformField
from django.conf import settings
import time
from pilight.classes import Color
from pilight.light.transforms import AVAILABLE_TRANSFORMS
from django.core.management.base import BaseCommand
import traceback
import sys


# Boilerplate to launch the light driver as a Django command
class Command(BaseCommand):
    args = '<>'
    help = 'Starts the light driver to await commands'

    def handle(self, *args, **options):
        driver = LightDriver()
        try:
            driver.run_lights()
        # The catch-all here is bad, but manage.py commands usually don't print
        # a stack trace, which is not very helpful for finding bugs
        except:
            print 'Exception while running light driver!'
            traceback.print_exc(file=sys.stdout)


class LightDriver(object):

    def __init__(self):
        self.should_run = False

    def wait(self):
        """
        Main entry point that waits for a start signal before running
        the actual light driver
        """
        self.run_lights()

    def run_lights(self):
        """
        Drives the actual lights in a continuous loop until receiving
        a stop signal
        """

        self.should_run = True

        # Setup the output device
        #spidev = file(settings.LIGHTS_DEV_NAME, 'wb')

        # Grab the simulation parameters
        Light.objects.reset()
        current_lights = list(Light.objects.get_current())
        current_colors = []

        if len(current_lights) != settings.LIGHTS_NUM_LEDS:
            return False

        for i in range(settings.LIGHTS_NUM_LEDS):
            current_colors.append(current_lights[i].color)

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
            colors = current_colors
            next_colors = []

            # Perform each transform step
            for transform in current_transforms:
                # Transform each light
                for i in range(settings.LIGHTS_NUM_LEDS):
                    color = transform.transform(elapsed_time, i, settings.LIGHTS_NUM_LEDS, colors[i], colors)
                    next_colors.append(color)

                # Save lights for next transform
                colors = next_colors
                next_colors = []

            # Prepare the final data
            raw_data = bytearray(settings.LIGHTS_NUM_LEDS * 3)
            for light in colors:
                raw_data[i*3:] = light.to_raw()

            # Write the data
            #spidev.write(raw_data)
            #spidev.flush()
            time.sleep(1)
            print len(raw_data)