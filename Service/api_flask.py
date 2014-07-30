#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
from flask import Flask
from flask.ext.jsonpify import jsonify
from datetime import datetime
from py2neo import cypher, neo4j, node, rel
from random import randint


app = Flask(__name__)


graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")

LABEL_STATION = "Station"
LABEL_LINE = "Line"
LABEL_BUS = "Bus"
REL_STATION_SIBLING = "SIBLING_STATION"
REL_LINE_SIBLING = "SIBLING_LINE"
REL_LINE_CONTAIN = "CONTAIN"
REL_STATION_CONNECT = "CONNECT_BY_"
REL_BUS_STATION = "STOP_AT"
REL_BUS_LINE = "SERVE_AT"


def save_json(filename, data):
    file = open(filename, 'w')
    file.write(json.dumps(data, sort_keys = True, indent = 4, ensure_ascii = False).encode('utf-8'))
    file.close()


# Convert time like "7:10:00" into Unix Timestamp
def string_to_timestamp(timestr, is_past = False):
    stamp_now = time.time()
    date_now = datetime.fromtimestamp(stamp_now)
    datestr = "%d-%d-%dT%s" % (date_now.year, date_now.month, date_now.day, timestr)
    date_target = datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%S')
    stamp_target = time.mktime(date_target.timetuple())
    if is_past:
        if stamp_target > stamp_now:
            stamp_target -= 24 * 60 * 60
    return stamp_target


# Template for API response
def response_template(line = [], bus = [], station = []):
    data = {
        "line_list" : line,
        "bus_list" : bus,
        "station_list" : station,
    }
    return jsonify(data)


# Merge shape arrays in a line into an array of dictionary
def merge_line_shape_array(line):
    shapes = []
    max_index = len(line["shape_station"])
    for index in range(max_index):
        shape = {
            "station" : line["shape_station"][index],
            "time" : line["shape_time"][index],
            "dist" : line["shape_dist"][index],
            "lat" : line["shape_lat"][index],
            "long" : line["shape_long"][index],
        }
        shapes.append(shape)
    line.pop("shape_station")
    line.pop("shape_time")
    line.pop("shape_dist")
    line.pop("shape_lat")
    line.pop("shape_long")
    line["shape"] = shapes
    return line


# Query for buses on the lines
def get_buses_serve_at_line(line_guid):
    buses = []
    collection = json.dumps(line_guid)
    query = neo4j.CypherQuery(graph_db, "MATCH (bus:%s)-[:%s]->(line:%s) WHERE line.guid in %s RETURN DISTINCT bus;" % (LABEL_BUS, REL_BUS_LINE, LABEL_LINE, collection))
    for record in query.stream():
        dict = record.values[0].get_properties()
        dict["arrival_time"] = string_to_timestamp(dict["arrival_time"], True)
        buses.append(dict)
    return buses


# Query for 5 nearest stations
def get_stations_nearest(lat, long, limit = 5):
    stations = []
    query = neo4j.CypherQuery(graph_db, "MATCH (n:%s) RETURN DISTINCT n ORDER BY ABS(n.geo_lat-%f) + ABS(n.geo_long-%f) LIMIT %d;" % (LABEL_STATION, lat, long, limit))
    for record in query.stream():
        dict = record.values[0].get_properties()
        stations.append(dict)
    return stations


# Query for stations on the line
def get_stations_containded_by_line(line_guid):
    stations = []
    collection = json.dumps(line_guid)
    query = neo4j.CypherQuery(graph_db, "MATCH (line:%s)-[:%s]->(station:%s) WHERE line.guid in %s RETURN DISTINCT station;" % (LABEL_LINE, REL_LINE_CONTAIN, LABEL_STATION, collection))
    for record in query.stream():
        dict = record.values[0].get_properties()
        stations.append(dict)
    return stations


# Query for at most 20 lines contains the stations
def get_lines_contains_stations(stations_code, limit = 20):
    lines = []
    collection = json.dumps(stations_code)
    query = neo4j.CypherQuery(graph_db, "MATCH (line:%s)-[:%s]->(station:%s) WHERE station.code in %s RETURN DISTINCT line LIMIT %d;" % (LABEL_LINE, REL_LINE_CONTAIN, LABEL_STATION, collection, limit))
    for record in query.stream():
        dict = record.values[0].get_properties()
        lines.append(merge_line_shape_array(dict))
    return lines


# Query for line by line.guid
def get_lines_by_guid(guid):
    lines = []
    query = neo4j.CypherQuery(graph_db, "MATCH (line:%s) WHERE line.guid = '%s' RETURN DISTINCT line;" % (LABEL_LINE, guid))
    for record in query.stream():
        dict = record.values[0].get_properties()
        lines.append(merge_line_shape_array(dict))
    return lines


# Query for line by line.name
def get_lines_by_name(name):
    lines = []
    query = neo4j.CypherQuery(graph_db, "MATCH (line:%s) WHERE line.name = '%s' RETURN DISTINCT line;" % (LABEL_LINE, name))
    for record in query.stream():
        dict = record.values[0].get_properties()
        lines.append(merge_line_shape_array(dict))
    return lines


# API : Search stations nearby
@app.route('/api/near_station/<float:lat>/<float:long>')
def search_station_nearby(lat, long):
    stations = get_stations_nearest(lat, long)
    stations_code = [ station["code"] for station in stations ]
    lines = get_lines_contains_stations(stations_code)
    lines_guid = [ line["guid"] for line in lines ]
    buses = get_buses_serve_at_line(lines_guid)
    return response_template(station = stations, line = lines, bus = buses)


# API : Search buses nearby
@app.route('/api/near_bus/<float:lat>/<float:long>')
def search_bus_nearby(lat, long):
    stations = get_stations_nearest(lat, long)
    stations_code = [ station["code"] for station in stations ]
    lines = get_lines_contains_stations(stations_code)
    lines_guid = [ line["guid"] for line in lines ]
    buses = get_buses_serve_at_line(lines_guid)
    return response_template(station = stations, line = lines, bus = buses)


# API : Search a line by guid
@app.route('/api/line/guid/<guid>')
def search_by_line_guid(guid):
    stations = get_stations_containded_by_line([ guid ])
    lines = get_lines_by_guid(guid)
    buses = get_buses_serve_at_line([ guid ])
    return response_template(station = stations, line = lines, bus = buses)


# API : Search a line by name
@app.route('/api/line/name/<name>')
def search_by_line_name(name):
    stations = []
    lines = get_lines_by_name(name)
    lines_guid = [ line["guid"] for line in lines ]
    stations = get_stations_containded_by_line(lines_guid)
    buses = get_buses_serve_at_line(lines_guid)
    return response_template(station = stations, line = lines, bus = buses)


# API : Alert me
@app.route('/api/alert/<code>/<guid>/<phone>')
def alert_me_message(code, guid, phone):
    if phone.isdigit():
        msg = u"Okay! I'll reminder you 10 minutes before the bus arrives."
    else:
        msg = u"Please input a valid phone number!"
    response = {
        "msg" : msg,
        "guid" : guid,
        "code" : code,
        "feel_lucky" : randint(1, 100),
        "time" : time.time(),
    }
    return jsonify(response)


if __name__ == "__main__":
    app.debug = True
    app.run(host = '127.0.0.1', port = 8090)


"""
http://localhost:8090/api/near_station/31.263931/120.730325
http://localhost:8090/api/near_bus/31.263931/120.730325
http://localhost:8090/api/line/guid/e31d7bb3-ba4c-4e24-85e8-95e9d0f4d49e
http://localhost:8090/api/line/name/115
"""


