import React, {PropTypes} from 'react';
import {
    Button,
    ButtonGroup,
    Table,
} from 'react-bootstrap';

import {ParamFactory} from './ParamFactory';

import css from './Transform.scss';


class Transform extends React.Component {
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

                const param = params[name];
                paramRows.push(
                    <tr key={name}>
                        <td>{paramDef.name}</td>
                        <td>{paramDef.description}</td>
                        <td>
                            <ParamFactory
                                paramDef={paramDef}
                                value={param}
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
                                <ButtonGroup>
                                    <Button onClick={this.props.moveUp} bsSize="xsmall">Up</Button>
                                    <Button onClick={this.props.moveDown} bsSize="xsmall">Down</Button>
                                </ButtonGroup>
                                {' '}
                                <Button
                                    bsStyle="danger"
                                    bsSize="xsmall"
                                    onClick={this.props.onDelete}
                                >Delete</Button>
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
