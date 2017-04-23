import collections
import json
import math
import random

from home.models import load_variable_params
from pilight.classes import Color
from pilight.light.params import BooleanParam, LongParam, FloatParam, PercentParam, \
    ColorParam, StringParam, ParamsDef, transform_params_from_dict

TimedColor = collections.namedtuple('TimedColor', ('time', 'color'))


class TransformBase(object):
    # Subclasses should override these values as appropriate
    name = 'Unknown'
    description = ''
    params_def = ParamsDef()
    display_order = 100

    def __init__(self, transform_instance, variables):
        # Base classes should override this - and do something with params if need be
        self.transform_instance = transform_instance
        self.params = transform_params_from_dict(
            json.loads(transform_instance.params or '{}'),
            load_variable_params(transform_instance, self.params_def),
            self.params_def, variables)

        self.color_channel = None

    def transform(self, time, input_colors):
        """
        Performs the actual color transformation for this transform step
        :var list[pilight.classes.Color] input_colors:
        """
        pass

    def tick_frame(self, time, num_positions):
        """
        Called once at the beginning of each frame - gives the transform
        an opportunity to update state. If the transform has set a
        color_channel, then it will receive the current value of that
        channel (if any)
        """
        pass

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

    def __init__(self, transform_instance, variables):
        super(LayerBase, self).__init__(transform_instance, variables)

        self.opacity = self.params.opacity
        self.blend_mode = self.params.blend_mode

    params_def = ParamsDef(
        opacity=PercentParam(
            'Opacity',
            1.0,
            'Opacity to blend layer',
        ),
        blend_mode=StringParam(
            'Blend Mode',
            'multiply',
            'Blend mode (valid: "multiply" or "normal")',
        ))

    def transform(self, time, input_colors):
        """
        Performs blending of the layer's color with the existing color in
        the given position, using opacity and blending modes. Should not be
        overridden by inherited classes - override get_color instead.
        """

        total = len(input_colors)
        colors = self.get_colors(time, total)
        for index, input_color in enumerate(input_colors):
            # Grab the color from the layer and apply the opacity
            color = colors[index].clone()
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

    def get_colors(self, time, num_positions):
        """
        Main method that inherited classes should implement - returns a
        color for the given position
        """
        pass


class BrightnessTransform(TransformBase):
    name = 'Brightness'
    description = 'Scales the brightness of each light. Use a number greater than one to increase ' + \
                  'brightness, or a fraction to decrease.'
    params_def = ParamsDef(
        brightness=FloatParam(
            'Brightness',
            1.0,
            'Brightness to apply to each light',
        ))
    display_order = 0

    def is_animated(self):
        return False

    def transform(self, time, input_colors):
        brightness = self.params.brightness
        for index in range(len(input_colors)):
            input_colors[index] *= brightness

        return input_colors


class BurstTransform(TransformBase):
    name = 'Burst'
    description = 'Generates "bursts" or "sparks" of light, allowing the underlying color to show through.'
    params_def = ParamsDef(
        burst_rate=FloatParam(
            'Burst Rate',
            4.0,
            'Rate at which to spawn new sparks (num/sec)',
        ),
        burst_duration=FloatParam(
            'Burst Duration',
            2.0,
            'Duration of time that sparks live (sec)',
        ),
        burst_radius=FloatParam(
            'Burst Radius',
            3.0,
            'Falloff radius for sparks',
        ))
    display_order = 3

    def __init__(self, transform_instance, variables):
        super(BurstTransform, self).__init__(transform_instance, variables)

        self.sparks = {}
        self.brightnesses = []
        self.last_time = 0

    def tick_frame(self, time, num_positions):
        if self.last_time == 0:
            self.last_time = time
        burst_duration = float(self.params.burst_duration)

        # Advance existing sparks
        elapsed_time = time - self.last_time
        for i in self.sparks.keys():
            self.sparks[i] += elapsed_time / burst_duration
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


class ColorLayer(LayerBase):
    name = 'Color Layer'
    description = 'Applies a single color to the lights as a layer.'
    params_def = ParamsDef(
        color=ColorParam(
            'Color',
            Color.get_default(),
            'Color to apply to the lights',
        ),
        **LayerBase.params_def.params_def.copy())
    display_order = 300

    def get_colors(self, time, num_positions):
        return [self.params.color] * num_positions


