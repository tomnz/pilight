import PropTypes from 'prop-types';
import React from 'react';
import {Alert, Button} from 'react-bootstrap';

import css from './AlertBar.scss';


export const AlertBar = ({message, style, onDismiss}) => {
    if (!message || message === "") {
        return <div></div>;
    }
    return (
        <div className={css.topBar}>
            <Alert
                className={css.paddingWrapper}
                bsStyle={!!style ? style : 'info'}
            >
                {!!onDismiss ?
                    <Button onClick={onDismiss}>&times;</Button>
                    : null}
                <span className={css.message}>
                    {message}
                </span>
            </Alert>
        </div>
    );
};

AlertBar.propTypes = {
    message: PropTypes.string,
    style: PropTypes.string,
    onDismiss: PropTypes.func,
};
