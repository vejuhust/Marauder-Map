#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import json
import codecs


data_directory = "../Data/Internal/"
data_extension = ".txt"


def load_json(filename):
    file = open(filename, 'r')
    content = file.read()
    file.close()
    return json.loads(content)


def load_csv(filename):
    # Read file
    file = codecs.open(filename, 'r', encoding='utf-8')
    lines = file.readlines()
    file.close()
    # Convert into list
    fields = [item.strip() for item in lines[0].lstrip(u"\ufeff").strip().split(",")]
    data = []
    for line in lines[1:]:
        item = {}
        values = line.strip().split(",")
        for index, value in enumerate(values):
            item[ fields[index] ] = value.strip()
        data.append(item)
    # Return result
    return data


def save_file(filename, data):
    file = open(filename, 'w')
    file.write(json.dumps(data, sort_keys = True, indent = 4, ensure_ascii = False).encode('utf-8'))
    file.close()


def convert_geo_station(geo_stop_list):
    station = {}
    for item in geo_stop_list:
        station[ item["stop_id"] ] = {
            "code" : item["stop_id"],
            "name" : item["stop_name"],
            "lat" : item["stop_lat"],
            "long" : item["stop_lon"],
            "parent" : item["parent_station"]
        }
    return station


def connect_sibling_station(station1):
    station1_id = station1["code"]
    parent = station1["parent"]
    for item in geo_station:
        station2 = geo_station[item]
        if (station1["parent"] == station2["parent"]) and (station1["name"] == station2["name"]) and (station1["code"] != station2["code"]):
            if "sibling" not in station1:
                station1["sibling"] = station2["code"]
            if "sibling" not in station2:
                station2["sibling"] = station1["code"]
            break


def convert_geo_line(geo_stop_time):
    line = {}
    for item in geo_stop_time:
        item_new = {
            "station_code" : item["stop_id"],
            "station_name" : geo_station[item["stop_id"]]["name"],
            "dist" : item["shape_dist_traveled"],
            "shape_index" : item["stop_sequence"],
        }
        if item["trip_id"] not in line:
            line[ item["trip_id"] ] = { "route" : [ item_new ], "id" : item["trip_id"] }
        else:
            line[ item["trip_id"] ]["route"].append(item_new)
    return line


def extract_geo_line_name(geo_line):
    for item in geo_route_index:
        id = item["route_id"]
        name = item["route_short_name"]
        geo_line[id]["name"] = name
    return geo_line


def connect_sibling_line(line1):
    parent_id = ""
    for item in geo_trip:
        if item["trip_id"] == line1["id"]:
            parent_id = item["route_id"]
            break
    if len(parent_id) > 0:
        line2 = False
        for item in geo_trip:
            if (item["route_id"] == parent_id) and (item["trip_id"] != line1["id"]):
                line2 = geo_line[item["trip_id"]]
                break
        if line2:
            if ("name" in line1) and ("name" not in line2):
                line2["name"] = line1["name"]
            elif ("name" not in line1) and ("name" in line2):
                line1["name"] = line2["name"]
            if "sibling" not in line1:
                line1["sibling"] = line2["id"]
            if "sibling" not in line2:
                line2["sibling"] = line1["id"]


if __name__ == '__main__':
    # Load all the data
    data_all = {}
    for filename in os.listdir(data_directory):
        if filename.endswith(data_extension):
            name = filename[:-len(data_extension)]
            data_all[name] = load_csv(data_directory + filename)

    # Keep what we need
    geo_freq = data_all["frequencies"]
    geo_route_index = data_all["routes"]
    geo_shape = data_all["shapes"]
    geo_stop_time = data_all["stop_times"]
    geo_stop_list = data_all["stops"]
    geo_trip = data_all["trips"]

    # Preview the result
    names = ['geo_freq', 'geo_route_index', 'geo_shape', 'geo_stop_time', 'geo_stop_list', 'geo_trip']
    for name in names:
        print name, len(eval(name)), json.dumps(eval(name)[0], indent = 4, sort_keys = True)

    # Get basic station info
    geo_station = convert_geo_station(geo_stop_list)

    # Connect siblings in geo_station
    for key in geo_station:
        station = geo_station[key]
        if "sibling" not in station:
            connect_sibling_station(station)

    # Get basic route info for each line
    geo_line = convert_geo_line(geo_stop_time)

    # Get name for each line
    geo_line = extract_geo_line_name(geo_line)

    # Connect siblings in geo_line
    for key in geo_line:
        line = geo_line[key]
        if "sibling" not in line:
            connect_sibling_line(line)

    # Save geo_line
    print "line:", len(geo_line)
    save_file("line.json", geo_line)

    # Save geo_station
    print "station:", len(geo_station)
    save_file("station.json", geo_station)
