import React, {PropTypes} from 'react';
import {Button} from 'react-bootstrap';
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
        this.props.dispatch(setColor(color.rgb));
    };

    render() {
        const color = !!this.props.color ? this.props.color : {r: 0, g: 0, b: 0};
        const colorString = `rgb(${Math.round(color.r*255)}, ${Math.round(color.g*255)}, ${Math.round(color.b*255)})`;

        return (
            <div>
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
                            color={color}
                            onChangeComplete={this.onChangeComplete}
                            disableAlpha={true}
                        />
                    </div> : null}
            </div>
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
