import React, {PropTypes} from 'react';
import {
    Alert,
    Col,
    Grid,
    Row,
} from 'react-bootstrap';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux';

import {loginAsync} from './store/auth';
import {Status} from './store/async';
import {clearError} from './store/client';
import {bootstrapClientAsync} from './store/root';

import {AlertBar} from './AlertBar';
import {Header} from './Header/Index';
import {LoginModal} from './Header/LoginModal';
import {Palette} from './Palette/Index';
import {Preview} from './Preview/Index';
import {Transforms} from './Transforms/Index';


class App extends React.Component {
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
                <Palette />
                <Preview />
                <Transforms />
            </div>
        );
    }
}

App.propTypes = {
    authRequired: PropTypes.bool,
    bootstrapStatus: PropTypes.string.isRequired,
    bootstrapClientAsync: PropTypes.func,
    errorMessage: PropTypes.string,
    clearError: PropTypes.func,
    loggedIn: PropTypes.bool,
    loginAsync: PropTypes.func,
};

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
