var $ = require('jquery'); 
var React = require('react');
var ReactDOM = require('react-dom');
var createReactClass = require('create-react-class');
var MapDiv = require('./MapDiv');

ReactDOM.render(
    <MapDiv />,
    document.getElementById('mapDiv')
    );