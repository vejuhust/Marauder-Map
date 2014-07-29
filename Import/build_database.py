#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
from datetime import datetime
from py2neo import cypher, neo4j, node, rel

"""
USEFUL CYPHERS
    
delete all:
match (n)-[r]->() delete n,r;
match (n) delete n;


"""


input_station_filename = "Merged/geo_station.json"
input_line_filename = "Merged/geo_line.json"

graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")


def load_json(filename):
    file = open(filename, 'r')
    content = file.read()
    file.close()
    return json.loads(content)


# Convert time like "7:10:00" into Unix Timestamp
stamp_now = time.time()
date_now = datetime.fromtimestamp(stamp_now)
def string_to_timestamp(timestr):
    datestr = "%d-%d-%dT%s" % (date_now.year, date_now.month, date_now.day, timestr)
    date_target = datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%S')
    stamp_target = time.mktime(date_target.timetuple())
    return stamp_target


def database_reset():
    graph_db.clear()


def create_line_node(line_data):
    # Prepare shape arrays
    shape_station, shape_time, shape_dist, shape_lat, shape_long = [], [], [], [], []
    time_baseline = None
    for shape in line_data["shape"]:
        shape_station.append(shape["shape_code"] if "shape_code" in shape else "")
        shape_dist.append(float(shape["shape_dist_traveled"]))
        shape_lat.append(float(shape["shape_pt_lat"]))
        shape_long.append(float(shape["shape_pt_lon"]))
        if "shape_time" in shape:
            if not time_baseline:
                time_baseline = string_to_timestamp(shape["shape_time"])
            time_offset = int(string_to_timestamp(shape["shape_time"]) - time_baseline)
        else:
            time_offset = 0
        shape_time.append(time_offset)
    # Create a node
    line_node = node(
        guid = line_data["guid"],
        name = line_data["name"],
        direction = line_data["direction"],
        time_start = line_data["time_start"],
        time_end = line_data["time_end"],
        duration = int(line_data["duration"]),
        station = line_data["station"],
        shape_station = shape_station,
        shape_time = shape_time,
        shape_dist = shape_dist,
        shape_lat = shape_lat,
        shape_long = shape_long,
    )
    line_node, = graph_db.create(line_node)
    # Add label
    line_node.add_labels("Line")



if __name__ == '__main__':
    # Load merged data
    dataset_station = load_json(input_station_filename)
    dataset_line = load_json(input_line_filename)

    # Check if loaded
    assert len(dataset_station) >= 700, "fail to load dataset_station"
    assert len(dataset_line) >= 700, "fail to load dataset_line"

    # Reset before create
    database_reset()

    # Create basic line nodes, only nodes, no other information
    line_selected = [ dataset_line[line_id] for line_id in dataset_line if "geo_line_id" in dataset_line[line_id] ]
    for line in line_selected:
        create_line_node(line)



#print json.dumps(dataset_line, indent=4)