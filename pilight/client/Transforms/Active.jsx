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
    deleteTransformAsync,
    moveTransformDownAsync,
    moveTransformUpAsync,
    updateTransformAsync,
} from '../store/transforms';

import {Transform} from './Transform';


class Active extends React.Component {
    deleteTransform = (id) => () => {
        this.props.deleteTransformAsync(id);
    };

    moveDown = (id) => () => {
        this.props.moveTransformDownAsync(id);
    };

    moveUp = (id) => () => {
        this.props.moveTransformUpAsync(id);
    };

    saveParams = (id) => (params) => {
        this.props.updateTransformAsync({
            id: id,
            params: params,
        });
    };

    render() {
        const orderedTransforms = this.props.transforms.slice();
        orderedTransforms.sort((a, b) => a.order - b.order);

        const transforms = orderedTransforms.map((transform) => {
            return (
                <Transform
                    key={transform.id}
                    moveDown={this.moveDown(transform.id)}
                    moveUp={this.moveUp(transform.id)}
                    onDelete={this.deleteTransform(transform.id)}
                    onSave={this.saveParams(transform.id)}
                    transform={transform}
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

Active.propTypes = {
    transforms: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.number.isRequired,
            transform: PropTypes.string.isRequired,
            name: PropTypes.string.isRequired,
            params: PropTypes.any,
        }).isRequired,
    ),
};

const mapStateToProps = (state) => {
    const {transforms} = state;
    return {
        transforms: transforms.active,
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
