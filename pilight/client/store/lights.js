import {createAction, handleActions} from 'redux-actions';

import {postObjectPromise} from './async';
import {setError} from './client';


const CLEAR_PREVIEW = 'lights/CLEAR_PREVIEW';
const SET_BASE_COLORS = 'lights/SET_BASE_COLORS';
const SET_PREVIEW = 'lights/SET_PREVIEW';

export const clearPreview = createAction(CLEAR_PREVIEW);
export const setBaseColors = createAction(SET_BASE_COLORS);
const setPreview = createAction(SET_PREVIEW);

export const doPreviewAsync = () => (dispatch) => {
    return postObjectPromise(
        `/api/light/preview/`,
        {},
        (data) => {
            dispatch(setPreview(data.frames));
        },
        (error) => { dispatch(setError(error)); },
    )
};


const INITIAL_STATE = {
    baseColors: [],
    numLights: 0,
    previewFrames: null,
};

export const lights = handleActions({
    [CLEAR_PREVIEW]: (state) => ({...state, previewFrames: null}),
    [SET_BASE_COLORS]: (state, action) => ({...state, baseColors: action.payload}),
    [SET_PREVIEW]: (state, action) => ({...state, previewFrames: action.payload}),
}, INITIAL_STATE);
