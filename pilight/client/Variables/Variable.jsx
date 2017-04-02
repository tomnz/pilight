import React, {PropTypes} from 'react';
import {
    Button,
    ButtonGroup,
    Checkbox,
    FormControl,
    Table,
} from 'react-bootstrap';

import {Param} from '../Params/Index';

import css from './Variable.scss';


class Variable extends React.Component {
    constructor(props) {
        super(props);
        // Do a JSON.stringify/parse to force a deep clone
        this.state = {
            name: this.props.variable.name,
            params: JSON.parse(JSON.stringify(this.props.variable.params)),
            modified: false,
        };
    }

    componentWillReceiveProps(nextProps) {
        if (JSON.stringify(nextProps.variable.params) !== JSON.stringify(this.props.variable.params) ||
            nextProps.name !== this.props.variable.name) {
            // Reset the current value
            this.setState({
                name: nextProps.variable.name,
                params: JSON.parse(JSON.stringify(nextProps.variable.params)),
                modified: false,
            });
        }
    }

    onValueChange = (name) => (value) => {
        const newParams = Object.assign({}, this.state.params);
        newParams[name] = value;
        this.setState({
            params: newParams,
            modified: true,
        });
    };

    onNameChange = (event) => {
        this.setState({
            name: event.target.value,
            modified: true,
        });
    };

    onSave = () => {
        this.props.onSave(this.state.name, this.state.params);
    };

    render() {
        const paramRows = [];
        const params = this.props.variable.params;
        for (let name in params) {
            if (params.hasOwnProperty(name)) {
                let paramDef = null;
                if (this.props.paramsDef.hasOwnProperty(name)) {
                    paramDef = this.props.paramsDef[name];
                } else {
                    // Unknown param?
                    continue;
                }

                const value = this.state.params[name];
                const origValue = params[name];

                paramRows.push(
                    <tr key={name}>
                        <td className={css.paramName}>{paramDef.name}</td>
                        <td className={css.paramDescription}>
                            <small>{paramDef.description}</small>
                        </td>
                        <td className={css.paramEditor}>
                            <Param
                                onChange={this.onValueChange(name)}
                                origValue={origValue}
                                paramDef={paramDef}
                                value={value}
                            />
                        </td>
                    </tr>
                );
            }
        }

        return (
            <Table bordered striped>
                <thead>
                <tr>
                    <th colSpan={3}>
                        <FormControl
                            className={css.nameEditor}
                            onChange={this.onNameChange}
                            value={this.state.name}
                        />
                        <div className={css.buttons}>
                            <Button
                                bsSize="xsmall"
                                bsStyle="danger"
                                onClick={this.props.onDelete}
                            >
                                Delete
                            </Button>
                            &nbsp;&nbsp;&nbsp;&nbsp;
                            <Button
                                bsSize="xsmall"
                                bsStyle={this.state.modified ? "primary" : "default"}
                                onClick={this.onSave}
                            >
                                Save
                            </Button>
                        </div>
                    </th>
                </tr>
                </thead>
                <tbody>
                    {paramRows}
                </tbody>
            </Table>
        )
    }
}

Variable.propTypes = {
    variable: PropTypes.shape({
        id: PropTypes.number.isRequired,
        variable: PropTypes.string.isRequired,
        name: PropTypes.string.isRequired,
        params: PropTypes.any,
    }).isRequired,
    paramsDef: PropTypes.objectOf(
        PropTypes.shape({
            type: PropTypes.string.isRequired,
            name: PropTypes.string,
            description: PropTypes.string,
            defaultValue: PropTypes.any,
        }),
    ).isRequired,
    onSave: PropTypes.func.isRequired,
    onDelete: PropTypes.func.isRequired,
};

export {Variable};
