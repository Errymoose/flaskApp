#!/usr/bin/python3

from __future__ import print_function
import sys
import sqlite3
import os
from flask import Flask, request
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

class Map(object):
    def __init__(self, isHeatmap = False):
        self._points = []
        self._isHeatmap = isHeatmap

    def add_point(self, coordinates):
        self._points.append(coordinates)
    def __str__(self):
        if len(self._points) > 0:
            centerLat = sum(( x[0] for x in self._points )) / len(self._points)
            centerLon = sum(( x[1] for x in self._points )) / len(self._points)
        else:
            centerLat = -33.8805995
            centerLon = 150.9983954

        markersCode = "\n".join(
            [ """{{\n
                "lat": "{lat}",\n
                "lon": "{lon}",\n
                "name": "{name}",\n
                "iv": "{iv}",\n
                "cp": "{cp}",\n
                "lvl": "{lvl}"\n
                }},\n""".format(lat=x[0], lon=x[1], name=x[2], iv=x[3], cp=x[4], lvl=x[5]) for x in self._points
            ])
        return '{\n"markers" : [\n' + markersCode[:-2] + '\n]\n}'            
        
        # markersCode = "\n".join(
        #     [ """new google.maps.Marker({{
        #         position: new google.maps.LatLng({lat}, {lon}),
        #         map: map,
        #         title: '{name} - {iv}% iv - {cp} CP - Level {lvl}' 
        #         }});""".format(lat=x[0], lon=x[1], name=x[2], iv=x[3], cp=x[4], lvl=x[5]) for x in self._points
        #     ])
        
        # heatmapData = '\n'.join(
        #     [                
        #         '{{ location: new google.maps.LatLng({lat}, {lon}), weight: 1 }},'.format(lat=x[0], lon=x[1]) for x in self._points
        #     ])

        # print(heatmapData[1:-1])

        # heatmapCode = '''
        #     let heatmapData = [
        #         ''' + heatmapData[:-1] + '''
        #     ];
        #     let heatmap = new google.maps.visualization.HeatmapLayer({
        #         data: heatmapData,
        #         radius: 20,
        #     });
        #     heatmap.setMap(map);'''

        # print(heatmapCode)

        # return """
        #     <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDL9B_RTJE3WI1Eqqt9TOoCbSVRCnhjFL4&libraries=visualization"></script>
        #     <div id="map-canvas" style="height: 100%; width: 100%"></div>
        #     <script type="text/javascript">
        #         var map;
        #         function show_map() {{
        #             map = new google.maps.Map(document.getElementById("map-canvas"), {{
        #                 zoom: 12,
        #                 center: new google.maps.LatLng({centerLat}, {centerLon})
        #             }});
        #             {mapcode}
        #         }};
        #         google.maps.event.addDomListener(window, 'load', show_map);
        #     </script>
        # """.format(centerLat=centerLat, centerLon=centerLon,
        #  mapcode=heatmapCode if self._isHeatmap else markersCode)


def findPokemonByName(cur, name):
    cur.execute('select * from pokemon where name = "%s"' % name)
    p = cur.fetchone()
    return p[0]
        
def encountersByName(cur, name, cp_limit, iv_limit, lvl_limit, time_limit):
    id = findPokemonByName(cur, name)
    if time_limit > 0:
        time_function = ' and datetime >= datetime("now", "-%d minutes")' % time_limit
    else:
        time_function = ''
    cur.execute('select * from encounters where id = %d and cp >= %d and iv >= %d and lvl >=%d%s' %(id, cp_limit, iv_limit, lvl_limit, time_function))
    return cur.fetchall()
    
@app.route("/map/<pokemon>")
def genMap(pokemon):
    iv_limit = 0
    if 'iv_limit' in request.args:
        iv_limit = int(request.args.get('iv_limit'))
    
    time_limit = 0
    if 'time_limit' in request.args:
        time_limit = int(request.args.get('time_limit'))

    cp_limit = 0
    if 'cp_limit' in request.args:
        cp_limit = int(request.args.get('cp_limit'))

    lvl_limit = 0
    if 'lvl_limit' in request.args:
        lvl_limit = int(request.args.get('lvl_limit'))


    map = Map()
    con = sqlite3.connect('pokemon.db')
    with con:
        cur = con.cursor()
        e = encountersByName(cur, pokemon, cp_limit, iv_limit, lvl_limit, time_limit)
        for item in e:
            map.add_point((float(item[2]), float(item[3]), pokemon, item[4], item[5], item[6]))

        return str(map)


@app.route("/heatmap/<pokemon>")
def genHeatMap(pokemon):
    iv_limit = 0
    if 'iv_limit' in request.args:
        iv_limit = int(request.args.get('iv_limit'))
    
    time_limit = 0
    if 'time_limit' in request.args:
        time_limit = int(request.args.get('time_limit'))

    cp_limit = 0
    if 'cp_limit' in request.args:
        cp_limit = int(request.args.get('cp_limit'))

    lvl_limit = 0
    if 'lvl_limit' in request.args:
        lvl_limit = int(request.args.get('lvl_limit'))


    map = Map(True)
    con = sqlite3.connect('pokemon.db')
    with con:
        cur = con.cursor()
        e = encountersByName(cur, pokemon, cp_limit, iv_limit, lvl_limit, time_limit)
        for item in e:
            print(item[2], item[3])
            map.add_point((float(item[2]), float(item[3]), pokemon, item[4], item[5], item[6]))

        return str(map)

@app.route("/getPokemonNames")
def getNames():
    con = sqlite3.connect('pokemon.db')
    with con:
        cur = con.cursor()
        cur.execute('select name from pokemon')
        p = cur.fetchall()
        return json.dumps(p)
        

if __name__ == '__main__':
    #call the functions here
    app.run(host='0.0.0.0')
