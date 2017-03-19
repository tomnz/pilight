import React, {PropTypes} from 'react';
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
        return (
            <FormGroup className={css.wrapper}>
                <ControlLabel>{this.props.label}</ControlLabel>
                &nbsp;&nbsp;
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
    min: PropTypes.number,
    max: PropTypes.number,
    value: PropTypes.number,
    onChange: PropTypes.func,
};
