import base64
import time

from django.conf import settings

from home.models import Light, TransformInstance
from pilight.classes import PikaConnection, Color
from pilight.light.transforms import AVAILABLE_TRANSFORMS


class LightDriver(object):

    def __init__(self):
        self.start_time = None
        self.messages_since_last_queue_check = 0
        self.color_channels = {}

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

    def publish_colors(self, raw_data):
        """
        Publishes the color data to a Pika queue for ingestion
        by a client - usually pilight-client
        """
        channel = PikaConnection.get_channel()
        if not channel:
            # Failed to get the channel
            return

        # Check for excessive messages in queue - and drop them if
        # there are too many. This is useful if the light driver is
        # running but no client is taking the messages, to save
        # on memory.
        if self.messages_since_last_queue_check > 5000:
            self.messages_since_last_queue_check = 0
            result = channel.queue_declare(
                queue=settings.PIKA_QUEUE_NAME_COLORS,
                auto_delete=False,
                durable=True,
                passive=True
            )
            if result.method.message_count > 4000:
                channel.queue_purge(settings.PIKA_QUEUE_NAME_COLORS)

        # Encode the raw data to base64 for transmission
        data = base64.b64encode(raw_data)
        channel.basic_publish(exchange='', routing_key=settings.PIKA_QUEUE_NAME_COLORS, body=data)

        self.messages_since_last_queue_check += 1

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

    def wait(self, spidev):
        """
        Main entry point that waits for a start signal before running
        the actual light driver
        """

        # Basically run this loop forever until interrupted
        running = True

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

    def write_data(self, spidev, raw_data):
        if settings.LIGHTS_DRIVER_MODE == 'standalone':
            # Write directly to the SPI device
            spidev.write(raw_data)
            spidev.flush()
        elif settings.LIGHTS_DRIVER_MODE == 'server':
            # Pass the data to the message queue
            self.publish_colors(raw_data)

    def clear_lights(self, spidev):
        if settings.LIGHTS_DRIVER_MODE in ('standalone', 'server'):
            raw_data = bytearray(settings.LIGHTS_NUM_LEDS * 3)
            for i in range(settings.LIGHTS_NUM_LEDS * 3):
                raw_data[i] = 0x00
            self.write_data(spidev, raw_data)

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
                    elif msg.startswith('color'):
                        self.process_color_message(msg)

            # Note that we always start from the same base lights on each iteration
            # The previous iteration has no effect on the current iteration
            colors = self.do_step(current_colors, elapsed_time, current_transforms)

            # Prepare the final data
            raw_data = bytearray(settings.LIGHTS_NUM_LEDS * 3)
            pos = 0
            for light in colors:
                raw_data[pos*3:] = light.to_raw_corrected()
                pos += 1

            # Write the data
            if settings.LIGHTS_DRIVER_MODE in ('standalone', 'server'):
                self.write_data(spidev, raw_data)

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
