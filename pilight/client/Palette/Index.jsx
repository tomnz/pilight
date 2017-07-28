import PropTypes from 'prop-types';
import React from 'react';
import {
    Button,
    Col,
    Form,
    FormGroup,
    Grid,
    Radio,
    Row,
} from 'react-bootstrap';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux';

import {fillAsync, setColor, setOpacity, setRadius, setTool} from '../store/palette';
import * as types from '../types';

import {ColorPicker} from '../Components/ColorPicker';
import {Slider} from '../Components/Slider';


class Palette extends React.Component {
    static propTypes = {
        color: types.Color.isRequired,
        fillAsync: PropTypes.func.isRequired,
        opacity: PropTypes.number.isRequired,
        radius: PropTypes.number.isRequired,
        setOpacity: PropTypes.func.isRequired,
        setRadius: PropTypes.func.isRequired,
        setTool: PropTypes.func.isRequired,
    };

    setTool = (name) => () => {
        this.props.setTool(name);
    };

    render() {
        return (
            <Grid>
                <Row>
                    <Col md={12}>
                        <h3>Base Colors</h3>
                        <p className="hidden-xs">
                            <small>
                                Specify what base colors are applied to each LED, prior to
                                transforms taking effect. Use the Solid/Smooth tool and pick
                                a color, then click on an LED.
                            </small>
                        </p>
                    </Col>
                </Row>
                <Row>
                    <Col md={12}>
                        <Form inline>
                            <FormGroup>
                                <Radio
                                    inline
                                    onChange={this.setTool('solid')}
                                    checked={this.props.tool === 'solid'}
                                >
                                    Solid
                                </Radio>
                                {' '}
                                <Radio
                                    inline
                                    onChange={this.setTool('smooth')}
                                    checked={this.props.tool === 'smooth'}
                                >
                                    Smooth
                                </Radio>
                            </FormGroup>
                            &nbsp;&nbsp;&nbsp;&nbsp;
                            <Slider
                                id="radius"
                                label="Radius"
                                min={1}
                                max={8}
                                onChange={this.props.setRadius}
                                value={this.props.radius}
                            />
                            {' '}
                            <Slider
                                id="opacity"
                                label="Opacity"
                                min={1}
                                max={100}
                                onChange={this.props.setOpacity}
                                value={this.props.opacity}
                            />
                            &nbsp;&nbsp;&nbsp;
                            <ColorPicker
                                color={this.props.color}
                                onChange={this.props.setColor}
                            />
                            {' '}
                            <Button onClick={this.props.fillAsync}>Fill</Button>
                        </Form>
                    </Col>
                </Row>
            </Grid>
        );
    }
}

const mapStateToProps = (state) => {
    const {palette} = state;
    return {
        color: palette.color,
        opacity: palette.opacity,
        radius: palette.radius,
        tool: palette.tool,
    }
};

const mapDispatchToProps = (dispatch) => {
    return bindActionCreators({
        fillAsync,
        setColor,
        setOpacity,
        setRadius,
        setTool,
    }, dispatch);
};

const PaletteRedux = connect(mapStateToProps, mapDispatchToProps)(Palette);

export default PaletteRedux;
