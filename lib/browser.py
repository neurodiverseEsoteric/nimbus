#!/usr/bin/env python3

## browser.py ##
# Provides a simple API for extensions.

windows = []
closedWindows = []

def activeWindow():
    for window in windows[::-1]:
        if window.isActiveWindow():
            return window
    return window

def currentTab():
    return activeWindow().tabWidget().currentWidget()
