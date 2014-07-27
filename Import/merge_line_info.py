#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import json


#cat ../Data/External/lines*.json | grep guid | awk {"print tolower($_)"} | sort | uniq | cut -d '"' -f4 | wc
datadir = "../Data/External/"


def load_json(filename):
    file = open(filename, 'r')
    content = file.read()
    file.close()
    return json.loads(content)


def save_file(filename, data):
    file = open(filename, 'w')
    file.write(json.dumps(data, sort_keys = True, indent = 4, ensure_ascii = False).encode('utf-8'))
    file.close()


def distill_data(data, raw):
    for line in raw:
        line_guid = line["line_guid"].lower().strip()
        line_name = line["line_name"].rstrip("(").strip()
        line_direction = line["line_direction"].strip()
        if line_guid not in data:
            data[line_guid] = {
                "guid" : line_guid,
                "name" : line_name,
                "direction" : line_direction
            }


def filter_round_bus(data):
    pairs = {}
    for line in data:
        item = data[line]
        name = item["name"]
        if name not in pairs:
            pairs[name] = [item]
        else:
            pairs[name].append(item)
    
    print len(pairs)
    for pair in pairs:
        item = pairs[pair]
        if len(item) != 2:
            print pair, " - ", len(item)
            for line in item:
                print "\t", line["direction"], line["guid"]



if __name__ == '__main__':
    data = {}
    for filename in os.listdir(datadir):
        if filename.startswith("lines") and filename.endswith(".json"):
            raw = load_json(datadir + filename)
            distill_data(data, raw)
    #filter_round_bus(data)
    save_file("Merged/line_info.json", data)

