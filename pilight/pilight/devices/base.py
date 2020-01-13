import abc
import multiprocessing


class DeviceBase(multiprocessing.Process, metaclass=abc.ABCMeta):
    def __init__(self, colors_pipe, num_leds, scale, repeat):
        super(DeviceBase, self).__init__()

        self.strip = None
        self.colors_pipe = colors_pipe
        self.num_leds = num_leds
        self.scale = scale
        self.repeat = repeat

    @abc.abstractmethod
    def init(self):
        pass

    def run(self):
        self.init()
        while True:
            try:
                colors = self.colors_pipe.recv()
                if not colors:
                    print('    Closed light device')
                    return

                self.show_colors(colors)

            except KeyboardInterrupt:
                # Ignore a terminate signal - it's handled in the main process, and
                # we still have cleanup work to do with the lights
                continue

    def show_colors(self, colors):
        for r in range(self.repeat):
            for i, color in enumerate(colors):
                for s in range(self.scale):
                    self.set_color(r * self.num_leds + i * self.scale + s, color)

        self.finish()

    @abc.abstractmethod
    def set_color(self, index, color):
        pass

    def finish(self):
        pass
