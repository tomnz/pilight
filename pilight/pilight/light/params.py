from pilight.classes import Color


class Param(object):
    def __init__(self, name, default=None, param_type=None, description=None):
        self.name = name
        self.default = default
        self.param_type = param_type
        self.description = description or ''

    @staticmethod
    def to_dict_value(value):
        return value

    @staticmethod
    def from_dict_value(value):
        return value


class BooleanParam(Param):
    def __init__(self, name, default=None, description=None):
        super(BooleanParam, self).__init__(name, default, ParamTypes.BOOLEAN, description)

    @staticmethod
    def to_dict_value(value):
        return bool(value)

    @staticmethod
    def from_dict_value(value):
        return bool(value)


class LongParam(Param):
    def __init__(self, name, default=None, description=None):
        super(LongParam, self).__init__(name, default, ParamTypes.LONG, description)

    @staticmethod
    def to_dict_value(value):
        return long(value)

    @staticmethod
    def from_dict_value(value):
        return long(value)


class FloatParam(Param):
    def __init__(self, name, default=None, description=None):
        super(FloatParam, self).__init__(name, default, ParamTypes.FLOAT, description)

    @staticmethod
    def to_dict_value(value):
        return float(value)

    @staticmethod
    def from_dict_value(value):
        return float(value)


class ColorParam(Param):
    def __init__(self, name, default=None, description=None):
        super(ColorParam, self).__init__(name, default, ParamTypes.COLOR, description)

    @staticmethod
    def to_dict_value(value):
        return {
            'r': value.r,
            'g': value.g,
            'b': value.b,
            'a': value.a,
        }

    @staticmethod
    def from_dict_value(value):
        return Color(
            value.get('r', 1.0),
            value.get('g', 1.0),
            value.get('b', 1.0),
            value.get('a', 1.0),
        )


class PercentParam(Param):
    def __init__(self, name, default=None, description=None):
        super(PercentParam, self).__init__(name, default, ParamTypes.PERCENT, description)

    @staticmethod
    def to_dict_value(value):
        return float(value)

    @staticmethod
    def from_dict_value(value):
        return float(value)


class StringParam(Param):
    def __init__(self, name, default=None, description=None):
        super(StringParam, self).__init__(name, default, ParamTypes.STRING, description)

    @staticmethod
    def to_dict_value(value):
        return str(value)

    @staticmethod
    def from_dict_value(value):
        return str(value)


class ParamTypes(object):
    BOOLEAN = 'boolean'
    LONG = 'long'
    FLOAT = 'float'
    COLOR = 'color'
    PERCENT = 'percent'
    STRING = 'string'


def param_from_dict(value, params_def):
    result = {}
    for name, param in params_def.iteritems():
        if name in value:
            result[name] = param.from_dict_value(value[name])
        else:
            result[name] = param.default

    return result


def param_to_dict(value, params_def):
    result = {}
    for name, param in params_def.iteritems():
        if name in value:
            result[name] = param.to_dict_value(value[name])
        else:
            result[name] = param.default

    return result
