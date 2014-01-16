#!/usr/bin/env python3

# This is a dumb hacky stand-in for QSettings.

import os
import json

class QSettings(object):
    IniFormat = None
    UserScope = None
    def __init__(self, *args, **kwargs):
        self.dirname = "." + args[2]
        self.fulldirname = os.path.join(os.path.expanduser("~"), self.dirname)
        if not os.path.isdir(self.fulldirname):
            os.makedirs(self.fulldirname)
        self.fname = args[3] + ".json"
        self.tables = {}
        if os.path.isfile(self.fileName()):
            try: f = open(self.fileName(), "r")
            except: pass
            else:
                try: self.tables = json.load(f)
                except: pass
                f.close()
    def fileName(self):
        return os.path.join(self.fulldirname, self.fname)
    def setValue(self, key, value):
        self.tables[key] = value
    def value(self, key):
        try: return self.tables[key]
        except: return None
    def sync(self):
        try: f = open(self.fileName(), "w")
        except: pass
        else:
            try: json.dump(self.tables, f)
            except: pass
            f.close()
