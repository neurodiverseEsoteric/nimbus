#!/usr/bin/env python3

import socket
import urllib.request
import time

def geolocate():
    ip = urllib.request.urlopen('http://icanhazip.com/').read().decode('utf-8').replace("\n", "")
    response = eval(urllib.request.urlopen('http://freegeoip.net/json/' + ip).read())
    return response

def getCurrentPosition():
    position = geolocate()
    position2 = {"coords": {"latitude": position["latitude"], "longitude": position["longitude"], "altitude": 0, "accuracy": 0, "altitudeAccuracy": 0, "heading": 0, "speed": 0}, "timestamp": time.time()}
    print(position2)
    return position2

def watchPosition():
    pass

def clearWatch():
    pass

if __name__ == "__main__":
    geolocate()
