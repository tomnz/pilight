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

import {addTransformAsync} from '../store/transforms';
import * as types from '../types';


class Picker extends React.Component {
    addTransform = (transform) => () => {
        this.props.addTransformAsync(transform);
    };

    render() {
        const availableRows = this.props.transforms.map((transform) => {
           return (
               <tr key={transform.transform}>
                   <td>{transform.name}</td>
                   <td>{transform.description}</td>
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
    transforms: PropTypes.arrayOf(types.AvailableTransform),
};

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
