from django.conf import settings

from pilight.devices import base


class Device(base.DeviceBase):
    def __init__(self, num_leds, scale, repeat):
        super(Device, self).__init__(num_leds, scale, repeat)

        import neopixel
        strip_type = getattr(neopixel.ws, settings.WS281X_STRIP)

        self.strip = neopixel.Adafruit_NeoPixel(
            num=num_leds * scale * repeat,
            pin=settings.WS281X_LED_PIN,
            freq_hz=settings.WS281X_FREQ_HZ,
            dma=settings.WS281X_DMA,
            invert=settings.WS281X_INVERT,
            brightness=255,
            channel=settings.WS281X_CHANNEL,
            strip_type=strip_type)
        self.strip.begin()

    def set_color(self, index, color):
        self.strip.setPixelColor(index, color.to_raw_corrected())

    def finish(self):
        self.strip.show()
