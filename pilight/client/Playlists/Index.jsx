import PropTypes from 'prop-types';
import React from 'react';
import {
    Button,
    Col,
    Form,
    Grid,
    Panel,
    Row,
} from 'react-bootstrap';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux';

import {newPlaylist} from '../store/playlist';
import {Playlist as PlaylistType} from '../types';

import {Editor} from './Editor';


class Playlist extends React.Component {
    static propTypes = {
        currentPlaylist: PlaylistType,
        newPlaylist: PropTypes.func.isRequired,
        playlists: PropTypes.arrayOf(PropTypes.shape({
            id: PropTypes.number,
            name: PropTypes.string,
            description: PropTypes.string,
        })),
    };

    render() {
        return (
            <Grid>
                <Row>
                    <Col>
                        <Panel>
                            <Form inline>
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
        newPlaylist,
    }, dispatch);
};

const PlaylistRedux = connect(mapStateToProps, mapDispatchToProps)(Playlist);
export default PlaylistRedux;
