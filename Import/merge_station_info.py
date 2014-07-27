#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import json


line_info_filename = "Merged/line_info.json"
line_route_filename = "Merged/line_route.json"


def load_json(filename):
    file = open(filename, 'r')
    content = file.read()
    file.close()
    return json.loads(content)


# grep SCode Merged/line_route.json | sort | uniq | wc
# Result: 428
def get_all_scode(data):
    scode_dict = {}
    for guid in data:
        item = data[guid]
        stations = item["list"]["StandInfo"]
        for station in stations:
            scode_dict[station["SCode"]] = station["SName"]
    return scode_dict


def save_file(filename, data):
    file = open(filename, 'w')
    file.write(json.dumps(data, sort_keys = True, indent = 4, ensure_ascii = False).encode('utf-8'))
    file.close()


if __name__ == '__main__':
    # Load merged data
    line_info = load_json(line_info_filename)
    line_route = load_json(line_route_filename)
    # Count all station codes
    scode_dict = get_all_scode(line_route)
    save_file("Merged/station_info.json", scode_dict)
