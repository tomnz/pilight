import React, {PropTypes} from 'react';
import {
    ControlLabel,
    FormGroup,
} from 'react-bootstrap';
import {ReactBootstrapSlider} from 'react-bootstrap-slider';


export class Slider extends React.Component {
    onChange = (event) => {
        if (!!this.props.onChange) {
            this.props.onChange(event.target.value);
        }
    };

   render() {
        return (
            <FormGroup>
                <ControlLabel>{this.props.label}</ControlLabel><br />
                <ReactBootstrapSlider
                    min={0}
                    max={30}
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
