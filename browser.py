#!/usr/bin/env python3

windows = []

def activeWindow():
    for window in windows[::-1]:
        if window.isActiveWindow():
            return window
