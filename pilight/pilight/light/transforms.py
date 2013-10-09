import json
import math


class TransformBase(object):

    def __init__(self, params):
        # Base classes should override this - and do something with params if need be
        pass

    def transform(self, time, position, num_positions, start_color, all_colors):
        """
        Performs the actual color transformation for this transform step
        """
        pass

    def serialize_params(self):
        """
        Serializes all parameters back to JSON
        """
        pass


class FlashTransform(TransformBase):

    def __init__(self, params):
        super(FlashTransform, self).__init__(params)

        self.valid = False

        try:
            param_vals = json.loads(params)
        except ValueError:
            return

        self.rate = float(param_vals['rate'])
        self.start_value = float(param_vals['start_value'])
        self.end_value = float(param_vals['end_value'])
        self.sine = bool(param_vals['sine'])

        self.valid = True

    def transform(self, time, position, num_positions, start_color, all_colors):
        if not self.valid:
            return start_color

        # Transform time/rate into a percentage for the current oscillation
        freq = 1.0 / self.rate
        progress = time / freq - int(time / freq)

        # Optional: Transform here to a sine wave
        if self.sine:
            progress = math.cos(progress * 2 * math.pi)
        else:
            # Otherwise transform to straight -1, 1, -1 sawtooth
            progress = 1 - (2 * abs(progress * 2 - 1))

        # Convert from -1 -> 1 into 0 -> 1
        progress = (progress + 1) / 2

        # Compute value based on progress and start/end vals
        scale = (1 - progress) * self.start_value + progress * self.end_value

        return start_color.scale(scale)

    def serialize_params(self):
        params = dict()
        params['rate'] = self.rate
        params['start_value'] = self.start_value
        params['end_value'] = self.end_value
        params['sine'] = self.sine
        return json.dumps(params)


class ScrollTransform(TransformBase):

    def __init__(self, params):
        super(ScrollTransform, self).__init__(params)

        self.valid = False

        try:
            param_vals = json.loads(params)
        except ValueError:
            return

        self.rate = float(param_vals['rate'])
        self.reverse = bool(param_vals['reverse'])

        self.valid = True

    def transform(self, time, position, num_positions, start_color, all_colors):
        if not self.valid:
            return start_color

        # Transform time/rate into a percentage
        freq = 1.0 / self.rate
        progress = time / freq - int(time / freq)

        # Calculate offset to source from
        offset = progress * num_positions
        source_position = (int(offset) + position) % num_positions
        next_position = (source_position + 1) % num_positions
        percent = offset % 1

        # Compute the blended color
        if percent == 0:
            return all_colors[source_position].clone()
        else:
            return all_colors[source_position].scale(percent) + all_colors[next_position].scale(1 - percent)

    def serialize_params(self):
        params = dict()
        params['rate'] = self.rate
        params['reverse'] = str(self.reverse)
        return json.dumps(params)


AVAILABLE_TRANSFORMS = {
    'flash': FlashTransform,
    'scroll': ScrollTransform,
}