import React, {PropTypes} from 'react';
import {
    Button,
    Col,
    FormControl,
    FormGroup,
    Grid,
    InputGroup,
    Row,
    Table,
} from 'react-bootstrap';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux';

import {setError} from '../store/client';
import {deleteTransformAsync, updateTransformAsync} from '../store/transforms';

import {ParamEditor} from './ParamEditor';


class Active extends React.Component {
    deleteTransform = (id) => () => {
        this.props.deleteTransformAsync(id);
    };

    saveParams = (id) => (params) => {
        this.props.updateTransformAsync({
            id: id,
            params: params,
        });
    };

    render() {
        const activeRows = this.props.transforms.map((transform) => {
            return (
                <tr key={transform.id}>
                    <td>{transform.longName}</td>
                    <td>
                        <ParamEditor
                            onSave={this.saveParams(transform.id)}
                            value={transform.params}
                        />
                    </td>
                    <td>
                        <Button
                            bsStyle="primary"
                            bsSize="sm"
                            onClick={this.deleteTransform(transform.id)}
                        >
                            Delete
                        </Button>
                    </td>
                </tr>
            );
        });

        return (
            <Grid>
                <Row>
                    <Col md={12}>
                        <h3>Active Transforms</h3>
                        <p className="hidden-xs">
                            <small>All currently active transforms. Set parameters for each transform and specify which
                                order they should run in.
                            </small>
                        </p>
                        <Table bordered striped>
                            <thead>
                            <tr>
                                <th>Name</th>
                                <th>Params</th>
                                <th>&nbsp;</th>
                            </tr>
                            </thead>
                            <tbody>
                            {activeRows}
                            </tbody>
                        </Table>
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
            name: PropTypes.string.isRequired,
            longName: PropTypes.string.isRequired,
            description: PropTypes.string,
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
        updateTransformAsync,
        setError,
    }, dispatch);
};

const ActiveRedux = connect(mapStateToProps, mapDispatchToProps)(Active);

export {ActiveRedux as Active};
