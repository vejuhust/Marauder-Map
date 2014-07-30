#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import urllib2
import json
import time
import argparse
from py2neo import cypher, neo4j, node, rel


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

api_url_template = "http://content.2500city.com/Json?method=GetBusLineDetail&Guid=%s"


def load_parser():
    parser = argparse.ArgumentParser(description = "crawling status of bus lines")
    parser.add_argument("guid", help = "guid of the bus line", type = str, action = 'store')
    parser.add_argument("filename", help = "line name as output filename, w/o extension name", type = str, action = 'store')
    return parser.parse_args()


def save_json(filename, data, readable = False):
    file = open(filename, 'a')
    if readable:
        file.write(json.dumps(data, sort_keys = True, indent = 4, ensure_ascii = False).encode('utf-8') + "\n")
    else:
        file.write(json.dumps(data, ensure_ascii = False).encode('utf-8') + "\n")
    file.close()


def data_request(guid):
    result = {}
    url = api_url_template % guid
    # Send request
    time_start = time.time()
    request = urllib2.urlopen(url)
    response = request.read()
    time_end = time.time()
    request.close()
    # Process response
    result["call_latency"] = time_end - time_start
    data = json.loads(response)
    result["response"] = data
    return result


errata = [
    {
        "guid" : "e31d7bb3-ba4c-4e24-85e8-95e9d0f4d49e",
        "name" : u"上娄路",
        "code" : u"HFT",
    },
    {
        "guid" : "edc1ecd6-2bf8-4b08-8727-385bb8943b9d",
        "name" : u"上娄路",
        "code" : u"BZT",
    },
]
def correct_station_code(station, line_guid):
    for item in errata:
        if (item["guid"] == line_guid) and (item["name"] == station["SName"]):
            station["SCode"] = item["code"]
            break
    return station["SCode"].upper().strip()


def extract_bus_info(station, line_guid):
    bus = {
        "tag" : station["BusInfo"].upper().strip(),
        "arrival_time" : station["InTime"].strip(),
        "arrival_station" : correct_station_code(station, line_guid),
        "arrival_line" : line_guid.lower().strip()
    }
    return bus


def current_time_string():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ')


def get_line_node(guid):
    line, = graph_db.find(LABEL_LINE, property_key = "guid", property_value = guid)
    return line


def get_station_node(code):
    station, = graph_db.find(LABEL_STATION, property_key = "code", property_value = code)
    return station


def get_bus_node(tag):
    bus, = graph_db.find(LABEL_BUS, property_key = "tag", property_value = tag)
    return bus


def check_exist_bus_node(tag):
    query = neo4j.CypherQuery(graph_db, "MATCH (bus:%s) WHERE bus.tag = '%s' RETURN count(bus);" % (LABEL_BUS, tag))
    for record in query.stream():
        count = record.values[0]
    return count > 0


def create_bus_node(bus_data):
    bus_node = node(
        tag = bus_data["tag"],
        arrival_time = bus_data["arrival_time"],
        arrival_station = bus_data["arrival_station"],
        arrival_line = bus_data["arrival_line"],
        last_update = current_time_string(),
    )
    bus_node, = graph_db.create(bus_node)
    bus_node.add_labels(LABEL_BUS)
    return bus_node


def create_bus_line_rel(bus_node, line_node):
    graph_db.create(rel(bus_node, REL_BUS_LINE, line_node))


def create_bus_station_rel(bus_node, station_node):
    graph_db.create(rel(bus_node, REL_BUS_STATION, station_node))


def clear_bus_rels(tag):
    query = neo4j.CypherQuery(graph_db, "MATCH (bus:%s)-[r]->() WHERE bus.tag = '%s' DELETE r;" % (LABEL_BUS, tag))


def update_database_bus_info(bus):
    line_node = get_line_node(bus["arrival_line"])
    station_node = get_station_node(bus["arrival_station"])
    tag = bus["tag"]
    # Check if bus node exists
    if check_exist_bus_node(tag):
        # Get it and updates
        bus_node = get_bus_node(bus["tag"])
        bus_node["arrival_time"] = bus["arrival_time"]
        bus_node["arrival_station"] = bus["arrival_station"]
        bus_node["arrival_line"] = bus["arrival_line"]
        bus_node["last_update"] = current_time_string()
        clear_bus_rels(tag)
    else:
        # Create it
        bus_node = create_bus_node(bus)
    create_bus_line_rel(bus_node, line_node)
    create_bus_station_rel(bus_node, station_node)



if __name__ == '__main__':
    args = load_parser()
    output_call_filename = os.path.dirname(os.path.realpath(__file__)) + "/line_" + args.filename + ".txt"
    output_bus_filename = os.path.dirname(os.path.realpath(__file__)) + "/bus_" + args.filename + ".txt"

    # Request for route details with bus info
    try:
        data = data_request(args.guid)
    except Exception as e:
        data = { "call_error" : str(e) }
    finally:
        data["call_time"] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime())
        data["call_guid"] = args.guid

    save_json(output_call_filename, data)

    # Exit if request failed
    if "call_error" in data:
        exit(0)

    # Extract bus info from response
    line_guid = data["response"]["list"]["LGUID"]
    station_list = data["response"]["list"]["StandInfo"]
    station_with_bus = [ station for station in station_list if station["BusInfo"] ]
    bus_list = [ extract_bus_info(station, line_guid) for station in station_with_bus ]

    # Update bus info in database
    for bus in bus_list:
        update_database_bus_info(bus)

    save_json(output_bus_filename, bus_list)

