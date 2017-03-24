import {createAction, handleActions} from 'redux-actions';

import {postObjectPromise} from './async';
import {setError} from './client';


const SET_ACTIVE_TRANSFORM = 'lights/SET_ACTIVE_TRANSFORM';
const SET_ACTIVE_TRANSFORMS = 'lights/SET_ACTIVE_TRANSFORMS';
const SET_AVAILABLE_TRANSFORMS = 'lights/SET_AVAILABLE_TRANSFORMS';

export const setActiveTransforms = createAction(SET_ACTIVE_TRANSFORMS);
export const setAvailableTransforms = createAction(SET_AVAILABLE_TRANSFORMS);
export const setActiveTransform = createAction(SET_ACTIVE_TRANSFORM, (id, transform) => ({
    id: id,
    transform: transform,
}));

export const addTransformAsync = (transform) => (dispatch) => {
    return postObjectPromise(
        `/api/transform/add/`,
        {transform: transform},
        (data) => {
            dispatch(setActiveTransforms(data.activeTransforms));
        },
        (error) => { dispatch(setError(error)); },
    );
};

export const deleteTransformAsync = (id) => (dispatch) => {
    return postObjectPromise(
        `/api/transform/delete/`,
        {id: id},
        (data) => {
            dispatch(setActiveTransforms(data.activeTransforms));
        },
        (error) => { dispatch(setError(error)); },
    );
};

export const updateTransformAsync = ({id, params}) => (dispatch) => {
    return postObjectPromise(
        `/api/transform/update/`,
        {id: id, params: params},
        (data) => {
            dispatch(setActiveTransform(id, data.transform));
        },
        (error) => { dispatch(setError(error)); },
    );
};

const INITIAL_STATE = {
    available: [],
    active: [],
};

export const transforms = handleActions({
    [SET_ACTIVE_TRANSFORMS]: (state, action) => ({...state, active: action.payload}),
    [SET_AVAILABLE_TRANSFORMS]: (state, action) => ({...state, available: action.payload}),
    [SET_ACTIVE_TRANSFORM]: (state, action) => {
        // Attempt to update the given id
        const newActive = state.active.map((transform) => {
            if (transform.id === action.payload.id) {
                return action.payload.transform;
            }
            return transform;
        });
        return {
            ...state,
            active: newActive,
        }
    }
}, INITIAL_STATE);
