#!/usr/bin/env python3
# 
#
# A sample REST client for the thingsIO application
#
import requests
import json
import time
import sys, os
import jsonpickle

def doStore(addr, json_body, debug=False):
    # prepare headers for http request
    headers = {'content-type': 'application/json'}
    # send http request with json and receive response
    store_url = addr + '/store'

    response = requests.post(store_url, data=json_body, headers=headers)
    if debug:
        print("Response is", response)

host = sys.argv[1]
cmd = sys.argv[2]

addr = 'http://{}'.format(host)

if cmd == 'store':
    json_body = sys.argv[3]
    doStore(addr, json_body, True)
else:
    print("Unknown option", cmd)

# Sample request json
# {"database":"example",
# "json_body":
# [ 
#     {
#         "measurement": "brushEvents",
#         "tags": {
#             "user": "Carol",
#             "brushId": "6c89f539-71c6-490d-a28d-6c5d84c0ee2f"
#         },
#         "time": "2020-11-27T12:30:45.123456-05:30",
#         "fields": {
#             "duration": 127
#         }
#     },
#     {
#         "measurement": "brushEvents",
#         "tags": {
#             "user": "Carol",
#             "brushId": "6c89f539-71c6-490d-a28d-6c5d84c0ee2f"
#         },
#         "time": "2020-11-27T12:31:45.123456-05:30",
#         "fields": {
#             "duration": 132
#         }
#     },
#     {
#         "measurement": "brushEvents",
#         "tags": {
#             "user": "Carol",
#             "brushId": "6c89f539-71c6-490d-a28d-6c5d84c0ee2f"
#         },
#         "time": "2020-11-27T12:32:45.123456-05:30",
#         "fields": {
#             "duration": 129
#         }
#     }
# ]}