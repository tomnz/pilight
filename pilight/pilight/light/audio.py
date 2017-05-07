import multiprocessing
import struct
import time

from django.conf import settings
import numpy as np
import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
SAMPLE_SIZE = pyaudio.get_sample_size(FORMAT)
MAX_y = 2.0 ** (SAMPLE_SIZE * 8) - 1
AUDIO_SECS = 0.03


class AudioComputeProcess(multiprocessing.Process):
    def __init__(self, exit_event, shared_val, audio_duration, lpf_freq, short_term_weight, long_term_weight,
                 ratio_cutoff, ratio_multiplier):

        super(AudioComputeProcess, self).__init__()

        self.exit_event = exit_event
        self.shared_val = shared_val
        self.short_term_weight = short_term_weight
        self.long_term_weight = long_term_weight
        self.ratio_cutoff = ratio_cutoff
        self.ratio_multiplier = ratio_multiplier

        self.audio_samples = int(RATE * audio_duration)
        self.val = 1.0
        self.norm_val = 1.0
        self.long_term = 1.0
        self.total_ffts = 0
        self.stream = None
        self.frames = None
        self.pyaudio = None

        self.determine_freqs(lpf_freq)

    def run(self):
        try:
            # Initialize the audio
            self.frames = np.array([0])
            self.pyaudio = pyaudio.PyAudio()

            self.stream = self.pyaudio.open(format=FORMAT,
                                            channels=CHANNELS,
                                            rate=RATE,
                                            input=True,
                                            frames_per_buffer=CHUNK)

            while not self.exit_event.is_set():
                current_time = time.time()
                self.do_fft()

                # Throttle to configured light update interval - extra computation beyond this rate
                # is wasted
                sleep_time = settings.LIGHTS_UPDATE_INTERVAL - (time.time() - current_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)

            self.close()

        except KeyboardInterrupt:
            self.close()

    def do_fft(self):
        while self.stream.get_read_available() >= CHUNK:
            try:
                data = self.stream.read(CHUNK)
            except:
                break

            self.frames = np.concatenate((self.frames, np.array(
                struct.unpack('%dh' % (len(data) / SAMPLE_SIZE), data)) / MAX_y))

        if len(self.frames) < self.audio_samples:
            self.val = 1.0
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
        self.long_term = self.long_term * self.long_term_weight + new_val * (1 - self.long_term_weight)

        # Smooth the value
        self.val = self.val * self.short_term_weight + new_val * (1 - self.short_term_weight)

        # Normalize for output to shared memory
        self.shared_val.value = max(0.0, min(1.0, (
            (self.val / self.long_term - self.ratio_cutoff) * self.ratio_multiplier
        )))

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pyaudio.terminate()
        print '    Closed audio device'

    def determine_freqs(self, lpf_freq):
        # Pre-compute which FFT values to include, based on their frequency
        for freq in np.fft.rfftfreq(self.audio_samples, d=1.0 / RATE):
            if freq < lpf_freq:
                self.total_ffts += 1
            else:
                break
