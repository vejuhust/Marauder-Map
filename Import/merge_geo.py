#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import json
import codecs


data_directory = "../Data/Internal/"
data_extension = ".txt"

line_info_filename = "Merged/line_info.json"
line_route_filename = "Merged/line_route.json"
station_filename = "Merged/station_all.json"


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


def convert_geo_line(geo_stop_time):
    station = {}
    for item in geo_stop_time:
        item_new = {
            "trip_id" : item["trip_id"],
            "station_id" : item["stop_id"],
            "dist" : item["shape_dist_traveled"],
            "shape_index" : item["stop_sequence"],
        }
        if item["trip_id"] not in station:
            station[ item["trip_id"] ] = [ item_new ]
        else:
            station[ item["trip_id"] ].append(item_new)
    return station


def search_sibling_route_index(given_id):
    id_set = set()
    for item in geo_trip:
        if (item["route_id"] == given_id) and (item["trip_id"] != given_id):
            id_set.add(item["trip_id"])
        elif (item["route_id"] != given_id) and (item["trip_id"] == given_id):
            id_set.add(item["route_id"])
    return list(id_set)


def search_route_index_by_name(keyword):
    if (not keyword.endswith(u"号")) and (not keyword.endswith(u"路")):
        keyword += u"路"
    lines = []
    for route in geo_route_index:
        if keyword in route["route_short_name"]:
            name = route["route_short_name"]
            route1_id = route["route_id"]
            route2_id = search_sibling_route_index(route1_id)[0]
            if route1_id > route2_id:
                route1_id, route2_id = route2_id, route1_id
            lines.append({"name" : name, "route1_id" : route1_id, "route2_id" : route2_id})
    return lines


def diff_station(m_station, g_station):
    pass


def diff_line(m_line, g_line):
    return "%d~%d" % (len(m_line), len(g_line))


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

    # Convert geo* data
    geo_station = convert_geo_station(geo_stop_list)
    geo_line = convert_geo_line(geo_stop_time)
    print len(geo_line)

    # Load existing data
    merged_line = load_json(line_info_filename)
    merged_route = load_json(line_route_filename)
    merged_station = load_json(station_filename)

    # Merge geo_* with merged_*
    for item in merged_route:
        m_line = merged_route[item]["list"]
        m_name = m_line["LName"]
        m_guid = m_line["LGUID"]
        m_direction = m_line["LDirection"]
        m_station = m_line["StandInfo"]
        candidate_route_index = search_route_index_by_name(m_name)
        print m_name, m_direction, m_guid, len(m_station), len(candidate_route_index)
        for item in candidate_route_index:
            print "\t", item["name"], item["route1_id"], diff_line(m_station, geo_line[item["route1_id"]])
            print "\t", item["name"], item["route2_id"], diff_line(m_station, geo_line[item["route2_id"]])

