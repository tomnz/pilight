from pilight.devices import base


class Device(base.DeviceBase):
    def __init__(self, num_leds, scale, repeat):
        super(Device, self).__init__(num_leds, scale, repeat)

    def set_color(self, index, color):
        pass
