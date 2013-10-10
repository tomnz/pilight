from home.models import Light, TransformInstance
import time
from pilight.light.transforms import AVAILABLE_TRANSFORMS
from django.conf import settings
from pilight.classes import PikaConnection


class LightDriver(object):

    def __init__(self):
        self.start_time = None

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

        # Purge all existing events
        channel.queue_purge('pilight_queue')

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

                # Reset start_time so that we start over on the next run
                self.start_time = None

    def clear_lights(self, spidev):
        if not settings.LIGHTS_NOOP:
            raw_data = bytearray(settings.LIGHTS_NUM_LEDS * 3)
            for i in range(settings.LIGHTS_NUM_LEDS * 3):
                raw_data[i] = 0x00
            spidev.write(raw_data)
            spidev.flush()

    def run_lights(self, spidev):
        """
        Drives the actual lights in a continuous loop until receiving
        a stop signal
        """

        print '* Light driver running...'

        # Grab the simulation parameters
        current_colors = self.get_colors()
        current_transforms = self.get_transforms()

        if not current_colors:
            return False

        # Run the simulation
        if not self.start_time:
            self.start_time = time.time()
        last_message_check = time.time()

        running = True
        while running:
            # Setup the current iteration
            current_time = time.time()
            elapsed_time = current_time - self.start_time

            # Check for messages only once couple of seconds
            # Slight optimization to stop rabbitmq being hammered
            # on Raspberry Pi devices
            if current_time - last_message_check > settings.LIGHTS_MESSAGE_CHECK_INTERVAL:
                msg = self.pop_message()
                last_message_check = current_time
                if msg:
                    if msg == 'stop':
                        print '    Stopping'
                        return False
                    elif msg == 'restart':
                        print '    Restarting'
                        return True

            # Note that we always start from the same base lights on each iteration
            # The previous iteration has no effect on the current iteration
            colors = self.do_step(current_colors, elapsed_time, current_transforms)

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

            # Rate limit if we're not running for real
            if settings.LIGHTS_NOOP:
                time.sleep(1)

        return False

    def run_simulation(self, time_step, steps):
        """
        Simulates a number of steps of applying transforms
        Returns [[color, color, ...], [color, color, ...], ...]
        """

        # Grab the simulation parameters
        current_colors = self.get_colors()
        current_transforms = self.get_transforms()

        if not current_colors:
            return None

        result = []

        for i in range(steps):
            elapsed_time = time_step * i
            result.append(self.do_step(current_colors, elapsed_time, current_transforms))

        return result

    def do_step(self, start_colors, elapsed_time, transforms):
        colors = start_colors
        next_colors = []

        # Perform each transform step
        for transform in transforms:
            # Transform each light
            for i in range(len(colors)):
                color = transform.transform(elapsed_time, i, len(colors), colors[i], colors)
                next_colors.append(color)

            # Save lights for next transform
            colors = next_colors
            next_colors = []

        return colors

    def get_transforms(self):
        # Grab transform instances out of the database, and
        # instantiate the corresponding classes
        transform_items = TransformInstance.objects.get_current()
        current_transforms = []

        for transform_item in transform_items:
            transform_obj = AVAILABLE_TRANSFORMS[transform_item.transform.name](transform_item)

            current_transforms.append(transform_obj)

        return current_transforms

    def get_colors(self):
        Light.objects.reset()
        current_lights = list(Light.objects.get_current())
        current_colors = []

        if len(current_lights) != settings.LIGHTS_NUM_LEDS:
            return None

        for i in range(settings.LIGHTS_NUM_LEDS):
            current_colors.append(current_lights[i].color)

        return current_colors
