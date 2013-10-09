import math
import struct
import sys
import pickle


def dec2hex(d):
    return "%02X" % d


class Color(object):

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

    # Operations
    def scale(self, scale):
        return Color(self.r * scale, self.g * scale, self.b * scale)

    # Clone
    def clone(self):
        return Color(self.r, self.g, self.b)

    # Utility functions
    def safe_r(self):
        return max(min(self.r, 1), 0)

    def safe_g(self):
        return max(min(self.g, 1), 0)

    def safe_b(self):
        return max(min(self.b, 1), 0)

    def to_hex(self):
        return dec2hex(self.safe_r()*255) + dec2hex(self.safe_g()*255) + dec2hex(self.safe_b()*255)

    def to_hex_web(self):
        return '#%s' % self.to_hex()

    def to_raw(self):
        return (
            struct.pack('B', int(self.safe_r() * (2 ** 8))),
            struct.pack('B', int(self.safe_g() * (2 ** 8))),
            struct.pack('B', int(self.safe_b() * (2 ** 8))),
        )
