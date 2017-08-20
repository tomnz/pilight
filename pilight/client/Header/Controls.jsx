import PropTypes from 'prop-types';
import React from 'react';
import {
    Button,
    ButtonGroup,
    FormControl,
    Navbar,
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
import {resetPlaylist, getPlaylistAsync} from '../store/playlist';

import Config from './Config';

import css from './Controls.scss';


class Controls extends React.Component {
    static propTypes = {
        configs: PropTypes.arrayOf(
            PropTypes.shape({
                id: PropTypes.number.isRequired,
                name: PropTypes.string.isRequired,
            }).isRequired,
        ).isRequired,
        doPreviewAsync: PropTypes.func.isRequired,
        getPlaylistAsync: PropTypes.func.isRequired,
        loadConfigAsync: PropTypes.func.isRequired,
        previewActive: PropTypes.bool.isRequired,
        resetPlaylist: PropTypes.func.isRequired,
        saveConfigAsync: PropTypes.func.isRequired,
        startDriverAsync: PropTypes.func.isRequired,
        stopDriverAsync: PropTypes.func.isRequired,
        currentPlaylistId: PropTypes.number,
        playlists: PropTypes.arrayOf(PropTypes.shape({
            id: PropTypes.number,
            name: PropTypes.string,
            description: PropTypes.string,
        })),
    };

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

    onPlaylistSelect = (event) => {
        const playlistId = event.target.value;
        if (playlistId) {
            this.props.getPlaylistAsync(parseInt(playlistId, 10));
        } else {
            this.props.resetPlaylist();
        }
    };

    render() {
        const playlistOptions = this.props.playlists ? this.props.playlists.map((playlist) => {
            return (
                <option key={playlist.id} value={playlist.id.toString()}>
                    {playlist.name}
                </option>
            );
        }) : [];

        return (
            <Navbar.Form pullRight>
                <Button bsStyle="default" onClick={this.showConfig}>Configs</Button>
                {' '}
                <FormControl
                    className={css.playlistDropdown}
                    componentClass="select"
                    onChange={this.onPlaylistSelect}
                    value={this.props.currentPlaylistId ? this.props.currentPlaylistId.toString() : ''}
                >
                    <option value="">Current</option>
                    {playlistOptions}
                </FormControl>
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

const mapStateToProps = (state) => {
    const {client, lights, playlist} = state;
    return {
        configs: client.configs,
        currentPlaylistId: playlist.currentId,
        playlists: client.playlists,
        previewActive: !!lights.previewFrames,
    }
};

const mapDispatchToProps = (dispatch) => {
    return bindActionCreators({
        doPreviewAsync,
        getPlaylistAsync,
        loadConfigAsync,
        resetPlaylist,
        saveConfigAsync,
        startDriverAsync,
        stopDriverAsync,
    }, dispatch);
};

const ControlsRedux = connect(mapStateToProps, mapDispatchToProps)(Controls);

export {ControlsRedux as Controls};
