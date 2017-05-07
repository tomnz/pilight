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
        if color.a != 1.0:
            color = color.flatten_alpha()

        r = int(color.safe_corrected_r() * 255)
        g = int(color.safe_corrected_g() * 255)
        b = int(color.safe_corrected_b() * 255)
        w = int(color.safe_corrected_w() * 255)
        self.strip.setPixelColorRGB(index, r, g, b, w)

    def finish(self):
        self.strip.show()
