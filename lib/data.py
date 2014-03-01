#!/usr/bin/env python3

# -------
# data.py
# -------
# Author:      Daniel Sim (foxhead128)
# License:     See LICENSE.md for more details.
# Description: This module contains data related to browser history, cookies,
#              etc.

from common import pyqt4
import network
import json
if not pyqt4:
    from PyQt5.QtCore import QCoreApplication, QByteArray, QUrl
    from PyQt5.QtNetwork import QNetworkCookie
    from qsettings import QSettings
else:
    try:
        from PyQt4.QtCore import QCoreApplication, QByteArray, QUrl, QSettings
        from PyQt4.QtNetwork import QNetworkCookie
    except:
        from PySide.QtCore import QCoreApplication, QByteArray, QUrl, QSettings
        from PySide.QtNetwork import QNetworkCookie

# Global list to store history.
history = {}

data = QSettings(QSettings.IniFormat, QSettings.UserScope, "nimbus", "data", QCoreApplication.instance())

# These store the geolocation whitelist and blacklist.
geolocation_whitelist = []
geolocation_blacklist = []

# Clippings.
clippings = {}

def load_clippings():
    global clippings
    try: clippings = json.loads(data.value("data/Clippings"))
    except: pass

load_clippings()

def save_clippings():
    try:
        data.setValue("data/Clippings", json.dumps(clippings))
        data.sync()
    except: pass

def shortUrl(url):
    i = url.partition("://")[-1] if "://" in url else url
    i = i.replace(("www." if i.startswith("www.") else ""), "")
    return i

# This function loads the browser's settings.
def loadData():
    # Load history.
    global history
    global geolocation_whitelist
    global geolocation_blacklist
    raw_history = data.value("data/History")
    if type(raw_history) is str:
        history = json.loads(raw_history)
        if type(history) is list:
            new_history = {}
            for item in history:
                new_history[item] = {"title": item, "last_visited": 0}
            history = new_history

    # Load cookies.
    try: raw_cookies = json.loads(str(data.value("data/Cookies")))
    except: pass
    else:
        if type(raw_cookies) is list:
            cookies = [QNetworkCookie().parseCookies(QByteArray(cookie))[0] for cookie in raw_cookies]
            network.cookie_jar.setAllCookies(cookies)

    try: wl = json.loads(str(data.value("data/GeolocationWhitelist")))
    except: pass
    else:
        if type(wl) is list:
            geolocation_whitelist = wl

    try: bl = json.loads(str(data.value("data/GeolocationBlacklist")))
    except: pass
    else:
        if type(bl) is list:
            geolocation_blacklist = bl

# This function saves the browser's settings.
def saveData():
    # Save history.
    global history
    for item in history:
        try: del history[item]["short"]
        except: pass
    data.setValue("data/History", json.dumps(history))

    # Save cookies.
    cookies = json.dumps([cookie.toRawForm().data().decode("utf-8") for cookie in network.cookie_jar.allCookies()])
    data.setValue("data/Cookies", cookies)

    data.setValue("data/GeolocationWhitelist", json.dumps(geolocation_whitelist))
    data.setValue("data/GeolocationBlacklist", json.dumps(geolocation_blacklist))

    # Sync any unsaved settings.
    data.sync()

# Clear history.
def clearHistory():
    global history
    history = {}
    saveData()

# Clear cookies.
def clearCookies():
    network.cookie_jar.setAllCookies([])
    network.incognito_cookie_jar.setAllCookies([])
    saveData()
