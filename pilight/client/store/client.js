import {createAction, handleActions} from 'redux-actions';

import {postObjectPromise} from './async';
import {bootstrapClientAsync} from './root';


const CLEAR_ERROR = 'client/CLEAR_ERROR';
const FINISH_BOOTSTRAP = 'client/FINISH_BOOTSTRAP';
const HANDLE_RESPONSE = 'client/HANDLE_RESPONSE';
const SET_CONFIGS = 'client/SET_CONFIGS';
const SET_ERROR = 'client/SET_ERROR';
const START_BOOTSTRAP = 'client/START_BOOTSTRAP';

export const clearError = createAction(CLEAR_ERROR);
export const finishBootstrap = createAction(FINISH_BOOTSTRAP);
export const setConfigs = createAction(SET_CONFIGS);
export const setError = createAction(SET_ERROR);
export const startBootstrap = createAction(START_BOOTSTRAP);


export const saveConfigAsync = (configName) => (dispatch) => {
    return postObjectPromise(
        `/api/config/save/`,
        {configName: configName},
        (data) => {
            dispatch(setConfigs(data.configs));
        },
        (error) => { dispatch(setError(error)); },
    );
};

export const loadConfigAsync = (id) => (dispatch) => {
    // The response from the server takes a second, so we immediate display loading
    // to make it feel snappy
    dispatch(startBootstrap());

    return postObjectPromise(
        `/api/config/load/`,
        {id: id},
        () => {
            // Easiest to just "reboot" our UI
            dispatch(bootstrapClientAsync());
        },
        (error) => {
            dispatch(finishBootstrap());
            dispatch(setError(error));
        },
    )
};


const INITIAL_STATE = {
    errorMessage: null,
    configs: [],
    // Using a const string to avoid depending on async
    bootstrapStatus: 'INVALID',
};

export const client = handleActions({
    [CLEAR_ERROR]: (state, action) => ({...state, errorMessage: null}),
    [FINISH_BOOTSTRAP]: (state, action) => ({...state, bootstrapStatus: 'VALID'}),
    [SET_CONFIGS]: (state, action) => ({...state, configs: action.payload}),
    [SET_ERROR]: (state, action) => ({...state, errorMessage: action.payload}),
    [START_BOOTSTRAP]: (state, action) => ({...state, bootstrapStatus: 'INVALID'}),
}, INITIAL_STATE);
