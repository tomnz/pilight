import React, {PropTypes} from 'react';
import {Checkbox} from 'react-bootstrap';

import css from './common.scss';


const Boolean = ({onChange,  value}) => {
    const onChangeEvent = (event) => {
        onChange(event.target.checked);
    };

    return (
        <Checkbox
            checked={value}
            className={css.formGroup}
            onChange={onChangeEvent}
        />
    );
};

Boolean.propTypes = {
    onChange: PropTypes.func.isRequired,
    value: PropTypes.bool.isRequired,
};

export {Boolean};
