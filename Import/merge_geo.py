#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import json
import codecs

data_directory = "../Data/Internal/"
data_extension = ".txt"

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


def convert_geo_station(geo_stop_list):
    station = {}
    for item in geo_stop_list:
        station[ item["stop_id"] ] = {
            "station_id" : item["stop_id"],
            "name" : item["stop_name"],
            "lat" : item["stop_lat"],
            "long" : item["stop_lon"],
            "sibling" : item["parent_station"]
        }
    return station


def search_sibling_line(given_id):
    id_set = set()
    for item in geo_trip:
        if (item["route_id"] == given_id) and (item["trip_id"] != given_id):
            id_set.add(item["trip_id"])
        elif (item["route_id"] != given_id) and (item["trip_id"] == given_id):
            id_set.add(item["route_id"])
    return list(id_set)


def search_line_by_name(keyword):
    lines = []
    for route in geo_route:
        if keyword in route["route_short_name"]:
            name = route["route_short_name"]
            route_id = route["route_id"]
            route2_id = search_sibling_line(route_id)[0]
            if route_id > route2_id:
                route_id, route2_id = route2_id, route_id
            lines.append({"name" : name, "line_id1" : route_id, "line_id2" : route2_id})
    return lines


def list_line_station(line_id):
    count = 0
    for item in geo_stop_time:
        if item["trip_id"] == line_id:
            count += 1
            print count, item["stop_sequence"], item["shape_dist_traveled"], item["stop_id"], geo_station[item["stop_id"]]["name"]


def list_line_by_name(name):
    # Search lines by name
    result_lines = search_line_by_name(name + u"路")
    print json.dumps(result_lines, indent = 4)
    # List all stations on the line 1
    print "\n", result_lines[-1]['name'], result_lines[-1]['line_id1']
    result_stations = list_line_station(result_lines[-1]['line_id1'])
    # List all stations on the line 2
    print "\n", result_lines[-1]['name'], result_lines[-1]['line_id2']
    result_stations = list_line_station(result_lines[-1]['line_id2'])


if __name__ == '__main__':
    # Load all the data
    data_all = {}
    for filename in os.listdir(data_directory):
        if filename.endswith(data_extension):
            name = filename[:-len(data_extension)]
            data_all[name] = load_csv(data_directory + filename)
    # Keep what we need
    geo_freq = data_all["frequencies"]
    geo_route = data_all["routes"]
    geo_shape = data_all["shapes"]
    geo_stop_time = data_all["stop_times"]
    geo_stop_list = data_all["stops"]
    geo_trip = data_all["trips"]
    # Preview the result
    names = ['geo_freq', 'geo_route', 'geo_shape', 'geo_stop_time', 'geo_stop_list', 'geo_trip']
    for name in names:
        print name, len(eval(name)), json.dumps(eval(name)[0], indent = 4, sort_keys = True)
    # Convert geo* data
    geo_station = convert_geo_station(geo_stop_list)

    # Search
    list_line_by_name(u"128")


