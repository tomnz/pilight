import json
import math
import random
from pilight.classes import Color
from PIL import ImageGrab, ImageFilter, Image


class TransformBase(object):

    def __init__(self, transforminstance):
        # Base classes should override this - and do something with params if need be
        self.transforminstance = transforminstance
        self.params = transforminstance.decoded_params
        self.color_channel = None

    def transform(self, time, position, num_positions, start_color, all_colors):
        """
        Performs the actual color transformation for this transform step
        """
        pass

    def tick_frame(self, time, num_positions, color_param=None):
        """
        Called once at the beginning of each frame - gives the transform
        an opportunity to update state. If the transform has set a
        color_channel, then it will receive the current value of that
        channel (if any)
        """
        pass

    def serialize_params(self):
        """
        Serializes all parameters back to JSON
        """
        return json.dumps(self.params)

    def is_animated(self):
        """
        This is used by the driver to optimize - if all transforms are
        static (not animated), then the update rate can be much lower
        """
        return True


class ExternalColorTransform(TransformBase):

    def __init__(self, transforminstance):
        super(ExternalColorTransform, self).__init__(transforminstance)

        self.color_channel = self.params['color_channel']
        self.color = Color.from_hex('default_color')

    def tick_frame(self, time, num_positions, color_param=None):
        if color_param:
            self.color = color_param

    def transform(self, time, position, num_positions, start_color, all_colors):
        return self.color * self.params['opacity'] + start_color * (1 - self.params['opacity'])


class ColorFlashTransform(TransformBase):

    def transform(self, time, position, num_positions, start_color, all_colors):
        # Transform time/rate into a percentage for the current oscillation
        length = self.params['length']
        progress = float(time) / float(length) - int(time / length)

        # Optional: Transform here to a sine wave
        if self.params['sine']:
            progress = -1 * math.cos(progress * 2 * math.pi)
        else:
            # Otherwise transform to straight -1, 1, -1 sawtooth
            progress = 1 - (2 * abs(progress * 2 - 1))

        # Convert from -1 -> 1 into 0 -> 1
        progress = (progress + 1) / 2

        # Colors
        flash_start_color = Color.from_hex(self.params['start_color'])
        flash_end_color = Color.from_hex(self.params['end_color'])

        # Compute value based on progress and start/end vals
        mult_color = (1 - progress) * flash_start_color + progress * flash_end_color

        return start_color * mult_color


class FlashTransform(TransformBase):

    def transform(self, time, position, num_positions, start_color, all_colors):
        # Transform time/rate into a percentage for the current oscillation
        length = self.params['length']
        progress = float(time) / float(length) - int(time / length)

        # Optional: Transform here to a sine wave
        if self.params['sine']:
            progress = -1 * math.cos(progress * 2 * math.pi)
        else:
            # Otherwise transform to straight -1, 1, -1 sawtooth
            progress = 1 - (2 * abs(progress * 2 - 1))

        # Convert from -1 -> 1 into 0 -> 1
        progress = (progress + 1) / 2

        # Compute value based on progress and start/end vals
        scale = (1 - progress) * self.params['start_value'] + progress * self.params['end_value']

        return start_color.scale(scale)


class StrobeTransform(TransformBase):

    def __init__(self, transforminstance):
        super(StrobeTransform, self).__init__(transforminstance)

        self.state_on = True
        self.frames = 0

    def tick_frame(self, time, num_positions, color_param=None):
        self.frames += 1
        if self.state_on:
            if self.frames > self.params['frames_on']:
                self.state_on = False
                self.frames = 0
        else:
            if self.frames > self.params['frames_off']:
                self.state_on = True
                self.frames = 0

    def transform(self, time, position, num_positions, start_color, all_colors):
        if self.state_on:
            return start_color
        else:
            return Color(0, 0, 0)


class ScrollTransform(TransformBase):

    def transform(self, time, position, num_positions, start_color, all_colors):
        # Transform time/rate into a percentage
        length = self.params['length']
        progress = float(time) / float(length) - int(time / length)

        # Calculate offset to source from
        offset = progress * num_positions
        source_position = (int(offset) + position) % num_positions
        next_position = (source_position + 1) % num_positions
        percent = offset % 1

        # Compute the blended color
        if percent == 0 or not self.params['blend']:
            return all_colors[source_position].clone()
        else:
            return all_colors[source_position] * (1 - percent) + all_colors[next_position] * percent


class RotateHueTransform(TransformBase):

    def transform(self, time, position, num_positions, start_color, all_colors):
        # Transform time/rate into a percentage
        length = self.params['length']
        progress = float(time) / float(length) - int(time / length)

        # Get color as HSV
        h, s, v = start_color.to_hsv()

        # Rotate H by given amount
        h = (h + progress * 360) % 360

        # Transform HSV back to RGB and return
        return Color.from_hsv(h, s, v)


class GaussianBlurTransform(TransformBase):

    def is_animated(self):
        return False

    def gaussian(self, x, sd):
        sd = float(sd)
        x = float(x)
        return (1 / (math.sqrt(2 * math.pi) * sd)) * math.exp(-1 * x * x / (2 * sd * sd))

    def transform(self, time, position, num_positions, start_color, all_colors):
        # Algorithm here:
        # http://homepages.inf.ed.ac.uk/rbf/HIPR2/gsmooth.htm (1-D case)
        sd = self.params['standarddev']

        radius = int(sd * 3)
        min_position = position - radius
        max_position = position + radius

        # Because the Gaussian distribution is asymptotic, if we use the
        # raw values then the integral will be <1 - thus we want to
        # grab the total and scale by the inverse of that amount
        gaussians = {}
        total = 0
        for i in range(-radius, radius):
            gaussians[i] = self.gaussian(i, sd)
            total += gaussians[i]

        # Build the new color
        result = Color(0, 0, 0)

        for i in range(min_position, max_position):
            current_position = i % num_positions
            result += all_colors[current_position] * (gaussians[i - position] / total)

        return result


