#!/usr/bin/env python3

# -----------------
# settings.py
# -----------------
# Author:      Daniel Sim (foxhead128)
# License:     See LICENSE.md for more details.
# Description: This module contains a global QSettings object that stores
#              the browser's settings. It also contains some convenience
#              functions.

import sys
import os.path
import json
import common
try:
    from PyQt4.QtCore import QCoreApplication, QUrl, QSettings
    from PyQt4.QtNetwork import QNetworkCookie
except:
    from PySide.QtCore import QCoreApplication, QUrl, QSettings
    from PySide.QtNetwork import QNetworkCookie

# Common settings manager.
settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "nimbus", "config", QCoreApplication.instance())
settings.setValue("general/TabsOnTop", True)

# This is a global variable that gets the settings folder on any platform.
settings_folder = os.path.dirname(settings.fileName())

# This stores the cache.
network_cache_folder = os.path.join(settings_folder, "Cache")
offline_cache_folder = os.path.join(settings_folder, "OfflineCache")

# Start page.
startpage = os.path.join(settings_folder, "start.html")

# Session file.
session_file = os.path.join(settings_folder, "session.pkl")

session_folder = os.path.join(settings_folder, "Sessions")

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
                    "content/JavascriptCanOpenWindows": False,
                    "content/JavascriptCanCloseWindows": False,
                    "content/JavascriptCanAccessClipboard": False,
                    "content/JavaEnabled": False,
                    "content/PrintElementBackgrounds": True,
                    "content/FrameFlatteningEnabled": False,
                    "content/PluginsEnabled": True,
                    "content/AdblockEnabled": False,
                    "content/HostFilterEnabled": True,
                    "content/ReplaceHTML5MediaTagsWithEmbedTags": (True if "win" in sys.platform else False),
                    "content/UseOnlineContentViewers": True,
                    "content/TiledBackingStoreEnabled": False,
                    "content/SiteSpecificQuirksEnabled": True,
                    "general/Homepage": QUrl.fromUserInput(startpage).toString(),
                    "general/Search": "https://duckduckgo.com/?q=%s" if not common.app_locale.startswith("zh") else "http://www.baidu.com/s?wd=%s",
                    "general/CloseWindowWithLastTab": True,
                    "data/RememberHistory": True,
                    "data/MaximumCacheSize": 50,
                    "general/OpenSettingsInTab": False,
                    "general/PinnedTabCount": 0,
                    "general/UpButtonVisible": False,
                    "general/HomeButtonVisible": False,
                    "general/FeedButtonVisible": False,
                    "extensions/Whitelist": [],
                    "general/ReopenableTabCount": 10,
                    "general/ReopenableWindowCount": 10,
                    "general/TabsOnTop": True}
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
extensions_folder = os.path.join(settings_folder, "Extensions")
extensions = []

# Stores all extension buttons.
extension_buttons = []

# List of extensions to load.
extensions_whitelist = []

# List of extensions not to load.
extensions_blacklist = []

# Userscripts
userscripts = []

def reload_userscripts():
    global userscripts
    while len(userscripts) > 0:
        userscripts.pop()
    for extension in extensions:
        if extension not in extensions_whitelist:
            continue
        extension_path = os.path.join(extensions_folder, extension)
        if os.path.isfile(extension_path):
            extension_data = {"match": [], "content": ""}
            try: f = open(extension_path, "r")
            except: pass
            else:
                try: content = f.read()
                except: content = ""
                extension_data["content"] = content
                f.close()
                lines = content.split("\n")
                for line in lines:
                    for r in ("@match", "@include"):
                        if r in line:
                            extension_data["match"].append(line.split(r)[-1].strip("\n\t ").replace("?", "\?").replace("#", "\#").replace("+", "\+").replace("|", "\|"))
                            break
                userscripts.append(extension_data)

reload_userscripts()

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
