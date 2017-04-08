import json
import random
import struct

from django.conf import settings
import numpy as np
if settings.ENABLE_AUDIO_VAR:
    import pyaudio

from pilight.light.params import BooleanParam, LongParam, FloatParam, PercentParam, \
    ColorParam, StringParam, ParamsDef, variable_params_from_dict
from pilight.light.types import ParamTypes
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
    param_type = None
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
    description = 'Emits a random floating point value between 0 and 1 each frame.'
    display_order = 500
    param_type = ParamTypes.FLOAT
    singleton = True

    def __init__(self, variable_instance):
        super(RandomVariable, self).__init__(variable_instance)
        self.value = 0.0

    def tick_frame(self, time):
        self.value = random.random()

    def get_value(self):
        return self.value


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
SAMPLE_SIZE = pyaudio.get_sample_size(FORMAT)
MAX_y = 2.0 ** (SAMPLE_SIZE * 8) - 1
AUDIO_SECS = 0.03


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
            0.5,
            'Amount subtracted from the ratio between current and long term values. Acts as a threshold for '
            'having a signal greater than zero. Higher cutoffs require more energetic audio to produce a signal.',
        ),
        ratio_multiplier=FloatParam(
            'Ratio Multiplier',
            0.4,
            'Multiplier applied after subtracting the cutoff from the ratio. Determines how much audio energy is '
            'required for the signal to reach the max (1.0). A higher multiplier increases the signal sensitivity.',
        ),
    )
    param_type = ParamTypes.FLOAT
    singleton = True

    def __init__(self, variable_instance):
        super(AudioVariable, self).__init__(variable_instance)

        if not settings.ENABLE_AUDIO_VAR:
            return

        # Initialize the audio
        self.pyaudio = pyaudio.PyAudio()

        self.stream = self.pyaudio.open(format=FORMAT,
                                        channels=CHANNELS,
                                        rate=RATE,
                                        input=True,
                                        frames_per_buffer=CHUNK)

        self.audio_samples = int(RATE * self.params.audio_duration)
        self.frames = np.array([0])
        self.val = 0.0
        self.norm_val = 0.0
        self.long_term = 0.0
        self.total_ffts = 0
        self.determine_freqs()

    def tick_frame(self, time):
        if not settings.ENABLE_AUDIO_VAR:
            return

        while self.stream.get_read_available() >= CHUNK:
            try:
                data = self.stream.read(CHUNK)
            except:
                break

            self.frames = np.concatenate((self.frames, np.array(struct.unpack('%dh' % (len(data) / SAMPLE_SIZE), data)) / MAX_y))

        if len(self.frames) < self.audio_samples:
            self.val = 0.0
            return

        # Truncate sample
        self.frames = self.frames[-self.audio_samples:]

        # Compute FFT over sample
        # Note the use of a Blackman filter to remove FFT jitter from rough ends of sample
        # Also note we truncate to the first n samples, where n was determined from the FFT frequencies
        fft = np.fft.fft(self.frames * np.blackman(self.audio_samples))[0:self.total_ffts]
        fftb = np.sqrt(fft.imag ** 2 + fft.real ** 2) / 5
        new_val = np.max(fftb)

        # Keep track of a long-term moving average, in order to detect spikes above background noise
        self.long_term = self.long_term * self.params.long_term_weight + new_val * (1 - self.params.long_term_weight)

        # Smooth the value
        self.val = self.val * self.params.short_term_weight + new_val * (1 - self.params.short_term_weight)

        # Normalize for output
        self.norm_val = max(0.0, min(1.0, (
            (self.val / self.long_term - self.params.ratio_cutoff) * self.params.ratio_multiplier
        )))

    def get_value(self):
        if not settings.ENABLE_AUDIO_VAR:
            return 1.0

        return self.norm_val

    def close(self):
        if not settings.ENABLE_AUDIO_VAR:
            return

        self.stream.stop_stream()
        self.stream.close()
        self.pyaudio.terminate()

    def determine_freqs(self):
        # Pre-compute which FFT values to include, based on their frequency
        for freq in np.fft.rfftfreq(self.audio_samples, d=1.0 / RATE):
            if freq < self.params.lpf_freq:
                self.total_ffts += 1
            else:
                break


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
