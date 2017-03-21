import abc


class DeviceBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, num_leds, scale):
        self.num_leds = num_leds
        self.scale = scale

    @abc.abstractmethod
    def set_colors(self, colors):
        pass
