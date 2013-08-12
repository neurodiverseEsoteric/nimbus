#!/usr/bin/env python3

import socket
import urllib.request
import time
try: from PySide.QtCore import QObject
except: from PyQt4.QtCore import QObject

def geolocate():
    ip = urllib.request.urlopen('http://icanhazip.com/').read().decode('utf-8').replace("\n", "")
    response = dict([item.split(": ") for item in urllib.request.urlopen('http://api.hostip.info/get_html.php?ip=' + ip + '&position=true').read().decode('utf-8').split("\n") if len(item.split(": ")) > 1])
    print(response)
    return response

class Geolocation(QObject):
    def __init__(self, *args, **kwargs):
        super(Geolocation, self).__init__(*args, **kwargs)
    def getCurrentPosition(self, success, error, options):
        position = geolocate()
        return {"coords": {"latitude": position["Latitude"], "longitude": position["Longitude"], "altitude": 0, "accuracy": 0, "altitudeAccuracy": 0, "heading": 0, "speed": 0}, "timestamp": time.time()}
    def watchPosition(self):
        pass
    def clearWatch(self):
        pass

if __name__ == "__main__":
    geolocate()
