import React from 'react';
import {
    Button,
    Col,
    Grid,
    Row
} from 'react-bootstrap';

import {Controls} from './Controls';


class Header extends React.Component {
    render() {
        return (
            <Grid>
                <Row>
                    <Col md={8}>
                        <h1>PiLight&nbsp;&nbsp;
                            <Button bsSize="xs">Logout</Button>
                        </h1>
                    </Col>
                    <Col md={4}>
                        <Controls />
                    </Col>
                </Row>
            </Grid>
        );
    }
}

export {Header};
