import PropTypes from 'prop-types';
import React from 'react';
import {
    Button,
    Col,
    Grid,
    OverlayTrigger,
    Row,
    Table,
    Tooltip,
} from 'react-bootstrap';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux';

import {addVariableAsync} from '../store/variables';
import * as types from '../types';


class Picker extends React.Component {
    static propTypes = {
        addVariableAsync: PropTypes.func.isRequired,
        variables: PropTypes.arrayOf(types.AvailableVariable),
    };

    addVariable = (variable) => () => {
        this.props.addVariableAsync(variable);
    };

    render() {
        const availableRows = this.props.variables.map((variable) => {
            const descriptionTooltip = (
                <Tooltip id={variable.variable}>{variable.description}</Tooltip>
            );
            return (
                <tr key={variable.variable}>
                    <td>
                        {variable.name}
                        {' '}
                        <OverlayTrigger placement="right" overlay={descriptionTooltip}>
                            <Button bsSize="xs" className="visible-xs-inline-block">?</Button>
                        </OverlayTrigger>
                    </td>
                    <td className="hidden-xs"><small>{variable.description}</small></td>
                    <td>
                        <Button
                            bsStyle="primary"
                            bsSize="xs"
                            onClick={this.addVariable(variable.variable)}
                        >
                            Add
                        </Button>
                    </td>
                </tr>
            );
        });

        return (
            <Grid>
                <Row>
                    <Col md={12}>
                        <h3>Available Variables</h3>
                        <p className="hidden-xs">
                            <small>All the available types of variables that can be instantiated. Activate one by
                                clicking Add.
                            </small>
                        </p>
                        <Table bordered striped condensed>
                            <thead>
                            <tr>
                                <th>Name</th>
                                <th className="hidden-xs">Description</th>
                                <th>&nbsp;</th>
                            </tr>
                            </thead>
                            <tbody>
                            {availableRows}
                            </tbody>
                        </Table>
                    </Col>
                </Row>
            </Grid>
        );
    }
}

const mapStateToProps = (state) => {
    const {variables} = state;
    return {
        variables: variables.available,
    }
};

const mapDispatchToProps = (dispatch) => {
    return bindActionCreators({
        addVariableAsync,
    }, dispatch);
};

const PickerRedux = connect(mapStateToProps, mapDispatchToProps)(Picker);

export {PickerRedux as Picker};
