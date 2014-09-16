#!/usr/bin/env python3

# This was originally supposed to be a drop-in replacement for Qt's QSettings.
# Not anymore, though. The name remains.

import os
import json
import paths

class QSettings(object):
    IniFormat = None
    UserScope = None
    def __init__(self, dirname="nimbus", fname="config", portable=False, **kwargs):
        self.root_folder = os.path.expanduser("~")
        self.portable = False
        if portable:
            self.root_folder = os.path.dirname(os.path.dirname(paths.app_folder))
            self.portable = True
        self.dirname = "." + dirname
        self.fulldirname = os.path.join(self.root_folder, self.dirname)
        if not os.path.isdir(self.fulldirname):
            os.makedirs(self.fulldirname)
        self.fname = fname + ".json"
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
    def allKeys(self):
        return sorted([key for key in self.tables.keys()])
    def sync(self):
        if self.portable:
            pass
        else:
            self.hardSync()
    def hardSync(self):
        try: f = open(self.fileName(), "w")
        except: pass
        else:
            try: json.dump(self.tables, f)
            except: pass
            f.close()
