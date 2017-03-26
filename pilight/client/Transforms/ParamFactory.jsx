import React, {PropTypes} from 'react';


class ParamFactory extends React.Component {
    render() {
        return (
            <div>
                {this.props.paramDef.type}
                {this.props.value}
            </div>
        );
    }
}

ParamFactory.propTypes = {
    paramDef: PropTypes.shape({
        name: PropTypes.string.isRequired,
        description: PropTypes.string,
        type: PropTypes.string.isRequired,
    }).isRequired,
    value: PropTypes.any.isRequired,
};

export {ParamFactory};
