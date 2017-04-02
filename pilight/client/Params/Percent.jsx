import React, {PropTypes} from 'react';
import {FormControl, FormGroup} from 'react-bootstrap';

import {Slider} from '../Components/Slider';


const Percent = ({onChange, value}) => {
    const onChangeEvent = (newValue) => {
        onChange(parseFloat(newValue) / 100.0);
    };

    return (
        <Slider
            min={0}
            max={100}
            onChange={onChangeEvent}
            value={parseInt(value * 100)}
        />
    );
};

Percent.propTypes = {
    onChange: PropTypes.func.isRequired,
    value: PropTypes.number.isRequired,
};

export {Percent};
