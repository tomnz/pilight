import PropTypes from 'prop-types';
import React from 'react';

import {Boolean} from './Boolean';
import {Color} from './Color';
import {Float} from './Float';
import {Long} from './Long';
import {Percent} from './Percent';
import {String} from './String';


export default class Param extends React.Component {
    static propTypes = {
        onChange: PropTypes.func.isRequired,
        origValue: PropTypes.any.isRequired,
        paramDef: PropTypes.shape({
            name: PropTypes.string.isRequired,
            description: PropTypes.string,
            type: PropTypes.string.isRequired,
        }).isRequired,
        value: PropTypes.any.isRequired,
    };

    render() {
        switch (this.props.paramDef.type) {
            case 'boolean':
                return (
                    <Boolean
                        onChange={this.props.onChange}
                        value={this.props.value}
                    />
                );
            case 'color':
                return (
                    <Color
                        onChange={this.props.onChange}
                        value={this.props.value}
                    />
                );
            case 'float':
                return (
                    <Float
                        onChange={this.props.onChange}
                        origValue={this.props.origValue}
                        value={this.props.value}
                    />
                );
            case 'long':
                return (
                    <Long
                        onChange={this.props.onChange}
                        origValue={this.props.origValue}
                        value={this.props.value}
                    />
                );
            case 'percent':
                return (
                    <Percent
                        onChange={this.props.onChange}
                        origValue={this.props.origValue}
                        value={this.props.value}
                    />
                );
            case 'string':
                return (
                    <String
                        onChange={this.props.onChange}
                        origValue={this.props.origValue}
                        value={this.props.value}
                    />
                );
            default:
                return (
                    <div>
                        Unknown type: {this.props.paramDef.type}
                    </div>
                );
        }
    }
}
