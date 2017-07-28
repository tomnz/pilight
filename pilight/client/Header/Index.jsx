import PropTypes from 'prop-types';
import React from 'react';
import {
    Button,
    Navbar,
} from 'react-bootstrap';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux';

import {loginAsync, logoutAsync} from '../store/auth';

import {Controls} from './Controls';
import {LoginModal} from './LoginModal';


class Header extends React.Component {
    static propTypes = {
        loggedIn: PropTypes.bool.isRequired,
        loginAsync: PropTypes.func.isRequired,
        logoutAsync: PropTypes.func.isRequired,
    };

    state = {
        loginVisible: false,
    };

    closeLogin = () => {
        this.setState({
            loginVisible: false,
        });
    };

    showLogin = () => {
        this.setState({
            loginVisible: true,
        });
    };

    render() {
        const authButton = this.props.loggedIn ? (
                <Button
                    onClick={this.props.logoutAsync}
                >
                    Logout
                </Button>
            ) : (
                <Button
                    onClick={this.showLogin}
                >
                    Login
                </Button>
            );

        return (
            <Navbar inverse collapseOnSelect fixedTop>
                <Navbar.Header>
                    <Navbar.Brand>PiLight</Navbar.Brand>
                    <Navbar.Toggle />
                </Navbar.Header>
                <Navbar.Collapse>
                    <Navbar.Form pullLeft>
                            {authButton}
                    </Navbar.Form>
                    <Controls />
                </Navbar.Collapse>
                <LoginModal
                    close={this.closeLogin}
                    loginAsync={this.props.loginAsync}
                    visible={this.state.loginVisible}
                />
            </Navbar>
        );
    }
}

const mapStateToProps = (state) => {
    const {auth} = state;
    return {
        loggedIn: auth.loggedIn,
    }
};

const mapDispatchToProps = (dispatch) => {
    return bindActionCreators({
        loginAsync,
        logoutAsync,
    }, dispatch);
};

const HeaderRedux = connect(mapStateToProps, mapDispatchToProps)(Header);

export default HeaderRedux;
