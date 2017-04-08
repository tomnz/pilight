import React, {PropTypes} from 'react';
import {FormControl, FormGroup} from 'react-bootstrap';

import css from './common.scss';


const VALID_FLOAT = /^(-|\+)?[0-9]+(\.[0-9]+)?$/;

class Float extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            text: props.value.toString(),
            valid: true,
        }
    }

    componentWillReceiveProps(nextProps) {
        if (nextProps.value !== this.props.value) {
            // Reset the current value
            this.setState({
                text: nextProps.value.toString(),
                valid: true,
            });
        }
    }

    onChangeEvent = (event) => {
        const valueStr = event.target.value;
        let valid = VALID_FLOAT.test(valueStr);
        this.setState({
            text: valueStr,
            valid: valid,
        });

        if (!valid) {
            return;
        }

        this.props.onChange(parseFloat(valueStr));
    };

    render() {
        const edited = this.state.text !== this.props.origValue.toString();

        return (
            <FormGroup
                className={css.formGroup}
                validationState={edited ? (this.state.valid ? 'success' : 'error') : null}
            >
                <FormControl
                    bsSize="small"
                    className={css.controlWidth}
                    onChange={this.onChangeEvent}
                    type="text"
                    value={this.state.text}
                />
            </FormGroup>
        );
    }
}

Float.propTypes = {
    onChange: PropTypes.func.isRequired,
    value: PropTypes.number.isRequired,
    origValue: PropTypes.number.isRequired,
};

export {Float};
