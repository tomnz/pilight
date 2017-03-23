from pilight.devices import base


class Device(base.DeviceBase):
    def __init__(self, num_leds, scale, repeat):
        super(Device, self).__init__(num_leds, scale, repeat)

        import Adafruit_WS2801
        from Adafruit_GPIO import SPI
        self.strip = Adafruit_WS2801.WS2801Pixels(
            num_leds * scale * repeat,
            spi=SPI.SpiDev(0, 0))
        self.strip.clear()
        self.strip.show()

    def set_color(self, index, color):
        self.strip.set_pixel(index, color.to_raw_corrected())

    def finish(self):
        self.strip.show()