class ColorBurstLayer(LayerBase):
    name = 'Color Burst Layer'
    description = 'Applies a burst pattern in the given color as a layer.'
    params_def = ParamsDef(
        color=ColorParam(
            'Color',
            Color.get_default(),
            'Color to burst',
        ),
        burst_rate=FloatParam(
            'Burst Rate',
            4.0,
            'Rate at which to spawn new sparks (num/sec)',
        ),
        burst_duration=FloatParam(
            'Burst Duration',
            2.0,
            'Duration of time that sparks live (sec)',
        ),
        burst_radius=FloatParam(
            'Burst Radius',
            3.0,
            'Falloff radius for sparks',
        ),
        **LayerBase.params_def.params_def.copy())
    display_order = 301

    def __init__(self, transform_instance, variables):
        super(ColorBurstLayer, self).__init__(transform_instance, variables)

        self.sparks = {}
        self.brightnesses = []
        self.last_time = 0

    def tick_frame(self, time, num_positions):
        if self.last_time == 0:
            self.last_time = time
        burst_duration = self.params.burst_duration
        burst_rate = self.params.burst_rate
        burst_radius = self.params.burst_radius

        # Advance existing sparks
        elapsed_time = time - self.last_time
        for i in self.sparks.keys():
            self.sparks[i] += elapsed_time / burst_duration
            if self.sparks[i] >= 1:
                del self.sparks[i]

        # Determine probability of making a spark
        chance = elapsed_time * burst_rate / num_positions

        # Spawn new sparks
        for i in range(num_positions):
            if random.random() < chance and i not in self.sparks.keys():
                self.sparks[i] = 0

        # Determine brightnesses
        self.brightnesses = [0] * num_positions
        radius = burst_radius
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

    def get_colors(self, time, num_positions):
        # Apply the saved brightnesses
        result = []
        base_color = self.params.color
        for idx in range(num_positions):
            color = base_color.clone()
            color.a = self.brightnesses[idx]
            result.append(color)

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
        duration=FloatParam(
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
    display_order = 200

    def __init__(self, transform_instance, variables):
        super(ColorFlashTransform, self).__init__(transform_instance, variables)
        self.color = Color.get_default()

    def tick_frame(self, time, num_positions):
        # Transform time/rate into a percentage for the current oscillation
        duration = self.params.duration
        progress = float(time) / float(duration) - int(time / duration)

        # Optional: Transform here to a sine wave
        if self.params.sine:
            progress = -1 * math.cos(progress * 2 * math.pi)
        else:
            # Otherwise transform to straight -1, 1, -1 sawtooth
            progress = 1 - (2 * abs(progress * 2 - 1))

        # Convert from -1 -> 1 into 0 -> 1
        progress = (progress + 1) / 2

        # Colors
        flash_start_color = self.params.start_color
        flash_end_color = self.params.end_color

        # Compute value based on progress and start/end vals
        self.color = flash_start_color * (1 - progress) + flash_end_color * progress

    def get_colors(self, time, num_positions):
        return [self.color] * num_positions


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
        duration=FloatParam(
            'Duration',
            2.0,
            'Duration of flash cycle (secs)',
        ),
        sine=BooleanParam(
            'Smooth',
            True,
            'Use a sine wave profile to smooth the flash',
        ))
    display_order = 10

    def transform(self, time, input_colors):
        # Transform time/rate into a percentage for the current oscillation
        duration = self.params.duration
        progress = float(time) / float(duration) - int(time / duration)

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


class GaussianBlurTransform(TransformBase):
    name = 'Gaussian Blur'
    description = 'Applies a gaussian blur across the entire set of lights, with the given standard ' + \
                  'deviation. Note that this is an expensive transform, use with care.'
    params_def = ParamsDef(
        standarddev=FloatParam(
            'Standard Deviation',
            1.0,
            'Standard deviation to be applied',
        ))
    display_order = 140

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


