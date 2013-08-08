#! /usr/bin/env python3

# Import everything we need.
import sys
import os
import abpy
import json
try:
    from PySide.QtCore import QTimer, SIGNAL, QByteArray, QCoreApplication, QSettings, QThread, QUrl
    from PySide.QtGui import QIcon, QInputDialog, QLineEdit
    from PySide.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkCookieJar, QNetworkDiskCache, QNetworkCookie, QNetworkReply
except:
    from PyQt4.QtCore import QTimer, SIGNAL, QByteArray, QCoreApplication, QSettings, QThread, QUrl
    from PyQt4.QtGui import QIcon, QInputDialog, QLineEdit
    from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkCookieJar, QNetworkDiskCache, QNetworkCookie, QNetworkReply

#####################
# DIRECTORY-RELATED #
#####################

# Folder that Nimbus is stored in.
app_folder = os.path.dirname(os.path.realpath(__file__)) if sys.executable != os.path.dirname(__file__) else os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# Icons folder
app_icons_folder = os.path.join(app_folder, "icons")

####################
# SETTINGS-RELATED #
####################

# Common settings manager.
settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "nimbus", "config", QCoreApplication.instance())
data = QSettings(QSettings.IniFormat, QSettings.UserScope, "nimbus", "data", QCoreApplication.instance())

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
                    "content/AdblockEnabled": False,
                    "content/ReplaceHTML5MediaTagsWithEmbedTags": (True if "win" in sys.platform else False),
                    "content/UseOnlineContentViewers": True,
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

# This stores the cache.
network_cache_folder = os.path.join(settings_folder, "Cache")
offline_cache_folder = os.path.join(settings_folder, "OfflineCache")

###################
# ADBLOCK-RELATED #
###################

# Dummy adblock filter class.
class Filter(object):
    def __init__(self, rules):
        super(Filter, self).__init__()
        self.index = {}
    def match(self, url):
        return None

# Global stuff.
adblock_folder = os.path.join(settings_folder, "adblock")
easylist = os.path.join(app_folder, "easylist.txt")
adblock_filter = Filter([])
shelved_filter = None
adblock_rules = []

# Content viewers
content_viewers = (("https://docs.google.com/viewer?embedded=true&url=%s", (".doc", ".pps", ".odt", ".sxw", ".pdf", ".ppt", ".pptx", ".docx", ".xls", ".xlsx", ".pages", ".ai", ".psd", ".tif", ".tiff", ".dxf", ".svg", ".eps", ".ps", ".ttf", ".xps", ".zip", ".rar")),
                   ("http://viewdocsonline.com/view.php?url=", (".ods", ".odp", ".odg", ".sxc", ".sxi", ".sxd")),
                   ("http://vuzit.com/view?url=", (".bmp", ".ppm", ".xpm")))

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
        self.quit()

# Create thread to load adblock filters.
adblock_filter_loader = AdblockFilterLoader()

# Get an application icon.
def icon(name):
    return os.path.join(app_icons_folder, name)

# Returns a QIcon
def complete_icon(name):
    try: return QIcon().fromTheme(name, QIcon(icon(name + ".png")))
    except: return QIcon()

# Global list to store history.
history = []

# Global cookiejar to store cookies.
# All nimbus.WebView instances use this.
cookieJar = QNetworkCookieJar(QCoreApplication.instance())

# All incognito nimbus.WebView instances use this one instead.
incognitoCookieJar = QNetworkCookieJar(QCoreApplication.instance())

# Global disk cache.
diskCache = QNetworkDiskCache(QCoreApplication.instance())

# Subclass of QNetworkReply that loads a local folder.
class NetworkReply(QNetworkReply):
    def __init__(self, parent, url, operation, content=""):
        QNetworkReply.__init__(self, parent)
        self.content = content
        self.offset = 0
        self.setHeader(QNetworkRequest.ContentTypeHeader, "text/html; charset=UTF-8")
        self.setHeader(QNetworkRequest.ContentLengthHeader, len(self.content))
        QTimer.singleShot(0, self, SIGNAL("readyRead()"))
        QTimer.singleShot(0, self, SIGNAL("finished()"))
        self.open(self.ReadOnly | self.Unbuffered)
        self.setUrl(url)

    def abort(self):
        pass

    def bytesAvailable(self):
        return len(self.content) - self.offset
    
    def isSequential(self):
        return True

    def readData(self, maxSize):
        if self.offset < len(self.content):
            end = min(self.offset + maxSize, len(self.content))
            data = self.content[self.offset:end]
            data = data.encode("utf-8")
            self.offset = end
            return bytes(data)