class BurstTransform(TransformBase):

    def __init__(self, transforminstance):
        super(BurstTransform, self).__init__(transforminstance)

        self.sparks = {}
        self.brightnesses = []
        self.last_time = 0

    def tick_frame(self, time, num_positions, color_param=None):
        if self.last_time == 0:
            self.last_time = time

        # Advance existing sparks
        elapsed_time = time - self.last_time
        for i in self.sparks.keys():
            self.sparks[i] += elapsed_time / self.params['burst_length']
            if self.sparks[i] >= 1:
                del self.sparks[i]

        # Determine probability of making a spark
        chance = elapsed_time * self.params['burst_rate'] / num_positions

        # Spawn new sparks
        for i in range(num_positions):
            if random.random() < chance and not i in self.sparks.keys():
                self.sparks[i] = 0

        # Determine brightnesses
        self.brightnesses = [0] * num_positions
        radius = self.params['burst_radius']
        for index, progress in self.sparks.iteritems():
            spark_strength = 1 - abs((progress - 0.5) * 2)
            min_index = int(max(0, index - radius))
            max_index = int(min(num_positions, index + radius + 1))
            for i in range(min_index, max_index):
                distance = abs(index - i)
                # TODO: Better falloff function
                self.brightnesses[i] += (1.0 - (float(distance) / radius)) * spark_strength

        # Save this time for the next iteration
        self.last_time = time

    def transform(self, time, position, num_positions, start_color, all_colors):
        # Apply the saved brightnesses
        return start_color * self.brightnesses[position]


class NoiseTransform(TransformBase):

    def __init__(self, transforminstance):
        super(NoiseTransform, self).__init__(transforminstance)

        self.last_time = 0
        self.progress = 0.0
        self.current_colors = []
        self.next_colors = []

    def get_random_colors(self, length):
        colors = []
        for i in range(length):
            colors.append(Color(random.random(), random.random(), random.random()))
        return colors

    def tick_frame(self, time, num_positions, color_param=None):
        # Do we need to initialize?
        if self.last_time == 0 or len(self.current_colors) != num_positions or len(self.next_colors) != num_positions:
            self.current_colors = self.get_random_colors(num_positions)
            self.next_colors = self.get_random_colors(num_positions)

        # Have we passed the next time to update colors?
        if time - self.last_time > self.params['length']:
            self.last_time = time
            self.current_colors = self.next_colors
            self.next_colors = self.get_random_colors(num_positions)

        self.progress = (float(time) - float(self.last_time)) / self.params['length']

    def transform(self, time, position, num_positions, start_color, all_colors):

        tween_color = self.next_colors[position] * self.progress + self.current_colors[position] * (1 - self.progress)

        r_str = self.params['red_strength']
        g_str = self.params['green_strength']
        b_str = self.params['blue_strength']

        return Color(start_color.r * (1 - r_str) + tween_color.r * r_str,
                     start_color.g * (1 - g_str) + tween_color.g * g_str,
                     start_color.b * (1 - b_str) + tween_color.b * b_str)


class BrightnessTransform(TransformBase):

    def is_animated(self):
        return False

    def transform(self, time, position, num_positions, start_color, all_colors):
        return start_color * self.params['brightness']


class ScreenAmbianceTransform(TransformBase):

    def __init__(self, transforminstance):
        super(ScreenAmbianceTransform, self).__init__(transforminstance)

        self.width = 0
        self.height = 0
        self.screen = None
        self.frames = 0
        self.saved = False

    def tick_frame(self, time, num_positions, color_param=None):
        # TODO: Check if we're on Windows - this will fail otherwise
        self.frames -= 1

        if self.frames <= 0:
            self.frames = 10
            self.screen = ImageGrab.grab()
            if self.screen:
                self.width = 50
                self.height = 50
                self.screen = self.screen.resize((50, 50), Image.BICUBIC)
                self.screen = self.screen.filter(ImageFilter.GaussianBlur(40))
                if not self.saved:
                    self.saved = True
                    self.screen.save("F:\\Store\\PiLight\\temp.png")

    def transform(self, time, position, num_positions, start_color, all_colors):

        percentage = float(position) / float(num_positions)
        if percentage < 0.3333:
            pixel = self.screen.getpixel((self.width - 1, self.height - 1 - self.height * percentage * 3))
            return Color(float(pixel[0]) / 255, float(pixel[1]) / 255, float(pixel[2]) / 255)
        elif percentage > 0.6667:
            pixel = self.screen.getpixel((0, self.height * (percentage - 0.6667) * 3))
            return Color(float(pixel[0]) / 255, float(pixel[1]) / 255, float(pixel[2]) / 255)
        else:
            pixel = self.screen.getpixel((self.width - 1 - self.width * (percentage - 0.3333) * 3, 0))
            return Color(float(pixel[0]) / 255, float(pixel[1]) / 255, float(pixel[2]) / 255)


AVAILABLE_TRANSFORMS = {
    'flash': FlashTransform,
    'scroll': ScrollTransform,
    'colorflash': ColorFlashTransform,
    'rotatehue': RotateHueTransform,
    'gaussian': GaussianBlurTransform,
    'brightness': BrightnessTransform,
    'noise': NoiseTransform,
    'burst': BurstTransform,
    'strobe': StrobeTransform,
    'external': ExternalColorTransform,
    'screen': ScreenAmbianceTransform,
}