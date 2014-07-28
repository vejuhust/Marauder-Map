#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import urllib2
import json
import time
from datetime import datetime


def string_to_timestamp(timestr, is_past = False):
    stamp_now = time.time()
    date_now = datetime.fromtimestamp(stamp_now)
    datestr = "%d-%d-%dT%s" % (date_now.year, date_now.month, date_now.day, timestr)
    date_target = datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%S')
    stamp_target = time.mktime(date_target.timetuple())
    if is_past:
        if stamp_target > stamp_now:
            stamp_target -= 24 * 60 * 60
    return stamp_target


line = [
    {
        "guid"      : "e31d7bb3-ba4c-4e24-85e8-95e9d0f4d49e", 
        "sibling"   : "edc1ecd6-2bf8-4b08-8727-385bb8943b9d", 
        "name"      : "115",
        "direction" : u"沪宁城铁园区站=>独墅湖高教区首末站",      #320500011013
        "time_start": string_to_timestamp("06:30:00"),
        "time_end"  : string_to_timestamp("22:20:00"),
        "duration"  : "1200",
        "is_active" : True,
        "shape"     : [
            { "lat" : 31.341645, "long" : 120.708744, "dist" : 0.0       , "station" : "PPX" },
            { "lat" : 31.342812, "long" : 120.714325, "dist" : 546.1875  , "station" : "" },
            { "lat" : 31.343714, "long" : 120.713687, "dist" : 663.2093  , "station" : "" },
            { "lat" : 31.344248, "long" : 120.713351, "dist" : 730.5372  , "station" : "RBC" },
            { "lat" : 31.344371, "long" : 120.713273, "dist" : 746.0493  , "station" : "" },
            { "lat" : 31.346473, "long" : 120.711844, "dist" : 1015.946  , "station" : "" },
            { "lat" : 31.347587, "long" : 120.711087, "dist" : 1158.9672 , "station" : "" },   
            { "lat" : 31.348072, "long" : 120.710783, "dist" : 1220.0466 , "station" : "" },   
            { "lat" : 31.348155, "long" : 120.710730, "dist" : 1230.4883 , "station" : "PPU" },   
            { "lat" : 31.348511, "long" : 120.710502, "dist" : 1275.5974 , "station" : "" },   
            { "lat" : 31.348546, "long" : 120.710479, "dist" : 1280.0538 , "station" : "" },   
        ],
        "station" : [
            "PPX",
            "RBC",
            "PPU",
        ],
        "bus" : [
            u"苏E-2N305",
            u"苏E-2N288",
        ]
    }, 
    {
        "guid"      : "edc1ecd6-2bf8-4b08-8727-385bb8943b9d", 
        "sibling"   : "e31d7bb3-ba4c-4e24-85e8-95e9d0f4d49e", 
        "name"      : "115",
        "direction" : u"独墅湖高教区首末站=>沪宁城铁园区站广场",   #320500011014
        "time_start": string_to_timestamp("06:30:00"),
        "time_end"  : string_to_timestamp("22:15:00"),
        "duration"  : "1200",
        "is_active" : True,
        "shape"     : [
            { "lat" : 31.267248, "long" : 120.748301, "dist" : 0.0       , "station" : "FGT" },   
            { "lat" : 31.263565, "long" : 120.749956, "dist" : 437.9111  , "station" : "" },
            { "lat" : 31.262372, "long" : 120.750518, "dist" : 580.6653  , "station" : "" },
            { "lat" : 31.261901, "long" : 120.750740, "dist" : 637.0294  , "station" : "" },
            { "lat" : 31.261240, "long" : 120.750982, "dist" : 713.89545 , "station" : "" },   
            { "lat" : 31.260550, "long" : 120.751361, "dist" : 798.5582  , "station" : "PUF" },
            { "lat" : 31.260294, "long" : 120.751502, "dist" : 829.93036 , "station" : "" },   
            { "lat" : 31.258769, "long" : 120.752582, "dist" : 1027.8911 , "station" : "" },   
            { "lat" : 31.258012, "long" : 120.750282, "dist" : 1262.3215 , "station" : "RVV" },   
            { "lat" : 31.258012, "long" : 120.750282, "dist" : 1262.3215 , "station" : "" },   
            { "lat" : 31.256784, "long" : 120.746551, "dist" : 1642.6125 , "station" : "" },   
        ],
        "station" : [
            "FGT",
            "PUF",
            "RVV",
        ],
        "bus" : [
            u"苏E-2N286",
            u"苏E-2N279",
        ]
    }
]


