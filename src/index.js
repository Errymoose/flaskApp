var $ = require('jquery'); 
var React = require('react');
var ReactDOM = require('react-dom');
var createReactClass = require('create-react-class');
var Map = require('./map');

ReactDOM.render(
    <Map />,
    document.getElementById('mapDiv')
    );