import React from 'react';
import {
    ButtonGroup,
    Col,
    Grid,
    Row,
} from 'react-bootstrap';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux';

import {applyToolAsync} from '../store/palette';

import {LightButton} from './LightButton';

import css from './Index.scss';


class Preview extends React.Component {
    applyToolAsync = (id) => () => {
        return this.props.applyToolAsync(id);
    };

    render() {
        let id = 1;
        const colors = !!this.props.previewFrame ? this.props.previewFrame : this.props.baseColors;

        let lightButtons = colors.map((color) => {
            let key = id++;
            return (
                <LightButton
                    color={color}
                    key={key}
                    id={key}
                    onClick={this.applyToolAsync(key - 1)}
                />
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
            <Grid className={css.lights}>
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
        previewFrame: lights.previewFrame,
    }
};

const mapDispatchToProps = (dispatch) => {
    return bindActionCreators({
        applyToolAsync,
    }, dispatch);
};

const PreviewRedux = connect(mapStateToProps, mapDispatchToProps)(Preview);

export {PreviewRedux as Preview};
