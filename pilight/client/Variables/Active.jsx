import React, {PropTypes} from 'react';
import {
    Button,
    Col,
    FormControl,
    FormGroup,
    Grid,
    InputGroup,
    Row,
} from 'react-bootstrap';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux';

import {setError} from '../store/client';
import {
    deleteVariableAsync,
    updateVariableAsync,
} from '../store/variables';

import {Variable} from './Variable';


class Active extends React.Component {
    deleteVariable = (id) => () => {
        this.props.deleteVariableAsync(id);
    };

    saveParams = (id) => (name, params) => {
        this.props.updateVariableAsync({
            id: id,
            name: name,
            params: params,
        });
    };

    render() {
        const orderedVariables = this.props.variables.slice();
        orderedVariables.sort((a, b) => a.order - b.order);

        const variables = orderedVariables.map((variable) => {
            let paramsDef = null;
            if (this.props.paramsDefs.hasOwnProperty(variable.variable)) {
                paramsDef = this.props.paramsDefs[variable.variable];
            } else {
                return null;
            }

            return (
                <Variable
                    key={variable.id}
                    onDelete={this.deleteVariable(variable.id)}
                    onSave={this.saveParams(variable.id)}
                    paramsDef={paramsDef}
                    variable={variable}
                />
            );
        });

        return (
            <Grid>
                <Row>
                    <Col md={12}>
                        <h3>Active Variables</h3>
                        <p className="hidden-xs">
                            <small>
                                All currently active variables. Set the name and parameters for each variable.
                            </small>
                        </p>
                        {variables}
                    </Col>
                </Row>
            </Grid>
        );
    }
}

Active.propTypes = {
    variables: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.number.isRequired,
            variable: PropTypes.string.isRequired,
            name: PropTypes.string.isRequired,
            params: PropTypes.any,
        }).isRequired,
    ),
    paramsDefs: PropTypes.objectOf(
        PropTypes.objectOf(
            PropTypes.shape({
                type: PropTypes.string.isRequired,
                name: PropTypes.string,
                description: PropTypes.string,
            }),
        ),
    ).isRequired,
};

const mapStateToProps = (state) => {
    const {variables} = state;

    // Convert list of available transforms into a map of transform -> paramsDef
    const paramsDefs = {};
    variables.available.forEach((variable) => {
        paramsDefs[variable.variable] = variable.paramsDef;
    });

    return {
        variables: variables.active,
        paramsDefs: paramsDefs,
    }
};

const mapDispatchToProps = (dispatch) => {
    return bindActionCreators({
        deleteVariableAsync,
        updateVariableAsync,
        setError,
    }, dispatch);
};

const ActiveRedux = connect(mapStateToProps, mapDispatchToProps)(Active);

export {ActiveRedux as Active};
