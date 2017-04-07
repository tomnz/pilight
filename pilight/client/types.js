import {PropTypes} from 'react';

export const Color = PropTypes.shape({
    r: PropTypes.number.isRequired,
    g: PropTypes.number.isRequired,
    b: PropTypes.number.isRequired,
    w: PropTypes.number,
    a: PropTypes.number,
});

export const ParamDef = PropTypes.shape({
    type: PropTypes.string.isRequired,
    name: PropTypes.string,
    description: PropTypes.string,
});

export const AvailableTransform = PropTypes.shape({
    transform: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    description: PropTypes.string,
    paramsDef: PropTypes.objectOf(ParamDef),
});

export const ActiveTransform = PropTypes.shape({
    id: PropTypes.number.isRequired,
    transform: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    params: PropTypes.any,
    variableParams: PropTypes.objectOf(
        PropTypes.shape({
            variableId: PropTypes.number,
            multiply: PropTypes.number,
            add: PropTypes.number,
        }).isRequired,
    )
});

export const AvailableVariable = PropTypes.shape({
    variable: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    description: PropTypes.string,
    paramsDef: PropTypes.objectOf(ParamDef),
});

export const ActiveVariable = PropTypes.shape({
    id: PropTypes.number.isRequired,
    variable: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    params: PropTypes.any,
});
