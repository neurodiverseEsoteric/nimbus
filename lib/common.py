#! /usr/bin/env python3

# ---------
# common.py
# ---------
# Author:      Daniel Sim (foxhead128)
# License:     See LICENSE.md for more details.
# Description: This module contains global variables and objects used by the
#              rest of Nimbus' components.

# Import everything we need.
import sys
import platform
import os
import subprocess
import locale
import base64
pyqt4 = False
if not "-4" in sys.argv and not "--pyqt4" in sys.argv and not "-pyqt4" in sys.argv:
    try:
        from PyQt5.QtCore import qVersion, QLocale, QUrl
        from PyQt5.QtGui import QIcon
        from PyQt5.QtWebKit import qWebKitVersion
    except:
        try:
            from PyQt4.QtCore import qVersion, QLocale, QUrl
            from PyQt4.QtGui import QIcon
            from PyQt4.QtWebKit import qWebKitVersion
        except:
            from PySide.QtCore import qVersion, QLocale, QUrl
            from PySide.QtGui import QIcon
            from PySide.QtWebKit import qWebKitVersion
        pyqt4 = True
else:
    try:
        from PyQt4.QtCore import qVersion, QLocale, QUrl
        from PyQt4.QtGui import QIcon
        from PyQt4.QtWebKit import qWebKitVersion
    except:
        from PySide.QtCore import qVersion, QLocale, QUrl
        from PySide.QtGui import QIcon
        from PySide.QtWebKit import qWebKitVersion
    pyqt4 = True

def rm(fname):
    subprocess.Popen(["rm", fname])

if sys.platform.startswith("win"):
    import shutil
    def rmr(fname):
        shutil.rmtree(fname)
    def cp(fname, dest):
        shutil.copy2(fname, dest)
    def cpr(fname, dest):
        shutil.copytree(fname, dest)
else:
    def rmr(fname):
        os.system("rm -rf \"%s\"" % (fname,))
    def cp(fname, dest):
        subprocess.Popen(["cp", fname, dest])
    def cpr(fname, dest):
        subprocess.Popen(["cp", "-r", fname, dest])

def htmlToBase64(html):
    return "data:text/html;charset=utf-8;base64," + base64.b64encode((html.replace('\n', '')).encode('utf-8')).decode('utf-8')

def cssToBase64(css):
    return "data:text/css;charset=utf-8;base64," + base64.b64encode((css.replace('\n', '')).encode('utf-8')).decode('utf-8')

# Folder that Nimbus is stored in.
app_folder = os.path.dirname(os.path.realpath(__file__)) if sys.executable != os.path.dirname(__file__) else os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# Start page
startpage = os.path.join(app_folder, "start.html")

# Extensions folder
extensions_folder = os.path.join(app_folder, "extensions")

# Icons folder
app_icons_folder = os.path.join(app_folder, "icons")

# Version info file
app_version_file = os.path.join(app_folder, "version.txt")

# Nimbus version
app_version = "0.0.0pre"
if os.path.isfile(app_version_file):
    try: f = open(app_version_file, "r")
    except: pass
    else:
        try: app_version = f.read().replace("\n", "")
        except: pass
        f.close()

# Valid top-level domains.
tlds_file = os.path.join(app_folder, "tlds.txt")
tlds = []
if os.path.isfile(tlds_file):
    try: f = open(tlds_file, "r")
    except: pass
    else:
        try: tlds = ["." + dom for dom in f.read().split("\n") if dom != ""]
        except: pass
        f.close()

def topLevelDomains():
    return tlds

# Qt version.
qt_version = qVersion()

defaultUserAgent = "Nimbus/%(app_version)s (%(system)s) AppleWebKit/%(webkit_version)s (KHTML, like Gecko) Chrome/22.%(qt_version)s" % {"app_version": app_version, "system": platform.system(), "qt_version": qt_version, "webkit_version": qWebKitVersion()}
mobileUserAgent = "Mozilla/5.0 (Linux; U; Android 2.3.5; en-us) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"

# Default user agent.
def createUserAgent():
    pass

# Python locale
try: app_locale = str(locale.getlocale()[0])
except: app_locale = str(QLocale.system().name())

# WIDGET RELATED #

# This is a global store for the settings dialog.
settingsDialog = None

#####################
# DIRECTORY-RELATED #
#####################

###################
# ADBLOCK-RELATED #
###################

# Content viewers
content_viewers = (("http://view.samurajdata.se/ps.php?url=%s", (".pdf", ".ps.gz", ".ps", ".doc")),
                   ("https://docs.google.com/viewer?url=%s", (".pps", ".odt", ".sxw", ".ppt", ".pptx", ".docx", ".xls", ".xlsx", ".pages", ".ai", ".psd", ".tif", ".tiff", ".dxf", ".svg", ".eps", ".ttf", ".xps", ".zip", ".rar")),
                   ("http://viewdocsonline.com/view.php?url=", (".ods", ".odp", ".odg", ".sxc", ".sxi", ".sxd")),
                   ("http://vuzit.com/view?url=", (".bmp", ".ppm", ".xpm")))

# Get an application icon.
def icon(name):
    return os.path.join(app_icons_folder, name)

complete_icons = {}

# Returns a QIcon
def complete_icon(name):
    global complete_icons
    try: return complete_icons[name]
    except:
        ic = icon(name + ".png")
        if not os.path.isfile(ic):
            ic = icon(name + ".gif")
        try: nic = QIcon().fromTheme(name, QIcon(ic))
        except: nic = QIcon()
        complete_icons[name] = nic
        return complete_icons[name]

def shortenURL(url):
    return QUrl(url).authority().replace("www.", "")

# This stylesheet is applied to toolbars that are blank.
blank_toolbar = "QToolBar { border: 0; background: transparent; }"

# Stores WebView instances.
webviews = []

# Stores WebView instances.
disconnected = []