# Custom NetworkAccessManager class with support for ad-blocking.
class NetworkAccessManager(QNetworkAccessManager):
    diskCache = diskCache
    diskCache.setCacheDirectory(network_cache_folder)
    def __init__(self, *args, nocache=False, **kwargs):
        super(NetworkAccessManager, self).__init__(*args, **kwargs)
        if not nocache:
            self.setCache(self.diskCache)
            self.diskCache.setParent(QCoreApplication.instance())
        self.authenticationRequired.connect(self.provideAuthentication)
    def provideAuthentication(self, reply, auth):
        username = QInputDialog.getText(None, "Authentication", "Enter your username:", QLineEdit.Normal)
        if username[1]:
            auth.setUser(username[0])
            password = QInputDialog.getText(None, "Authentication", "Enter your password:", QLineEdit.Password)
            if password[1]:
                auth.setPassword(password[0])
    def createRequest(self, op, request, device=None):
        url = request.url()
        x = adblock_filter.match(url.toString())
        if url.scheme() == "file" and os.path.isdir(os.path.abspath(url.path())):
            return NetworkReply(self, url, self.GetOperation, "<!DOCTYPE html><html><head><title>" + url.path() + "</title></head><body><object type=\"application/x-qt-plugin\" data=\"" + url.toString() + "\" classid=\"directoryView\" style=\"position: fixed; top: 0; left: 0; width: 100%; height: 100%;\"></object></body></html>")
        elif url.scheme() == "file" and not os.path.isfile(os.path.abspath(url.path())):
            return NetworkReply(self, url, self.GetOperation, "<!DOCTYPE html><html><head><title>Settings</title></head><body><object type=\"application/x-qt-plugin\" classid=\"settingsDialog\" style=\"position: fixed; top: 0; left: 0; width: 100%; height: 100%;\"></object></body></html>")
        if x != None:
            return QNetworkAccessManager.createRequest(self, QNetworkAccessManager.GetOperation, QNetworkRequest(QUrl()))
        else:
            return QNetworkAccessManager.createRequest(self, op, request, device)

# Create global instance of NetworkAccessManager.
networkAccessManager = NetworkAccessManager()
incognitoNetworkAccessManager = NetworkAccessManager(nocache=True)

# This function loads the browser's settings.
def loadData():
    # Load history.
    global history
    raw_history = data.value("data/History")
    if type(raw_history) is str:
        history = json.loads(raw_history)

    # Load cookies.
    try: raw_cookies = json.loads(str(data.value("data/Cookies")))
    except: return
    if type(raw_cookies) is list:
        cookies = [QNetworkCookie().parseCookies(QByteArray(cookie))[0] for cookie in raw_cookies]
        cookieJar.setAllCookies(cookies)

def shortenURL(url):
    url2 = (url.partition("://")[-1] if "://" in url else url)
    url2 = url2.replace(("www." if url2.startswith("www.") else ""), "")
    return url2

# This function saves the browser's settings.
def saveData():
    # Save history.
    global history
    history = [(item.partition("://")[-1] if "://" in item else item) for item in history]
    history = [item.replace(("www." if item.startswith("www.") else ""), "") for item in history]
    history = list(set(history))
    history.sort()
    data.setValue("data/History", json.dumps(history))

    # Save cookies.
    cookies = json.dumps([cookie.toRawForm().data().decode("utf-8") for cookie in cookieJar.allCookies()])
    data.setValue("data/Cookies", cookies)

    # Sync any unsaved settings.
    data.sync()

# Clear history.
def clearHistory():
    global history
    history = []
    saveData()

# Clear cookies.
def clearCookies():
    cookieJar.setAllCookies([])
    incognitoCookieJar.setAllCookies([])
    saveData()

# Clear cache:
def clearCache():
    networkAccessManager.cache().clear()

# New tab page.
new_tab_page = os.path.join(settings_folder, "new-tab-page.html")

# Lock file used to determine if program is running.
# This is obsolete. Nimbus now uses D-Bus to determine whether it is running or not.
lock_file = os.path.join(settings_folder, ".lock")

# This stylesheet is applied to toolbars that are blank.
blank_toolbar = "QToolBar { border: 0; background: transparent; }"

# Stores WebView instances.
webviews = []

# Stores browser windows.
windows = []

# List of extensions.
extensions_folder = os.path.join(app_folder, "extensions")
extensions = []

# Reloads extensions.
def reload_extensions():
    global extensions
    if os.path.isdir(extensions_folder):
        extensions = sorted(os.listdir(extensions_folder))
    else:
        extensions = []

reload_extensions()

# Stores all extension buttons.
extension_buttons = []

# List of extensions not to load.
extensions_blacklist = []

# Reloads extension blacklist.
def reload_extensions_blacklist():
    global extensions_blacklist
    if settings.value("extensions/whitelist") != None:
        extensions_blacklist = [extension for extension in extensions if extension not in settings.value("extensions/whitelist")]
    else:
        extensions_blacklist = [extension for extension in extensions]

# Clear extensions.
def reset_extensions():
    global extension_buttons
    for extension in extension_buttons:
        extension.deleteLater()
    while len(extension_buttons) > 0:
        extension_buttons.pop()

# Reload extension blacklist.
reload_extensions_blacklist()
