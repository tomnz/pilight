import React, {PropTypes} from 'react';
import {FormControl} from 'react-bootstrap';

import css from './common.scss';


class Variable extends React.Component {
    onChange = (event) => {
        const variable = event.target.value;
        if (variable !== '') {
            this.props.onChange({'variable': event.target.value});
        }
    };

    render() {
        const variableOptions = this.props.variables.map((variable) => {
            return (
                <option key={variable.variable} value={variable.variable}>
                    {variable.name}
                </option>
            );
        });

        return (
            <FormControl
                className={css.textbox}
                componentClass="select"
                onChange={this.onChange}
                value={this.props.value}
            >
                <option value="">None</option>
                {variableOptions}
            </FormControl>
        );
    }
}

Variable.propTypes = {
    onChange: PropTypes.func.isRequired,
    value: PropTypes.string.isRequired,
    variables: PropTypes.arrayOf(
        PropTypes.shape({
            variable: PropTypes.string.isRequired,
            name: PropTypes.string.isRequired,
            type: PropTypes.string,
        }),
    ).isRequired,
};

export {Variable};
