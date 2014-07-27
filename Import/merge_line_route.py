#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import json


datadir = "../Data/External/"
offset = 11
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

# http://content.2500city.com/Json?method=SearchBusStation&standName=%E4%B8%8A%E5%A8%84%E8%B7%AF
# http://content.2500city.com/Json?method=GetBusStationDetail&NoteGuid=BZT
# http://content.2500city.com/Json?method=GetBusLineDetail&Guid=e31d7bb3-ba4c-4e24-85e8-95e9d0f4d49e


def extract_data(filename):
    file = open(filename, 'r')
    content = file.readlines()
    file.close()
    for index, line in enumerate(content):
        if ("call_error" not in line) and (index >= offset):
            data = line.strip()
            break
    return json.loads(data)


def save_file(filename, data):
    file = open(filename, 'w')
    file.write(json.dumps(data, sort_keys = True, indent = 4, ensure_ascii = False).encode('utf-8'))
    file.close()


def correct_data(data):
    for item in errata:
        stations = data[item["guid"]]["list"]["StandInfo"]
        for station in stations:
            if station["SName"] == item["name"]:
                station["SCode"] = item["code"]


def verify_data(data):
    for guid in data:
        item = data[guid]
        assert len(item["list"]) > 0, "invalid response for %s" % guid
        stations = item["list"]["StandInfo"]
        assert len(stations) > 0, "valid response for %s should contain staion list" % guid
        for station in stations:
            assert type(station["SCode"]) == unicode, "invalid SCode for %s" % (station["SName"].encode('utf-8'))
            assert len(station["SCode"]) == 3, "invalid SCode length for %s" % (station["SName"].encode('utf-8'))



if __name__ == '__main__':
    data = {}
    for filename in os.listdir(datadir):
        if filename.startswith("line") and filename.endswith(".txt"):
            raw = extract_data(datadir + filename)
            guid = raw["call_guid"].lower().strip()
            data[guid] = raw["response"]
    correct_data(data)
    verify_data(data)
    save_file("Merged/line_route.json", data)

