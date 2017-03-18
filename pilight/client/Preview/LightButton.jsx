import React, {PropTypes} from 'react';
import {
    Button,
} from 'react-bootstrap';

import css from './LightButton.scss';


export const LightButton = ({color, id, onClick}) => {
    const colorString = `rgb(${Math.round(color.r*255)}, ${Math.round(color.g*255)}, ${Math.round(color.b*255)})`;
    return (
        <Button
            className={css.button}
            key={id}
            onClick={onClick}
            style={{backgroundColor: colorString}}
        >
            {id}
        </Button>
    );
};

LightButton.propTypes = {
    color: PropTypes.shape({
        r: PropTypes.number,
        g: PropTypes.number,
        b: PropTypes.number,
    }).isRequired,
    id: PropTypes.number.isRequired,
    onClick: PropTypes.func,
};
