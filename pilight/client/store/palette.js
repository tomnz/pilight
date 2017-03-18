import {createAction, handleActions} from 'redux-actions';


const SET_COLOR = 'palette/SET_COLOR';
const SET_OPACITY = 'palette/SET_OPACITY';
const SET_RADIUS = 'palette/SET_RADIUS';

export const setColor = createAction(SET_COLOR);
export const setOpacity = createAction(SET_OPACITY);
export const setRadius = createAction(SET_RADIUS);


const INITIAL_STATE = {
    color: {
        r: 0,
        g: 0,
        b: 0,
        a: 0,
    },
    opacity: 100,
    radius: 5,
};

export const palette = handleActions({
    [SET_COLOR]: (state, action) => ({...state, color: action.payload}),
    [SET_OPACITY]: (state, action) => ({...state, opacity: action.payload}),
    [SET_RADIUS]: (state, action) => ({...state, radius: action.payload}),
}, INITIAL_STATE);
