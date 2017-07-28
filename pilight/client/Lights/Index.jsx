import PropTypes from 'prop-types';
import React from 'react';
import {
    ButtonGroup,
    Col,
    Grid,
    Row,
} from 'react-bootstrap';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux';

import {clearPreview} from '../store/lights';
import {applyToolAsync} from '../store/palette';
import * as types from '../types';

import {LightButton} from './LightButton';
import Preview from './Preview';

import css from './Index.scss';


class Lights extends React.Component {
    static propTypes = {
        baseColors: PropTypes.arrayOf(types.Color).isRequired,
        previewFrames: PropTypes.arrayOf(
            PropTypes.arrayOf(types.Color)
        ),
    };

    applyToolAsync = (id) => () => {
        return this.props.applyToolAsync(id);
    };

    render() {
        if (!!this.props.previewFrames) {
            return (
                <Preview
                    clearPreview={this.props.clearPreview}
                    previewFrames={this.props.previewFrames}
                />
            );
        }

        let id = 1;
        let lightButtons = this.props.baseColors.map((color) => {
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
        previewFrames: lights.previewFrames,
    }
};

const mapDispatchToProps = (dispatch) => {
    return bindActionCreators({
        applyToolAsync,
        clearPreview,
    }, dispatch);
};

const LightsRedux = connect(mapStateToProps, mapDispatchToProps)(Lights);
export default LightsRedux;
