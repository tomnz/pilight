import abc
import json
import math
import random

from pilight.classes import Color
from pilight.light.params import BooleanParam, LongParam, FloatParam, PercentParam, \
    ColorParam, StringParam, ParamsDef, params_from_dict


class TransformBase(object):
    # Subclasses should override these values as appropriate
    name = 'Unknown'
    description = ''
    params_def = ParamsDef()

    def __init__(self, transforminstance):
        # Base classes should override this - and do something with params if need be
        self.transforminstance = transforminstance
        self.params = params_from_dict(
            getattr(transforminstance, 'decoded_params', {}), self.params_def)
        self.color_channel = None

    def transform(self, time, input_colors):
        """
        Performs the actual color transformation for this transform step
        :var list[pilight.classes.Color] input_colors:
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


class LayerBase(TransformBase):
    """
    Specialized type of transform - produces color information
    independently of any prior colors (like a layer in an image
    editor), and then uses a common method and params to blend
    the color information into the existing color data.
    """

    def __init__(self, transforminstance):
        super(LayerBase, self).__init__(transforminstance)

        self.opacity = self.params.opacity
        self.blend_mode = self.params.blend_mode

    params_def = ParamsDef(**{
        'opacity': PercentParam(
            'Opacity',
            1.0,
            'Opacity to blend layer',
        ),
        'blend_mode': StringParam(
            'Blend Mode',
            'multiply',
            'Blend mode (valid: "multiply" or "normal")',
        ),
    })

    def transform(self, time, input_colors):
        """
        Performs blending of the layer's color with the existing color in
        the given position, using opacity and blending modes. Should not be
        overridden by inherited classes - override get_color instead.
        """

        total = len(input_colors)
        for index, input_color in enumerate(input_colors):
            # Grab the color from the layer and apply the opacity
            color = self.get_color(time, index, total)
            color.a *= self.opacity

            # Perform blending with the given blend mode
            # Currently support "multiply" and "normal" modes - normal being the default
            # if an unknown mode gets passed in
            if self.blend_mode == 'multiply':
                # TODO: Actually implement multiplicative blending
                color = Color.blend_mult(input_color, color)
            else:
                color = Color.blend_normal(input_color, color)

            input_colors[index] = color

        return input_colors

    def get_color(self, time, position, num_positions):
        """
        Main method that inherited classes should implement - returns a
        color for the given position
        """
        pass


class ExternalColorLayer(LayerBase):
    name = 'External Color'
    description = 'Designed to accept color updates from an external source - applying the given color ' + \
                  'to all of the LEDs. Do not use unless you know what you are doing! Make sure color_channel ' + \
                  'matches what the external source is providing.'
    params_def = ParamsDef(
        color_channel=StringParam(
            'Color Channel',
            'unknown',
            'Key for the color channel that the transform should read from',
        ),
        default_color=ColorParam(
            'Default Color',
            Color.get_default(),
            'Color to use when none has been provided for the channel',
        ),
        **LayerBase.params_def.params_def.copy())

    def __init__(self, transforminstance):
        super(ExternalColorLayer, self).__init__(transforminstance)

        self.color_channel = self.params.color_channel
        self.color = Color.from_hex(self.params.default_color)

    def tick_frame(self, time, num_positions, color_param=None):
        if color_param:
            self.color = color_param

    def get_color(self, time, position, num_positions):
        return self.color


class ExternalColorBurstLayer(LayerBase):
    name = 'External Color Burst'
    description = 'Designed to accept color updates from an external source - applying the given color ' + \
                  'to all of the LEDs. Do not use unless you know what you are doing! Make sure color_channel ' + \
                  'matches what the external source is providing. Adds a burst effect to the color.'
    params_def = ParamsDef(
        color_channel=StringParam(
            'Color Channel',
            'unknown',
            'Key for the color channel that the transform should read from',
        ),
        default_color=ColorParam(
            'Default Color',
            Color.get_default(),
            'Color to use when none has been provided for the channel',
        ),
        burst_rate=FloatParam(
            'Burst Rate',
            4.0,
            'Rate at which to spawn new sparks (num/sec)',
        ),
        burst_length=FloatParam(
            'Burst Length',
            2.0,
            'Length of time that sparks live (sec)',
        ),
        burst_radius=FloatParam(
            'Burst Radius',
            3.0,
            'Falloff radius for sparks',
        ),
        **LayerBase.params_def.params_def.copy())

    def __init__(self, transforminstance):
        super(ExternalColorBurstLayer, self).__init__(transforminstance)

        self.color_channel = self.params.color_channel
        self.color = Color.from_hex(self.params.default_color)
        self.sparks = {}
        self.brightnesses = []
        self.last_time = 0

    def tick_frame(self, time, num_positions, color_param=None):
        if color_param:
            self.color = color_param

        if self.last_time == 0:
            self.last_time = time

        # Advance existing sparks
        elapsed_time = time - self.last_time
        for i in self.sparks.keys():
            self.sparks[i] += elapsed_time / self.params.burst_length
            if self.sparks[i] >= 1:
                del self.sparks[i]

        # Determine probability of making a spark
        chance = elapsed_time * self.params.burst_rate / num_positions

        # Spawn new sparks
        for i in range(num_positions):
            if random.random() < chance and i not in self.sparks.keys():
                self.sparks[i] = 0

        # Determine brightnesses
        self.brightnesses = [0] * num_positions
        radius = self.params.burst_radius
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

    def get_color(self, time, position, num_positions):
        # Apply the saved brightnesses
        result = self.color.clone()
        result.a = self.brightnesses[position]
        return result


class ColorFlashTransform(LayerBase):
    name = 'Color Flash'
    description = 'Alternates between two colors, over the given time period, blending into the base ' + \
                  'color. Can produce either a sine wave (smooth) effect, or triangle wave effect.'
    params_def = ParamsDef(
        start_color=ColorParam(
            'Start Color',
            Color.get_default(),
            'Color to use for start of animation',
        ),
        end_color=ColorParam(
            'End Color',
            Color(0.5, 0.5, 0.5),
            'Color to use for end of animation',
        ),
        length=FloatParam(
            'Duration',
            2.0,
            'Duration of flash cycle (secs)',
        ),
        sine=BooleanParam(
            'Smooth',
            True,
            'Use a sine wave profile to smooth the flash',
        ),
        **LayerBase.params_def.params_def.copy())

    def transform(self, time, input_colors):
        # Transform time/rate into a percentage for the current oscillation
        length = self.params.length
        progress = float(time) / float(length) - int(time / length)

        # Optional: Transform here to a sine wave
        if self.params.sine:
            progress = -1 * math.cos(progress * 2 * math.pi)
        else:
            # Otherwise transform to straight -1, 1, -1 sawtooth
            progress = 1 - (2 * abs(progress * 2 - 1))

        # Convert from -1 -> 1 into 0 -> 1
        progress = (progress + 1) / 2

        # Colors
        flash_start_color = Color.from_hex(self.params.start_color)
        flash_end_color = Color.from_hex(self.params.end_color)

        # Compute value based on progress and start/end vals
        mult_color = flash_start_color * (1 - progress) + flash_end_color * progress

        for index, color in enumerate(input_colors):
            input_colors[index] = Color.blend_mult(color, mult_color)

        return input_colors


class FlashTransform(TransformBase):
    name = 'Flash'
    description = 'Flashes all lights between two brightness percentages, over the given time period. ' + \
                  'Can produce either a sine wave (smooth) effect, or triangle wave effect.'
    params_def = ParamsDef(
        start_value=FloatParam(
            'Start Brightness',
            1.0,
            'Brightness to use for start of animation',
        ),
        end_value=FloatParam(
            'End Brightness',
            0.5,
            'Brightness to use for end of animation',
        ),
        length=FloatParam(
            'Duration',
            2.0,
            'Duration of flash cycle (secs)',
        ),
        sine=BooleanParam(
            'Smooth',
            True,
            'Use a sine wave profile to smooth the flash',
        ))

    def transform(self, time, input_colors):
        # Transform time/rate into a percentage for the current oscillation
        length = self.params.length
        progress = float(time) / float(length) - int(time / length)

        # Optional: Transform here to a sine wave
        if self.params.sine:
            progress = -1 * math.cos(progress * 2 * math.pi)
        else:
            # Otherwise transform to straight -1, 1, -1 sawtooth
            progress = 1 - (2 * abs(progress * 2 - 1))

        # Convert from -1 -> 1 into 0 -> 1
        progress = (progress + 1) / 2

        # Compute value based on progress and start/end vals
        scale = (1 - progress) * self.params.start_value + progress * self.params.end_value

        for index in range(len(input_colors)):
            input_colors[index] *= scale

        return input_colors


class StrobeTransform(TransformBase):
    name = 'Strobe'
    description = 'Alternates the lights on and off completely.'
    params_def = ParamsDef(**{
        'frames_on': LongParam(
            'Frames On',
            1,
            'Number of frames to turn lights on for',
        ),
        'frames_off': LongParam(
            'Frames Off',
            4,
            'Number of frames to turn lights off for',
        ),
    })

    def __init__(self, transforminstance):
        super(StrobeTransform, self).__init__(transforminstance)

        self.state_on = True
        self.frames = 0

    def tick_frame(self, time, num_positions, color_param=None):
        self.frames += 1
        if self.state_on:
            if self.frames > self.params.frames_on:
                self.state_on = False
                self.frames = 0
        else:
            if self.frames > self.params.frames_off:
                self.state_on = True
                self.frames = 0

    def transform(self, time, input_colors):
        if self.state_on:
            return input_colors
        else:
            return [Color(0, 0, 0)] * len(input_colors)


class ScrollTransform(TransformBase):
    name = 'Scroll'
    description = 'Scrolls all the lights over the given time period. Can be reversed.'
    params_def = ParamsDef(**{
        'length': FloatParam(
            'Duration',
            10.0,
            'Duration of a full scroll (secs)',
        ),
        'reverse': BooleanParam(
            'Reverse',
            False,
            'Scroll in the opposite direction',
        ),
        'blend': BooleanParam(
            'Blend',
            True,
            'Smoothly blend the scroll effect between lights',
        ),
    })

    def transform(self, time, input_colors):
        total = len(input_colors)

        # Transform time/rate into a percentage
        length = self.params.length
        progress = float(time) / float(length) - int(time / length)

        # Calculate offset to source from
        offset = progress * total

        colors = []
        for index, input_color in enumerate(input_colors):
            source_position = (int(offset) + index) % total
            percent = offset % 1

            if percent == 0 or not self.params.blend:
                colors.append(input_colors[source_position])
                continue

            next_position = (source_position + 1) % total
            colors.append(input_colors[source_position] * (1 - percent) + input_colors[next_position] * percent)

        return colors


class RotateHueTransform(TransformBase):
    name = 'Rotate Hue'
    description = 'Rotates hue through the full set of colors over the given time period.'
    params_def = ParamsDef(**{
        'length': FloatParam(
            'Duration',
            10.0,
            'Duration of a full rotation (secs)',
        ),
    })

    def transform(self, time, input_colors):
        # Transform time/rate into a percentage
        length = self.params.length
        progress = float(time) / float(length) - int(time / length)

        for index, input_color in enumerate(input_colors):
            # Get color as HSV
            h, s, v, a = input_color.to_hsv()

            # Rotate H by given amount
            h = (h + progress * 360) % 360

            # Transform HSV back to RGB and return
            input_colors[index] = Color.from_hsv(h, s, v, a)

        return input_colors


class GaussianBlurTransform(TransformBase):
    name = 'Gaussian Blur'
    description = 'Applies a gaussian blur across the entire set of lights, with the given standard ' + \
                  'deviation. Note that this is an expensive transform, use with care.'
    params_def = ParamsDef(**{
        'standarddev': FloatParam(
            'Standard Deviation',
            1.0,
            'Standard deviation to be applied',
        ),
    })

    def is_animated(self):
        return False

    @staticmethod
    def gaussian(x, sd):
        sd = float(sd)
        x = float(x)
        return (1 / (math.sqrt(2 * math.pi) * sd)) * math.exp(-1 * x * x / (2 * sd * sd))

    def transform(self, time, input_colors):
        # Algorithm here:
        # http://homepages.inf.ed.ac.uk/rbf/HIPR2/gsmooth.htm (1-D case)
        sd = self.params.standarddev

        radius = int(sd * 3)
        # Because the Gaussian distribution is asymptotic, if we use the
        # raw values then the integral will be <1 - thus we want to
        # grab the total and scale by the inverse of that amount
        gaussians = {}
        total = 0
        for offset in range(-radius, radius):
            gaussians[offset] = self.gaussian(offset, sd)
            total += gaussians[offset]

        colors = []
        num_colors = len(input_colors)
        for index in range(len(input_colors)):
            color = Color(0.0, 0.0, 0.0)

            for offset in range(-radius, radius):
                current_position = (offset + index) % num_colors
                color += input_colors[current_position] * (gaussians[offset] / total)

            colors.append(color)

        return colors


class BurstTransform(TransformBase):
    name = 'Burst'
    description = 'Generates "bursts" or "sparks" of light, allowing the underlying color to show through.'
    params_def = ParamsDef(**{
        'burst_rate': FloatParam(
            'Burst Rate',
            4.0,
            'Rate at which to spawn new sparks (num/sec)',
        ),
        'burst_length': FloatParam(
            'Burst Length',
            2.0,
            'Length of time that sparks live (sec)',
        ),
        'burst_radius': FloatParam(
            'Burst Radius',
            3.0,
            'Falloff radius for sparks',
        ),
    })

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
            self.sparks[i] += elapsed_time / float(self.params.burst_length)
            if self.sparks[i] >= 1:
                del self.sparks[i]

        # Determine probability of making a spark
        chance = elapsed_time * self.params.burst_rate / num_positions

        # Spawn new sparks
        for i in range(num_positions):
            if random.random() < chance and i not in self.sparks.keys():
                self.sparks[i] = 0

        # Determine brightnesses
        self.brightnesses = [0.0] * num_positions
        radius = int(self.params.burst_radius)
        for index, progress in self.sparks.iteritems():
            spark_strength = 1.0 - abs((progress - 0.5) * 2)

            for offset in range(-radius, radius + 1):
                # TODO: Better falloff function
                position = (index + offset) % num_positions
                self.brightnesses[position] += (1.0 - (float(abs(offset)) / float(radius))) * spark_strength

        # Save this time for the next iteration
        self.last_time = time

    def transform(self, time, input_colors):
        # Apply the saved brightnesses
        for index in range(len(input_colors)):
            input_colors[index] *= self.brightnesses[index]
        return input_colors


class NoiseTransform(TransformBase):
    name = 'Noise'
    description = 'Introduces random variations to each light, each frame. Strength defines the ' + \
                  'maximum amount that the light can vary by in each of the base colors.'

    params_def = ParamsDef(**{
        'length': FloatParam(
            'Duration',
            0.5,
            'Time between new noise patterns (secs)',
        ),
        'blue_strength': FloatParam(
            'Blue Strength',
            0.5,
            'Amount that the color will randomly vary by in blue',
        ),
        'green_strength': FloatParam(
            'Green Strength',
            0.5,
            'Amount that the color will randomly vary by in green',
        ),
        'red_strength': FloatParam(
            'Red Strength',
            0.5,
            'Amount that the color will randomly vary by in red',
        ),
    })

    def __init__(self, transforminstance):
        super(NoiseTransform, self).__init__(transforminstance)

        self.last_time = 0
        self.progress = 0.0
        self.current_colors = []
        self.next_colors = []

    @staticmethod
    def get_random_colors(length):
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
        if time - self.last_time > self.params.length:
            self.last_time = time
            self.current_colors = self.next_colors
            self.next_colors = self.get_random_colors(num_positions)

        self.progress = (float(time) - float(self.last_time)) / self.params.length

    def transform(self, time, input_colors):

        for index, color in enumerate(input_colors):
            tween_color = self.next_colors[index] * self.progress + self.current_colors[index] * (1 - self.progress)

            r_str = self.params.red_strength
            g_str = self.params.green_strength
            b_str = self.params.blue_strength

            input_colors[index] = Color(color.r * (1 - r_str) + tween_color.r * r_str,
                                        color.g * (1 - g_str) + tween_color.g * g_str,
                                        color.b * (1 - b_str) + tween_color.b * b_str)

        return input_colors


class BrightnessTransform(TransformBase):
    name = 'Brightness'
    description = 'Scales the brightness of each light. Use a number greater than one to increase ' + \
                  'brightness, or a fraction to decrease.'
    params_def = ParamsDef(**{
        'brightness': FloatParam(
            'Brightness',
            1.0,
            'Brightness to apply to each light',
        ),
    })

    def is_animated(self):
        return False

    def transform(self, time, input_colors):
        for index in range(len(input_colors)):
            input_colors[index] *= self.params.brightness

        return input_colors


class BrightnessVariableTransform(TransformBase):
    def __init__(self, transforminstance, variable):
        super(BrightnessVariableTransform, self).__init__(transforminstance)
        self.variable = variable

    def is_animated(self):
        return True

    def transform(self, time, input_colors):
        val = self.variable.get_value()
        for index, color in enumerate(input_colors):
            input_colors[index] = Color(
                color.r * val,
                min(color.g * val, 0.3),
                min(color.b * val, 0.1),
                color.a)


TRANSFORMS = {
    'flash': FlashTransform,
    'scroll': ScrollTransform,
    'colorflash': ColorFlashTransform,
    'rotatehue': RotateHueTransform,
    'gaussian': GaussianBlurTransform,
    'brightness': BrightnessTransform,
    'noise': NoiseTransform,
    'burst': BurstTransform,
    'strobe': StrobeTransform,
    'external': ExternalColorLayer,
    'externalburst': ExternalColorBurstLayer,
}
