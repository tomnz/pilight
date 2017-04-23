import PropTypes from 'prop-types';
import React from 'react';

import * as types from '../types';

import {ColorPicker} from '../Components/ColorPicker';


const Color = ({onChange,  value}) => {
    return (
        <ColorPicker
            bsSize="xsmall"
            color={value}
            onChange={onChange}
        />
    );
};

Color.propTypes = {
    onChange: PropTypes.func.isRequired,
    value: types.Color.isRequired,
};

export {Color};
