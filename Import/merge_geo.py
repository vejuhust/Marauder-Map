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
    # Preview the result
    names = ['geo_freq', 'geo_route', 'geo_shape', 'geo_stop_time', 'geo_stop_list']
    for name in names:
        print name, json.dumps(eval(name)[0], indent = 4, sort_keys = True)

