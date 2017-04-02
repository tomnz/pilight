import {createAction, handleActions} from 'redux-actions';

import {postObjectPromise} from './async';
import {setError} from './client';
import {setActiveTransforms} from './transforms';


const SET_ACTIVE_VARIABLE = 'variables/SET_ACTIVE_VARIABLE';
const SET_ACTIVE_VARIABLES = 'variables/SET_ACTIVE_VARIABLES';
const SET_AVAILABLE_VARIABLES = 'variables/SET_AVAILABLE_VARIABLES';

export const setActiveVariables = createAction(SET_ACTIVE_VARIABLES);
export const setAvailableVariables = createAction(SET_AVAILABLE_VARIABLES);
export const setActiveVariable = createAction(SET_ACTIVE_VARIABLE, (id, variable) => ({
    id: id,
    variable: variable,
}));

export const addVariableAsync = (variable) => (dispatch) => {
    return postObjectPromise(
        `/api/variable/add/`,
        {variable: variable},
        (data) => {
            dispatch(setActiveVariables(data.activeVariables));
        },
        (error) => { dispatch(setError(error)); },
    );
};

export const deleteVariableAsync = (id) => (dispatch) => {
    return postObjectPromise(
        `/api/variable/delete/`,
        {id: id},
        (data) => {
            dispatch(setActiveVariables(data.activeVariables));
            dispatch(setActiveTransforms(data.activeTransforms));
        },
        (error) => { dispatch(setError(error)); },
    );
};

export const updateVariableAsync = ({id, name, params}) => (dispatch) => {
    return postObjectPromise(
        `/api/variable/update/`,
        {id: id, name: name, params: params},
        (data) => {
            dispatch(setActiveVariable(id, data.variable));
        },
        (error) => { dispatch(setError(error)); },
    );
};


const INITIAL_STATE = {
    available: [],
    active: [],
    activeByType: {},
};

export const variables = handleActions({
    [SET_ACTIVE_VARIABLES]: (state, action) => {
        // Map variables by type
        const newActiveByType = {};
        action.payload.forEach((variable) => {
            if (!newActiveByType.hasOwnProperty(variable.type)) {
                newActiveByType[variable.type] = [];
            }
            newActiveByType[variable.type].push({
                id: variable.id,
                name: variable.name,
            });
        });
        return {
            ...state,
            active: action.payload,
            activeByType: newActiveByType,
        }
    },
    [SET_ACTIVE_VARIABLE]: (state, action) => {
        // Attempt to update the given id
        const newActive = state.active.map((variable) => {
            if (variable.id === action.payload.id) {
                return action.payload.variable;
            }
            return variable;
        });
        return {
            ...state,
            active: newActive,
        };
    },
    [SET_AVAILABLE_VARIABLES]: (state, action) => ({...state, available: action.payload}),
}, INITIAL_STATE);
