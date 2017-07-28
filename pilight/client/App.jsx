import PropTypes from 'prop-types';
import React from 'react';
import {
    Alert,
    Nav,
    Navbar,
    NavItem,
    Tab,
} from 'react-bootstrap';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux';

import {loginAsync} from './store/auth';
import {Status} from './store/async';
import {clearError} from './store/client';
import {bootstrapClientAsync} from './store/root';

import {AlertBar} from './AlertBar';
import Header from './Header';
import {LoginModal} from './Header/LoginModal';
import Lights from './Lights';
import Palette from './Palette';
import Playlists from './Playlists';
import Transforms from './Transforms';
import Variables from './Variables';

import css from './App.scss';


class App extends React.Component {
    static propTypes = {
        authRequired: PropTypes.bool,
        bootstrapStatus: PropTypes.string.isRequired,
        bootstrapClientAsync: PropTypes.func,
        errorMessage: PropTypes.string,
        clearError: PropTypes.func,
        loggedIn: PropTypes.bool,
        loginAsync: PropTypes.func,
    };

    constructor(props) {
        super(props);
        props.bootstrapClientAsync();
    }

    closeLogin = () => {
        this.props.bootstrapClientAsync();
    };

    render() {
        if (this.props.bootstrapStatus !== Status.DONE) {
            return (
                <Alert bsStyle="info">
                    Loading, please wait...
                </Alert>
            );
        }

        if (this.props.authRequired && !this.props.loggedIn) {
            return (
                <LoginModal
                    close={this.closeLogin}
                    loginAsync={this.props.loginAsync}
                    visible={true}
                />
            )
        }

        return (
            <div>
                <AlertBar
                    style="warning"
                    onDismiss={this.props.clearError}
                    message={this.props.errorMessage}
                />
                <Header />
                <div className={css.bodyContainer}>
                    <Tab.Container id="subnav" defaultActiveKey="lights">
                        <div>
                            <Navbar staticTop>
                                <Nav>
                                    <NavItem eventKey="lights">Lights</NavItem>
                                    <NavItem eventKey="playlists">Playlists</NavItem>
                                    <NavItem eventKey="variables">Variables</NavItem>
                                </Nav>
                            </Navbar>
                            <Tab.Content animation>
                                <Tab.Pane eventKey="lights">
                                    <Palette />
                                    <Lights />
                                    <Transforms />
                                </Tab.Pane>
                                <Tab.Pane eventKey="playlists">
                                    <Playlists />
                                </Tab.Pane>
                                <Tab.Pane eventKey="variables">
                                    <Variables />
                                </Tab.Pane>
                            </Tab.Content>
                        </div>
                    </Tab.Container>
                </div>
            </div>
        );
    }
}

const mapStateToProps = (state) => {
    const {auth, client} = state;
    return {
        authRequired: auth.authRequired,
        bootstrapStatus: client.bootstrapStatus,
        errorMessage: client.errorMessage,
        loggedIn: auth.loggedIn,
    }
};

const mapDispatchToProps = (dispatch) => {
    return bindActionCreators({
        bootstrapClientAsync,
        clearError,
        loginAsync,
    }, dispatch);
};

const AppRedux = connect(mapStateToProps, mapDispatchToProps)(App);

export {AppRedux as App};
