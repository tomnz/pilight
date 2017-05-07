from django.conf import settings

from pilight.devices import base


class Device(base.DeviceBase):
    def init(self):
        import neopixel
        strip_type = getattr(neopixel.ws, settings.WS281X_STRIP)

        self.strip = neopixel.Adafruit_NeoPixel(
            num=self.num_leds * self.scale * self.repeat,
            pin=settings.WS281X_LED_PIN,
            freq_hz=settings.WS281X_FREQ_HZ,
            dma=settings.WS281X_DMA,
            invert=settings.WS281X_INVERT,
            brightness=255,
            channel=settings.WS281X_CHANNEL,
            strip_type=strip_type)
        self.strip.begin()

    def set_color(self, index, color):
        self.strip.setPixelColorRGB(index, color[0], color[1], color[2], color[3])

    def finish(self):
        self.strip.show()
