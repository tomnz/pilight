import {createAction, handleActions} from 'redux-actions';

import {fetchObjectPromise} from './async';
import {setError} from './client';


const SET_BASE_COLORS = 'lights/SET_BASE_COLORS';

export const setBaseColors = createAction(SET_BASE_COLORS);

export const getBaseColorsAsync = () => (dispatch) => {
    return fetchObjectPromise(
        `/api/light/base-colors/`,
        (data) => {
            dispatch(setBaseColors(data.baseColors));
        },
        (error) => { dispatch(setError(error)); },
    );
};

const INITIAL_STATE = {
    baseColors: [],
    numLights: 0,
};

export const lights = handleActions({
    [SET_BASE_COLORS]: (state, action) => ({...state, baseColors: action.payload}),
}, INITIAL_STATE);
