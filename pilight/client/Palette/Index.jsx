import React, {PropTypes} from 'react';
import {
    Button,
    ButtonGroup,
    Col,
    ControlLabel,
    Form,
    FormGroup,
    FormControl,
    Grid,
    InputGroup,
    Panel,
    Radio,
    Row,
} from 'react-bootstrap';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux';

import {fillAsync, setOpacity, setRadius, setTool} from '../store/palette';

import {ColorPicker} from '../Components/ColorPicker';
import {Slider} from '../Components/Slider';


class Palette extends React.Component {
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
                                min={0}
                                max={30}
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
                            <ColorPicker />
                            {' '}
                            <Button onClick={this.props.fillAsync}>Fill</Button>
                        </Form>
                    </Col>
                </Row>
            </Grid>
        );
    }
}

Palette.propTypes = {
    color: PropTypes.shape({
        r: PropTypes.number,
        g: PropTypes.number,
        b: PropTypes.number,
        a: PropTypes.number,
    }),
    fillAsync: PropTypes.func,
    opacity: PropTypes.number,
    radius: PropTypes.number,
    setOpacity: PropTypes.func,
    setRadius: PropTypes.func,
    setTool: PropTypes.func,
};

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
        setOpacity,
        setRadius,
        setTool,
    }, dispatch);
};

const PaletteRedux = connect(mapStateToProps, mapDispatchToProps)(Palette);

export {PaletteRedux as Palette};
