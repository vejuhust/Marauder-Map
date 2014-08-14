#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
from datetime import datetime
from py2neo import cypher, neo4j, node, rel


input_station_filename = "station.json"
input_line_filename = "line.json"

graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")


LABEL_STATION = "Station"
LABEL_LINE = "Line"
REL_STATION_SIBLING = "SIBLING_STATION"
REL_LINE_SIBLING = "SIBLING_LINE"
REL_LINE_CONTAIN = "CONTAIN"
REL_STATION_CONNECT = "CONNECT_BY_"


def load_json(filename):
    file = open(filename, 'r')
    content = file.read()
    file.close()
    return json.loads(content)


def save_json(filename, data):
    file = open(filename, 'w')
    file.write(json.dumps(data, sort_keys = True, indent = 4, ensure_ascii = False).encode('utf-8'))
    file.close()


def database_reset():
    graph_db.clear()


def create_station_node(station_data):
    node_existed = graph_db.find(LABEL_STATION, property_key = "code", property_value = station_data["code"])
    if not list(node_existed):
        station_node = node(
            code = station_data["code"].upper().strip(),
            name = station_data["name"].strip(),
            lat = float(station_data["lat"]),
            long = float(station_data["long"]),
        )
        station_node, = graph_db.create(station_node)
        station_node.add_labels(LABEL_STATION)


def create_station_sibling_rel(code1, code2):
    station1, = graph_db.find(LABEL_STATION, property_key = "code", property_value = code1)
    station2, = graph_db.find(LABEL_STATION, property_key = "code", property_value = code2)
    graph_db.create(rel(station1, REL_STATION_SIBLING, station2))
    graph_db.create(rel(station2, REL_STATION_SIBLING, station1))


def create_line_node(line_data):
    node_existed = graph_db.find(LABEL_LINE, property_key = "id", property_value = line_data["id"])
    if not list(node_existed):
        line_node = node(
            id = line_data["id"].lower().strip(),
            title = line_data["name"].strip(),
            direction = line_data["route"][0]["station_name"].strip() + "=>" + line_data["route"][-1]["station_name"].strip(),
        )
        line_node, = graph_db.create(line_node)
        line_node.add_labels(LABEL_LINE)


def create_line_sibling_rel(id1, id2):
    line1, = graph_db.find(LABEL_LINE, property_key = "id", property_value = id1)
    line2, = graph_db.find(LABEL_LINE, property_key = "id", property_value = id2)
    graph_db.create(rel(line1, REL_LINE_SIBLING, line2))
    graph_db.create(rel(line2, REL_LINE_SIBLING, line1))


def create_line_station_rel(line_node, station_node, number):
    graph_db.create(rel(line_node, REL_LINE_CONTAIN, station_node, { "number" : number}))


def create_station_connect_rel(node1, node2, dist, line_id):
    graph_db.create(rel(node1, REL_STATION_CONNECT + line_id, node2, { "id" : line_id, "dist" : dist }))


def find_line_node(id):
    line, = graph_db.find(LABEL_LINE, property_key = "id", property_value = id)
    assert list(line), "line node '%s' missing" % guid
    return line


def find_station_node(code):
    station, = graph_db.find(LABEL_STATION, property_key = "code", property_value = code)
    assert list(station), "station node '%s' missing" % code
    return station


if __name__ == '__main__':
    # Load merged data
    dataset_station = load_json(input_station_filename)
    dataset_line = load_json(input_line_filename)

    # Check if loaded
    assert len(dataset_station) >= 21933, "fail to load dataset_station"
    assert len(dataset_line) >= 1279, "fail to load dataset_line"

    # Reset before create
    database_reset()

    # Create all station nodes
    for key in dataset_station:
        station = dataset_station[key]
        create_station_node(station)

    # Create rels for sibling station nodes
    station_sibling_set = set()
    for key1 in dataset_station:
        station1 = dataset_station[key1]
        if (key1 not in station_sibling_set) and ("sibling" in station1):
            key2 = station1["sibling"]
            if key2 not in station_sibling_set:
                create_station_sibling_rel(key1, key2)
                station_sibling_set.add(key1)
                station_sibling_set.add(key2)

    # Create all line nodes
    for key in dataset_line:
        line = dataset_line[key]
        create_line_node(line)

    # Create rels for sibling lines nodes
    line_sibling_set = set()
    for key1 in dataset_line:
        line1 = dataset_line[key1]
        if (key1 not in line_sibling_set) and ("sibling" in line1):
            key2 = line1["sibling"]
            if key2 not in line_sibling_set:
                create_line_sibling_rel(key1, key2)
                line_sibling_set.add(key1)
                line_sibling_set.add(key2)

    # Create rels from line nodes to station nodes and connected stations
    for key_line in dataset_line:
        line = dataset_line[key_line]
        line_node = find_line_node(line["id"])
        station_list = line["route"]
        previous_station = False
        previous_station_node = False
        for index, station in enumerate(station_list):
            station_node = find_station_node(station["station_code"])
            create_line_station_rel(line_node, station_node, index)
            if previous_station and previous_station_node:
                dist = float(station["dist"]) - float(previous_station["dist"])
                create_station_connect_rel(previous_station_node, station_node, dist, line["id"])
            previous_station = station
            previous_station_node = station_node
