#!/usr/bin/env python3

# ----------
# browser.py
# ----------
# Author:      Daniel Sim (foxhead128)
# License:     See LICENSE.md for more details.
# Description: Provides a simple API for extensions.

windows = []
closedWindows = []

def activeWindow():
    for window in windows[::-1]:
        if window.isActiveWindow():
            return window
    return window

def currentTab():
    return activeWindow().tabWidget().currentWidget()
