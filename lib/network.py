#! /usr/bin/env python3

## network.py ##
# This module contains data related to networking,
# such as a cookie jar, disk cache, and QNetworkAccessManager.
# It also contains a function to detect whether the browser is online or not.

import os.path
import settings
import filtering
import settings
from translate import tr
try:
    from PyQt4.QtCore import QCoreApplication, QUrl, QTimer, SIGNAL
    from PyQt4.QtGui import QInputDialog, QLineEdit
    from PyQt4.QtNetwork import QNetworkInterface, QNetworkCookieJar, QNetworkAccessManager, QNetworkDiskCache, QNetworkRequest, QNetworkReply
except:
    from PySide.QtCore import QCoreApplication, QUrl, QTimer, SIGNAL
    from PySide.QtGui import QInputDialog, QLineEdit
    from PySide.QtNetwork import QNetworkInterface, QNetworkCookieJar, QNetworkAccessManager, QNetworkDiskCache, QNetworkRequest, QNetworkReply

# Global cookiejar to store cookies.
# All nimbus.WebView instances use this.
cookieJar = QNetworkCookieJar(QCoreApplication.instance())

# All incognito nimbus.WebView instances use this one instead.
incognitoCookieJar = QNetworkCookieJar(QCoreApplication.instance())

# Global disk cache.
diskCache = QNetworkDiskCache(QCoreApplication.instance())
diskCache.setCacheDirectory(settings.network_cache_folder)
diskCache.setMaximumCacheSize(settings.setting_to_int("data/MaximumCacheSize"))

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

# Error page generator.
def errorPage(title="Problem loading page", heading="Whoops...", error="Nimbus could not load the requested page.", suggestions=["Try reloading the page.", "Make sure you're connected to the Internet. Once you're connected, try loading this page again.", "Check for misspellings in the URL (e.g. <b>ww.google.com</b> instead of <b>www.google.com</b>).", "The server may be experiencing some downtime. Wait for a while before trying again.", "If your computer or network is protected by a firewall, make sure that Nimbus is permitted ."]):
    return "<!DOCTYPE html><html><title>%(title)s</title><body><h1>%(heading)s</h1><p>%(error)s</p><ul>%(suggestions)s</ul></body></html>" % {"title": tr(title), "heading": tr(heading), "error": tr(error), "suggestions": "".join(["<li>" + tr(suggestion) + "</li>" for suggestion in suggestions])}

# Custom NetworkAccessManager class with support for ad-blocking.
class NetworkAccessManager(QNetworkAccessManager):
    diskCache = diskCache
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
        x = filtering.adblock_filter.match(url.toString())
        y = url.authority() in filtering.host_rules if settings.setting_to_bool("content/HostFilterEnabled") and url.authority() != "" else False
        if url.scheme() == "file" and os.path.isdir(os.path.abspath(url.path())):
            return NetworkReply(self, url, self.GetOperation, "<!DOCTYPE html><html><head><title>" + url.path() + "</title></head><body><object type=\"application/x-qt-plugin\" data=\"" + url.toString() + "\" classid=\"directoryView\" style=\"position: fixed; top: 0; left: 0; width: 100%; height: 100%;\"></object></body></html>")
        elif url.scheme() == "file" and not os.path.isfile(os.path.abspath(url.path())):
            return NetworkReply(self, url, self.GetOperation, "<!DOCTYPE html><html><head><title>Settings</title></head><body><object type=\"application/x-qt-plugin\" classid=\"settingsDialog\" style=\"position: fixed; top: 0; left: 0; width: 100%; height: 100%;\"></object></body></html>")
        if x != None or y:
            return QNetworkAccessManager.createRequest(self, self.GetOperation, QNetworkRequest(QUrl()))
        else:
            return QNetworkAccessManager.createRequest(self, op, request, device)

# Create global instance of NetworkAccessManager.
networkAccessManager = NetworkAccessManager()
incognitoNetworkAccessManager = NetworkAccessManager(nocache=True)

# Clear cache.
def clearCache():
    networkAccessManager.cache().clear()

# This function checks whether the system is connected to a network interface.
# It is used by Nimbus to determine whether the system is connected to the
# Internet, though this is technically a misuse of it.
# Ported from http://stackoverflow.com/questions/2475266/verfiying-the-network-connection-using-qt-4-4
# and http://stackoverflow.com/questions/13533710/pyqt-convert-enum-value-to-key
def isConnectedToNetwork():
    ifaces = QNetworkInterface.allInterfaces()
    result = False
    for iface in ifaces:
        if int(iface.flags() & QNetworkInterface.IsUp) != 0 and int(iface.flags() & QNetworkInterface.IsLoopBack) == 0:
            if len(iface.addressEntries()) > 0:
                result = True
                break
    return result
