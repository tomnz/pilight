import React, {PropTypes} from 'react';
import {
    Alert,
    Col,
    Grid,
    Row,
} from 'react-bootstrap';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux';

import {Status} from './store/async';
import {clearError} from './store/client';
import {bootstrapClientAsync} from './store/root';

import {AlertBar} from './AlertBar';
import {Header} from './Header/Index';
import {Palette} from './Palette/Index';
import {Preview} from './Preview/Index';
import {Transforms} from './Transforms/Index';


class App extends React.Component {
    constructor(props) {
        super(props);
        props.bootstrapClientAsync();
    }

    render() {
        if (this.props.bootstrapStatus !== Status.VALID) {
            return (
                <Alert bsStyle="info">
                    Loading, please wait...
                </Alert>
            );
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
    bootstrapStatus: PropTypes.string.isRequired,
    errorMessage: PropTypes.string,
    clearError: PropTypes.func,
};

const mapStateToProps = (state) => {
    const {client} = state;
    return {
        bootstrapStatus: client.bootstrapStatus,
        errorMessage: client.errorMessage,
    }
};

const mapDispatchToProps = (dispatch) => {
    return bindActionCreators({
        bootstrapClientAsync,
        clearError,
    }, dispatch);
};

const AppRedux = connect(mapStateToProps, mapDispatchToProps)(App);

export {AppRedux as App};
