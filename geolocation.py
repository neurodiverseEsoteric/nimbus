#!/usr/bin/env python3

import socket
import urllib.request
import time

try:
    from PyQt4.QtCore import QObject, pyqtSlot
    Slot = pyqtSlot
except:
    from PySide.QtCore import QObject, Slot

def geolocate():
    ip = urllib.request.urlopen('http://icanhazip.com/').read().decode('utf-8').replace("\n", "")
    response = eval(urllib.request.urlopen('http://freegeoip.net/json/' + ip).read())
    return response

def getCurrentPosition():
    try:
        position = geolocate()
        position2 = {"coords": {"latitude": position["latitude"], "longitude": position["longitude"], "altitude": 0, "accuracy": 0, "altitudeAccuracy": 0, "heading": 0, "speed": 0}, "timestamp": time.time()}
    except:
        position2 = {"coords": {"latitude": 0, "longitude": 0, "altitude": 0, "accuracy": 0, "altitudeAccuracy": 0, "heading": 0, "speed": 0}, "timestamp": time.time()}
    return position2

def watchPosition():
    pass

def clearWatch():
    pass

class Geolocation(QObject):
    def __init__(self, *args, **kwargs):
        super(Geolocation, self).__init__(*args, **kwargs)
    @Slot(result=str)
    def getCurrentPosition(self):
        return str(getCurrentPosition())

if __name__ == "__main__":
    geolocate()
