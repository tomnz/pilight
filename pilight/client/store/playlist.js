import {createAction, handleActions} from 'redux-actions';

import {fetchObjectPromise, postObjectPromise, Status} from './async';
import {setPlaylists, setError} from './client';


const NEW_PLAYLIST = 'playlist/NEW_PLAYLIST';
const RESET_PLAYLIST = 'playlist/RESET_PLAYLIST';
const SET_PLAYLIST = 'playlist/SET_PLAYLIST';

const ADD_CONFIG = 'playlist/ADD_CONFIG';
const DELETE_CONFIG = 'playlist/DELETE_CONFIG';
const MOVE_CONFIG_DOWN = 'playlist/MOVE_CONFIG_DOWN';
const MOVE_CONFIG_UP = 'playlist/MOVE_CONFIG_UP';
const SET_CONFIG = 'playlist/SET_CONFIG';
const SET_CONFIG_DURATION = 'playlist/SET_CONFIG_DURATION';
const SET_DESCRIPTION = 'playlist/SET_DESCRIPTION';
const SET_NAME = 'playlist/SET_NAME';


export const newPlaylist = createAction(NEW_PLAYLIST);
export const resetPlaylist = createAction(RESET_PLAYLIST);
const setPlaylist = createAction(SET_PLAYLIST);

export const addConfig = createAction(ADD_CONFIG);
export const deleteConfig = createAction(DELETE_CONFIG);
export const moveConfigDown = createAction(MOVE_CONFIG_DOWN);
export const moveConfigUp = createAction(MOVE_CONFIG_UP);
export const setConfig = createAction(SET_CONFIG, (index, configId) => ({index, configId}));
export const setConfigDuration = createAction(SET_CONFIG_DURATION, (index, duration) => ({index, duration}));
export const setDescription = createAction(SET_DESCRIPTION);
export const setName = createAction(SET_NAME);


export const getPlaylistAsync = (id) => (dispatch) => {
    dispatch(resetPlaylist());
    return fetchObjectPromise(
        `/api/playlist/get/${id}/`,
        (data) => {
            dispatch(setPlaylist(data.playlist));
        },
        (error) => {
            dispatch(setError(error));
        },
    );
};

export const savePlaylistAsync = () => (dispatch, getState) => {
    const {playlist} = getState();
    if (!playlist.current) {
        return;
    }

    return postObjectPromise(
        `/api/playlist/save/`,
        playlist.current,
        (data) => {
            dispatch(setPlaylist(data.playlist));
            dispatch(setPlaylists(data.playlists));
        },
        (error) => { dispatch(setError(error)); },
    );
};

export const deletePlaylistAsync = () => (dispatch, getState) => {
    const {playlist} = getState();
    if (!playlist.current) {
        return;
    }

    dispatch(resetPlaylist());
    return postObjectPromise(
        `/api/playlist/delete/`,
        {id: playlist.current.id},
        (data) => {
            dispatch(setPlaylists(data.playlists));
        },
        (error) => { dispatch(setError(error)); },
    );
};

export const startPlaylistAsync = (id) => (dispatch) => {
    return postObjectPromise(
        `/api/driver/start-playlist/`,
        {id: id},
        (data) => {},
        (error) => { dispatch(setError(error)); },
    );
};


const INITIAL_STATE = {
    status: Status.PENDING,
    current: null,
};

export const playlist = handleActions({
    [NEW_PLAYLIST]: (state) => ({
        ...state,
        status: Status.DONE,
        current: {
            name: '',
            description: '',
            configs: [],
        },
    }),
    [RESET_PLAYLIST]: (state) => ({
        ...state,
        status: Status.PENDING,
        current: null,
    }),
    [SET_PLAYLIST]: (state, action) => ({
        ...state,
        status: Status.DONE,
        current: action.payload,
    }),

    [ADD_CONFIG]: (state) => {
        if (!state.current) {
            return state;
        }

        const configs = state.current.configs.slice();
        configs.push({
            configId: null,
            duration: 1.0,
        });
        return {
            ...state,
            current: {
                ...state.current,
                configs,
            }
        };
    },
    [DELETE_CONFIG]: (state, action) => {
        if (!state.current) {
            return state;
        }

        const configs = [];
        state.current.configs.forEach((config, index) => {
            if (index !== action.payload) {
                configs.push(config)
            }
        });
        return {
            ...state,
            current: {
                ...state.current,
                configs,
            }
        };
    },
    [MOVE_CONFIG_DOWN]: (state, action) => {
        if (!state.current) {
            return state;
        }
        if (action.payload < 0 || action.payload >= state.current.configs.length - 1) {
            return state;
        }

        const configs = state.current.configs.slice();
        const config = configs[action.payload];
        configs[action.payload] = configs[action.payload + 1];
        configs[action.payload + 1] = config;

        return {
            ...state,
            current: {
                ...state.current,
                configs,
            }
        };
    },
    [MOVE_CONFIG_UP]: (state, action) => {
        if (!state.current) {
            return state;
        }
        if (action.payload < 1 || action.payload > state.current.configs.length - 1) {
            return state;
        }

        const configs = state.current.configs.slice();
        const config = configs[action.payload];
        configs[action.payload] = configs[action.payload - 1];
        configs[action.payload - 1] = config;

        return {
            ...state,
            current: {
                ...state.current,
                configs,
            }
        };
    },
    [SET_CONFIG]: (state, action) => {
        if (!state.current) {
            return state;
        }

        const configs = state.current.configs.map((config, index) => {
            if (index === action.payload.index) {
                return {
                    ...config,
                    configId: action.payload.configId,
                };
            }
            return config;
        });
        return {
            ...state,
            current: {
                ...state.current,
                configs,
            },
        };
    },
    [SET_CONFIG_DURATION]: (state, action) => {
        if (!state.current) {
            return state;
        }

        const configs = state.current.configs.map((config, index) => {
            if (index === action.payload.index) {
                return {
                    ...config,
                    duration: action.payload.duration,
                };
            }
            return config;
        });
        return {
            ...state,
            current: {
                ...state.current,
                configs,
            },
        };
    },
    [SET_DESCRIPTION]: (state, action) => {
        if (!state.current) {
            return state;
        }

        return {
            ...state,
            current: {
                ...state.current,
                description: action.payload,
            }
        }
    },
    [SET_NAME]: (state, action) => {
        if (!state.current) {
            return state;
        }

        return {
            ...state,
            current: {
                ...state.current,
                name: action.payload,
            }
        }
    },

}, INITIAL_STATE);
