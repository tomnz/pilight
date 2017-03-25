import {createAction, handleActions} from 'redux-actions';

import {postObjectPromise} from './async';
import {setError} from './client';


const CLEAR_PREVIEW = 'lights/CLEAR_PREVIEW';
const SET_BASE_COLORS = 'lights/SET_BASE_COLORS';
const SET_PREVIEW_FRAME = 'lights/SET_PREVIEW_FRAME';

const clearPreview = createAction(CLEAR_PREVIEW);
export const setBaseColors = createAction(SET_BASE_COLORS);
const setPreviewFrame = createAction(SET_PREVIEW_FRAME);

const PREVIEW_FRAME_TIME = 50;
function nextFrame(frames, dispatch) { return () => {
    if (frames.length === 0) {
        dispatch(clearPreview());
        return;
    }
    // "Pop" the next frame from the list
    dispatch(setPreviewFrame(frames.shift()));
    setTimeout(nextFrame(frames, dispatch), PREVIEW_FRAME_TIME);
}}

export const doPreviewAsync = () => (dispatch) => {
    return postObjectPromise(
        `/api/light/preview/`,
        {},
        (data) => {
            nextFrame(data.frames, dispatch)();
        },
        (error) => { dispatch(setError(error)); },
    )
};


const INITIAL_STATE = {
    baseColors: [],
    numLights: 0,
    previewFrame: null,
};

export const lights = handleActions({
    [CLEAR_PREVIEW]: (state) => ({...state, previewFrame: null}),
    [SET_BASE_COLORS]: (state, action) => ({...state, baseColors: action.payload}),
    [SET_PREVIEW_FRAME]: (state, action) => ({...state, previewFrame: action.payload}),
}, INITIAL_STATE);
