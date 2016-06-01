import struct
import numpy as np
import pyaudio


class Variable(object):
    """
    Defines a common interface for updating and retrieving a dynamic variable
    value.
    """

    def update(self, time):
        pass

    def get_value(self):
        raise NotImplementedError()


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
MAX_y = 2.0 ** (pyaudio.get_sample_size(FORMAT) * 8 - 1)
AUDIO_SECS = 0.05
AUDIO_SAMPLES = int(RATE * AUDIO_SECS)
PRIOR_WEIGHT = 0.2

class AudioVariable(Variable):

    def __init__(self, ):
        super(AudioVariable, self).__init__()

        # Initialize the audio
        self.pyaudio = pyaudio.PyAudio()

        self.stream = self.pyaudio.open(format=FORMAT,
                                        channels=CHANNELS,
                                        rate=RATE,
                                        input=True,
                                        frames_per_buffer=CHUNK)

        self.frames = np.array([0])
        self.val = 0.0
        self.fft_weights = {}
        self.build_weights()

    def build_weights(self):
        self.total_ffts = 0
        for freq in np.fft.rfftfreq(AUDIO_SAMPLES, d=1.0 / RATE):
            if freq < 90:
                self.fft_weights[self.total_ffts] = 1.0
                self.total_ffts += 1
            else:
                print self.fft_weights
                break

    def update(self, time):
        while self.stream.get_read_available() >= CHUNK:
            data = self.stream.read(CHUNK, exception_on_overflow=False)
            self.frames = np.concatenate((self.frames, np.array(struct.unpack('%dh' % CHUNK, data)) / MAX_y))

        if len(self.frames) < AUDIO_SAMPLES:
            self.val = 0.0
            return

        self.frames = self.frames[-AUDIO_SAMPLES:]

        fft_weights = np.fft.rfft(self.frames).real

        new_val = 0.0
        for idx, weight in self.fft_weights.iteritems():
            new_val += abs(fft_weights[idx]) * weight

        self.val = self.val * PRIOR_WEIGHT + (new_val / self.total_ffts) * (1 - PRIOR_WEIGHT)

    def get_value(self):
        val = max(0.0, min(1.0, self.val - 0.5))
        return val

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pyaudio.terminate()

