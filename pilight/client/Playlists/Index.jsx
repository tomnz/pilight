import PropTypes from 'prop-types';
import React from 'react';
import {
    Button,
    Col,
    Form,
    FormControl,
    Grid,
    Panel,
    Row,
} from 'react-bootstrap';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux';

import {getPlaylistAsync, newPlaylist, resetPlaylist} from '../store/playlist';
import {Playlist as PlaylistType} from '../types';

import {Editor} from './Editor';

import css from './Index.scss';


class Playlists extends React.Component {
    static propTypes = {
        getPlaylistAsync: PropTypes.func.isRequired,
        currentPlaylist: PlaylistType,
        newPlaylist: PropTypes.func.isRequired,
        playlists: PropTypes.arrayOf(PropTypes.shape({
            id: PropTypes.number,
            name: PropTypes.string,
            description: PropTypes.string,
        })),
        resetPlaylist: PropTypes.func.isRequired,
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
            <Grid>
                <Row>
                    <Col>
                        <Panel>
                            <Form inline>
                                <FormControl
                                    bsSize="small"
                                    className={css.controlWidth}
                                    componentClass="select"
                                    onChange={this.onPlaylistSelect}
                                    value={this.props.currentPlaylist && this.props.currentPlaylist.id ?
                                        this.props.currentPlaylist.id.toString() : ''}
                                >
                                    <option value="">Load</option>
                                    {playlistOptions}
                                </FormControl>
                                {' '}
                                <Button
                                    bsStyle="success"
                                    bsSize="small"
                                    onClick={this.props.newPlaylist}
                                >
                                    New
                                </Button>
                            </Form>
                        </Panel>
                    </Col>
                </Row>
                {this.props.currentPlaylist &&
                    <Row>
                        <Col>
                            <Editor playlist={this.props.currentPlaylist} />
                        </Col>
                    </Row>
                }
            </Grid>
        );
    }
}

const mapStateToProps = (state) => {
    const {client, playlist} = state;
    return {
        playlists: client.playlists,
        currentPlaylist: playlist.current,
    }
};

const mapDispatchToProps = (dispatch) => {
    return bindActionCreators({
        getPlaylistAsync,
        newPlaylist,
        resetPlaylist,
    }, dispatch);
};

const PlaylistsRedux = connect(mapStateToProps, mapDispatchToProps)(Playlists);
export default PlaylistsRedux;
