import React, {PropTypes} from 'react';
import {
    Button,
    ButtonGroup,
    Table,
} from 'react-bootstrap';

import {ParamFactory} from './ParamFactory';

import css from './Transform.scss';


class Transform extends React.Component {
    constructor(props) {
        super(props);
        // Do a JSON.stringify/parse to force a deep clone
        this.state = {
            params: JSON.parse(JSON.stringify(this.props.transform.params)),
            modified: false,
        };
    }

    componentWillReceiveProps(nextProps) {
        if (JSON.stringify(nextProps.transform.params) !== JSON.stringify(this.props.transform.params)) {
            // Reset the current value
            this.setState({
                params: JSON.parse(JSON.stringify(nextProps.transform.params)),
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

    onSave = () => {
        this.props.onSave(this.state.params);
    };

    render() {
        const paramRows = [];
        const params = this.props.transform.params;
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
                        <td className={css.paramDescription}><small>{paramDef.description}</small></td>
                        <td className={css.paramEditor}>
                            <ParamFactory
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
                            {this.props.transform.name}
                            <div className={css.buttons}>
                                <Button
                                    bsSize="xsmall"
                                    bsStyle="danger"
                                    onClick={this.props.onDelete}
                                >
                                    Delete
                                </Button>
                                &nbsp;&nbsp;&nbsp;&nbsp;
                                <ButtonGroup>
                                    <Button onClick={this.props.moveUp} bsSize="xsmall">Up</Button>
                                    <Button onClick={this.props.moveDown} bsSize="xsmall">Down</Button>
                                </ButtonGroup>
                                {' '}
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

Transform.propTypes = {
    transform: PropTypes.shape({
        id: PropTypes.number.isRequired,
        transform: PropTypes.string.isRequired,
        name: PropTypes.string.isRequired,
        params: PropTypes.any,
    }).isRequired,
    paramsDef: PropTypes.objectOf(
        PropTypes.shape({
            type: PropTypes.string.isRequired,
            name: PropTypes.string,
            description: PropTypes.string,
        }),
    ).isRequired,
    description: PropTypes.string,
    moveDown: PropTypes.func.isRequired,
    moveUp: PropTypes.func.isRequired,
    onSave: PropTypes.func.isRequired,
    onDelete: PropTypes.func.isRequired,
};

export {Transform};
