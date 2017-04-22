import React, {PropTypes} from 'react';
import {
    Button,
    ButtonGroup,
    DropdownButton,
    FormControl,
    InputGroup,
    MenuItem,
    Nav,
    Navbar,
    NavItem,
} from 'react-bootstrap';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux';

import {
    loadConfigAsync,
    saveConfigAsync,
    startDriverAsync,
    stopDriverAsync,
} from '../store/client';
import {doPreviewAsync} from '../store/lights';

import {Config} from './Config/Index';


class Controls extends React.Component {
    state = {
        configVisible: false,
    };

    hideConfig = () => {
        this.setState({
            configVisible: false,
        });
    };

    showConfig = () => {
        this.setState({
            configVisible: true,
        });
    };

    render() {
        return (
            <Navbar.Form pullRight>
                <Button bsStyle="default" onClick={this.showConfig}>Configs</Button>
                {' '}
                <ButtonGroup>
                    <Button bsStyle="success" onClick={this.props.startDriverAsync}>Start</Button>
                    <Button bsStyle="danger" onClick={this.props.stopDriverAsync}>Stop</Button>
                </ButtonGroup>
                {' '}
                <Button
                    bsStyle="info"
                    disabled={this.props.previewActive}
                    onClick={this.props.doPreviewAsync}
                >Preview</Button>
                <Config
                    hide={this.hideConfig}
                    visible={this.state.configVisible}
                />
            </Navbar.Form>
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
        saveConfigAsync,
        startDriverAsync,
        stopDriverAsync,
    }, dispatch);
};

const ControlsRedux = connect(mapStateToProps, mapDispatchToProps)(Controls);

export {ControlsRedux as Controls};