class NoiseTransform(TransformBase):
    name = 'Noise'
    description = 'Introduces random variations to each light, each frame. Strength defines the ' + \
                  'maximum amount that the light can vary by in each of the base colors.'

    params_def = ParamsDef(
        duration=FloatParam(
            'Duration',
            0.5,
            'Time between new noise patterns (secs)',
        ),
        blue_strength=FloatParam(
            'Blue Strength',
            0.5,
            'Amount that the color will randomly vary by in blue',
        ),
        green_strength=FloatParam(
            'Green Strength',
            0.5,
            'Amount that the color will randomly vary by in green',
        ),
        red_strength=FloatParam(
            'Red Strength',
            0.5,
            'Amount that the color will randomly vary by in red',
        ),
        white_strength=FloatParam(
            'White Strength',
            0.0,
            'Amount that white will vary randomly by',
        ))
    display_order = 8

    def __init__(self, transform_instance, variables):
        super(NoiseTransform, self).__init__(transform_instance, variables)

        self.last_time = -1
        self.progress = 0.0
        self.current_colors = []
        self.next_colors = []

    @staticmethod
    def get_random_colors(length):
        colors = []
        for i in range(length):
            colors.append(Color(random.random(), random.random(), random.random(), random.random()))
        return colors

    def tick_frame(self, time, num_positions):
        # Do we need to initialize?
        if self.last_time == -1 or len(self.current_colors) != num_positions or len(self.next_colors) != num_positions:
            self.current_colors = self.get_random_colors(num_positions)
            self.next_colors = self.get_random_colors(num_positions)
            self.last_time = time

        # Have we passed the next time to update colors?
        if time - self.last_time > self.params.duration:
            self.last_time = time
            self.current_colors = self.next_colors
            self.next_colors = self.get_random_colors(num_positions)

        self.progress = (float(time) - float(self.last_time)) / self.params.duration

    def transform(self, time, input_colors):
        r_str = self.params.red_strength
        g_str = self.params.green_strength
        b_str = self.params.blue_strength
        w_str = self.params.white_strength

        for index, color in enumerate(input_colors):
            tween_color = self.next_colors[index] * self.progress + self.current_colors[index] * (1 - self.progress)

            input_colors[index] = Color(color.r * (1 - r_str) + tween_color.r * r_str,
                                        color.g * (1 - g_str) + tween_color.g * g_str,
                                        color.b * (1 - b_str) + tween_color.b * b_str,
                                        color.w * (1 - w_str) + tween_color.w * w_str,
                                        color.a)

        return input_colors


class PixelateTransform(TransformBase):
    name = 'Pixelate'
    description = 'Averages color in blocks of the given length, applying the same color to each light in the' \
                  'block.'
    params_def = ParamsDef(
        block_size=LongParam(
            'Block Size',
            5,
            'Number of lights per block',
        ))
    display_order = 12

    def transform(self, time, input_colors):
        result = []
        block_size = self.params.block_size

        next_color = Color(0, 0, 0)
        num_colors = 0
        for input_color in input_colors:
            next_color += input_color
            num_colors += 1

            if num_colors == block_size:
                next_color /= block_size
                result.extend([next_color] * block_size)
                next_color = Color(0, 0, 0)
                num_colors = 0

        if num_colors > 0:
            next_color /= num_colors
            result.extend([next_color] * num_colors)

        return result


class RotateHueTransform(TransformBase):
    name = 'Rotate Hue'
    description = 'Rotates hue through the full set of colors over the given time period.'
    params_def = ParamsDef(
        duration=FloatParam(
            'Duration',
            10.0,
            'Duration of a full rotation (secs)',
        ))
    display_order = 2

    def transform(self, time, input_colors):
        # Transform time/rate into a percentage
        duration = self.params.duration
        progress = float(time) / float(duration) - int(time / duration)

        for index, input_color in enumerate(input_colors):
            # Get color as HSV
            h, s, v, w, a = input_color.to_hsv()

            # Rotate H by given amount
            h = (h + progress * 360) % 360

            # Transform HSV back to RGB and return
            input_colors[index] = Color.from_hsv(h, s, v, w, a)

        return input_colors


class ScrollTransform(TransformBase):
    name = 'Scroll'
    description = 'Scrolls all the lights over the given time period. Can be reversed.'
    params_def = ParamsDef(
        duration=FloatParam(
            'Duration',
            10.0,
            'Duration of a full scroll (secs)',
        ),
        reverse=BooleanParam(
            'Reverse',
            False,
            'Scroll in the opposite direction',
        ),
        blend=BooleanParam(
            'Blend',
            True,
            'Smoothly blend the scroll effect between lights',
        ))
    display_order = 1

    def __init__(self, transform_instance, variables):
        super(ScrollTransform, self).__init__(transform_instance, variables)
        self.last_time = 0.0
        self.offset = 0.0

    def transform(self, time, input_colors):
        total = len(input_colors)

        # Transform time/rate into a percentage
        duration = self.params.duration
        progress = (time - self.last_time) / float(duration)
        self.last_time = time

        # Calculate offset to source from
        self.offset += progress * total
        self.offset %= total

        colors = []
        for index, input_color in enumerate(input_colors):
            source_position = (int(self.offset) + index) % total
            percent = self.offset % 1

            if percent == 0 or not self.params.blend:
                colors.append(input_colors[source_position])
                continue

            next_position = (source_position + 1) % total
            colors.append(input_colors[source_position] * (1 - percent) + input_colors[next_position] * percent)

        return colors


