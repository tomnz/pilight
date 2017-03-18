import React, {PropTypes} from 'react';
import {
    Button,
    ButtonGroup,
    Col,
    DropdownButton,
    FormControl,
    Grid,
    InputGroup,
    ListGroup,
    ListGroupItem,
    MenuItem,
    Panel,
    Row
} from 'react-bootstrap';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux';

import {loadConfigAsync, saveConfigAsync} from '../store/client';


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
            <Panel>
                <ListGroup fill>
                    <ListGroupItem>
                        <ButtonGroup>
                            <Button bsStyle="success">Start</Button>
                            <Button bsStyle="danger">Stop</Button>
                            <Button bsStyle="primary">Refresh</Button>
                        </ButtonGroup>
                        &nbsp;
                        <Button bsStyle="info">Preview</Button>
                    </ListGroupItem>
                    <ListGroupItem>
                        <InputGroup>
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
                    </ListGroupItem>
                </ListGroup>
            </Panel>
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
    loadConfigAsync: PropTypes.func.isRequired,
    saveConfigAsync: PropTypes.func.isRequired,
};

const mapStateToProps = (state) => {
    const {client} = state;
    return {
        configs: client.configs,
    }
};

const mapDispatchToProps = (dispatch) => {
    return bindActionCreators({
        loadConfigAsync,
        saveConfigAsync,
    }, dispatch);
};

const ControlsRedux = connect(mapStateToProps, mapDispatchToProps)(Controls);

export {ControlsRedux as Controls};
