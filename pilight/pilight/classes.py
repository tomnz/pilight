import struct

from django.conf import settings
import pickle
import pika


class PikaConnection(object):
    """
    Encapsulates a Pika connection, ensuring we resuse the connection
    as much as possible
    """

    connection_obj = None
    channel_obj = None

    @staticmethod
    def clear_channel():
        PikaConnection.connection_obj = None
        PikaConnection.channel_obj = None

    @staticmethod
    def get_channel():
        if (PikaConnection.connection_obj and not PikaConnection.connection_obj.is_open) or \
                (PikaConnection.channel_obj and not PikaConnection.channel_obj.is_open):
            # Just start over in this case...
            PikaConnection.connection_obj = None
            PikaConnection.channel_obj = None

        if not PikaConnection.connection_obj:
            # Connect
            try:
                PikaConnection.connection_obj = pika.BlockingConnection(
                    pika.ConnectionParameters(host=settings.PIKA_HOST_NAME, heartbeat_interval=60)
                )
            except pika.exceptions.AMQPConnectionError:
                # Connection failed - just silently return nothing
                return None

            # Open our queues
            PikaConnection.connection_obj.channel().queue_declare(
                queue=settings.PIKA_QUEUE_NAME,
                auto_delete=False,
                durable=True
            )
            if settings.LIGHTS_DEVICE == 'client':
                PikaConnection.connection_obj.channel().queue_declare(
                    queue=settings.PIKA_QUEUE_NAME_COLORS,
                    auto_delete=False,
                    durable=True
                )

        if not PikaConnection.channel_obj:
            PikaConnection.channel_obj = PikaConnection.connection_obj.channel()
        return PikaConnection.channel_obj


def dec2hex(d):
    return "%02X" % d


