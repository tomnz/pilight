import React, {PropTypes} from 'react';
import {
    Button,
    Col,
    Grid,
    Row
} from 'react-bootstrap';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux';

import {loginAsync, logoutAsync} from '../store/auth';

import {Controls} from './Controls';
import {LoginModal} from './LoginModal';

import css from './Index.scss';


class Header extends React.Component {
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
                    bsSize="xs"
                    onClick={this.props.logoutAsync}
                >
                    Logout
                </Button>
            ) : (
                <Button
                    bsSize="xs"
                    onClick={this.showLogin}
                >
                    Login
                </Button>
            );

        return (
            <Grid className={css.wrapper}>
                <Row>
                    <Col xs={12} md={6}>
                        <h1>PiLight&nbsp;&nbsp;
                            {authButton}
                        </h1>
                    </Col>
                    <Controls />
                    <LoginModal
                        close={this.closeLogin}
                        loginAsync={this.props.loginAsync}
                        visible={this.state.loginVisible}
                    />
                </Row>
            </Grid>
        );
    }
}

Header.propTypes = {
    loggedIn: PropTypes.bool.isRequired,
    loginAsync: PropTypes.func.isRequired,
    logoutAsync: PropTypes.func.isRequired,
};

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

export {HeaderRedux as Header};
