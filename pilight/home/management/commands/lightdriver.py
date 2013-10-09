from home.models import Light, TransformInstance, Transform, TransformField
from django.conf import settings
import time
from pilight.classes import PikaConnection
from pilight.light.transforms import AVAILABLE_TRANSFORMS
from django.core.management.base import BaseCommand
from django.core.cache import cache
from optparse import make_option
import traceback
import sys


# How long to wait to expire an old lock
# Set to a day by default
LOCK_EXPIRE = 60 * 60 * 24


# Boilerplate to launch the light driver as a Django command
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '--force-run',
            action='store_true',
            dest='force_run',
            default=False,
            help="Forces the light driver to run, even if there appears to be another instance. Useful if " +
                 "the last driver exited unexpectedly and didn't clear the running flag",
        ),
        make_option(
            '--clear-lock',
            action='store_true',
            dest='clear_lock',
            default=False,
            help="Forces clearing of the flag indicating that another driver is running. Only use if you are " +
                 "sure that another instance of the driver is not running. This should never be necessary. Does " +
                 "not actually run the driver.",
        ),
    )

    help = 'Starts the light driver to await commands'

    def handle(self, *args, **options):
        lock_id = 'light-driver-running'

        if options['clear_lock']:
            # This is a "last ditch" utility function to clear the running flag
            # Return immediately afterwards
            cache.delete(lock_id)
            return

        # Perform locking - can we even run right now?
        acquire_lock = lambda: cache.add(lock_id, 'true', LOCK_EXPIRE)
        release_lock = lambda: cache.delete(lock_id)

        got_lock = acquire_lock()
        if got_lock or options['force_run']:
            # Setup the output device
            spidev = None
            if not settings.LIGHTS_NOOP:
                try:
                    spidev = file(settings.LIGHTS_DEV_NAME, 'wb')
                except:
                    # Ugly catch-all...
                    print 'Exception opening SPI device!'
                    traceback.print_exc(file=sys.stdout)

            driver = LightDriver()
            try:
                driver.wait(spidev)
            except KeyboardInterrupt:
                # The user has interrupted execution - close our resources
                print '* Cleaning up...'
                pass
            except:
                # The catch-all here is bad, but manage.py commands usually don't print
                # a stack trace, which is not very helpful for finding bugs
                print 'Exception while running light driver!'
                traceback.print_exc(file=sys.stdout)
            finally:
                # Clean up resources
                if not settings.LIGHTS_NOOP:
                    spidev.close()

                # Only release lock if it was ours to begin with (i.e. don't release if
                # someone else already had it and we were forced to run)
                if got_lock:
                    release_lock()
        else:
            print 'Another light driver appears to already be running'
            print 'Force light driver to run with --force-run'
            print 'Note that you WILL encounter issues if more than one driver runs at once'


class LightDriver(object):

    def pop_message(self):
        """
        Grabs the latest message from Pika, if one is waiting
        Returns the body of the message if present, otherwise None
        """

        connection = PikaConnection.get_connection()
        channel = connection.channel()
        channel.queue_declare('pilight_queue')
        method, properties, body = channel.basic_get('pilight_queue', no_ack=True)
        if method:
            return body
        else:
            return None

    def wait(self, spidev):
        """
        Main entry point that waits for a start signal before running
        the actual light driver
        """

        # Basically run this loop forever until interrupted
        running = True

        connection = PikaConnection.get_connection()
        channel = connection.channel()
        channel.queue_declare('pilight_queue')

        while running:
            # First wait for a "start" or "restart" command
            # "consume" is a blocking method that will wait for the first message to come in
            body = None
            print '* Light driver idle...'
            for method, properties, body in channel.consume('pilight_queue'):
                channel.basic_ack(method.delivery_tag)
                # Just break out after reading the first message
                break

            channel.cancel()

            # Note: right now we ignore 'restart' and 'stop' commands if they come in
            # In future we may want to also handle a 'restart' command here
            if body == 'start':
                # We received a start command!
                print '    Starting'
                restart = True
                while restart:
                    # Actually run the light driver
                    # Note that run_lights can return true to request that it be restarted
                    restart = self.run_lights(spidev)

                # Clear the lights to black since we're no longer running
                self.clear_lights(spidev)

    def clear_lights(self, spidev):
        raw_data = [0x00 for x in range(settings.LIGHTS_NUM_LEDS * 3)]
        if not settings.LIGHTS_NOOP:
            spidev.write(raw_data)
            spidev.flush()

    def run_lights(self, spidev):
        """
        Drives the actual lights in a continuous loop until receiving
        a stop signal
        """

        print '* Light driver running...'

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
        running = True
        while running:
            # Check for messages
            msg = self.pop_message()
            if msg:
                if msg == 'stop':
                    print '    Stopping'
                    return False
                elif msg == 'restart':
                    print '    Restarting'
                    return True

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
            pos = 0
            for light in colors:
                raw_data[pos*3:] = light.to_raw()
                pos += 1

            # Write the data
            if not settings.LIGHTS_NOOP:
                spidev.write(raw_data)
                spidev.flush()
            time.sleep(1)

        return False