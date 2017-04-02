import React, {PropTypes} from 'react';

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
    value: PropTypes.shape({
        r: PropTypes.number.isRequired,
        g: PropTypes.number.isRequired,
        b: PropTypes.number.isRequired,
        a: PropTypes.number,
    }).isRequired,
};

export {Color};
