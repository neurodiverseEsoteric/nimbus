#!/usr/bin/env python3

## settings.py ##
# This module contains data related to browser settings.

import sys
import os
import json
import common
import hashlib
try:
    from PyQt4.QtCore import QCoreApplication, QUrl, QSettings
    from PyQt4.QtNetwork import QNetworkCookie
except:
    from PySide.QtCore import QCoreApplication, QUrl, QSettings
    from PySide.QtNetwork import QNetworkCookie


# Common settings manager.
settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "nimbus", "config", QCoreApplication.instance())

# This is a global variable that gets the settings folder on any platform.
settings_folder = os.path.dirname(settings.fileName())

# This stores the cache.
network_cache_folder = os.path.join(settings_folder, "Cache")
offline_cache_folder = os.path.join(settings_folder, "OfflineCache")

# Start page.
startpage = os.path.join(common.app_folder, "start.html")

# Default settings.
default_settings = {"proxy/Type": "None",
                    "proxy/Hostname": "",
                    "proxy/Port": 8080,
                    "proxy/User": "",
                    "proxy/Password": "",
                    "network/DnsPrefetchEnabled": False,
                    "network/XSSAuditingEnabled": False,
                    "content/AutoLoadImages": True,
                    "network/GeolocationEnabled": True,
                    "content/JavascriptEnabled": True,
                    "content/JavaEnabled": False,
                    "content/PrintElementBackgrounds": True,
                    "content/FrameFlatteningEnabled": False,
                    "content/PluginsEnabled": True,
                    "content/AdblockEnabled": False,
                    "content/HostFilterEnabled": False,
                    "content/ReplaceHTML5MediaTagsWithEmbedTags": (True if "win" in sys.platform else False),
                    "content/UseOnlineContentViewers": True,
                    "content/TiledBackingStoreEnabled": False,
                    "content/SiteSpecificQuirksEnabled": True,
                    "general/Homepage": QUrl.fromUserInput(startpage).toString(),
                    "general/Search": "http://www.google.com/search?client=nimbus&q=%s" if not common.app_locale.startswith("zh") else "http://www.baidu.com/s?wd=%s",
                    "general/CloseWindowWithLastTab": True,
                    "data/RememberHistory": True,
                    "data/MaximumCacheSize": 50,
                    "general/OpenSettingsInTab": False,
                    "extensions/Whitelist": [],
                    "general/ReopenableTabCount": 10,
                    "general/ReopenableWindowCount": 10}
default_port = default_settings["proxy/Port"]

# New tab page.
new_tab_page = os.path.join(settings_folder, "new-tab-page.html")

# Set up default values.
for setting, value in default_settings.items():
    if settings.value(setting) == None:
        settings.setValue(setting, value)

settings.sync()

def setting_to_bool(value=""):
    try: return bool(eval(str(settings.value(value)).title()))
    except: return False

def setting_to_int(value=""):
    try: return int(settings.value(value))
    except: return 0

# List of extensions.
extensions_folder = os.path.join(common.app_folder, "extensions")
extensions = []

# PDF viewer is hacked to try and use pdf.js in Qt5.
if not common.qt_version.startswith("4"):
    pdf_viewer = (QUrl.fromUserInput(os.path.join(extensions_folder, "pdf.js", "web", "viewer.html")).toString() + "?file=%s", (".pdf",))
    temp_folder = os.path.join(settings_folder, "Temp")
    print(pdf_viewer)
    common.content_viewers.append(pdf_viewer)
else:
    pdf_viewer = ("https://docs.google.com/viewer?url=%s", (".pdf",))
    temp_folder = os.path.join(settings_folder, "Temp")
    print(pdf_viewer)
    common.content_viewers.append(pdf_viewer)

# temporary file scheme.
def tempFile(fname):
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    m = hashlib.md5()
    m.update(fname.encode('utf-8'))
    h = m.hexdigest()
    return os.path.join(temp_folder, h)

# Stores all extension buttons.
extension_buttons = []

# List of extensions to load.
extensions_whitelist = []

# List of extensions not to load.
extensions_blacklist = []

# Reloads extension blacklist.
def reload_extensions2():
    global extensions_blacklist
    global extensions_whitelist
    try:
        extensions_blacklist = [extension for extension in extensions if extension not in json.loads(settings.value("extensions/whitelist"))]
        extensions_whitelist = [extension for extension in extensions if extension in json.loads(settings.value("extensions/whitelist"))]
    except:
        extensions_blacklist = [extension for extension in extensions]
        extensions_whitelist = []

# Reloads extensions.
def reload_extensions():
    global extensions
    if os.path.isdir(extensions_folder):
        extensions = sorted(os.listdir(extensions_folder))
    else:
        extensions = []
    reload_extensions2()

reload_extensions()

# Clear extensions.
def reset_extensions():
    global extension_buttons
    for extension in extension_buttons:
        try: extension.deleteLater()
        except: pass
    while len(extension_buttons) > 0:
        extension_buttons.pop()
