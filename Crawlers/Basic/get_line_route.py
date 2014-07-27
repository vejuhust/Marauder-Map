#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
import urllib2
import json
import time
import random
import argparse


api_url_template = "http://content.2500city.com/Json?method=GetBusLineDetail&Guid=%s"

def load_parser():
    parser = argparse.ArgumentParser(description = "crawling status of bus lines")
    parser.add_argument("guid", help = "guid of the bus line", type = str, action = 'store')
    parser.add_argument("filename", help = "line name as output filename, w/o extension name", type = str, action = 'store')
    return parser.parse_args()


def save_result(filename, data):
    file = open(filename, 'a')
    file.write(data)
    file.close()


def data_request(guid):
    result = {}
    url = api_url_template % guid
    # Send request
    time_start = time.time()
    request = urllib2.urlopen(url)
    response = request.read()
    time_end = time.time()
    request.close()
    # Process response
    result["call_latency"] = time_end - time_start
    data = json.loads(response)
    result["response"] = data
    return result



if __name__ == '__main__':
    args = load_parser()
    output_filename = os.path.dirname(os.path.realpath(__file__)) + "/line_" + args.filename + ".txt"

    try:
        data = data_request(args.guid)
    except Exception as e:
        data = { "call_error" : str(e) }
    finally:
        data["call_time"] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime())
        data["call_guid"] = args.guid

    save_result(output_filename, json.dumps(data, sort_keys = True, ensure_ascii = False).encode('utf-8') + "\n")

