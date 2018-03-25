var $ = require('jquery'); 
var React = require('react');
var ReactDOM = require('react-dom');
var createReactClass = require('create-react-class');

module.exports = createReactClass({
    getInitialState: function() {
        return {
            pokemon: new Array(),
            markers: new Array(),
            curName: '',
            iv: 0,
            cp: 0,
            lvl: 0,
            timeLimit: 0,
            mapType: 'map',
            displayedMarkers: 0,
        };
    },

    componentDidMount: function() {
        var reactState = this;
        $.ajax({
            url: "http://john-medusa.bnr.la:5000/getPokemonNames",
            crossDomain: true,
            success: function(data) {
                let jsonData = JSON.parse(data);
                reactState.setState({
                    pokemon: jsonData,
                    curName: jsonData[0][0]
                });
            },
        });


    },

    markers: function(marker)
    {
        let m = new google.maps.Marker({
            position: new google.maps.LatLng(marker.lat, marker.lon),
            map: map,
            title: marker.name + ' - ' + marker.iv + '% iv - ' + marker.cp + ' CP - Level ' + marker.lvl 
            });
        markers.push(m);
    },

    heatmapPoints: function(marker)
    {
        let m = { 
            location : new google.maps.LatLng(marker.lat, marker.lon), 
            weight: 1 
        };
        markers.push(m);
    },

    createHeatmap: function(data) {
        data.markers.forEach(this.heatmapPoints);
        var newdata = new google.maps.MVCArray(markers);
        heatmap.set('data', newdata);
        heatmap.setMap(map);
    },

    clearMapData: function() {
        heatmap.set('data', null);
        heatmap.setMap(null);
        if(this.state.mapType == 'map') {
            markers.forEach(function(marker) {
                marker.setMap(null);
            });
        }

        markers = new Array();
    },

    toggleMapType: function(evt) {
        this.clearMapData();
        let newState = this.state.mapType == 'map' ? 'heatmap' : 'map';
        this.setState({'mapType' : newState});
        if(newState == 'map') {
            pointData.markers.forEach(this.markers);
        }
        else {
            this.createHeatmap(pointData);
        }
    },

    submit: function(evt) {
        evt.preventDefault();
        evt.stopPropagation();
        
        if(this.state.isBusy) {
            return false;
        }
        else {
            document.getElementById('loadingSpinner').className += 'loader';
            document.getElementById('filterButton').setAttribute('disabled','');
            document.getElementById('toggleHeatmap').setAttribute('disabled','');
            document.getElementById('filterButton').className += 'disabled';
            document.getElementById('toggleHeatmap').className += 'disabled';
            this.setState({
                status: 'Processing: Please Wait...',
                isBusy: true,
            });
            this.clearMapData();

            let react_state = this;
            $.ajax({
                url: "http://john-medusa.bnr.la:5000/" + this.state.mapType + "/" + this.state.curName + "?iv_limit=" + this.state.iv + "&cp_limit=" + this.state.cp + "&lvl_limit=" + this.state.lvl,
                crossDomain: true,
                success: function (data) {
                    pointData = JSON.parse(data);
                    
                    if(react_state.state.mapType == 'map') {
                        pointData.markers.forEach(react_state.markers);
                    }
                    else {
                        react_state.createHeatmap(pointData);
                    }

                    react_state.setState({
                        displayedMarkers: pointData.markers.length,
                        isBusy: false
                    });

                    document.getElementById('loadingSpinner').classList.remove('loader');
                    document.getElementById('filterButton').classList.remove('disabled');
                    document.getElementById('filterButton').removeAttribute('disabled');
                    document.getElementById('toggleHeatmap').removeAttribute('disabled');
                    document.getElementById('toggleHeatmap').classList.remove('disabled');
                },
            });
        }
    },

    handleChange: function(ev) {
        console.log('changed!');
        this.setState(
            {[ev.target.name]: ev.target.value}
        );
    },

    render: function() {
        return <div class='float-vertical'>
                <form id="genMapForm" onSubmit={this.submit}>
                    <textbox class="form-item">Filter by level (0-35)</textbox>
                    <div class="slideContainer form-item">
                        <input name="lvl" type="range" min="0" max="35" step="1" class="slider" id="lvlRange" defaultValue={this.state.lvl} onChange={this.handleChange} />
                        <p><textbox id="lvlLimit">{this.state.lvl}</textbox></p>
                    </div>
                    <textbox class="form-item">Filter by combat power (0-4000)</textbox>
                    <div class="slideContainer form-item">
                        <input name="cp" type="range" min="0" max="4000" step="50" class="slider" id="cpRange" defaultValue={this.state.cp} onChange={this.handleChange} />
                        <p><textbox id="cpLimit">{this.state.cp}</textbox></p>
                    </div>
                    
                    <textbox class="form-item">Filter by IV (0-100)</textbox>
                    <div class="slideContainer form-item">
                        <input name="iv" type="range" min="0" max="100" step="5" class="slider" id="ivRange" defaultValue={this.state.iv} onChange={this.handleChange} />
                        <p><textbox id="ivLimit">{this.state.iv}</textbox></p>
                    </div>

                    <select id="pokemonList" name="curName" onChange={this.handleChange}>
                        {this.state.pokemon.map(p => <option class="item" name={p} value={p}>{p}</option>)}
                    </select>
                    <br />
                    <div class="button-div">
                        <input id="filterButton" type="submit" value="Apply Filter" />
                    </div>
                    <div class="button-div">
                        <input id="toggleHeatmap" type="button" value="Toggle Heatmap/Points" onClick={this.toggleMapType} />
                    </div>
                    <div class="button-div">
                        <div id="loadingSpinner"/>
                    </div>  
                </form>
                <div>
                    <label id="response">data from {this.state.displayedMarkers} encounters with {this.state.curName}</label>
                </div>
            </div>;
    }
});