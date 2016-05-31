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
RATE = 32000
MAX_y = 2.0 ** (pyaudio.get_sample_size(FORMAT) * 8 - 1)
AUDIO_SECS = 0.25
FFT_N = 20

# Frequencies for 1024 sample size @ 32000 Hz
FFT_WEIGHTS = {
    0: 0.2,  # 0
    1: 0.5,  # 31.25
    2: 0.5,  # 62.5
    3: 0.5,  # 93.75
    4: 0.5,  # 125
    5: 0.2   # 156.25
}
PRIOR_WEIGHT = 0.7

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

    def update(self, time):
        chunk = None
        while self.stream.get_read_available() >= CHUNK:
            data = self.stream.read(CHUNK, exception_on_overflow=False)
            chunk = np.array(struct.unpack('%dh' % CHUNK, data)) / MAX_y

        if chunk is None or not chunk.any():
            self.val = 0.0
            return

        fft_weights = np.fft.rfft(chunk).real

        val = 0.0
        for idx, weight in FFT_WEIGHTS.iteritems():
            val += abs(fft_weights[idx]) * weight

        self.val = self.val * PRIOR_WEIGHT + val * (1 - PRIOR_WEIGHT)

    def get_value(self):
        return max(0.0, min(1.0, self.val - 0.2))

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pyaudio.terminate()
