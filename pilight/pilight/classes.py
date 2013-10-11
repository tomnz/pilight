from django.conf import settings
import struct
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
    def get_channel():
        if not PikaConnection.connection_obj:
            # Connect
            PikaConnection.connection_obj = pika.BlockingConnection(
                pika.ConnectionParameters(host=settings.PIKA_HOST_NAME)
            )
            # Open our queues
            PikaConnection.connection_obj.channel().queue_declare(
                queue=settings.PIKA_QUEUE_NAME,
                auto_delete=False,
                durable=True
            )
            if settings.LIGHTS_DRIVER_MODE == 'server':
                PikaConnection.connection_obj.channel().queue_declare(
                    queue=settings.PIKA_QUEUE_NAME_COLORS,
                    auto_delete=False,
                    durable=True
                )
        if not PikaConnection.connection_obj.is_open:
            PikaConnection.connection_obj.connect()
        if not PikaConnection.channel_obj:
            PikaConnection.channel_obj = PikaConnection.connection_obj.channel()
        return PikaConnection.channel_obj


def dec2hex(d):
    return "%02X" % d


class Color(object):
    """
    Helper class that stores an RGB color and provides many utility
    methods. This is the class that gets stored in the database to
    represent a light's color.
    Each color value (r, g, b) is a floating point value between 0
    and 1 - however, values can be greater than 1 or less than 0 in
    order to support HDR operations. This can be very powerful.
    """

    # Constructor
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    # Serialize/deserialize
    def serialize(self):
        return pickle.dumps(self, pickle.HIGHEST_PROTOCOL)

    @classmethod
    def deserialize(cls, val):
        return pickle.loads(val)

    # Creators
    @classmethod
    def from_hex(cls, hex_val):
        if len(hex_val) == 7:
            hex_val = hex_val[1:]
        if len(hex_val) == 6:
            return cls(float(int(hex_val[0:2], 16)) / 255.0, float(int(hex_val[2:4], 16)) / 255.0, float(int(hex_val[4:6], 16)) / 255.0)
        else:
            return cls.get_default()

    @classmethod
    def get_default(cls):
        return cls(1.0, 1.0, 1.0)

    # Operators
    def __add__(self, other):
        if isinstance(other, Color):
            return Color(self.r + other.r, self.g + other.g, self.b + other.b)
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, long, float)):
            return Color(self.r * other, self.g * other, self.b * other)
        elif isinstance(other, Color):
            return Color(self.r * other.r, self.g * other.g, self.b * other.b)
        else:
            return NotImplemented

    def __div__(self, other):
        if isinstance(other, (int, long, float)):
            return Color(self.r / other, self.g / other, self.b / other)
        else:
            return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, (int, long, float)):
            return Color(self.r * other, self.g * other, self.b * other)
        elif isinstance(other, Color):
            return Color(self.r * other.r, self.g * other.g, self.b * other.b)
        else:
            return NotImplemented

    def __imul__(self, other):
        if isinstance(other, (int, long, float)):
            return Color(self.r * other, self.g * other, self.b * other)
        elif isinstance(other, Color):
            return Color(self.r * other.r, self.g * other.g, self.b * other.b)
        else:
            return NotImplemented

    def __idiv__(self, other):
        if isinstance(other, (int, long, float)):
            return Color(self.r / other, self.g / other, self.b / other)
        else:
            return NotImplemented

    # Operations
    def scale(self, scale):
        return Color(self.r * scale, self.g * scale, self.b * scale)

    # Clone
    def clone(self):
        return Color(self.r, self.g, self.b)

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

    def as_safe(self):
        return Color(self.safe_r(), self.safe_g(), self.safe_b())

    def to_hex(self):
        return dec2hex(self.safe_r()*255) + dec2hex(self.safe_g()*255) + dec2hex(self.safe_b()*255)

    def to_hex_web(self):
        return ('#%s' % self.to_hex()).lower()

    def to_raw(self):
        return (
            struct.pack('B', int(self.safe_r() * (2 ** 8 - 1))),
            struct.pack('B', int(self.safe_g() * (2 ** 8 - 1))),
            struct.pack('B', int(self.safe_b() * (2 ** 8 - 1))),
        )

    def to_raw_corrected(self):
        return (
            struct.pack('B', int(self.safe_corrected_r() * (2 ** 8 - 1))),
            struct.pack('B', int(self.safe_corrected_g() * (2 ** 8 - 1))),
            struct.pack('B', int(self.safe_corrected_b() * (2 ** 8 - 1))),
        )

    # Conversion
    def to_hsv(self):
        # Algorithm from:
        # http://www.cs.rit.edu/~ncs/color/t_convert.html
        safe_color = self.as_safe()
        min_val = min(safe_color.r, safe_color.g, safe_color.b)
        max_val = max(safe_color.r, safe_color.g, safe_color.b)
        v = max_val

        delta = max_val - min_val

        if max_val != 0:
            s = delta / max_val
        else:
            s = 0
            h = -1
            return h, s, v

        if safe_color.r == max_val:
            h = (safe_color.g - safe_color.b) / delta
        elif safe_color.g == max_val:
            h = 2 + (safe_color.b - safe_color.r) / delta
        else:
            h = 4 + (safe_color.r - safe_color.g) / delta

        h *= 60
        if h < 0:
            h += 360

        return h, s, v

    @classmethod
    def from_hsv(cls, h, s, v):
        # Algorithm from:
        # http://www.cs.rit.edu/~ncs/color/t_convert.html
        if s == 0:
            return Color(v, v, v)

        h /= 60
        i = int(h)
        f = h - i
        p = v * (1 - s)
        q = v * (1 - s * f)
        t = v * (1 - s * (1 - f))

        if i == 0:
            return Color(v, t, p)
        elif i == 1:
            return Color(q, v, p)
        elif i == 2:
            return Color(p, v, t)
        elif i == 3:
            return Color(p, q, v)
        elif i == 4:
            return Color(t, p, v)
        else:
            return Color(v, p, q)