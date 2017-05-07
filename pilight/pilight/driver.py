import multiprocessing
import time

from django.conf import settings

from home.models import Light, TransformInstance, VariableInstance
from pilight.devices import client, noop, ws2801, ws281x
from pilight.classes import PikaConnection, Color
from pilight.light.transforms import TRANSFORMS
from pilight.light.variables import create_variable


DEVICES = {
    'noop': noop.Device,
    'client': client.Device,
    'ws2801': ws2801.Device,
    'ws281x': ws281x.Device,
}

# How often to display FPS (in secs) when running in debug mode
FPS_INTERVAL = 10.0


class LightDriver(object):

    def __init__(self, simulation=False):
        self.start_time = None
        self.messages_since_last_queue_check = 0
        self.color_channels = {}

        if simulation:
            return

        if settings.LIGHTS_DEVICE not in DEVICES:
            raise KeyError('Unknown device specified, please check your settings')

        colors_recv, colors_send = multiprocessing.Pipe(duplex=False)
        self.colors_pipe = colors_send

        self.device = DEVICES[settings.LIGHTS_DEVICE](
            colors_recv,
            settings.LIGHTS_NUM_LEDS,
            settings.LIGHTS_SCALE,
            settings.LIGHTS_REPEAT,
        )
        self.device.start()

    def wait(self):
        """
        Main entry point that waits for a start signal before running
        the actual light driver.
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
        """
        Main driver entry point once a start signal has been received.
        Takes care of variable lifetime, and restarts the inner loop
        until a stop is requested.
        """
        print '   Starting'

        # Init variables - these stay "alive" through restarts
        current_variables = self.get_variables()

        restart = True
        while restart:
            # Actually run the light driver
            # Note that run_lights can return true to request that it be restarted
            restart = self.run_lights(current_variables)

        # Clear the lights to black since we're no longer running
        self.clear_lights()

        # Close variables
        for variable in current_variables.itervalues():
            variable.close()

        # Reset start_time so that we start over on the next run
        self.start_time = None

    def run_lights(self, current_variables):
        """
        Drives the actual lights in a continuous loop until a new signal is received.
        Takes care of transform lifetime. Exits upon a stop or restart signal.
        """

        print '* Light driver running...'

        # Grab the simulation parameters
        current_colors = self.get_colors()
        current_transforms = self.get_transforms(current_variables)

        if not current_colors:
            return False

        # Are we animating? (If not, we can operate at a much lower refresh rate).
        animating = False
        for transform in current_transforms:
            if transform.is_animated():
                animating = True
                break

        # Run the simulation
        if not self.start_time:
            self.start_time = time.time()
        last_message_check = self.start_time

        frame_count = 0
        last_fps_time = time.time()
        running = True
        while running:
            # Setup the current iteration
            current_time = time.time()
            elapsed_time = current_time - self.start_time
            frame_count += 1

            # Display FPS when in debug mode
            if settings.LIGHTS_DRIVER_DEBUG and current_time - last_fps_time > FPS_INTERVAL:
                print '      FPS: %0.1f' % (float(frame_count) / (current_time - last_fps_time))
                last_fps_time = current_time
                frame_count = 0

            # Check for messages only once every so often...
            # Slight optimization to stop rabbitmq getting hammered every frame
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

            # Send new colors to device
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
        current_variables = self.get_variables()
        current_transforms = self.get_transforms(current_variables)

        if not current_colors:
            return None

        print len(current_colors)

        result = []

        for i in range(steps):
            elapsed_time = time_step * i
            result.append(self.do_step(current_colors, elapsed_time, current_transforms, current_variables))

        for variable in current_variables.itervalues():
            variable.close()

        return result

    def set_colors(self, colors):
        """Passes the given colors down to the output device for display."""
        send_colors = []
        for color in colors:
            if color.a != 1.0:
                color = color.flatten_alpha()

            send_colors.append((
                int(color.safe_corrected_r() * 255),
                int(color.safe_corrected_g() * 255),
                int(color.safe_corrected_b() * 255),
                int(color.safe_corrected_w() * 255),
            ))

        self.colors_pipe.send(send_colors)

    def clear_lights(self):
        """Sets all of the lights to black. Useful when exiting."""
        black = [Color(0, 0, 0)] * settings.LIGHTS_NUM_LEDS
        self.set_colors(black)

    def close_device(self):
        # Signal close to the device, and wait
        self.colors_pipe.send(None)
        self.device.join()

    @staticmethod
    def do_step(start_colors, elapsed_time, transforms, variables):
        # Some transforms mutate colors directly, so we always start with a cloned set of colors
        colors = [color.clone() for color in start_colors]

        # Update variables
        for variable in variables.itervalues():
            variable.tick_frame(elapsed_time)

        # Perform each transform step
        for transform in transforms:
            # Tick the transform frame
            transform.tick_frame(elapsed_time, len(colors))

            # Run the transform
            colors = transform.transform(elapsed_time, colors)

        return colors

    @staticmethod
    def pop_message():
        """
        Grabs the latest message from Pika, if one is waiting.
        Returns the body of the message if present, otherwise None.
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
        # ok... Worst case scenario we end up with a blank color for
        # a bogus channel key. Some sanitation is done - channel is
        # truncated to 30 chars to match the web side, and the color
        # gets safely parsed by from_hex().
        self.color_channels[(color_parts[1])[0:30]] = Color.from_hex(color_parts[2])

    @staticmethod
    def get_colors():
        Light.objects.reset()
        current_lights = list(Light.objects.get_current())
        current_colors = []

        if len(current_lights) != settings.LIGHTS_NUM_LEDS:
            return None

        for i in range(settings.LIGHTS_NUM_LEDS):
            current_colors.append(current_lights[i].color)

        return current_colors

    @staticmethod
    def get_transforms(variables):
        # Grab transform instances out of the database, and
        # instantiate the corresponding classes
        transform_items = TransformInstance.objects.get_current()
        current_transforms = []

        for transform_item in transform_items:
            transform_obj = TRANSFORMS[transform_item.transform](transform_item, variables)
            current_transforms.append(transform_obj)

        return current_transforms

    def get_variables(self):
        # Grab variable instances out of the database, and
        # instantiate the corresponding classes
        variable_instances = VariableInstance.objects.get_current()
        current_variables = {}

        for variable_instance in variable_instances:
            # create_variable takes extra inputs to set up specialized vars, e.g.:
            #   - color_channels is used to subscribe to color updates via the API
            variable_obj = create_variable(variable_instance, self.color_channels)
            current_variables[variable_instance.id] = variable_obj

        return current_variables
