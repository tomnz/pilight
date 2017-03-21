from pilight.devices import base


class Device(base.DeviceBase):
    def __init__(self, num_leds, scale):
        super(Device, self).__init__(num_leds, scale)

        import Adafruit_WS2801
        from Adafruit_GPIO import SPI
        self.strip = Adafruit_WS2801.WS2801Pixels(
            num_leds * scale,
            spi=SPI.SpiDev(0, 0))
        self.strip.clear()
        self.strip.show()

    def set_colors(self, colors):
        for idx, color in enumerate(colors):
            out_color = color.to_raw_corrected()
            for light_num in range(self.scale):
                self.strip.set_pixel(idx * self.scale + light_num, out_color)

        self.strip.show()
