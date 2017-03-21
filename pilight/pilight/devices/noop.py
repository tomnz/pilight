from pilight.devices import base


class Device(base.DeviceBase):
    def __init__(self, num_leds, scale):
        super(Device, self).__init__(num_leds, scale)

    def set_colors(self, colors):
        pass
