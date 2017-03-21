import time

from django.conf import settings

from home.models import Light, TransformInstance
from pilight.devices import client, noop, ws2801, ws281x
from pilight.classes import PikaConnection, Color
from pilight.light.transforms import AVAILABLE_TRANSFORMS, BrightnessVariableTransform
from pilight.light.variables import AudioVariable


DEVICES = {
    'noop': noop.Device,
    'client': client.Device,
    'ws2801': ws2801.Device,
    'ws281x': ws281x.Device,
}


class LightDriver(object):

    def __init__(self, simulation=False):
        self.start_time = None
        self.messages_since_last_queue_check = 0
        self.color_channels = {}

        if simulation:
            return

        if settings.LIGHTS_DEVICE not in DEVICES:
            raise KeyError('Unknown device specified, please check your settings')

        self.device = DEVICES[settings.LIGHTS_DEVICE](settings.LIGHTS_NUM_LEDS, settings.LIGHTS_SCALE)

    def pop_message(self):
        """
        Grabs the latest message from Pika, if one is waiting
        Returns the body of the message if present, otherwise None
        """
        channel = PikaConnection.get_channel()
        if not channel:
            return None

        method, properties, body = channel.basic_get(settings.PIKA_QUEUE_NAME, no_ack=True)
        if method:
            return body
        else:
            return None

    def process_color_message(self, msg):
        """
        Processes a raw color message into its parts, populating the
        given channel with the given color
        """
        color_parts = msg.split('_')
        if len(color_parts) != 3:
            return

        # We have the right number of parts - assume the message is
        # ok... Worse case scenario we end up with a blank color for
        # a bogus channel key. Some sanitation is done - channel is
        # truncated to 30 chars to match the web side, and the color
        # gets safely parsed by from_hex().
        self.color_channels[(color_parts[1])[0:30]] = Color.from_hex(color_parts[2])

    def wait(self):
        """
        Main entry point that waits for a start signal before running
        the actual light driver
        """

        # Basically run this loop forever until interrupted
        running = True

        # If we are configured to autostart, then just go crazy - we don't need Pika until
        # the driver stops
        if settings.AUTO_START:
            self.start()

        # Purge all existing events
        channel = None
        while not channel:
            channel = PikaConnection.get_channel()
            if not channel:
                print 'Failed to connect... Retrying in 30 seconds'
                time.sleep(30)
        channel.queue_purge(settings.PIKA_QUEUE_NAME)

        while running:
            # Try to obtain the channel again
            channel = None
            while not channel:
                channel = PikaConnection.get_channel()
            if not channel:
                print 'Failed to connect... Retrying in 30 seconds'
                time.sleep(30)

            # First wait for a "start" or "restart" command
            # "consume" is a blocking method that will wait for the first message to come in
            body = None
            print '* Light driver idle...'
            for method, properties, body in channel.consume(settings.PIKA_QUEUE_NAME):
                channel.basic_ack(method.delivery_tag)
                # Just break out after reading the first message
                break

            channel.cancel()

            # Note: right now we ignore 'restart' and 'stop' commands if they come in
            # In future we may want to also handle a 'restart' command here
            if body == 'start':
                # We received a start command!
                self.start()

    def start(self):
            print '   Starting'

            # Init audio
            current_variables = {
                'audio': AudioVariable()
            }

            restart = True
            while restart:
                # Actually run the light driver
                # Note that run_lights can return true to request that it be restarted
                restart = self.run_lights(current_variables)

            # Clear the lights to black since we're no longer running
            self.clear_lights()

            # Close variables
            current_variables['audio'].close()

            # Reset start_time so that we start over on the next run
            self.start_time = None

    def set_colors(self, colors):
        self.device.set_colors(colors)

    def clear_lights(self):
        black = [Color(0, 0, 0)] * settings.LIGHTS_NUM_LEDS
        self.set_colors(black)

    def run_lights(self, current_variables):
        """
        Drives the actual lights in a continuous loop until receiving
        a stop signal
        """

        print '* Light driver running...'

        # Grab the simulation parameters
        current_colors = self.get_colors()
        current_transforms = self.get_transforms(current_variables)

        if not current_colors:
            return False

        # Are we animating?
        animating = False
        for transform in current_transforms:
            if transform.is_animated():
                animating = True
                break

        # Run the simulation
        if not self.start_time:
            self.start_time = time.time()
        last_message_check = time.time()

        frame_count = 0
        last_fps = time.time()
        running = True
        while running:
            # Setup the current iteration
            current_time = time.time()
            elapsed_time = current_time - self.start_time
            frame_count += 1

            if current_time - last_fps > 10.0 and settings.LIGHTS_DRIVER_DEBUG:
                print '      FPS: %0.1f' % (float(frame_count) / (current_time - last_fps))
                last_fps = current_time
                frame_count = 0

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
                    elif msg.startswith('color'):
                        self.process_color_message(msg)

            # Note that we always start from the same base lights on each iteration
            # The previous iteration has no effect on the current iteration
            colors = self.do_step(current_colors, elapsed_time, current_transforms, current_variables)

            # Prepare the final data
            self.set_colors(colors)

            # Rate limit
            # If we have no transforms, don't bother updating very often
            if not animating:
                time.sleep(1)
            else:
                # Otherwise, sleep based on the requested update interval
                sleep_time = settings.LIGHTS_UPDATE_INTERVAL - (time.time() - current_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)

        return False

    def run_simulation(self, time_step, steps):
        """
        Simulates a number of steps of applying transforms
        Returns [[color, color, ...], [color, color, ...], ...]
        """

        # Grab the simulation parameters
        current_colors = self.get_colors()
        current_variables = {
            'audio': AudioVariable()
        }
        current_transforms = self.get_transforms(current_variables)

        if not current_colors:
            return None

        result = []

        for i in range(steps):
            elapsed_time = time_step * i
            result.append(self.do_step(current_colors, elapsed_time, current_transforms, current_variables))

        current_variables['audio'].close()

        return result

    def do_step(self, start_colors, elapsed_time, transforms, variables):
        colors = start_colors
        next_colors = []

        # Update variables
        for variable in variables.itervalues():
            variable.update(elapsed_time)

        # Perform each transform step
        for transform in transforms:
            # Does the transform subscribe to a color channel?
            external_color = None
            if transform.color_channel:
                external_color = self.color_channels.get(transform.color_channel, None)

            # Tick the transform frame
            transform.tick_frame(elapsed_time, len(colors), external_color)

            # Transform each light
            for i in range(len(colors)):
                color = transform.transform(elapsed_time, i, len(colors), colors[i], colors)
                next_colors.append(color)

            # Save lights for next transform
            colors = next_colors
            next_colors = []

        return colors

    def get_transforms(self, variables):
        # Grab transform instances out of the database, and
        # instantiate the corresponding classes
        transform_items = TransformInstance.objects.get_current()
        current_transforms = []

        for transform_item in transform_items:
            transform_obj = AVAILABLE_TRANSFORMS[transform_item.transform.name](transform_item)

            current_transforms.append(transform_obj)

        if settings.ENABLE_AUDIO_VAR:
            current_transforms.append(BrightnessVariableTransform(None, variables['audio']))

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
