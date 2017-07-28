from pilight.classes import Color
from pilight.light.types import ParamTypes


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
        return int(value)

    @staticmethod
    def from_dict_value(value):
        return int(value)


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
            'w': value.w,
            'a': value.a,
        }

    @staticmethod
    def from_dict_value(value):
        return Color(
            value.get('r', 1.0),
            value.get('g', 1.0),
            value.get('b', 1.0),
            value.get('w', 1.0),
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


class VariableParam(object):
    def __init__(self, variable_id, get_value, multiply=1.0, add=0, convert=None):
        self.variable_id = variable_id
        self.get_value = get_value
        self.multiply = multiply
        self.add = add
        self.convert = convert

    @property
    def value(self):
        val = self.get_value() * self.multiply + self.add
        if self.convert:
            return self.convert(val)
        return val

    def to_dict(self):
        return {
            'variableId': self.variable_id,
            'multiply': self.multiply,
            'add': self.add,
        }


class ParamsDef(object):
    def __init__(self, **kwargs):
        self.params_def = kwargs

    def __getattr__(self, item):
        return self.params_def[item]

    def iteritems(self):
        for key, value in self.params_def.iteritems():
            yield key, value

    def to_dict(self):
        result = {}
        for name, param_def in self.params_def.iteritems():
            result[name] = {
                'name': param_def.name,
                'description': param_def.description,
                'type': param_def.param_type,
                'defaultValue': param_def.to_dict_value(param_def.default),
            }
        return result


class TransformParams(object):
    def __init__(self, params_def, variable_params, **kwargs):
        self.params_def = params_def
        self.variable_params = variable_params
        self.params = kwargs

    def __getattr__(self, item):
        if item in self.variable_params:
            return self.variable_params[item].value

        return self.params[item]

    def iteritems(self):
        for key, value in self.params.iteritems():
            yield key, value

    def to_dict(self):
        params = {}

        for name, param in self.params_def.iteritems():
            if name in self.params:
                params[name] = param.to_dict_value(self.params[name])
            else:
                params[name] = param.default

        return params


class VariableParams(object):
    def __init__(self, params_def, **kwargs):
        self.params_def = params_def
        self.params = kwargs

    def __getattr__(self, item):
        return self.params[item]

    def iteritems(self):
        for key, value in self.params.iteritems():
            yield key, value

    def to_dict(self):
        params = {}

        for name, param in self.params_def.iteritems():
            if name in self.params:
                params[name] = param.to_dict_value(self.params[name])
            else:
                params[name] = param.default

        return params


def transform_params_from_dict(values, variable_params, params_def, variables=None):
    params = {}

    for name, param in params_def.iteritems():
        if name in values:
            params[name] = param.from_dict_value(values[name])
        else:
            params[name] = param.default

        if name in variable_params:
            variable_param = variable_params[name]
            if variables and variable_param.variable_id in variables:
                variable_param.get_value = variables[variable_param.variable_id].get_value

    return TransformParams(params_def, variable_params, **params)


PARAM_CONVERSIONS = {
    ParamTypes.BOOLEAN: lambda value: bool(value),
    ParamTypes.LONG: lambda value: int(round(value)),
}


def transform_variable_params_from_dict(values, params_def):
    variable_params = {}

    for name, param in params_def.iteritems():
        if name in values:
            variable_value = values[name]
            variable_params[name] = VariableParam(
                variable_id=variable_value['variableId'],
                get_value=lambda: 1.0,
                multiply=variable_value.get('multiply', 1.0),
                add=variable_value.get('add', 0.0),
                convert=PARAM_CONVERSIONS.get(param.param_type, None)
            )

    return variable_params


def variable_params_from_dict(values, params_def):
    params = {}

    for name, param in params_def.iteritems():
        if name in values:
            params[name] = param.from_dict_value(values[name])
        else:
            params[name] = param.default

    return VariableParams(params_def, **params)
