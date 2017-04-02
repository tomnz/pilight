import React, {PropTypes} from 'react';
import {FormControl} from 'react-bootstrap';

import {Float} from './Float';

import css from './common.scss';


class Variable extends React.Component {
    onVariableChange = (event) => {
        this.props.onChange({
            ...this.props.variable,
            variableId: parseInt(event.target.value),
        });
    };

    onMultiplyChange = (value) => {
        this.props.onChange({
            ...this.props.variable,
            multiply: value,
        });
    };

    onAddChange = (value) => {
        this.props.onChange({
            ...this.props.variable,
            add: value,
        });
    };

    render() {
        const variableOptions = !!this.props.variables ? this.props.variables.map((variable) => {
            return (
                <option key={variable.id} value={variable.id.toString()}>
                    {variable.name}
                </option>
            );
        }) : [];
        return (
            <div>
                <FormControl
                    className={css.textbox}
                    componentClass="select"
                    onChange={this.onVariableChange}
                    value={!!this.props.variable.variableId ? this.props.variable.variableId.toString() : ""}
                >
                    <option value="">None</option>
                    {variableOptions}
                </FormControl>
                <Float
                    onChange={this.onMultiplyChange}
                    origValue={1}
                    value={this.props.variable.multiply}
                />
                <Float
                    onChange={this.onAddChange}
                    origValue={0}
                    value={this.props.variable.add}
                />
            </div>
        );
    }
}

Variable.propTypes = {
    onChange: PropTypes.func.isRequired,
    variable: PropTypes.shape({
        variableId: PropTypes.number,
        multiply: PropTypes.any,
        add: PropTypes.any,
    }).isRequired,
    variables: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.number.isRequired,
            name: PropTypes.string.isRequired,
        }),
    ),
};

export {Variable};
