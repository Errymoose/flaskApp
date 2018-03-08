module.exports = createReactClass({
    getInitialState: function() {
        let pokemonList = [];
        $.ajax({
            url: "http://john-medusa.bnr.la:5000/getPokemonNames",
            success: function(data) {
                pokemonList = data;
            },
        });

        this.state = {
            pokemon: pokemonList,
            curName: '',
            ivLimit: 0,
            cpLimit: 0,
            lvlLimit: 0,
            timeLimit: 0,
            mapType: 'map'
        };
    },

    submit: function(evt) {
        $.ajax({
            url: "http://john-medusa.bnr.la:5000/{this.state.maptype}/{this.state.curName}?iv_limit={this.state.ivLimit}&cp_limit={this.sate.cpLimit}&lvl_limit={this.state.lvlLimit}",
            success: function (data) {
                console.log(data);
                $("#map-js").remove();
                elem = document.createElement("script");
                elem.type="text/javascript";
                elem.id="map-js";
                elem.innerText = data;
                $("#map-content").append(elem);
            },
        });
    },

    render: function() {
        let optionList = [];
        this.state.pokemonList.forEach(pokemon =>
            optionList.add(
                new Option(pokemon[0])
            )
        );

        return (
            <div>
                <form id="genMapForm" onSubmit={this.submit}>
                <div class="slideContainer">
                        <input type="range" min="0" max="35" value="{this.state.lvlLimit}" class="slider" id="lvlRange" />
                    </div>
                    <div class="slideContainer">
                        <input type="range" min="0" max="4000" value="{this.state.cpLimit}" class="slider" id="cpRange" />
                    </div>
                    <div class="slideContainer">
                        <input type="range" min="0" max="100" value="{this.state.ivLimit}" class="slider" id="ivRange" />
                    </div>
                    
                    <select name="pokemon">
                        {optionList}
                    </select>
                    
                    <input id="filterButton" type="submit" value="Apply Filter" /> 
                </form>

                <div id="mapData">
                    <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDL9B_RTJE3WI1Eqqt9TOoCbSVRCnhjFL4&libraries=visualization"></script>
                    <div id="map-canvas" style="height: 100%; width: 100%"></div>
                    <script type="text/javascript" id="map-js">
                    </script>
                </div>
            </div>
        );
    }
});