class SpectrumFlowLayer(LayerBase):
    name = 'Spectrum Flow Layer'
    description = 'Scrolls a color spectrum, based on the given value. Designed primarily to be used with an ' \
                  'audio variable.'
    params_def = ParamsDef(
        duration=FloatParam(
            'Duration',
            3.0,
            'Duration of a full scroll (secs)',
        ),
        reverse=BooleanParam(
            'Reverse',
            False,
            'Scroll in the opposite direction',
        ),
        low_color=ColorParam(
            'Low Color',
            Color(0, 1, 0),
            'Color applied when the value is zero',
        ),
        mid_color=ColorParam(
            'Mid Color',
            Color(0.7, 0.7, 0),
            'Color applied when the value is 0.5',
        ),
        high_color=ColorParam(
            'High Color',
            Color(1, 0, 0),
            'Color applied when the value is 1.0',
        ),
        value=FloatParam(
            'Value',
            0.0,
            'Value to apply the spectrum over',
        ),
        **LayerBase.params_def.params_def.copy())
    display_order = 302

    def __init__(self, transform_instance, variables):
        super(SpectrumFlowLayer, self).__init__(transform_instance, variables)
        self.colors = collections.deque()
        self.display_colors = []

    def tick_frame(self, time, num_positions):
        duration = self.params.duration

        # Drop colors that are no longer relevant - look ahead by one
        while len(self.colors) > 1 and time - self.colors[1].time > duration:
            self.colors.pop()

        # Compute spectrum color
        value = min(1.0, max(0.0, self.params.value))
        if value < 0.5:
            value *= 2.0
            color = self.params.low_color * (1.0 - value) + self.params.mid_color * value
        else:
            value = (value - 0.5) * 2.0
            color = self.params.mid_color * (1.0 - value) + self.params.high_color * value

        self.colors.appendleft(TimedColor(
            time=time,
            color=color,
        ))

    def get_colors(self, time, num_positions):
        if len(self.colors) == 1:
            return [self.colors[0].color.clone()] * num_positions

        colors = []
        curr_color = self.colors[0]
        next_color = self.colors[1]
        next_index = 2

        duration = self.params.duration
        for i in range(num_positions):
            light_time = time - i * duration / num_positions

            # Walk input colors
            while light_time <= next_color.time and next_index < len(self.colors):
                curr_color = next_color
                next_color = self.colors[next_index]
                next_index += 1

            # Interpolate between colors
            progress = min(1.0, max(0.0, (
                (curr_color.time - light_time) / (curr_color.time - next_color.time)
            )))

            color = curr_color.color * (1.0 - progress) + next_color.color * progress
            colors.append(color)

        return colors


class StrobeTransform(TransformBase):
    name = 'Strobe'
    description = 'Alternates the lights on and off completely.'
    params_def = ParamsDef(
        frames_on=LongParam(
            'Frames On',
            1,
            'Number of frames to turn lights on for',
        ),
        frames_off=LongParam(
            'Frames Off',
            4,
            'Number of frames to turn lights off for',
        ))
    display_order = 12

    def __init__(self, transform_instance, variables):
        super(StrobeTransform, self).__init__(transform_instance, variables)

        self.state_on = True
        self.frames = 0

    def tick_frame(self, time, num_positions):
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


class CrushColorTransform(TransformBase):
    name = 'Crush Color'
    description = 'Crushes color and brightness according to the strength of the parameter. ' + \
                  'Works best with a variable.'
    params_def = ParamsDef(
        strength=FloatParam(
            'Strength',
            1.0,
            'Higher values increase brightness and color crush',
        ),
        red_max=PercentParam(
            'Red Max',
            1.0,
            'Maximum allowed red amount',
        ),
        green_max=PercentParam(
            'Green Max',
            0.3,
            'Maximum allowed green amount',
        ),
        blue_max=PercentParam(
            'Blue Max',
            0.1,
            'Maximum allowed blue amount',
        ))
    display_order = 15

    def __init__(self, transform_instance, variables):
        super(CrushColorTransform, self).__init__(transform_instance, variables)

    def is_animated(self):
        return True

    def transform(self, time, input_colors):
        strength = self.params.strength
        red_max = self.params.red_max
        green_max = self.params.green_max
        blue_max = self.params.blue_max

        for index, color in enumerate(input_colors):
            input_colors[index] = Color(
                min(color.r * strength, red_max),
                min(color.g * strength, green_max),
                min(color.b * strength, blue_max),
                # Don't impact white
                color.w,
                color.a)

        return input_colors


TRANSFORMS = {
    'brightness': BrightnessTransform,
    'burst': BurstTransform,
    'color': ColorLayer,
    'colorburst': ColorBurstLayer,
    'colorflash': ColorFlashTransform,
    'crushcolor': CrushColorTransform,
    'flash': FlashTransform,
    'gaussian': GaussianBlurTransform,
    'noise': NoiseTransform,
    'pixelate': PixelateTransform,
    'rotatehue': RotateHueTransform,
    'scroll': ScrollTransform,
    'spectrumflow': SpectrumFlowLayer,
    'strobe': StrobeTransform,
}
