import abc


class DeviceBase(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, num_leds, scale, repeat):
        self.num_leds = num_leds
        self.scale = scale
        self.repeat = repeat

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
