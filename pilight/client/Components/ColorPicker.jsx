import React, {PropTypes} from 'react';
import {Button, FormGroup} from 'react-bootstrap';
import {SketchPicker} from 'react-color';
import {connect} from 'react-redux';

import {setColor} from '../store/palette';

import css from './ColorPicker.scss';


class ColorPicker extends React.Component {
    state = {
        displayColorPicker: false,
    };

    togglePicker = () => {
        this.setState({displayColorPicker: !this.state.displayColorPicker})
    };

    closePicker = () => {
        this.setState({displayColorPicker: false})
    };

    onChangeComplete = (color) => {
        const rgb = color.rgb;
        this.props.dispatch(setColor({
            r: rgb.r / 255,
            g: rgb.g / 255,
            b: rgb.b / 255,
            a: rgb.a,
        }));
    };

    render() {
        const pickerColor = !!this.props.color ? {
                r: this.props.color.r * 255,
                g: this.props.color.g * 255,
                b: this.props.color.b * 255,
                a: this.props.color.a,
            } : {r: 0, g: 0, b: 0};
        const colorString = `rgb(${Math.round(pickerColor.r)}, ${Math.round(pickerColor.g)}, ${Math.round(pickerColor.b)})`;

        return (
            <FormGroup>
                <Button
                    onClick={this.togglePicker}
                    style={{backgroundColor: colorString}}
                >
                    <span className={css.swatchText}>Color</span>
                </Button>
                {this.state.displayColorPicker ?
                    <div className={css.popover}>
                        <div className={css.cover} onClick={this.closePicker}/>
                        <SketchPicker
                            color={pickerColor}
                            onChangeComplete={this.onChangeComplete}
                            disableAlpha={true}
                        />
                    </div> : null}
            </FormGroup>
        )
    }
}

ColorPicker.propTypes = {
    color: PropTypes.shape({
        r: PropTypes.number,
        g: PropTypes.number,
        b: PropTypes.number,
    })
};

const mapStateToProps = (state) => {
    const {palette} = state;
    return {
        color: palette.color,
    }
};
const ColorPickerRedux = connect(mapStateToProps)(ColorPicker);

export {ColorPickerRedux as ColorPicker};
