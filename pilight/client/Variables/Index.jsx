import React from 'react';
import {
    Col,
    Grid,
    Row,
} from 'react-bootstrap';

import {Active} from './Active';
import {Picker} from './Picker';


class Variables extends React.Component {
    render() {
        return (
            <div>
                <Active />
                <Picker />
            </div>
        );
    }
}

export {Variables};
