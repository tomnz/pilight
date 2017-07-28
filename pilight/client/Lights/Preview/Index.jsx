import PropTypes from 'prop-types';
import React from 'react';
import {
    Modal,
} from 'react-bootstrap';

import * as types from '../../types';

import css from './Index.scss';


const PREVIEW_FRAME_TIME = 50;

export default class Preview extends React.Component {
    static propTypes = {
        clearPreview: PropTypes.func.isRequired,
        previewFrames: PropTypes.arrayOf(
            PropTypes.arrayOf(types.Color),
        ),
    };

    constructor(props) {
        super(props);
        // Not using state so we can bypass React... Not great, but performs better.
        this.lightElements = [];
        this.frame = 0;
    }

    shouldComponentUpdate = () => {
        // NEVER re-render this component - we always operate on initial props, and remove/add
        // a new component as needed
        return false;
    };

    nextFrame = () => {
        if (!this.props.previewFrames) {
            // Preview was cleared? Just return
            this.frame = 0;
            return;
        }
        if (this.frame >= this.props.previewFrames.length) {
            // No more frames - clear the preview so the modal will close
            this.frame = 0;
            this.props.clearPreview();
            return;
        }

        const frameColors = this.props.previewFrames[this.frame];
        for (let i = 0; i < frameColors.length; i++) {
            if (i >= this.lightElements.length) {
                // Safety - shouldn't ever happen
                break;
            }

            const color = frameColors[i];
            this.lightElements[i].style.backgroundColor = `rgb(${Math.round(color.r * 255)}, ` +
                `${Math.round(color.g * 255)}, ${Math.round(color.b * 255)})`;
        }

        // Schedule the next frame
        this.frame++;
        setTimeout(this.nextFrame, PREVIEW_FRAME_TIME);
    };

    render() {
        this.lightElements = [];
        const lights = [];

        for (let i = 0; i < this.props.previewFrames[0].length; i++) {
            // Stash all of the light refs so we can manually change the color later
            lights.push(
                <div
                    className={css.light}
                    key={i}
                    ref={light => {this.lightElements.push(light)}}
                >
                    &nbsp;
                </div>
            );
        }

        setTimeout(this.nextFrame, PREVIEW_FRAME_TIME);

        return (
            <Modal dialogClassName={css.modal} onHide={this.props.clearPreview} show>
                <Modal.Header closeButton>
                    <Modal.Title>Preview</Modal.Title>
                </Modal.Header>
                <Modal.Body className={css.modalBody}>
                    {lights}
                </Modal.Body>
            </Modal>
        );
    }
}
