import PropTypes from 'prop-types';
import React from 'react';

import {Slider} from '../Components/Slider';


export const Percent = ({onChange, value}) => {
    const onChangeEvent = (newValue) => {
        onChange(parseFloat(newValue) / 100.0);
    };

    return (
        <Slider
            min={0}
            max={100}
            onChange={onChangeEvent}
            value={parseInt(value * 100, 10)}
        />
    );
};

Percent.propTypes = {
    onChange: PropTypes.func.isRequired,
    value: PropTypes.number.isRequired,
};
