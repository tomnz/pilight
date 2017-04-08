import React, {PropTypes} from 'react';
import {FormControl, FormGroup} from 'react-bootstrap';

import css from './common.scss';


const String = ({onChange, origValue, value}) => {
    const onChangeEvent = (event) => {
        onChange(event.target.value);
    };

    const edited = value !== origValue;

    return (
        <FormGroup
            className={css.formGroup}
            validationState={edited ? 'success' : null}
        >
            <FormControl
                bsSize="small"
                className={css.controlWidth}
                onChange={onChangeEvent}
                type="text"
                value={value}
            />
        </FormGroup>
    );
};

String.propTypes = {
    onChange: PropTypes.func.isRequired,
    origValue: PropTypes.string.isRequired,
    value: PropTypes.string.isRequired,
};

export {String};
