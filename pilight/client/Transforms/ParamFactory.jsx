import React, {PropTypes} from 'react';

import {Boolean} from './Params/Boolean';
import {Color} from './Params/Color';
import {Float} from './Params/Float';
import {Long} from './Params/Long';
import {Percent} from './Params/Percent';
import {String} from './Params/String';


class ParamFactory extends React.Component {
    render() {
        switch (this.props.paramDef.type) {
            case 'boolean':
                return (
                    <Boolean
                        onChange={this.props.onChange}
                        value={this.props.value}
                    />
                );
                break;
            case 'color':
                return (
                    <Color
                        onChange={this.props.onChange}
                        value={this.props.value}
                    />
                );
                break;
            case 'float':
                return (
                    <Float
                        onChange={this.props.onChange}
                        origValue={this.props.origValue}
                        value={this.props.value}
                    />
                );
                break;
            case 'long':
                return (
                    <Long
                        onChange={this.props.onChange}
                        origValue={this.props.origValue}
                        value={this.props.value}
                    />
                );
                break;
            case 'percent':
                return (
                    <Percent
                        onChange={this.props.onChange}
                        origValue={this.props.origValue}
                        value={this.props.value}
                    />
                );
                break;
            case 'string':
                return (
                    <String
                        onChange={this.props.onChange}
                        origValue={this.props.origValue}
                        value={this.props.value}
                    />
                );
                break;
            default:
                return (
                    <div>
                        Unknown type: {this.props.paramDef.type}
                    </div>
                );
        }
    }
}

ParamFactory.propTypes = {
    onChange: PropTypes.func.isRequired,
    origValue: PropTypes.any.isRequired,
    paramDef: PropTypes.shape({
        name: PropTypes.string.isRequired,
        description: PropTypes.string,
        type: PropTypes.string.isRequired,
    }).isRequired,
    value: PropTypes.any.isRequired,
};

export {ParamFactory};
