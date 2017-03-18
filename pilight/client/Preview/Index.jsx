import React from 'react';
import {
    ButtonGroup,
    Col,
    Grid,
    Row,
} from 'react-bootstrap';
import {connect} from 'react-redux';

import {LightButton} from './LightButton';

import css from './Index.scss';


class Preview extends React.Component {
    render() {
        let id = 1;
        let lightButtons = this.props.baseColors.map((color) => {
            let key = id++;
            return (
                <LightButton key={key} id={key} color={color} />
            );
        });

        // Group buttons in 5s
        let key = 1;
        let buttonGroups = [];
        let lightButtonsGroup = [];
        while (lightButtons.length > 0) {
            lightButtonsGroup.push(lightButtons.shift());
            if (lightButtonsGroup.length === 5 || lightButtons.length === 0) {
                buttonGroups.push(
                    <ButtonGroup key={key++} className={css.lightGroup}>
                        {lightButtonsGroup}
                    </ButtonGroup>
                );
                lightButtonsGroup = [];
            }
        }

        return (
            <Grid>
                <Row>
                    <Col md={12}>
                        {buttonGroups}
                    </Col>
                </Row>
            </Grid>
        );
    }
}

const mapStateToProps = (state) => {
    const {lights} = state;
    return {
        baseColors: lights.baseColors,
    }
};
const PreviewRedux = connect(mapStateToProps)(Preview);

export {PreviewRedux as Preview};
