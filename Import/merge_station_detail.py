#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import json


station_detail_filename = "../Data/External/station_detail.json"
merged_filename = "Merged/station_all.json"

def load_json(filename):
    file = open(filename, 'r')
    content = file.read()
    file.close()
    return json.loads(content)


def save_file(filename, data):
    file = open(filename, 'w')
    file.write(json.dumps(data, sort_keys = True, indent = 4, ensure_ascii = False).encode('utf-8'))
    file.close()


# grep NoteGuid ../Data/External/station_detail.json | sort | uniq | wc -l
# Result: 699
def merge_detail(raw, data):
    for item in raw:
        if "call_error" not in item:
            stations = item["response"]["list"]
            for station in stations:
                code = station["NoteGuid"]
                if code not in data:
                    if len(station["Sect"]) > 0 and station["Sect"] != station["Road"]:
                        address_parts = [station["Canton"], station["Road"], u"近", station["Sect"], u"交叉口处"]
                    else:
                        address_parts = [station["Canton"], station["Road"]]
                    address = "".join([part.strip() for part in address_parts ])
                    data[code] = {
                        "code" : code.upper().strip(),
                        "name" : station["Name"].strip(),
                        "geo_side" : station["Direct"].strip(),
                        "geo_road" : address
                    }
    return data

if __name__ == '__main__':
    raw = load_json(station_detail_filename)
    data = {}
    merge_detail(raw, data)
    print len(data)
    save_file(merged_filename, data)
