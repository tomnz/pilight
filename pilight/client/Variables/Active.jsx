import PropTypes from 'prop-types';
import React from 'react';
import {
    Col,
    Grid,
    Row,
} from 'react-bootstrap';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux';

import {setError} from '../store/client';
import {
    deleteVariableAsync,
    updateVariableAsync,
} from '../store/variables';
import * as types from '../types';

import {Variable} from './Variable';


class Active extends React.Component {
    static propTypes = {
        variables: PropTypes.arrayOf(types.ActiveVariable),
        paramsDefs: PropTypes.objectOf(
            PropTypes.objectOf(types.ParamDef),
        ).isRequired,
    };

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