bus = [
    {
        "tag" : u"苏E-2N305",
        "arrival_time" : string_to_timestamp("18:11:37", True),
        "arrival_station" : "PPX",
        "arrival_line" : "e31d7bb3-ba4c-4e24-85e8-95e9d0f4d49e",
        "next_station" : "RBC",
        "next_dist" : 730.5372,
        "eta_duration" : 342,
    },
    {
        "tag" : u"苏E-2N288",
        "arrival_time" : string_to_timestamp("18:10:30", True),
        "arrival_station" : "RBC",
        "arrival_line" : "e31d7bb3-ba4c-4e24-85e8-95e9d0f4d49e",
        "next_station" : "PPU",
        "next_dist" : 499.9511,
        "eta_duration" : 278,    
    },
     {
        "tag" : u"苏E-2N286",
        "arrival_time" : string_to_timestamp("18:11:18", True),
        "arrival_station" : "FGT",
        "arrival_line" : "edc1ecd6-2bf8-4b08-8727-385bb8943b9d",
        "next_station" : "PUF",
        "next_dist" : 798.5582,
        "eta_duration" : 165,    
    },
     {
        "tag" : u"苏E-2N279",
        "arrival_time" : string_to_timestamp("18:11:37", True),
        "arrival_station" : "PUF",
        "arrival_line" : "edc1ecd6-2bf8-4b08-8727-385bb8943b9d",
        "next_station" : "RVV",
        "next_dist" : 463.7633,
        "eta_duration" : 89,    
    },
 ]


station = [
    {
        "code"     : "PPX",
        "name"     : u"沪宁城铁园区站",
        "sibling"  : "PPV",
        "geo_road" : u"工业园区至和路",
        "geo_side" : u"场内北",
        "geo_lat"  : 31.341645,
        "geo_long" : 120.708744,
    },
    {
        "code"     : "RBC",
        "name"     : u"青青家园",
        "sibling"  : "RBD",
        "geo_road" : u"工业园区珠泾路近至和路-葑亭大道交叉口处",
        "geo_side" : u"东",
        "geo_lat"  : 31.344230,
        "geo_long" : 120.713322,
    },
     {
        "code"     : "PPU",
        "name"     : u"珠泾路葑亭大道南",
        "sibling"  : "PPT",
        "geo_road" : u"工业园区珠泾路近葑亭大道-至和路交叉口处",
        "geo_side" : u"东",
        "geo_lat"  : 31.348148,
        "geo_long" : 120.710720,
    },
    {
        "code"     : "FGT",
        "name"     : u"独墅湖高教区首末站",
        "sibling"  : "GDR",
        "geo_road" : u"工业园区近林泉街-无名路交叉口处",
        "geo_side" : u"场内东",
        "geo_lat"  : 31.267248,
        "geo_long" : 120.748301,
    },
     {
        "code"     : "PUF",
        "name"     : u"职业技术学院北",
        "sibling"  : "PUE",
        "geo_road" : u"工业园区林泉街近若水路-裕新路交叉口处",
        "geo_side" : u"西",
        "geo_lat"  : 31.260538,
        "geo_long" : 120.751340,
    },
    {
        "code"     : "RVV",
        "name"     : u"园区服务外包学院",
        "sibling"  : "RVW",
        "geo_road" : u"工业园区裕新路近林泉街-雪堂街交叉口处",
        "geo_side" : u"北",
        "geo_lat"  : 31.257750,
        "geo_long" : 120.749474,
    },
]


def save_file(filename, data):
    file = open(filename, 'w')
    file.write(json.dumps(data, sort_keys = True, indent = 4, ensure_ascii = False).encode('utf-8'))
    file.close()


if __name__ == '__main__':
    data = {
        "line_list" : line,
        "bus_list" : bus,
        "station_list" : station,
    }
    save_file("mock.json", data)