class Color(object):
    """
    Helper class that stores an RGBA color and provides many utility
    methods. This is the class that gets stored in the database to
    represent a light's color.
    Each color value (r, g, b, a) is a floating point value between 0
    and 1 - however, values can be greater than 1 or less than 0 in
    order to support HDR operations. This can be very powerful.
    """

    # Constructors
    def __init__(self, r, g, b, w=0.0, a=1.0):
        self.r = r
        self.g = g
        self.b = b
        self.w = w
        self.a = a

    # Serialize/deserialize
    def serialize(self):
        return pickle.dumps(self, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def deserialize(val):
        return pickle.loads(val)

    # Creators
    @staticmethod
    def from_hex(hex_val):
        if len(hex_val) == 7:
            hex_val = hex_val[1:]
        if len(hex_val) == 6:
            return Color(
                float(int(hex_val[0:2], 16)) / 255.0,
                float(int(hex_val[2:4], 16)) / 255.0,
                float(int(hex_val[4:6], 16)) / 255.0)
        else:
            return Color.get_default()

    @staticmethod
    def from_dict(color_dict):
        return Color(
            color_dict.get('r', 0.0),
            color_dict.get('g', 0.0),
            color_dict.get('b', 0.0),
            color_dict.get('w', 0.0),
            color_dict.get('a', 1.0),
        )

    @staticmethod
    def get_default():
        return Color(1.0, 1.0, 1.0, 0.0, 1.0)

    # Blending operations
    @staticmethod
    def blend_normal(bg, fg):
        if not isinstance(bg, Color) or not isinstance(fg, Color):
            return Color.get_default()

        fg_a = getattr(fg, 'a', 1.0)
        bg_a = getattr(bg, 'a', 1.0)

        # Basic easy cases
        if fg_a == 1.0:
            return fg.clone()
        elif fg_a == 0:
            return bg.clone()
        elif bg_a == 0:
            return fg.clone()
        elif bg_a == 1.0:
            return Color(
                bg.r * (1 - fg_a) + fg.r * fg_a,
                bg.g * (1 - fg_a) + fg.g * fg_a,
                bg.b * (1 - fg_a) + fg.b * fg_a,
                bg.w * (1 - fg_a) + fg.w * fg_a,)

        # Both channels have alpha
        a = fg_a + bg_a - fg_a * bg_a
        bg_scaled = bg * bg_a
        bg_scaled.a = 1.0
        fg_scaled = fg * fg_a
        fg_scaled.a = 1.0

        final = fg_scaled * fg_a + bg_scaled * (1 - fg_a)
        if a > 0:
            final /= a
        final.a = a

        return final

    @staticmethod
    def blend_mult(a, b):
        if getattr(a, 'a', 1.0) == 1.0 and getattr(b, 'a', 1.0) == 1.0:
            return Color(a.r * b.r, a.g * b.g, a.b * b.b, getattr(a, 'w', 0.0) * getattr(b, 'w', 0.0))
        else:
            return Color.blend_mult(a.flatten_alpha(), b.flatten_alpha())

    # Operators
    def __add__(self, other):
        if getattr(self, 'a', 1.0) == 1.0 and getattr(other, 'a', 1.0) == 1.0:
            return Color(
                self.r + other.r,
                self.g + other.g,
                self.b + other.b,
                getattr(self, 'w', 0.0) + getattr(other, 'w', 0.0))
        else:
            return self.flatten_alpha() + other.flatten_alpha()

    def __mul__(self, other):
        # Don't multiply the alpha
        return Color(
            self.r * other,
            self.g * other,
            self.b * other,
            getattr(self, 'w', 0.0) * other,
            getattr(self, 'a', 1.0))

    def __rmul__(self, other):
        return self * other

    def __div__(self, other):
        return Color(
            self.r / other,
            self.g / other,
            self.b / other,
            getattr(self, 'w', 0.0) / other,
            getattr(self, 'a', 1.0))

    # Clone
    def clone(self):
        return Color(
            self.r,
            self.g,
            self.b,
            getattr(self, 'w', 0.0),
            getattr(self, 'a', 0.0))

    # Utility functions
    def safe_r(self):
        return max(min(self.r, 1), 0)

    def safe_corrected_r(self):
        return max(min(self.r * settings.LIGHTS_MULTIPLIER_R, 1), 0)

    def safe_g(self):
        return max(min(self.g, 1), 0)

    def safe_corrected_g(self):
        return max(min(self.g * settings.LIGHTS_MULTIPLIER_G, 1), 0)

    def safe_b(self):
        return max(min(self.b, 1), 0)

    def safe_corrected_b(self):
        return max(min(self.b * settings.LIGHTS_MULTIPLIER_B, 1), 0)

    def safe_w(self):
        return max(min(getattr(self, 'w', 0.0), 1), 0)

    def safe_corrected_w(self):
        return max(min(getattr(self, 'w', 0.0) * settings.LIGHTS_MULTIPLIER_W, 1), 0)

    def safe_a(self):
        return max(min(getattr(self, 'a', 1.0), 1), 0)

    def safe_dict(self):
        return {
            'r': self.safe_r(),
            'g': self.safe_g(),
            'b': self.safe_b(),
            'w': self.safe_w(),
            'a': self.safe_a(),
        }

    def as_safe(self):
        return Color(self.safe_r(), self.safe_g(), self.safe_b(), self.safe_w(), self.safe_a())

    def flatten_alpha(self):
        flattened = self * getattr(self, 'a', 1.0)
        flattened.a = 1.0
        return flattened

    def to_hex(self):
        flattened = self.flatten_alpha()
        return dec2hex(flattened.safe_r()*255) + dec2hex(flattened.safe_g()*255) + dec2hex(flattened.safe_b()*255)

    def to_hex_web(self):
        return ('#%s' % self.to_hex()).lower()

    def to_raw(self):
        flattened = self.flatten_alpha()
        return (
            struct.pack('B', int(flattened.safe_r() * (2 ** 8 - 1))),
            struct.pack('B', int(flattened.safe_g() * (2 ** 8 - 1))),
            struct.pack('B', int(flattened.safe_b() * (2 ** 8 - 1))),
        )

    def to_raw_corrected(self):
        flattened = self.flatten_alpha()
        return (
            struct.pack('B', int(flattened.safe_corrected_r() * (2 ** 8 - 1))),
            struct.pack('B', int(flattened.safe_corrected_g() * (2 ** 8 - 1))),
            struct.pack('B', int(flattened.safe_corrected_b() * (2 ** 8 - 1))),
        )

    # Conversion
    def to_hsv(self):
        # Algorithm from:
        # http://www.cs.rit.edu/~ncs/color/t_convert.html
        w = getattr(self, 'w', 0.0)
        a = getattr(self, 'a', 1.0)

        safe_color = self.as_safe()
        min_val = min(safe_color.r, safe_color.g, safe_color.b)
        max_val = max(safe_color.r, safe_color.g, safe_color.b)
        v = max_val

        delta = max_val - min_val

        if delta == 0:
            # Grayscale
            s = 0
            h = -1
            return h, s, v, w, a

        if max_val != 0:
            s = delta / max_val
        else:
            s = 0
            h = -1
            return h, s, v, w, a

        if safe_color.r == max_val:
            h = (safe_color.g - safe_color.b) / delta
        elif safe_color.g == max_val:
            h = 2 + (safe_color.b - safe_color.r) / delta
        else:
            h = 4 + (safe_color.r - safe_color.g) / delta

        h *= 60
        if h < 0:
            h += 360

        return h, s, v, w, a

    @classmethod
    def from_hsv(cls, h, s, v, w=0.0, a=1.0):
        # Algorithm from:
        # http://www.cs.rit.edu/~ncs/color/t_convert.html
        if s == 0:
            return Color(v, v, v, w, a)

        h /= 60
        i = int(h)
        f = h - i
        p = v * (1 - s)
        q = v * (1 - s * f)
        t = v * (1 - s * (1 - f))

        if i == 0:
            return Color(v, t, p, w, a)
        elif i == 1:
            return Color(q, v, p, w, a)
        elif i == 2:
            return Color(p, v, t, w, a)
        elif i == 3:
            return Color(p, q, v, w, a)
        elif i == 4:
            return Color(t, p, v, w, a)
        else:
            return Color(v, p, q, w, a)
