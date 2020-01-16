from pilight.devices import base


class Device(base.DeviceBase):
    def init(self):
        import adafruit_ws2801
        import board

        self.strip = adafruit_ws2801.WS2801(
            board.SCLK,
            board.MOSI,
            n=self.num_leds * self.scale * self.repeat,
            auto_write=False)
        self.strip.show()

    def set_color(self, index, color):
        self.strip[index] = (color[0], color[1], color[2])

    def finish(self):
        self.strip.show()
