from picklefield.fields import PickledObjectField


class ColorField(PickledObjectField):
    def __init__(self, *args, **kwargs):
        super(ColorField, self).__init__(*args, **kwargs)
