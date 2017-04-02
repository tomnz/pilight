import React, {PropTypes} from 'react';
import {
    Button,
    Col,
    Grid,
    Row,
    Table,
} from 'react-bootstrap';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux';

import {addVariableAsync} from '../store/variables';


class Picker extends React.Component {
    addVariable = (variable) => () => {
        this.props.addVariableAsync(variable);
    };

    render() {
        const availableRows = this.props.variables.map((variable) => {
           return (
               <tr key={variable.variable}>
                   <td>{variable.name}</td>
                   <td>{variable.description}</td>
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
                                    <th>Description</th>
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

Picker.propTypes = {
    addVariableAsync: PropTypes.func.isRequired,
    variables: PropTypes.arrayOf(
        PropTypes.shape({
            variable: PropTypes.string.isRequired,
            name: PropTypes.string.isRequired,
            description: PropTypes.string,
            paramsDef: PropTypes.objectOf(
                PropTypes.shape({
                    type: PropTypes.string.isRequired,
                    name: PropTypes.string,
                    description: PropTypes.string,
                }),
            ),
        }).isRequired,
    ).isRequired,
};

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
