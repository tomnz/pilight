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
    deleteTransformAsync,
    moveTransformDownAsync,
    moveTransformUpAsync,
    updateTransformAsync,
} from '../store/transforms';
import * as types from '../types';

import {Transform} from './Transform';


class Active extends React.Component {
    static propTypes = {
        transforms: PropTypes.arrayOf(
            types.ActiveTransform.isRequired,
        ),
        paramsDefs: PropTypes.objectOf(
            PropTypes.objectOf(types.ParamDef),
        ),
        variablesByType: PropTypes.objectOf(
            PropTypes.arrayOf(
                PropTypes.shape({
                    id: PropTypes.number.isRequired,
                    name: PropTypes.string.isRequired,
                }),
            ),
        ),
    };

    deleteTransform = (id) => () => {
        this.props.deleteTransformAsync(id);
    };

    moveDown = (id) => () => {
        this.props.moveTransformDownAsync(id);
    };

    moveUp = (id) => () => {
        this.props.moveTransformUpAsync(id);
    };

    saveParams = (id) => (params, variableParams) => {
        this.props.updateTransformAsync({
            id: id,
            params: params,
            variableParams: variableParams,
        });
    };

    render() {
        const orderedTransforms = this.props.transforms.slice();
        orderedTransforms.sort((a, b) => a.order - b.order);

        const transforms = orderedTransforms.map((transform) => {
            let paramsDef = null;
            if (this.props.paramsDefs.hasOwnProperty(transform.transform)) {
                paramsDef = this.props.paramsDefs[transform.transform];
            } else {
                return null;
            }

            return (
                <Transform
                    key={transform.id}
                    moveDown={this.moveDown(transform.id)}
                    moveUp={this.moveUp(transform.id)}
                    onDelete={this.deleteTransform(transform.id)}
                    onSave={this.saveParams(transform.id)}
                    paramsDef={paramsDef}
                    transform={transform}
                    variablesByType={this.props.variablesByType}
                />
            );
        });

        return (
            <Grid>
                <Row>
                    <Col md={12}>
                        <h3>Active Transforms</h3>
                        <p className="hidden-xs">
                            <small>All currently active transforms. Set parameters for each transform and specify which
                                order they should run in (first to last).
                            </small>
                        </p>
                        {transforms}
                    </Col>
                </Row>
            </Grid>
        );
    }
}

const mapStateToProps = (state) => {
    const {transforms, variables} = state;

    // Convert list of available transforms into a map of transform -> paramsDef
    const paramsDefs = {};
    transforms.available.forEach((transform) => {
        paramsDefs[transform.transform] = transform.paramsDef;
    });

    return {
        transforms: transforms.active,
        paramsDefs: paramsDefs,
        variablesByType: variables.activeByType,
    }
};

const mapDispatchToProps = (dispatch) => {
    return bindActionCreators({
        deleteTransformAsync,
        moveTransformDownAsync,
        moveTransformUpAsync,
        updateTransformAsync,
        setError,
    }, dispatch);
};

const ActiveRedux = connect(mapStateToProps, mapDispatchToProps)(Active);

export {ActiveRedux as Active};
