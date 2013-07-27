#! /usr/bin/env python3

# Import everything we need.
import os
import abpy
import pickle
from PyQt4.QtCore import QCoreApplication, QSettings, QThread
from PyQt4.QtGui import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QLineEdit
from PyQt4.QtNetwork import QNetworkCookieJar

# Dummy adblock filter class.
class Filter(object):
    def __init__(self, rules):
        super(Filter, self).__init__()
    def match(self, url):
        return None

# Folder that Nimbus is stored in.
app_folder = os.path.dirname(os.path.realpath(__file__))

# Global cookiejar to store cookies.
# All nimbus.WebView instances use this.
cookieJar = QNetworkCookieJar(QCoreApplication.instance())

# All incognito nimbus.WebView instances use this one instead.
incognitoCookieJar = QNetworkCookieJar(QCoreApplication.instance())

# Common settings manager.
settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "nimbus", "config", QCoreApplication.instance())

# Default settings.
default_settings = {"proxy/type": "None",
                    "proxy/hostname": "",
                    "proxy/port": 8080,
                    "proxy/user": "",
                    "proxy/password": "",
                    "homepage": "https://github.com/foxhead128/nimbus",
                    "search": "https://duckduckgo.com/?q=%s",
                    "extensions/whitelist": [],
                    "sessionCount": 0}
default_port = default_settings["proxy/port"]

# Set up default values.
for setting, value in default_settings.items():
    if settings.value(setting) == None:
        settings.setValue(setting, value)

settings.sync()

# This is a global variable that gets the settings folder on any platform.
settings_folder = os.path.dirname(settings.fileName())

# This stylesheet is applied to toolbars that are blank.
blank_toolbar = "QToolBar { border: 0; background: transparent; }"

# Stores WebView instances.
webviews = []

# Stores browser windows.
windows = []

# List of extensions.
extensions_folder = os.path.join(app_folder, "extensions")
if os.path.isdir(extensions_folder):
    extensions = sorted(os.listdir(extensions_folder))
else:
    extensions = []

# Stores all extension buttons.
extension_buttons = []

# List of extensions not to load.
extensions_blacklist = []

# Reloads extension blacklist.
def reload_extensions_blacklist():
    global extensions_blacklist
    extensions_blacklist = [extension for extension in extensions if extension not in settings.value("extensions/whitelist")]

# Reload extension blacklist.
reload_extensions_blacklist()

# Adblock related functions.
adblock_folder = os.path.join(settings_folder, "adblock")
easylist = os.path.join(app_folder, "easylist.txt")
adblock_filter = Filter([])

# Load adblock rules.
def load_adblock_rules():
    global adblock_filter
    adblock_rules = []

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
    adblock_filter = abpy.Filter(adblock_rules)

# Thread to load Adblock filters.
class AdblockFilterLoader(QThread):
    def __init__(self, parent=None):
        super(AdblockFilterLoader, self).__init__(parent)
    def run(self):
        load_adblock_rules()

# Row widget.
class Row(QWidget):
    def __init__(self, parent=None):
        super(Row, self).__init__(parent)
        newLayout = QHBoxLayout()
        self.setLayout(newLayout)
        self.layout().setContentsMargins(0,0,0,0)
    def addWidget(self, widget):
        self.layout().addWidget(widget)

# This is a row with a label and a QLineEdit.
class LineEditRow(Row):
    def __init__(self, text="Enter something here:", parent=None):
        super(LineEditRow, self).__init__(parent)
        self.label = QLabel(text, self)
        self.addWidget(self.label)
        self.lineEdit = QLineEdit(self)
        self.addWidget(self.lineEdit)

# Column widget.
class Column(QWidget):
    def __init__(self, parent=None):
        super(Column, self).__init__(parent)
        newLayout = QVBoxLayout()
        self.setLayout(newLayout)
        self.layout().setContentsMargins(0,0,0,0)
    def addWidget(self, widget):
        self.layout().addWidget(widget)

# Blank widget to take up space.
class Expander(QLabel):
    def __init__(self, parent=None):
        super(Expander, self).__init__(parent)
        self.setText("")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
