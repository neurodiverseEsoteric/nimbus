#! /usr/bin/env python3

import os.path
import abpy
import common
import settings
try: from PyQt4.QtCore import QThread
except: from PySide.QtCore import QThread

# Dummy adblock filter class.
class Filter(object):
    def __init__(self, rules):
        super(Filter, self).__init__()
        self.index = {}
    def match(self, url):
        return None

# Global stuff.
adblock_folder = os.path.join(settings.settings_folder, "adblock")
easylist = os.path.join(common.app_folder, "easylist.txt")
adblock_filter = Filter([])
shelved_filter = None
adblock_rules = []

# Load adblock rules.
def load_adblock_rules():
    global adblock_filter
    global adblock_rules
    global shelved_filter

    if len(adblock_rules) < 1:
        # Load easylist.
        if os.path.exists(easylist):
            f = open(easylist)
            try: adblock_rules += [rule.rstrip("\n") for rule in f.readlines()]
            except: pass
            f.close()
        # Load additional filters.
        if os.path.exists(adblock_folder):
           for fname in os.listdir(adblock_folder):
               f = open(os.path.join(adblock_folder, fname))
               try: adblock_rules += [rule.rstrip("\n") for rule in f.readlines()]
               except: pass
               f.close()

    # Create instance of abpy.Filter.
    if shelved_filter:
        adblock_filter = shelved_filter
    else:
        adblock_filter = abpy.Filter(adblock_rules)
        shelved_filter = adblock_filter

# Thread to load Adblock filters.
class AdblockFilterLoader(QThread):
    def __init__(self, parent=None):
        super(AdblockFilterLoader, self).__init__(parent)
    def run(self):
        if settings.setting_to_bool("content/AdblockEnabled"):
            load_adblock_rules()
        else:
            global adblock_filter
            global shelved_filter
            if len(adblock_filter.index.keys()) > 0:
                shelved_filter = adblock_filter
            adblock_filter = abpy.Filter([])
        self.quit()

# Create thread to load adblock filters.
adblock_filter_loader = AdblockFilterLoader()

# Host filter.
hosts_file = os.path.join(common.app_folder, "hosts")
host_rules = []

def load_host_rules():
    global host_rules
    if os.path.exists(hosts_file):
        try: f = open(hosts_file, "r")
        except: pass
        else:
            try: host_rules = [line.split(" ")[1].replace("\n", "") for line in f.readlines() if len(line.split(" ")) > 1 and not line.startswith("#") and len(line) > 1]
            except: pass
            f.close()

load_host_rules()
