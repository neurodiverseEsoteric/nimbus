#! /usr/bin/env python3

# Import everything we need.
import sys
import os
import abpy
import pickle
from PyQt4.QtCore import QCoreApplication, QSettings, QThread
from PyQt4.QtGui import QIcon, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QLineEdit, QToolBar, QStyle, QStylePainter, QStyleOptionToolBar
from PyQt4.QtNetwork import QNetworkCookieJar

# Dummy adblock filter class.
class Filter(object):
    def __init__(self, rules):
        super(Filter, self).__init__()
        self.index = {}
    def match(self, url):
        return None

# Folder that Nimbus is stored in.
app_folder = os.path.dirname(os.path.realpath(__file__))

# Icons folder
app_icons_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons")

# Get an application icon.
def app_icon(name):
    return os.path.join(app_icons_folder, name)

# Returns a QIcon
def complete_icon(name):
    try: return QIcon().fromTheme(name, QIcon(app_icon(name + ".png")))
    except: return QIcon()

# Global cookiejar to store cookies.
# All nimbus.WebView instances use this.
cookieJar = QNetworkCookieJar(QCoreApplication.instance())

# All incognito nimbus.WebView instances use this one instead.
incognitoCookieJar = QNetworkCookieJar(QCoreApplication.instance())

# Common settings manager.
settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "nimbus", "config", QCoreApplication.instance())

# Default settings.
default_settings = {"proxy/Type": "None",
                    "proxy/Hostname": "",
                    "proxy/Port": 8080,
                    "proxy/User": "",
                    "proxy/Password": "",
                    "network/DnsPrefetchEnabled": False,
                    "network/XSSAuditingEnabled": False,
                    "content/AutoLoadImages": True,
                    "content/JavascriptEnabled": True,
                    "content/PluginsEnabled": True,
                    "content/AdblockEnabled": True,
                    "content/ReplaceHTML5MediaTagsWithEmbedTags": (True if "win" in sys.platform else False),
                    "content/UseGoogleDocsViewer": True,
                    "content/TiledBackingStoreEnabled": False,
                    "content/SiteSpecificQuirksEnabled": True,
                    "general/Homepage": "https://github.com/foxhead128/nimbus",
                    "general/Search": "https://duckduckgo.com/?q=%s",
                    "general/CloseWindowWithLastTab": True,
                    "extensions/Whitelist": []}
default_port = default_settings["proxy/Port"]

# Set up default values.
for setting, value in default_settings.items():
    if settings.value(setting) == None:
        settings.setValue(setting, value)

settings.sync()

def setting_to_bool(value=""):
    return bool(eval(str(settings.value(value)).title()))

# This is a global variable that gets the settings folder on any platform.
settings_folder = os.path.dirname(settings.fileName())

# New tab page.
new_tab_page = os.path.join(settings_folder, "new-tab-page.html")

# Lock file.
lock_file = os.path.join(settings_folder, ".lock")

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

# Clear extensions.
def reset_extensions():
    global extension_buttons
    for extension in extension_buttons:
        extension.deleteLater()
    while len(extension_buttons) > 0:
        extension_buttons.pop()

# Reload extension blacklist.
reload_extensions_blacklist()

# Adblock related functions.
adblock_folder = os.path.join(settings_folder, "adblock")
easylist = os.path.join(app_folder, "easylist.txt")
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
        if setting_to_bool("content/AdblockEnabled"):
            load_adblock_rules()
        else:
            global adblock_filter
            global shelved_filter
            if len(adblock_filter.index.keys()) > 0:
                shelved_filter = adblock_filter
            adblock_filter = abpy.Filter([])

# Create thread to load adblock filters.
adblock_filter_loader = AdblockFilterLoader()

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

# Toolbar that looks like a menubar.
class MenuToolBar(QToolBar):
    def __init__(self, *args, **kwargs):
        super(MenuToolBar, self).__init__(*args, **kwargs)
    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionToolBar()
        self.initStyleOption(option)
        style = self.style()
        style.drawControl(QStyle.CE_MenuBarEmptyArea, option, painter, self)
