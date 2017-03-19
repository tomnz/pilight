import React, {PropTypes} from 'react';
import {
    Button,
    FormControl,
    FormGroup,
    InputGroup,
} from 'react-bootstrap';

import css from './ParamEditor.scss';


export class ParamEditor extends React.Component {
    constructor(props) {
        super(props);
        const text = JSON.stringify(props.value);
        this.state = {
            text: text,
            origText: text,
            valid: true,
        }
    }

    componentWillReceiveProps(nextProps) {
        if (nextProps.value !== this.props.value) {
            // Reset the current value
            const text = JSON.stringify(nextProps.value);
            this.setState({
                text: text,
                origText: text,
                valid: true,
            });
        }
    }

    onChange = (event) => {
        // Check if input is valid
        let valid = true;
        try {
            JSON.parse(event.target.value);
        } catch (e) {
            valid = false;
        }

        this.setState({
            text: event.target.value,
            valid: valid,
        });
    };

    onSave = () => {
        this.props.onSave(
            JSON.parse(this.state.text),
        );
    };

    render() {
        const edited = this.state.text !== this.state.origText;

        return (
            <FormGroup
                className={css.formGroup}
                validationState={edited ? (this.state.valid ? 'success' : 'error') : null}
            >
                <InputGroup>
                    <FormControl
                        bsSize="sm"
                        onChange={this.onChange}
                        type="text"
                        value={this.state.text}
                    />
                    <InputGroup.Button>
                        <Button
                            bsSize="sm"
                            bsStyle={edited ? 'primary' : 'default'}
                            disabled={!edited || !this.state.valid}
                            onClick={this.onSave}
                        >
                            Save
                        </Button>
                    </InputGroup.Button>
                </InputGroup>
            </FormGroup>
        );
    }
}

ParamEditor.propTypes = {
    value: PropTypes.object,
    onSave: PropTypes.func.isRequired,
};
