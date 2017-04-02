import {createAction, handleActions} from 'redux-actions';

import {postObjectPromise} from './async';
import {setError} from './client';


const SET_ACTIVE_TRANSFORM = 'transforms/SET_ACTIVE_TRANSFORM';
const SET_ACTIVE_TRANSFORMS = 'transforms/SET_ACTIVE_TRANSFORMS';
const SET_AVAILABLE_TRANSFORMS = 'transforms/SET_AVAILABLE_TRANSFORMS';

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

export const updateTransformAsync = ({id, params, variableParams}) => (dispatch) => {
    return postObjectPromise(
        `/api/transform/update/`,
        {id: id, params: params, variableParams: variableParams},
        (data) => {
            dispatch(setActiveTransform(id, data.transform));
        },
        (error) => { dispatch(setError(error)); },
    );
};

export const moveTransformDownAsync = (id) => (dispatch, getState) => {
    const {transforms} = getState();

    // Figure out new order
    const ids = transforms.active.map((transform) => transform.id);
    const index = ids.findIndex((transformId) => transformId === id);
    if (index === -1 || index === ids.length - 1) {
        // No order change - item is not found, or already bottom
        return;
    }
    ids[index] = ids[index + 1];
    ids[index + 1] = id;

    postOrder(ids, dispatch);
};

export const moveTransformUpAsync = (id) => (dispatch, getState) => {
    const {transforms} = getState();

    // Figure out new order
    const ids = transforms.active.map((transform) => transform.id);
    const index = ids.findIndex((transformId) => transformId === id);
    if (index <= 0) {
        // No order change - item is not found, or already top
        return;
    }
    ids[index] = ids[index - 1];
    ids[index - 1] = id;

    postOrder(ids, dispatch);
};

function postOrder(ids, dispatch) {
    return postObjectPromise(
        `/api/transform/reorder/`,
        {order: ids},
        (data) => {
            dispatch(setActiveTransforms(data.activeTransforms));
        },
        (error) => { dispatch(setError(error)); },
    );
}


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
        };
    },
}, INITIAL_STATE);
