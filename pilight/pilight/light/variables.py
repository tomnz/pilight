import random
import struct

from django.conf import settings
import numpy as np
if settings.ENABLE_AUDIO_VAR:
    import pyaudio

from pilight.light.types import ParamTypes


class Variable(object):
    """
    Defines a common interface for updating and retrieving a dynamic variable
    value.
    """

    param_type = None

    def update(self, time):
        pass

    def get_value(self):
        raise NotImplementedError()

    def close(self):
        pass


class RandomVariable(Variable):
    param_type = ParamTypes.FLOAT

    def get_value(self):
        return random.random()


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
SAMPLE_SIZE = pyaudio.get_sample_size(FORMAT)
MAX_y = 2.0 ** (SAMPLE_SIZE * 8) - 1
AUDIO_SECS = 0.03
AUDIO_SAMPLES = int(RATE * AUDIO_SECS)
PRIOR_WEIGHT = 0.7
LONG_TERM_WEIGHT = 0.999


class AudioVariable(Variable):
    param_type = ParamTypes.FLOAT

    def __init__(self, ):
        super(AudioVariable, self).__init__()

        if not settings.ENABLE_AUDIO_VAR:
            return

        # Initialize the audio
        self.pyaudio = pyaudio.PyAudio()

        self.stream = self.pyaudio.open(format=FORMAT,
                                        channels=CHANNELS,
                                        rate=RATE,
                                        input=True,
                                        frames_per_buffer=CHUNK)

        self.frames = np.array([0])
        self.val = 0.0
        self.norm_val = 0.0
        self.long_term = 0.0
        self.total_ffts = 0
        self.determine_freqs()

    def update(self, time):
        if not settings.ENABLE_AUDIO_VAR:
            return

        while self.stream.get_read_available() >= CHUNK:
            try:
                data = self.stream.read(CHUNK)
            except:
                break

            self.frames = np.concatenate((self.frames, np.array(struct.unpack("%dh" % (len(data) / SAMPLE_SIZE), data)) / MAX_y))

        if len(self.frames) < AUDIO_SAMPLES:
            self.val = 0.0
            return

        # Truncate sample
        self.frames = self.frames[-AUDIO_SAMPLES:]

        # Compute FFT over sample
        # Note the use of a Blackman filter to remove FFT jitter from rough ends of sample
        # Also note we truncate to the first n samples, where n was determined from the FFT frequencies
        fft = np.fft.fft(self.frames * np.blackman(AUDIO_SAMPLES))[0:self.total_ffts]
        fftb = np.sqrt(fft.imag ** 2 + fft.real ** 2) / 5
        new_val = np.max(fftb)

        # Keep track of a long-term moving average, in order to detect spikes above background noise
        self.long_term = self.long_term * LONG_TERM_WEIGHT + new_val * (1 - LONG_TERM_WEIGHT)

        # Smooth the value
        self.val = self.val * PRIOR_WEIGHT + new_val * (1 - PRIOR_WEIGHT)

        # Normalize for output
        self.norm_val = max(0.0, min(1.0, ((self.val / self.long_term - 1.0) / 3)))

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
        for freq in np.fft.rfftfreq(AUDIO_SAMPLES, d=1.0 / RATE):
            if freq < 120:
                self.total_ffts += 1
            else:
                break
