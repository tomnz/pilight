from picklefield.fields import PickledObjectField
from pilight.widgets import ColorPickerWidget


class ColorField(PickledObjectField):
    def __init__(self, *args, **kwargs):
        super(ColorField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs['widget'] = ColorPickerWidget
        return super(ColorField, self).formfield(**kwargs)
