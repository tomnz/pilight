import {createAction, handleActions} from 'redux-actions';

import {postObjectPromise} from './async';
import {bootstrapClientAsync} from './root';


const CLEAR_ERROR = 'client/CLEAR_ERROR';
const FINISH_BOOTSTRAP = 'client/FINISH_BOOTSTRAP';
const HANDLE_RESPONSE = 'client/HANDLE_RESPONSE';
const SET_CONFIGS = 'client/SET_CONFIGS';
const SET_ERROR = 'client/SET_ERROR';
const SET_NUM_LIGHTS = 'client/SET_NUM_LIGHTS';
const SET_PLAYLISTS = 'client/SET_PLAYLISTS';
const START_BOOTSTRAP = 'client/START_BOOTSTRAP';

export const clearError = createAction(CLEAR_ERROR);
export const finishBootstrap = createAction(FINISH_BOOTSTRAP);
export const setConfigs = createAction(SET_CONFIGS);
export const setError = createAction(SET_ERROR);
export const setPlaylists = createAction(SET_PLAYLISTS);
export const setNumLights = createAction(SET_NUM_LIGHTS);
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

export const deleteConfigAsync = (id) => (dispatch) => {
    return postObjectPromise(
        `/api/config/delete/`,
        {id: id},
        (data) => {
            dispatch(setConfigs(data.configs));
        },
        (error) => { dispatch(setError(error)); },
    );
};

export const loadConfigAsync = (id) => (dispatch) => {
    // The response from the server takes a second, so we immediately display loading
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
    );
};

export const startDriverAsync = () => (dispatch) => {
    return postObjectPromise(
        `/api/driver/start/`, {}, () => {},
        (error) => { dispatch(setError(error)); },
    );
};

export const stopDriverAsync = () => (dispatch) => {
    return postObjectPromise(
        `/api/driver/stop/`, {}, () => {},
        (error) => { dispatch(setError(error)); },
    );
};


const INITIAL_STATE = {
    // Using a const string to avoid depending on async
    bootstrapStatus: 'PENDING',
    configs: [],
    errorMessage: null,
    numLights: 0,
    playlists: [],
};

export const client = handleActions({
    [CLEAR_ERROR]: (state) => ({...state, errorMessage: null}),
    [FINISH_BOOTSTRAP]: (state) => ({...state, bootstrapStatus: 'DONE'}),
    [SET_CONFIGS]: (state, action) => ({...state, configs: action.payload}),
    [SET_ERROR]: (state, action) => ({...state, errorMessage: action.payload}),
    [SET_NUM_LIGHTS]: (state, action) => ({...state, numLights: action.payload}),
    [SET_PLAYLISTS]: (state, action) => ({...state, playlists: action.payload}),
    [START_BOOTSTRAP]: (state) => ({...state, bootstrapStatus: 'PENDING'}),
}, INITIAL_STATE);
