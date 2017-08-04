import json
import multiprocessing
import random

from django.conf import settings

from pilight.light.params import LongParam, FloatParam, ColorParam, StringParam, ParamsDef, variable_params_from_dict
from pilight.light.types import NUMBER_TYPES, ParamTypes
from pilight.classes import Color


class Variable(object):
    """
    Defines a common interface for updating and retrieving a dynamic variable
    value.
    """

    name = 'Unknown'
    description = ''
    params_def = ParamsDef()
    display_order = 100
    param_types = set()
    singleton = False

    def __init__(self, variable_instance):
        self.variable_instance = variable_instance
        self.params = variable_params_from_dict(
            json.loads(variable_instance.params or '{}'),
            self.params_def)

    def tick_frame(self, time):
        pass

    def get_value(self):
        raise NotImplementedError()

    def close(self):
        pass


class RandomVariable(Variable):
    name = 'Random'
    description = 'Emits a random floating point value between 0 and 1 each time it\'s accessed.'
    display_order = 500
    param_types = NUMBER_TYPES
    singleton = True

    def __init__(self, variable_instance):
        super(RandomVariable, self).__init__(variable_instance)

    def get_value(self):
        return random.random()


adc = None
if settings.ENABLE_ADC:
    import Adafruit_GPIO.SPI as SPI
    import Adafruit_MCP3008
    adc = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(0, 0))


class AnalogVariable(Variable):
    name = 'Analog'
    description = 'Reads analog signals from attached analog devices such as switches or pots.'
    display_order = 3
    params_def = ParamsDef(
        channel=LongParam(
            'Analog Channel',
            0,
            'Channel to read from the ADC',
        ),
        min_raw=LongParam(
            'Min Value',
            0,
            'Minimum ADC value (scales to 0)',
        ),
        max_raw=LongParam(
            'Max Value',
            1023,
            'Maximum ADC value (scales to 1)',
        ),
    )
    param_types = NUMBER_TYPES

    def __init__(self, variable_instance):
        super(AnalogVariable, self).__init__(variable_instance)

        self.val = 1.0
        if not settings.ENABLE_ADC:
            return

    def tick_frame(self, time):
        if not settings.ENABLE_ADC:
            return

        min_raw = float(self.params.min_raw)
        max_raw = float(self.params.max_raw)

        adc_val = float(adc.read_adc(int(self.params.channel)))
        self.val = min(1.0, max(0.0, (adc_val - min_raw) / (max_raw - min_raw)))

    def get_value(self):
        if not settings.ENABLE_ADC:
            return 1.0

        return self.val


if settings.ENABLE_AUDIO_VAR:
    from pilight.light import audio


class AudioVariable(Variable):
    name = 'Audio'
    description = 'Detects bass frequencies over time and emits a high value when a beat is detected.'
    display_order = 5
    params_def = ParamsDef(
        lpf_freq=LongParam(
            'Low-pass Frequency',
            200,
            'Maximum frequency (in Hz) to monitor for changes',
        ),
        long_term_weight=FloatParam(
            'Long-term Weight',
            0.999,
            'Weighting for the prior value in determining a long-term average (closer to 1 means slower and more '
            'stable adjustment to volume changes)',
        ),
        short_term_weight=FloatParam(
            'Short-term Weight',
            0.7,
            'Weighting for the prior value in determining the current volume (closer to 1 smooths out the '
            'variable\'s signal, but makes it feel less responsive)',
        ),
        audio_duration=FloatParam(
            'Audio Sample Duration',
            0.03,
            'Prior audio duration (secs) to sample from in determining frequency distribution (closer to 0 '
            'results in more responsive signal, but may feel choppy or less stable)',
        ),
        ratio_cutoff=FloatParam(
            'Ratio Cutoff',
            0.7,
            'Amount subtracted from the ratio between current and long term values. Acts as a threshold for '
            'having a signal greater than zero. Higher cutoffs require more energetic audio to produce a signal.',
        ),
        ratio_multiplier=FloatParam(
            'Ratio Multiplier',
            0.6,
            'Multiplier applied after subtracting the cutoff from the ratio. Determines how much audio energy is '
            'required for the signal to reach the max (1.0). A higher multiplier increases the signal sensitivity.',
        ),
    )
    param_types = NUMBER_TYPES
    singleton = True

    def __init__(self, variable_instance):
        super(AudioVariable, self).__init__(variable_instance)

        if not settings.ENABLE_AUDIO_VAR:
            return

        self.exit_event = multiprocessing.Event()
        self.shared_val = multiprocessing.Value('d', 1.0)
        self.val = 1.0
        self.long_term = 1.0
        self.norm_val = 1.0

        # Initialize the audio process
        self.audio_compute_process = audio.AudioComputeProcess(
            exit_event=self.exit_event,
            shared_val=self.shared_val,
            audio_duration=self.params.audio_duration,
            lpf_freq=self.params.lpf_freq,
            short_term_weight=self.params.short_term_weight,
            long_term_weight=self.params.long_term_weight,
            ratio_cutoff=self.params.ratio_cutoff,
            ratio_multiplier=self.params.ratio_multiplier,
        )

        self.audio_compute_process.start()

    def tick_frame(self, time):
        if not settings.ENABLE_AUDIO_VAR:
            return 1.0

        new_val = self.shared_val.value

        # Keep track of a long-term moving average, in order to detect spikes above background noise
        self.long_term = self.long_term * self.params.long_term_weight + new_val * (1 - self.params.long_term_weight)

        # Smooth the value
        self.val = self.val * self.params.short_term_weight + new_val * (1 - self.params.short_term_weight)

        # Normalize for output to shared memory
        self.norm_val = max(0.0, min(1.0, (
            (self.val / self.long_term - self.params.ratio_cutoff) * self.params.ratio_multiplier
        )))

    def get_value(self):
        if not settings.ENABLE_AUDIO_VAR:
            return 1.0

        return self.norm_val

    def close(self):
        if not settings.ENABLE_AUDIO_VAR or not self.audio_compute_process.is_alive():
            return

        # Signal the process to exit
        self.exit_event.set()
        self.audio_compute_process.join()


class ColorChannelVariable(Variable):
    param_type = ParamTypes.COLOR
    name = 'Color Channel'
    description = 'Listens for colors on the given channel. This can be updated dynamically via the API.'
    params_def = ParamsDef(
        channel=StringParam(
            'Channel',
            'default',
            'Color channel to emit',
        ),
        default=ColorParam(
            'Default Color',
            Color.get_default(),
            'Default color to emit when the channel hasn\'t been set',
        ),
    )
    display_order = 400

    def __init__(self, variable_instance, color_channels=None):
        super(ColorChannelVariable, self).__init__(variable_instance)
        self.color_channels = color_channels or {}

    def get_value(self):
        return self.color_channels.get(self.params.channel, self.params.default)


class UnknownVariable(Variable):
    """Used internally when an unrecognized variable is specified"""
    def get_value(self):
        return 1.0


VARIABLES = {
    'colorchannel': ColorChannelVariable,
    'random': RandomVariable,
}

if settings.ENABLE_ADC:
    VARIABLES['analog'] = AnalogVariable

if settings.ENABLE_AUDIO_VAR:
    VARIABLES['audio'] = AudioVariable


def create_variable(variable_instance, color_channels=None):
    # Instantiate a concrete variable based on the given database instance
    variable_cls = VARIABLES.get(variable_instance.variable, UnknownVariable)

    # Special handling for some variables
    if variable_instance.variable == 'colorchannel':
        return variable_cls(variable_instance, color_channels)
    else:
        return variable_cls(variable_instance)
