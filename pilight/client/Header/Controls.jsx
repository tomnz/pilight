import React, {PropTypes} from 'react';
import {
    Button,
    ButtonGroup,
    Col,
    DropdownButton,
    FormControl,
    Grid,
    InputGroup,
    MenuItem,
    Row
} from 'react-bootstrap';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux';

import {
    loadConfigAsync,
    restartDriverAsync,
    saveConfigAsync,
    startDriverAsync,
    stopDriverAsync,
} from '../store/client';
import {doPreviewAsync} from '../store/lights';

import css from './Controls.scss';


class Controls extends React.Component {
    state = {
        storeName: '',
    };

    onConfigNameChange = (event) => {
        this.setState({
            storeName: event.target.value,
        })
    };

    loadConfig = (id) => {
        this.props.loadConfigAsync(id);
    };

    saveConfig = () => {
        this.props.saveConfigAsync(this.state.storeName);
    };

    render() {
        const configs = this.props.configs.map((config) => {
            return (
                <MenuItem key={config.id} eventKey={config.id}>{config.name}</MenuItem>
            );
        });

        return (
            <Col xs={12} md={6} className={css.wrapper}>
                <Row>
                    <Col md={6}>
                        <InputGroup>
                            <ButtonGroup>
                                <Button bsStyle="success" onClick={this.props.startDriverAsync}>Start</Button>
                                <Button bsStyle="danger" onClick={this.props.stopDriverAsync}>Stop</Button>
                                <Button bsStyle="primary" onClick={this.props.restartDriverAsync}>Restart</Button>
                                <Button
                                    bsStyle="info"
                                    disabled={this.props.previewActive}
                                    onClick={this.props.doPreviewAsync}
                                >Preview</Button>
                            </ButtonGroup>
                        </InputGroup>
                    </Col>
                </Row>
                <Row>
                    <Col md={6}>
                        <InputGroup className={css.configLoader}>
                            <FormControl
                                bsSize="sm"
                                id="saveConfig"
                                onChange={this.onConfigNameChange}
                                placeholder="Save as..."
                                type="text"
                                value={this.state.storeName}
                            />
                            <InputGroup.Button>
                                <Button bsSize="sm" bsStyle="success" onClick={this.saveConfig}>Save</Button>
                                <DropdownButton
                                    bsSize="sm"
                                    bsStyle="primary"
                                    id="loadConfigMenu"
                                    onSelect={this.loadConfig}
                                    role="menu"
                                    title="Load"
                                >
                                    {configs}
                                </DropdownButton>
                            </InputGroup.Button>
                        </InputGroup>
                    </Col>
                </Row>
            </Col>
        );
    }
}

Controls.propTypes = {
    configs: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.number.isRequired,
            name: PropTypes.string.isRequired,
        }).isRequired,
    ).isRequired,
    doPreviewAsync: PropTypes.func.isRequired,
    loadConfigAsync: PropTypes.func.isRequired,
    previewActive: PropTypes.bool.isRequired,
    restartDriverAsync: PropTypes.func.isRequired,
    saveConfigAsync: PropTypes.func.isRequired,
    startDriverAsync: PropTypes.func.isRequired,
    stopDriverAsync: PropTypes.func.isRequired,
};

const mapStateToProps = (state) => {
    const {client, lights} = state;
    return {
        configs: client.configs,
        previewActive: !!lights.previewFrame,
    }
};

const mapDispatchToProps = (dispatch) => {
    return bindActionCreators({
        doPreviewAsync,
        loadConfigAsync,
        restartDriverAsync,
        saveConfigAsync,
        startDriverAsync,
        stopDriverAsync,
    }, dispatch);
};

const ControlsRedux = connect(mapStateToProps, mapDispatchToProps)(Controls);

export {ControlsRedux as Controls};
