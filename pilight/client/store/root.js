import {applyMiddleware, combineReducers, createStore} from 'redux';
import thunk from 'redux-thunk';

import {setCsrfToken, fetchObjectPromise} from './async';
import {auth, setAuthRequired, setLoggedIn} from './auth';
import {client, finishBootstrap, setConfigs, setError, startBootstrap} from './client';
import {setBaseColors, lights} from './lights';
import {palette, setColor} from './palette';
import {transforms, setActiveTransforms, setAvailableTransforms} from './transforms';


export const bootstrapClientAsync = () => (dispatch) => {
    dispatch(startBootstrap());

    return fetchObjectPromise(
        `/api/`,
        (data) => {
            if (!!data.authRequired && !data.loggedIn) {
                // If we need to be logged in, then short circuit
                dispatch(setAuthRequired(true));
                dispatch(setLoggedIn(false));
                dispatch(finishBootstrap());
                return;
            }

            setCsrfToken(data.csrfToken);

            dispatch(setActiveTransforms(data.activeTransforms));
            dispatch(setAvailableTransforms(data.availableTransforms));
            dispatch(setBaseColors(data.baseColors));
            dispatch(setColor(data.toolColor));
            dispatch(setConfigs(data.configs));
            dispatch(setLoggedIn(data.loggedIn));

            dispatch(finishBootstrap());
        },
        (error) => { dispatch(setError(error)); },
    );
};

const rootReducer = combineReducers({
    auth: auth,
    client: client,
    lights: lights,
    palette: palette,
    transforms: transforms,
});

export const store = createStore(
    rootReducer,
    applyMiddleware(thunk),
);
