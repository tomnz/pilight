import {applyMiddleware, combineReducers, createStore} from 'redux';
import thunk from 'redux-thunk';

import {setCsrfToken, fetchObjectPromise} from './async';
import {auth, setAuthRequired, setLoggedIn} from './auth';
import {client, finishBootstrap, setConfigs, setError, setNumLights, setPlaylists, startBootstrap} from './client';
import {setBaseColors, lights} from './lights';
import {palette, setColor} from './palette';
import {getPlaylistAsync, playlist} from './playlist';
import {transforms, setActiveTransforms, setAvailableTransforms} from './transforms';
import {variables, setActiveVariables, setAvailableVariables} from './variables';


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

            dispatch(setNumLights(data.numLights));
            dispatch(setActiveTransforms(data.activeTransforms));
            dispatch(setAvailableTransforms(data.availableTransforms));
            dispatch(setActiveVariables(data.activeVariables));
            dispatch(setAvailableVariables(data.availableVariables));
            dispatch(setBaseColors(data.baseColors));
            dispatch(setColor(data.toolColor));
            dispatch(setConfigs(data.configs));
            dispatch(setPlaylists(data.playlists));
            dispatch(getPlaylistAsync(data.lastPlayed));
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
    playlist: playlist,
    transforms: transforms,
    variables: variables,
});

export const store = createStore(
    rootReducer,
    applyMiddleware(thunk),
);
