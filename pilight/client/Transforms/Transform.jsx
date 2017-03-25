import React, {PropTypes} from 'react';
import {
    Button,
    ButtonGroup,
    Table,
} from 'react-bootstrap';

import {ParamEditor} from './ParamEditor';

import css from './Transform.scss';


class Transform extends React.Component {
    render() {
        return (
            <Table bordered striped>
                <thead>
                    <tr>
                        <th colSpan={2}>
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
                    <tr>
                        <td>Params</td>
                        <td>
                            <ParamEditor
                                onSave={this.props.onSave}
                                value={this.props.transform.params}
                            />
                        </td>
                    </tr>
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
    description: PropTypes.string,
    moveDown: PropTypes.func.isRequired,
    moveUp: PropTypes.func.isRequired,
    onSave: PropTypes.func.isRequired,
    onDelete: PropTypes.func.isRequired,
};

export {Transform};
