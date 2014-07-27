#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import urllib2
import json
import time
import random


lineinfo_url = "http://content.2500city.com/Json?method=SearchBusLine&lineName=%d"
data_filename = "lines.json"
guid_set = set()

def notification(message):
    print '[%s] %s' % (time.strftime('%a, %d %b %Y %H:%M:%S %Z', time.localtime()), message)


def read_line_item(list, result):
    for line in list:
        if ('Guid' in line) and ('LName' in line) and ('LDirection' in line):
            guid = line['Guid'].strip()
            name = line['LName'].strip()
            direction = line['LDirection'].strip()      
            if guid in guid_set:
                continue
            guid_set.add(guid)
            result.append(
                {
                    'line_guid' : guid,
                    'line_name' : name,
                    'line_direction' : direction,
                }
            )


def send_api_request(line_number):
    # Send requests
    url = lineinfo_url % line_number
    request = urllib2.urlopen(url)
    response = request.read()
    request.close()
    # Process response
    data = json.loads(response)
    result = []
    if 'list' in data:
        read_line_item(data['list'], result)
    if 'list2' in data:
        read_line_item(data['list2'], result)
    return result


def save_file(data):
    file = open(data_filename, "w")
    file.write(json.dumps(data, sort_keys = True, indent = 4, ensure_ascii = False).encode('utf-8'))
    file.close()


if __name__ == '__main__':
    data = []
    unique = set()
    seconds = [0.2, 0.3, 0.5, 0.7, 1.1, 1.3]
    for line_number in range(1, 1000):
        data += send_api_request(line_number)
        save_file(data)
        second = random.choice(seconds)
        notification("Line %d done! %d lines in total! Gonna rest for %s seconds" % (line_number, len(data), second))
        time.sleep(second)
