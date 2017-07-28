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

import {addTransformAsync} from '../store/transforms';
import * as types from '../types';


class Picker extends React.Component {
    static propTypes = {
        transforms: PropTypes.arrayOf(types.AvailableTransform),
    };

    addTransform = (transform) => () => {
        this.props.addTransformAsync(transform);
    };

    render() {
        const availableRows = this.props.transforms.map((transform) => {
            const descriptionTooltip = (
                <Tooltip id={transform.transform}>{transform.description}</Tooltip>
            );
            return (
                <tr key={transform.transform}>
                    <td>
                        {transform.name}
                        {' '}
                        <OverlayTrigger placement="right" overlay={descriptionTooltip}>
                            <Button bsSize="xs" className="visible-xs-inline-block">?</Button>
                        </OverlayTrigger>
                    </td>
                    <td className="hidden-xs">
                        <small>{transform.description}</small>
                    </td>
                    <td>
                        <Button
                            bsStyle="primary"
                            bsSize="xs"
                            onClick={this.addTransform(transform.transform)}
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
                        <h3>Available Transforms</h3>
                        <p className="hidden-xs">
                            <small>All the available types of transforms that can be applied. Activate one by clicking
                                Add.
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
    const {transforms} = state;
    return {
        transforms: transforms.available,
    }
};

const mapDispatchToProps = (dispatch) => {
    return bindActionCreators({
        addTransformAsync,
    }, dispatch);
};

const PickerRedux = connect(mapStateToProps, mapDispatchToProps)(Picker);

export {PickerRedux as Picker};
