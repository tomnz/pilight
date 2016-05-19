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
FFT_WEIGHTS = {
    0: 1.0,
    1: 1.0,
    2: 1.0,
    3: 1.0
}

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

        self.frames = np.array()
        self.val = 0.0

    def update(self, time):
        while self.stream.get_read_available() >= CHUNK:
            data = self.stream.read(CHUNK)
            self.frames.append(data)

        self.frames = self.frames[-RATE*AUDIO_SECS:]
        fft = np.fft.fft(self.frames, n=FFT_N)

        self.val = 0.0
        for idx, weight in FFT_WEIGHTS.iteritems():
            self.val += fft[idx] * weight

    def get_value(self):
        return max(0.0, min(1.0, self.val))
