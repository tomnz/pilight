from django.conf import settings

from pilight.devices import base


class Device(base.DeviceBase):
    def __init__(self, num_leds, scale):
        super(Device, self).__init__(num_leds, scale)

        import neopixel
        strip_type = getattr(neopixel.ws, settings.WS281X_STRIP)

        self.strip = neopixel.Adafruit_NeoPixel(
            num=num_leds * scale,
            pin=settings.WS281X_LED_PIN,
            freq_hz=settings.WS281X_FREQ_HZ,
            dma=settings.WS281X_DMA,
            invert=settings.WS281X_INVERT,
            brightness=255,
            channel=settings.WS281X_CHANNEL,
            strip_type=strip_type)
        self.strip.begin()

    def set_colors(self, colors):
        for idx, color in enumerate(colors):
            out_r = int(color.safe_corrected_r() * 255)
            out_g = int(color.safe_corrected_g() * 255)
            out_b = int(color.safe_corrected_b() * 255)

            for light_num in range(self.scale):
                self.strip.setPixelColorRGB(
                    idx * self.scale + light_num,
                    out_r, out_g, out_b)

        self.strip.show()
