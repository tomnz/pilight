import PropTypes from 'prop-types';
import React from 'react';
import {
    Alert,
    Button,
    ControlLabel,
    Form,
    FormControl,
    FormGroup,
    Modal,
} from 'react-bootstrap';


class LoginModal extends React.Component {
    state = {
        username: '',
        password: '',
        failed: false,
    };

    onUsernameChange = (event) => {
        this.setState({
            username: event.target.value,
            failed: false,
        });
    };

    onPasswordChange = (event) => {
        this.setState({
            password: event.target.value,
            failed: false,
        });
    };

    login = () => {
        this.props.loginAsync(
            this.state.username,
            this.state.password,
        ).then((data) => {
            if (data.loggedIn) {
                this.setState({
                    failed: false,
                });
                this.props.close();
            } else {
                this.setState({
                    failed: true,
                });
            }
        });
    };

    render() {
        const failedAlert = this.state.failed ? (
                <Alert bsStyle="danger">Login failed! Try again...</Alert>
            ) : null;

        return (
            <Modal show={this.props.visible} onHide={this.props.close}>
                <Modal.Header closeButton>
                    <Modal.Title>Login</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {failedAlert}
                    <Form>
                        <FormGroup>
                            <ControlLabel>Username</ControlLabel>
                            <FormControl
                                onChange={this.onUsernameChange}
                                placeholder="Username"
                                type="text"
                                value={this.state.username}
                            />
                        </FormGroup>
                        <FormGroup>
                            <ControlLabel>Password</ControlLabel>
                            <FormControl
                                onChange={this.onPasswordChange}
                                placeholder="Password"
                                type="password"
                                value={this.state.password}
                            />
                        </FormGroup>
                        <Button
                            bsStyle="primary"
                            onClick={this.login}
                        >
                            Login
                        </Button>
                    </Form>
                </Modal.Body>
            </Modal>
        );
    }
}

LoginModal.propTypes = {
    close: PropTypes.func.isRequired,
    loginAsync: PropTypes.func.isRequired,
    visible: PropTypes.bool.isRequired,
};

export {LoginModal};
