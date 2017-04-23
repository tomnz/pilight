import PropTypes from 'prop-types';
import React from 'react';
import {
    ControlLabel,
    FormGroup,
} from 'react-bootstrap';
import {ReactBootstrapSlider} from 'react-bootstrap-slider';

import css from './Slider.scss';


export class Slider extends React.Component {
    onChange = (event) => {
        if (!!this.props.onChange) {
            this.props.onChange(event.target.value);
        }
    };

    render() {
        const label = !!this.props.label && <ControlLabel className={css.label}>{this.props.label}</ControlLabel>;
        return (
            <FormGroup className={css.wrapper}>
                {label}
                <ReactBootstrapSlider
                    min={this.props.min}
                    max={this.props.max}
                    slideStop={this.onChange}
                    value={this.props.value}
                />
            </FormGroup>
        );
    }
}

Slider.propTypes = {
    label: PropTypes.string,
    min: PropTypes.number.isRequired,
    max: PropTypes.number.isRequired,
    value: PropTypes.number.isRequired,
    onChange: PropTypes.func,
};
