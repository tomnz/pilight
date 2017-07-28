import PropTypes from 'prop-types';
import React from 'react';
import {
    Button,
    Form,
    FormControl,
    Modal,
    Table,
} from 'react-bootstrap';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux';

import {
    deleteConfigAsync,
    loadConfigAsync,
    saveConfigAsync,
} from '../../store/client';

import css from './Index.scss';


class Config extends React.Component {
    static propTypes = {
        configs: PropTypes.arrayOf(
            PropTypes.shape({
                id: PropTypes.number.isRequired,
                name: PropTypes.string.isRequired,
            }).isRequired,
        ).isRequired,
        deleteConfigAsync: PropTypes.func.isRequired,
        hide: PropTypes.func.isRequired,
        loadConfigAsync: PropTypes.func.isRequired,
        saveConfigAsync: PropTypes.func.isRequired,
        visible: PropTypes.bool.isRequired,
    };

    state = {
        configName: '',
    };

    onConfigNameChange = (event) => {
        this.setState({
            configName: event.target.value,
        })
    };

    loadConfig = (id) => () => {
        this.props.loadConfigAsync(id);
    };

    saveConfig = () => {
        this.props.saveConfigAsync(this.state.configName);
    };

    deleteConfig = (id) => () => {
        this.props.deleteConfigAsync(id)
    };

    render() {
        const configs = this.props.configs.map((config) => {
            return (
                <tr key={config.id}>
                    <td>{config.name}</td>
                    <td>
                        <Button
                            bsStyle="danger"
                            bsSize="xs"
                            onClick={this.deleteConfig(config.id)}
                        >
                            Delete
                        </Button>
                        &nbsp;&nbsp;
                        <Button
                            bsStyle="primary"
                            bsSize="xs"
                            onClick={this.loadConfig(config.id)}
                        >
                            Load
                        </Button>
                    </td>
                </tr>
            );
        });

        return (
            <Modal show={this.props.visible} onHide={this.props.hide}>
                <Modal.Header closeButton>
                    <Modal.Title>Configs</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <p><small>Specify the same name as an existing config to overwrite.</small></p>
                    <Form inline className={css.saveControls}>
                        <FormControl
                            onChange={this.onConfigNameChange}
                            placeholder="Save as..."
                            value={this.state.configName}
                        />
                        {' '}
                        <Button
                            bsStyle="primary"
                            disabled={!this.state.configName}
                            onClick={this.saveConfig}
                        >
                            Save
                        </Button>
                    </Form>
                    <Table bordered striped condensed>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>&nbsp;</th>
                            </tr>
                        </thead>
                        <tbody>
                            {configs}
                        </tbody>
                    </Table>
                </Modal.Body>
            </Modal>
        );
    }
}

const mapStateToProps = (state) => {
    const {client} = state;
    return {
        configs: client.configs,
    }
};

const mapDispatchToProps = (dispatch) => {
    return bindActionCreators({
        deleteConfigAsync,
        loadConfigAsync,
        saveConfigAsync,
    }, dispatch);
};

const ConfigRedux = connect(mapStateToProps, mapDispatchToProps)(Config);

export default ConfigRedux;
