import PropTypes from 'prop-types';
import React from 'react';
import {Button, ButtonGroup, FormControl, Table} from 'react-bootstrap';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux';

import {
    addConfig,
    deleteConfig,
    deletePlaylistAsync,
    moveConfigDown,
    moveConfigUp,
    savePlaylistAsync,
    setConfig,
    setConfigDuration,
    setDescription,
    setName,
    startPlaylistAsync,
} from '../store/playlist';
import {Playlist as PlaylistType} from '../types';

import {Float} from '../Params/Float';
import {String} from '../Params/String';


class Editor extends React.Component {
    static propTypes = {
        addConfig: PropTypes.func.isRequired,
        deleteConfig: PropTypes.func.isRequired,
        deletePlaylistAsync: PropTypes.func.isRequired,
        configs: PropTypes.arrayOf(
            PropTypes.shape({
                id: PropTypes.number,
                name: PropTypes.string,
            }).isRequired,
        ),
        moveConfigDown: PropTypes.func.isRequired,
        moveConfigUp: PropTypes.func.isRequired,
        playlist: PlaylistType.isRequired,
        setConfig: PropTypes.func.isRequired,
        setConfigDuration: PropTypes.func.isRequired,
        setDescription: PropTypes.func.isRequired,
        setName: PropTypes.func.isRequired,
        startPlaylistAsync: PropTypes.func.isRequired,
    };

    onConfigChange = (index) => (event) => {
        const configId = event.target.value;
        if (configId) {
            this.props.setConfig(index, parseInt(event.target.value, 10));
        } else {
            this.props.setConfig(index, null);
        }
    };

    onDurationChange = (index) => (duration) => {
        this.props.setConfigDuration(index, duration);
    };

    deleteConfig = (index) => () => {
        this.props.deleteConfig(index);
    };

    moveConfigDown = (index) => () => {
        this.props.moveConfigDown(index);
    };

    moveConfigUp = (index) => () => {
        this.props.moveConfigUp(index);
    };

    startPlaylist = (id) => () => {
        this.props.startPlaylistAsync(id);
    };

    render() {
        const availableConfigs = this.props.configs.map((config) => {
            return (
                <option key={config.id} value={config.id.toString()}>
                    {config.name}
                </option>
            );
        });

        const configRows = this.props.playlist.configs ? this.props.playlist.configs.map((config, index) => {
            return (
                <tr key={[index, this.props.playlist.configs.length]}>
                    <td>
                        <FormControl
                            bsSize="small"
                            componentClass="select"
                            onChange={this.onConfigChange(index)}
                            value={config.configId || ''}
                        >
                            <option value="">Config</option>
                            {availableConfigs}
                        </FormControl>
                    </td>
                    <td>
                        <Float
                            onChange={this.onDurationChange(index)}
                            value={config.duration}
                            origValue={config.duration}
                        />
                    </td>
                    <td>
                        <Button
                            bsSize="xsmall"
                            bsStyle="danger"
                            onClick={this.deleteConfig(index)}
                        >
                            Delete
                        </Button>
                        &nbsp;&nbsp;&nbsp;&nbsp;
                        <ButtonGroup>
                            <Button onClick={this.moveConfigUp(index)} bsSize="xsmall">Up</Button>
                            <Button onClick={this.moveConfigDown(index)} bsSize="xsmall">Down</Button>
                        </ButtonGroup>
                    </td>
                </tr>
            );
        }) : [];

        return (
            <Table bordered striped>
                <thead>
                    <tr>
                        <th>
                            Name
                            <String
                                onChange={this.props.setName}
                                value={this.props.playlist.name}
                                origValue={this.props.playlist.name}
                            />
                        </th>
                        <th>
                            Description
                            <String
                                onChange={this.props.setDescription}
                                value={this.props.playlist.description}
                                origValue={this.props.playlist.description}
                            />
                        </th>
                        <th>
                            <Button onClick={this.props.savePlaylistAsync} bsStyle="success" bsSize="small">
                                Save
                            </Button>
                            {' '}
                            <Button onClick={this.props.deletePlaylistAsync} bsStyle="danger" bsSize="small">
                                Delete
                            </Button>
                            {' '}
                            <Button onClick={this.startPlaylist(this.props.playlist.id)} bsStyle="success" bsSize="small">
                                Play
                            </Button>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {configRows}
                    <tr>
                        <td colSpan="3">
                            <Button
                                bsSize="xsmall"
                                bsStyle="primary"
                                onClick={this.props.addConfig}
                            >
                                Add Config
                            </Button>
                        </td>
                    </tr>
                </tbody>
            </Table>
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
        addConfig,
        deleteConfig,
        deletePlaylistAsync,
        moveConfigDown,
        moveConfigUp,
        savePlaylistAsync,
        setConfig,
        setConfigDuration,
        setDescription,
        setName,
        startPlaylistAsync,
    }, dispatch);
};

const EditorRedux = connect(mapStateToProps, mapDispatchToProps)(Editor);
export {EditorRedux as Editor};
