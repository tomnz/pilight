import json
import math
import random
from pilight.classes import Color


class TransformBase(object):

    def __init__(self, transforminstance):
        # Base classes should override this - and do something with params if need be
        self.transforminstance = transforminstance
        self.params = transforminstance.decoded_params

    def transform(self, time, position, num_positions, start_color, all_colors):
        """
        Performs the actual color transformation for this transform step
        """
        pass

    def serialize_params(self):
        """
        Serializes all parameters back to JSON
        """
        return json.dumps(self.params)


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

    def transform(self, time, position, num_positions, start_color, all_colors):
        # Do we need to animate sparks?
        if self.last_time != time or len(self.brightnesses) == 0:
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

        # Apply the saved brightnesses
        return start_color * self.brightnesses[position]


class BrightnessTransform(TransformBase):

    def transform(self, time, position, num_positions, start_color, all_colors):
        return start_color * self.params['brightness']


AVAILABLE_TRANSFORMS = {
    'flash': FlashTransform,
    'scroll': ScrollTransform,
    'colorflash': ColorFlashTransform,
    'rotatehue': RotateHueTransform,
    'gaussian': GaussianBlurTransform,
    'brightness': BrightnessTransform,
    'burst': BurstTransform,
}