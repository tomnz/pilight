let CopyWebpackPlugin = require('copy-webpack-plugin');
let HtmlWebpackPlugin = require('html-webpack-plugin');
let path = require('path');


if (process.argv.indexOf('-p') !== -1) {
    console.log('Using production config!');
    module.exports = {
        entry: path.resolve(__dirname, 'client/Index.jsx'),

        output: {
            path: path.resolve(__dirname, 'home/static'),
            filename: 'app.bundle.js'
        },

        resolve: {
            extensions: ['.js', '.jsx']
        },

        module: {
            rules: [{
                test: /\.jsx?$/,
                exclude: /node_modules/,
                use: [{
                    loader: 'babel-loader',
                    options: {
                        presets: [
                            ['es2015', {modules: false}],
                            'react',
                            'stage-0'
                        ],
                    }
                }]
            }, {
                test: /\.scss$/,
                use: [{
                    // Create style nodes from JS strings
                    loader: 'style-loader'
                }, {
                    // Translate CSS into CommonJS
                    loader: 'css-loader', options: {
                        module: true,
                        importLoaders: 1,
                    }
                }, {
                    // Compile SASS to CSS
                    loader: 'sass-loader', options: {
                        outputStyle: 'compressed',
                    }
                }]
            }]
        },

        plugins: [
            new CopyWebpackPlugin([{
                from: path.resolve(__dirname, 'client/static'),
                to: path.resolve(__dirname, 'home/static')
            }])
        ],
    };
} else {
    console.log('Using development config!');
    module.exports = {
        entry: path.resolve(__dirname, 'client/Index.jsx'),
        devtool: "source-map",

        output: {
            path: path.resolve(__dirname, 'home/static'),
            filename: 'app.bundle.js'
        },

        resolve: {
            extensions: ['.js', '.jsx']
        },

        module: {
            rules: [{
                test: /\.jsx?$/,
                exclude: /node_modules/,
                use: [{
                    loader: 'react-hot-loader'
                }, {
                    loader: 'babel-loader',
                    options: {
                        sourceMap: true,
                        presets: [
                            'es2015',
                            'react',
                            'stage-0'
                        ],
                    }
                }]
            }, {
                test: /\.scss$/,
                use: [{
                    // Create style nodes from JS strings
                    loader: 'style-loader'
                }, {
                    // Translate CSS into CommonJS
                    loader: 'css-loader', options: {
                        sourceMap: true,
                        module: true,
                        importLoaders: 1,
                    }
                }, {
                    // Compile SASS to CSS
                    loader: 'sass-loader', options: {
                        sourceMap: true,
                        outputStyle: 'compressed',
                    }
                }]
            }]
        },

        plugins: [
            new HtmlWebpackPlugin({
                template: path.resolve(__dirname, 'client/index.html'),
                filename: 'index.html',
                inject: 'body'
            }),
            new CopyWebpackPlugin([{
                from: path.resolve(__dirname, 'client/static'),
                to: path.resolve(__dirname, 'home/static')
            }])
        ],

        devServer: {
            proxy: {
                "/api/*": {
                    host: "localhost:8081",
                    target: "http://localhost:8000",
                    proxyTimeout: 2000,
                },
            },
        },
    };
}
