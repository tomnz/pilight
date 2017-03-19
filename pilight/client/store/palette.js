import {createAction, handleActions} from 'redux-actions';

import {postObjectPromise} from './async';
import {setError} from './client';
import {setBaseColors} from './lights';


const SET_COLOR = 'palette/SET_COLOR';
const SET_OPACITY = 'palette/SET_OPACITY';
const SET_RADIUS = 'palette/SET_RADIUS';
const SET_TOOL = 'palette/SET_TOOL';

export const setColor = createAction(SET_COLOR);
export const setOpacity = createAction(SET_OPACITY);
export const setRadius = createAction(SET_RADIUS);
export const setTool = createAction(SET_TOOL);

export const fillAsync = () => (dispatch, getState) => {
    const {palette} = getState();

    return postObjectPromise(
        `/api/light/fill-color/`,
        {'color': palette.color},
        (data) => {
            dispatch(setBaseColors(data.baseColors));
        },
        (error) => { dispatch(setError(error)); },
    );
};

export const applyToolAsync = (index) => (dispatch, getState) => {
    const {palette} = getState();

    return postObjectPromise(
        `/api/light/apply-tool/`,
        {
            'tool': palette.tool,
            'index': index,
            'radius': palette.radius,
            'opacity': palette.opacity,
            'color': palette.color,
        },
        (data) => {
            dispatch(setBaseColors(data.baseColors));
        },
        (error) => { dispatch(setError(error)); },
    );
};


const INITIAL_STATE = {
    color: {
        r: 0,
        g: 0,
        b: 0,
        a: 0,
    },
    opacity: 100,
    radius: 5,
    tool: 'smooth',
};

export const palette = handleActions({
    [SET_COLOR]: (state, action) => ({...state, color: action.payload}),
    [SET_OPACITY]: (state, action) => ({...state, opacity: action.payload}),
    [SET_RADIUS]: (state, action) => ({...state, radius: action.payload}),
    [SET_TOOL]: (state, action) => ({...state, tool: action.payload}),
}, INITIAL_STATE);
