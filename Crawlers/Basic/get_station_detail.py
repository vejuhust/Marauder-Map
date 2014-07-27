#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import json
import time
import urllib2
import random


station_list_filename = "../../Import/Merged/station_info.json"
trailing_list = [u"东", u"西", u"南", u"北", u"②"]
additonal_keyword = [u"榭雨街"]

api_url_template = "http://content.2500city.com/Json?method=SearchBusStation&standName=%s"
seconds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]

result_filename = "station_detail.json"


def notification(message):
    print '[%s] %s' % (time.strftime('%a, %d %b %Y %H:%M:%S %Z', time.localtime()), message)


def load_json(filename):
    file = open(filename, 'r')
    content = file.read()
    file.close()
    return json.loads(content)


def save_file(filename, data):
    file = open(filename, 'w')
    file.write(json.dumps(data, sort_keys = True, indent = 4, ensure_ascii = False).encode('utf-8'))
    file.close()


def filter_station_code(station_list):
    station_code = set()
    for code in station_list:
        station_code.add(code)
    return station_code


def filter_station_name(station_list):
    station_name = set()
    for code in station_list:
        name = station_list[code]
        for tail in trailing_list:
            if name[-len(tail):] == tail:
                name = name[:-len(tail)]
                break
        station_name.add(name)
    return station_name


def data_request(name):
    result = {}
    url = api_url_template % name.encode('utf-8')
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


def get_single_info(name):
    try:
        data = data_request(name)
    except Exception as e:
        data = { "call_error" : str(e) }
    finally:
        data["call_time"] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime())
        data["call_name"] = name
    return data


def response_status(counter, data):
    global station_code
    if "call_error" in data:
        # If it returns error
        notification("No.%d keyword %s got error: %s" % (counter, data["call_name"], data["call_error"]))
    else:
        # Remove covered station code
        code_list = []
        for item in data["response"]["list"]:
            code = item["NoteGuid"]
            if code in station_code:
                station_code.remove(code)
                code_list += [ code ]
        # Output status
        second = random.choice(seconds)
        notification("No.%d keyword %s done! %d results in total, %d valid: %s, %d left! Gonna rest for %s seconds" %
                    (counter, data["call_name"], len(data["response"]["list"]), len(code_list), code_list, len(station_code), second))
        time.sleep(second)


if __name__ == '__main__':
    global station_code
    # Figure out keywords to request
    station_list = load_json(station_list_filename)
    station_code = filter_station_code(station_list)
    station_name = filter_station_name(station_list)
    for keyword in additonal_keyword:
        station_name.add(keyword)
    notification("Got %d station codes to cover, with %d keywords" % (len(station_code), len(station_name)))
    # Request with each keyword
    counter = 0
    data = []
    for name in station_name:
        single = get_single_info(name)
        data += [ single ]
        counter += 1
        response_status(counter, single)
        save_file(result_filename, data)
    # Final status
    notification("Got %d station codes left uncovered: %s" % (len(station_code), station_code))

