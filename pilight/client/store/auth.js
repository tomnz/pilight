import {createAction, handleActions} from 'redux-actions';

import {postObjectPromise} from './async';
import {setError} from './client';


const SET_AUTH_REQUIRED = 'auth/SET_AUTH_REQUIRED';
const SET_LOGGED_IN = 'auth/SET_LOGGED_IN';

export const setAuthRequired = createAction(SET_AUTH_REQUIRED);
export const setLoggedIn = createAction(SET_LOGGED_IN);

export const loginAsync = (username, password) => (dispatch) => {
    return postObjectPromise(
        `/api/auth/login/`,
        { username: username, password: password },
        (data) => {
            dispatch(setLoggedIn(data.loggedIn));
        },
        (error) => { dispatch(setError(error)); },
    );
};

export const logoutAsync = (username, password) => (dispatch) => {
    return postObjectPromise(
        `/api/auth/logout/`, {},
        () => {
            dispatch(setLoggedIn(false));
        },
        (error) => { dispatch(setError(error)); },
    );
};


const INITIAL_STATE = {
    authRequired: false,
    loggedIn: false,
};

export const auth = handleActions({
    [SET_AUTH_REQUIRED]: (state, action) => ({...state, authRequired: action.payload}),
    [SET_LOGGED_IN]: (state, action) => ({...state, loggedIn: action.payload}),
}, INITIAL_STATE);
