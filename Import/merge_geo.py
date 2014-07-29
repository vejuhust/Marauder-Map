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


def save_file(filename, data):
    file = open(filename, 'w')
    file.write(json.dumps(data, sort_keys = True, indent = 4, ensure_ascii = False).encode('utf-8'))
    file.close()


def convert_geo_station(geo_stop_list):
    station = {}
    for item in geo_stop_list:
        station[ item["stop_id"] ] = {
            "station_id" : item["stop_id"],
            "name" : item["stop_name"],
            "lat" : item["stop_lat"],
            "long" : item["stop_lon"],
            "parent" : item["parent_station"]
        }
    return station


def convert_geo_line(geo_stop_time):
    station = {}
    for item in geo_stop_time:
        item_new = {
            "trip_id" : item["trip_id"],
            "station_id" : item["stop_id"],
            "station_name" : geo_station[item["stop_id"]]["name"],
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
    m_name = m_station["SName"]
    g_name = g_station["station_name"]
    len_m = len(m_name)
    len_g = len(g_name)
    min_len = len_m if len_m <= len_g else len_g
    result = False if m_name[:min_len] == g_name[:min_len] else True
    return result


def diff_station_count(m_line, g_line, display = False):
    counter = 0
    len_m = len(m_line)
    len_g = len(g_line)
    max_index = len_m if len_m <= len_g else len_g
    for index in range(max_index):
        is_diff = diff_station(m_line[index], g_line[index])
        if is_diff:
            counter += 1
        if display:
            mark = "[x]" if is_diff else "[ ]"
            print "\t %s %s %s" % (mark, m_line[index]["SName"], g_line[index]["station_name"])

    return counter


def connect_sibling_station(station1):
    station1_id = station1["station_id"]
    parent = station1["parent"]
    for item in geo_station:
        station2 = geo_station[item]
        if (station1["parent"] == station2["parent"]) and (station1["name"] == station2["name"]) and (station1["station_id"] != station2["station_id"]):
            station1["sibling"] = station2["station_id"]
            station2["sibling"] = station1["station_id"]
            break


def merge_station(m_station, g_station):
    g_station = geo_station[g_station["station_id"]]
    g_station["code"] = m_station["SCode"]
    m_station = merged_station[m_station["SCode"]]
    m_station["geo_station_id"] = g_station["station_id"]
    m_station["geo_lat"] = g_station["lat"]
    m_station["geo_long"] = g_station["long"]
    connect_sibling_station(g_station)


def merge_line_station(m_line, g_line):
    counter = 0
    len_m = len(m_line)
    len_g = len(g_line)
    max_index = len_m if len_m <= len_g else len_g
    for index in range(max_index):
        merge_station(m_line[index], g_line[index])


def merge_line_shape(m_line, g_line):
    trip_id = m_line["geo_line_id"]
    shapes = []
    for shape in geo_shape:
        if shape["shape_id"] == trip_id:
            shapes.append(shape)
    for station in g_line:
        for shape in shapes:
            if int(station["shape_index"]) == int(shape["shape_pt_sequence"]):
                shape["shape_station"] = station["station_id"]
                shape["shape_code"] = geo_station[station["station_id"]]["code"]
                break
    m_line["shape"] = shapes


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

    # Load existing data
    merged_line = load_json(line_info_filename)
    merged_route = load_json(line_route_filename)
    merged_station = load_json(station_filename)

    # Match route_id and merged_line by station name
    for item in merged_route:
        # Basic info of merged_line
        m_line = merged_route[item]["list"]
        m_name = m_line["LName"]
        m_guid = m_line["LGUID"]
        m_direction = m_line["LDirection"]
        m_station = m_line["StandInfo"]
        # Search for similar geo_line
        candidate_route_index = search_route_index_by_name(m_name)
        #print m_name, m_direction, m_guid, len(m_station), len(candidate_route_index)
        match_id = ""
        match_name = ""
        match_diff = len(m_station)
        # Compare the similarity
        for item in candidate_route_index:
            for route_id in [item["route1_id"], item["route2_id"]]:
                diff_count = diff_station_count(m_station, geo_line[route_id])
                if diff_count < match_diff:
                    match_diff = diff_count
                    match_id = route_id
                    match_name = item["name"]
        if match_diff == 0:
            merged_line[m_guid]["geo_line_id"] = match_id

    # Merge the stations in matched lines
    for item in merged_line:
        line = merged_line[item]
        if "geo_line_id" in line:
            m_line = merged_route[line["guid"]]["list"]["StandInfo"]
            g_line = geo_line[line["geo_line_id"]]
            merge_line_station(m_line, g_line)
            merge_line_shape(line, g_line)

    # Merge merged_route into merged_line
    for item in merged_line:
        line = merged_line[item]
        if "geo_line_id" in line:
            station_list = merged_route[item]["list"]["StandInfo"]
            station_id = []
            for station in station_list:
                station_id.append(station["SCode"].upper().strip())
            line["station"] = station_id

#    # Save output
#    save_file("tmp_geo_station.json", geo_station)
#    save_file("tmp_geo_line.json", geo_line)
#    save_file("tmp_merged_station.json", merged_station)
#    save_file("tmp_merged_line.json", merged_line)
