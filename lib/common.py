#! /usr/bin/env python3

# ---------
# common.py
# ---------
# Author:      Daniel Sim (foxhead128)
# License:     See LICENSE.md for more details.
# Description: This module contains global variables and objects used by the
#              rest of Nimbus' components.

# Import everything we need.
import traceback
import sys
import os
import subprocess
import locale
import base64
try:
    from PyQt4.QtCore import qVersion, QLocale, QUrl
    from PyQt4.QtGui import QIcon
except:
    from PySide.QtCore import qVersion, QLocale, QUrl
    from PySide.QtGui import QIcon

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
        except: traceback.print_exc()
        f.close()

def topLevelDomains():
    return tlds

# Qt version.
qt_version = qVersion()

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
content_viewers = (("https://docs.google.com/viewer?url=%s", (".doc", ".pps", ".odt", ".sxw", ".pdf", ".ppt", ".pptx", ".docx", ".xls", ".xlsx", ".pages", ".ai", ".psd", ".tif", ".tiff", ".dxf", ".svg", ".eps", ".ps", ".ttf", ".xps", ".zip", ".rar")),
                   ("http://viewdocsonline.com/view.php?url=", (".ods", ".odp", ".odg", ".sxc", ".sxi", ".sxd")),
                   ("http://vuzit.com/view?url=", (".bmp", ".ppm", ".xpm")))

# Get an application icon.
def icon(name):
    return os.path.join(app_icons_folder, name)

# Returns a QIcon
def complete_icon(name):
    try: return QIcon().fromTheme(name, QIcon(icon(name + ".png")))
    except: return QIcon()

def shortenURL(url):
    return QUrl(url).authority().replace("www.", "")

# This stylesheet is applied to toolbars that are blank.
blank_toolbar = "QToolBar { border: 0; background: transparent; }"

# Stores WebView instances.
webviews = []
