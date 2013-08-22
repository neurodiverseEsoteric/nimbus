#! /usr/bin/env python3

###############
## nimbus.py ##
###############

# Description:
# This is the core module that contains all the very specific components
# related to loading Nimbus.

# Import everything we need.
import sys
import os
import json
import re
import subprocess
import copy
import traceback
import hashlib

# This is a hack for installing Nimbus.
try: import common
except: import nimbus.common as common
sys.path.append(common.app_folder)

import geolocation
import browser
import filtering
import translate
from translate import tr
import custom_widgets
import clear_history_dialog
import settings
if not os.path.exists(settings.extensions_folder):
    import shutil
import status_bar
import extension_server
import settings_dialog
import data
import network

# Python DBus
has_dbus = True
try:
    import dbus
    import dbus.service
    from dbus.mainloop.qt import DBusQtMainLoop
except:
    has_dbus = False

# This was made for an attempt to compile Nimbus to CPython,
# but it is now useless.
try: exec
except:
    def exec(code):
        pass

# Extremely specific imports from PyQt4/PySide.
# We give PyQt4 priority because it supports Qt5.
try:
    from PyQt4.QtCore import Qt, QObject, QCoreApplication, pyqtSignal, pyqtSlot, QUrl, QFile, QIODevice, QTimer
    from PyQt4.QtGui import QApplication, QDockWidget, QKeySequence, QListWidget, QSpinBox, QListWidgetItem, QMessageBox, QIcon, QMenu, QAction, QMainWindow, QToolBar, QToolButton, QComboBox, QLineEdit, QTabWidget, QPrinter, QPrintDialog, QPrintPreviewDialog, QInputDialog, QFileDialog, QProgressBar, QLabel, QCalendarWidget, QSlider, QFontComboBox, QLCDNumber, QImage, QDateTimeEdit, QDial, QSystemTrayIcon
    from PyQt4.QtNetwork import QNetworkProxy, QNetworkRequest, QNetworkAccessManager
    from PyQt4.QtWebKit import QWebView, QWebPage
    Signal = pyqtSignal
    Slot = pyqtSlot
except:
    from PySide.QtCore import Qt, QObject, QCoreApplication, Signal, Slot, QUrl, QFile, QIODevice, QTimer
    from PySide.QtGui import QApplication, QDockWidget, QKeySequence, QListWidget, QSpinBox, QListWidgetItem, QMessageBox, QIcon, QMenu, QAction, QMainWindow, QToolBar, QToolButton, QComboBox, QLineEdit, QTabWidget, QPrinter, QPrintDialog, QPrintPreviewDialog, QInputDialog, QFileDialog, QProgressBar, QLabel, QCalendarWidget, QSlider, QFontComboBox, QLCDNumber, QImage, QDateTimeEdit, QDial, QSystemTrayIcon
    from PySide.QtNetwork import QNetworkProxy, QNetworkRequest, QNetworkAccessManager
    from PySide.QtWebKit import QWebView, QWebPage

# chdir to the app folder. This way, we won't have issues related to
# relative paths.
os.chdir(common.app_folder)

# Create extension server.
server_thread = extension_server.ExtensionServerThread()

# Add an item to the browser history.
def addHistoryItem(url):
    if not url in data.history and settings.setting_to_bool("data/RememberHistory"):
        data.history.append(url)

# Progress bar used for downloads.
# This was ripped off of Ryouko.
class DownloadProgressBar(QProgressBar):

    # Initialize class.
    def __init__(self, reply=False, destination=os.path.expanduser("~"), parent=None):
        super(DownloadProgressBar, self).__init__(parent)
        self.setWindowTitle(reply.request().url().toString().split("/")[-1])
        self.networkReply = reply
        self.destination = destination
        self.progress = [0, 0]
        if self.networkReply:
            self.networkReply.downloadProgress.connect(self.updateProgress)
            self.networkReply.finished.connect(self.finishDownload)

    # Writes downloaded file to the disk.
    def finishDownload(self):
        if self.networkReply.isFinished():
            data = self.networkReply.readAll()
            f = QFile(self.destination)
            f.open(QIODevice.WriteOnly)
            f.write(data)
            f.flush()
            f.close()
            self.progress = [0, 0]
            if sys.platform.startswith("linux"):
                subprocess.Popen(["notify-send", "--icon=emblem-downloads", tr("Download complete: %s") % (os.path.split(self.destination)[1],)])
            else:
                common.trayIcon.showMessage(tr("Download complete"), os.path.split(self.destination)[1])

    # Updates the progress bar.
    def updateProgress(self, received, total):
        self.setMaximum(total)
        self.setValue(received)
        self.progress[0] = received
        self.progress[1] = total
        self.show()

    # Abort download.
    def abort(self):
        self.networkReply.abort()

# File download toolbar.
# These are displayed at the bottom of a MainWindow.
class DownloadBar(QToolBar):
    def __init__(self, reply, destination, parent=None):
        super(DownloadBar, self).__init__(parent)
        self.setMovable(False)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setStyleSheet(common.blank_toolbar)
        label = QLabel(self)
        self.addWidget(label)
        self.progressBar = DownloadProgressBar(reply, destination, self)
        self.progressBar.networkReply.finished.connect(self.close)
        self.progressBar.networkReply.finished.connect(self.deleteLater)
        self.addWidget(self.progressBar)
        label.setText(os.path.split(self.progressBar.destination)[1])
        abortAction = QAction(QIcon().fromTheme("process-stop", QIcon(common.icon("process-stop.png"))), tr("Abort"), self)
        abortAction.triggered.connect(self.progressBar.abort)
        abortAction.triggered.connect(self.deleteLater)
        self.addAction(abortAction)

# Class for exposing fullscreen API to DOM.
class FullScreenRequester(QObject):
    fullScreenRequested = Signal(bool)
    @Slot(bool)
    def setFullScreen(self, fullscreen=False):
        self.fullScreenRequested.emit(fullscreen)

# Custom WebPage class with support for filesystem.
class WebPage(QWebPage):
    plugins = (("qcalendarwidget", QCalendarWidget),
               ("qslider", QSlider),
               ("qprogressbar", QProgressBar),
               ("qfontcombobox", QFontComboBox),
               ("qlcdnumber", QLCDNumber),
               ("qimage", QImage),
               ("qdatetimeedit", QDateTimeEdit),
               ("qdial", QDial),
               ("qspinbox", QSpinBox))
    
    # This is used to fire JavaScript events related to navigator.onLine.
    isOnlineTimer = QTimer()

    fullScreenRequested = Signal(bool)
    def __init__(self, *args, **kwargs):
        super(WebPage, self).__init__(*args, **kwargs)

        # Load userContent.css
        if os.path.exists(filtering.adblock_css):
            self.settings().setUserStyleSheetUrl(QUrl(filtering.adblock_css))

        # Connect this so that permissions for geolocation and stuff work.
        self.featurePermissionRequested.connect(self.permissionRequested)

        # This object is exposed to the DOM to allow geolocation.
        self.geolocation = geolocation.Geolocation(self)

        # This object is exposed to the DOM to allow full screen mode.
        self.fullScreenRequester = FullScreenRequester(self)
        self.fullScreenRequester.fullScreenRequested.connect(self.toggleFullScreen)

        self._userScriptsLoaded = False
        self.mainFrame().javaScriptWindowObjectCleared.connect(lambda: self.setUserScriptsLoaded(False))

        # Connect to self.tweakDOM, which carries out some hacks to
        # improve HTML5 support.
        self.mainFrame().javaScriptWindowObjectCleared.connect(self.tweakDOM)

        # Connect loadFinished to checkForNavigatorGeolocation and loadUserScripts.
        self.loadFinished.connect(self.checkForNavigatorGeolocation)
        self.loadFinished.connect(self.loadUserScripts)

        # This stores the user agent.
        self._userAgent = ""
        self._fullScreen = False

        # Start self.isOnlineTimer.
        if not self.isOnlineTimer.isActive():
            self.isOnlineTimer.timeout.connect(self.setNavigatorOnline)
            self.isOnlineTimer.start(1000)

        # Set user agent to default value.
        self.setUserAgent()

    # Sends a request to become fullscreen.
    def toggleFullScreen(self):
        if self._fullScreen:
            self.fullScreenRequested.emit(False)
            self._fullScreen = False
        else:
            self.fullScreenRequested.emit(True)
            self._fullScreen = True

    def setUserScriptsLoaded(self, loaded=False):
        self._userScriptsLoaded = loaded

    # Load userscripts.
    def loadUserScripts(self):
        if not self._userScriptsLoaded:
            self._userScriptsLoaded = True
            for userscript in settings.userscripts:
                for match in userscript["match"]:
                    if match == "*":
                        r = True
                    else:
                        r = re.match(match, self.mainFrame().url().toString())
                    if r:
                        self.mainFrame().evaluateJavaScript(userscript["content"])
                        break

    # Returns user agent string.
    def userAgentForUrl(self, url):

        if not "github" in url.authority():
            return self._userAgent
        # This is a workaround for GitHub not loading properly
        # with the default Nimbus user agent.
        else:
            return QWebPage.userAgentForUrl(self, url)

    # Convenience function.
    def setUserAgent(self, ua=None):
        if type(ua) is str:
            self._userAgent = ua
        else:
            self._userAgent = common.defaultUserAgent

    # This is a hacky way of checking whether a website wants to use
    # geolocation. It checks the page source for navigator.geolocation,
    # and if it is present, it assumes that the website wants to use it.
    def checkForNavigatorGeolocation(self):
        if "navigator.geolocation" in self.mainFrame().toHtml() and not self.mainFrame().url().authority() in data.geolocation_whitelist:
            self.allowGeolocation()

    # Prompts the user to enable or block geolocation, and reloads the page if the
    # user said yes.
    def allowGeolocation(self):
        reload_ = self.permissionRequested(self.mainFrame(), self.Geolocation)
        if reload_:
            self.action(self.Reload).trigger()

    # Sets permissions for features.
    # Currently supports geolocation.
    def permissionRequested(self, frame, feature):
        authority = frame.url().authority()
        if feature == self.Geolocation and frame == self.mainFrame() and settings.setting_to_bool("network/GeolocationEnabled") and not authority in data.geolocation_blacklist:
            confirm = True
            if not authority in data.geolocation_whitelist:
                confirm = QMessageBox.question(None, tr("Nimbus"), tr("This website would like to track your location."), QMessageBox.Ok | QMessageBox.No | QMessageBox.NoToAll, QMessageBox.Ok)
            if confirm == QMessageBox.Ok:
                if not authority in data.geolocation_whitelist:
                    data.geolocation_whitelist.append(authority)
                    data.saveData()
                self.setFeaturePermission(frame, feature, self.PermissionGrantedByUser)
            elif confirm == QMessageBox.NoToAll:
                if not authority in data.geolocation_blacklist:
                    data.geolocation_blacklist.append(authority)
                    data.saveData()
                self.setFeaturePermission(frame, feature, self.PermissionDeniedByUser)
            return confirm == QMessageBox.Ok
        return False

    # Fires JavaScript events pertaining to online/offline mode.
    def setNavigatorOnline(self):
        script = "window.navigator.onLine = " + str(network.isConnectedToNetwork()).lower() + ";"
        self.mainFrame().evaluateJavaScript(script)
        self.mainFrame().evaluateJavaScript("if (window.onLine) {\n" + \
                                            "   document.dispatchEvent(window.nimbus.onLineEvent);\n" + \
                                            "}")
        self.mainFrame().evaluateJavaScript("if (!window.onLine) {\n" + \
                                            "   document.dispatchEvent(window.nimbus.offLineEvent);\n" + \
                                            "}")

    # This loads a bunch of hacks to improve HTML5 support.
    def tweakDOM(self):
        authority = self.mainFrame().url().authority()
        self.mainFrame().addToJavaScriptWindowObject("nimbusFullScreenRequester", self.fullScreenRequester)
        self.mainFrame().evaluateJavaScript("window.nimbus = new Object();")
        self.mainFrame().evaluateJavaScript("window.nimbus.fullScreenRequester = nimbusFullScreenRequester; delete nimbusFullScreenRequester;")
        if settings.setting_to_bool("network/GeolocationEnabled") and authority in data.geolocation_whitelist:
            self.mainFrame().addToJavaScriptWindowObject("nimbusGeolocation", self.geolocation)
            script = "window.nimbus.geolocation = nimbusGeolocation;\n" + \
                     "delete nimbusGeolocation;\n" + \
                     "window.navigator.geolocation = {};\n" + \
                     "window.navigator.geolocation.getCurrentPosition = function(success, error, options) { var getCurrentPosition = eval('(' + window.nimbus.geolocation.getCurrentPosition() + ')'); success(getCurrentPosition); return getCurrentPosition; };"
            self.mainFrame().evaluateJavaScript(script)
        self.mainFrame().evaluateJavaScript("HTMLElement.prototype.requestFullScreen = function() { window.nimbus.fullScreenRequester.setFullScreen(true); var style = ''; if (this.hasAttribute('style')) { style = this.getAttribute('style'); }; this.setAttribute('oldstyle', style); this.setAttribute('style', style + ' position: fixed; top: 0; left: 0; padding: 0; margin: 0; width: 100%; height: 100%;'); document.fullScreen = true; }")
        self.mainFrame().evaluateJavaScript("HTMLElement.prototype.requestFullscreen = HTMLElement.prototype.requestFullScreen")
        self.mainFrame().evaluateJavaScript("HTMLElement.prototype.webkitRequestFullScreen = HTMLElement.prototype.requestFullScreen")
        self.mainFrame().evaluateJavaScript("document.cancelFullScreen = function() { window.nimbus.fullScreenRequester.setFullScreen(false); document.fullScreen = false; var allElements = document.getElementsByTagName('*'); for (var i=0;i<allElements.length;i++) { var element = allElements[i]; if (element.hasAttribute('oldstyle')) { element.setAttribute('style', element.getAttribute('oldstyle')); } } }")
        self.mainFrame().evaluateJavaScript("document.webkitCancelFullScreen = document.cancelFullScreen")
        self.mainFrame().evaluateJavaScript("document.fullScreen = false;")
        self.mainFrame().evaluateJavaScript("document.exitFullscreen = document.cancelFullScreen")
        self.mainFrame().evaluateJavaScript("window.nimbus.onLineEvent = document.createEvent('Event');\n" + \
                                            "window.nimbus.onLineEvent.initEvent('online',true,false);")
        self.mainFrame().evaluateJavaScript("window.nimbus.offLineEvent = document.createEvent('Event');\n" + \
                                            "window.nimbus.offLineEvent.initEvent('offline',true,false);")

    # Creates Qt-based plugins.
    # One plugin pertains to the settings dialog,
    # while another pertains to local directory views.
    def createPlugin(self, classid, url, paramNames, paramValues):
        if classid.lower() == "settingsdialog":
            sdialog = settings_dialog.SettingsDialog(self.view())
            return sdialog
        elif classid.lower() == "directoryview":
            directoryview = QListWidget(self.view())
            try:
                if 1:
                    u = url.path()
                    u2 = QUrl(u).path()
                    directoryview.addItem(os.path.dirname(u2))
                    if os.path.isdir(u2):
                        l = os.listdir(u2)
                        l.sort()
                        for fname in l:
                            directoryview.addItem(os.path.join(u2, fname))
                    directoryview.itemDoubleClicked.connect(lambda item: self.mainFrame().load(QUrl(item.text())))
                    directoryview.itemActivated.connect(lambda item: self.mainFrame().load(QUrl(item.text())))
            except: pass
            else: return directoryview
        else:
            for name, widgetclass in self.plugins:
                if classid.lower() == name:
                    widget = widgetclass(self.view())
                    widgetid = classid
                    pnames = [name.lower() for name in paramNames]
                    if "id" in pnames:
                        widgetid = paramValues[pnames.index("id")]
                    self.mainFrame().addToJavaScriptWindowObject(widgetid, widget)
                    return widget
        return

# Custom WebView class with support for ad-blocking, new tabs, downloads,
# recording history, and more.
class WebView(QWebView):

    # This is used to store references to webViews so that they don't
    # automatically get cleaned up.
    webViews = []

    # Downloads
    downloads = []

    # This is a signal used to inform everyone a new window was created.
    windowCreated = Signal(QWebView)

    # This is a signal used to tell everyone a download has started.
    downloadStarted = Signal(QToolBar)

    # Initialize class.
    def __init__(self, *args, incognito=False, **kwargs):
        super(WebView, self).__init__(*args, **kwargs)

        # Add this webview to the list of webviews.
        common.webviews.append(self)
        self._url = ""

        self._cacheLoaded = False

        # Private browsing.
        self.incognito = incognito

        # Stores the mime type of the current page.
        self._contentType = None

        # This is used to store the text entered in using WebView.find(),
        # so that WebView.findNext() and WebView.findPrevious() work.
        self._findText = False

        # This is used to store the current status message.
        self._statusBarMessage = ""

        # This is used to store the current page loading progress.
        self._loadProgress = 0

        # This stores the link last hovered over.
        self._hoveredLink = ""

        self.setPage(WebPage(self))

        # Create a NetworkAccessmanager that supports ad-blocking and set it.
        if not self.incognito:
            self.nAM = network.networkAccessManager
            self.page().setNetworkAccessManager(self.nAM)
            self.nAM.setParent(QCoreApplication.instance())
        else:
            self.nAM = network.incognitoNetworkAccessManager
            self.page().setNetworkAccessManager(self.nAM)
            self.nAM.setParent(QCoreApplication.instance())

        # Enable Web Inspector
        self.settings().setAttribute(self.settings().DeveloperExtrasEnabled, True)

        self.updateProxy()
        self.updateNetworkSettings()
        self.updateContentSettings()

        # What to do if private browsing is not enabled.
        if not self.incognito:
            # Set persistent storage path to settings_folder.
            self.settings().enablePersistentStorage(settings.settings_folder)

            # Set the CookieJar.
            self.page().networkAccessManager().setCookieJar(network.cookieJar)

            # Do this so that cookieJar doesn't get deleted along with WebView.
            network.cookieJar.setParent(QCoreApplication.instance())

            # Recording history should only be done in normal browsing mode.
            self.urlChanged.connect(self.addHistoryItem)

        # What to do if private browsing is enabled.
        else:
            # Global incognito cookie jar, so that logins are preserved
            # between incognito tabs.
            self.page().networkAccessManager().setCookieJar(network.incognitoCookieJar)
            network.incognitoCookieJar.setParent(QCoreApplication.instance())

            # Enable private browsing for QWebSettings.
            self.settings().setAttribute(self.settings().PrivateBrowsingEnabled, True)

        # Handle unsupported content.
        self.page().setForwardUnsupportedContent(True)
        self.page().unsupportedContent.connect(self.handleUnsupportedContent)

        # This is what Nimbus should do when faced with a file to download.
        self.page().downloadRequested.connect(self.downloadFile)

        # Connect signals.
        self.titleChanged.connect(self.setWindowTitle)
        self.page().linkHovered.connect(self.setStatusBarMessage)
        self.statusBarMessage.connect(self.setStatusBarMessage)
        self.loadProgress.connect(self.setLoadProgress)

        # PyQt4 doesn't support <audio> and <video> tags on Windows.
        # This is a little hack to work around it.
        self.loadStarted.connect(self.resetContentType)
        self.loadFinished.connect(self.replaceAVTags)
        self.loadFinished.connect(self.savePageToCache)

        # Check if content viewer.
        self._isUsingContentViewer = False
        self.loadStarted.connect(self.checkIfUsingContentViewer)
        self.loadFinished.connect(self.finishLoad)

        self.setWindowTitle("")

        if os.path.exists(settings.new_tab_page):
            self.load(QUrl("about:blank"))

    # Calls network.errorPage.
    def errorPage(self, title="Problem loading page", heading="Whoops...", error="Nimbus could not load the requested page.", suggestions=["Try reloading the page.", "Make sure you're connected to the Internet. Once you're connected, try loading this page again.", "Check for misspellings in the URL (e.g. <b>ww.google.com</b> instead of <b>www.google.com</b>).", "The server may be experiencing some downtime. Wait for a while before trying again.", "If your computer or network is protected by a firewall, make sure that Nimbus is permitted ."]):
        return network.errorPage(title, heading, error, suggestions)

    # This is a half-assed implementation of error pages,
    # which doesn't work yet.
    def supportsExtension(self, extension):
        if extension == QWebPage.ErrorPageExtension:
            return True
        return False

    def extension(self, extension, option=None, output=None):
        if extension == QWebPage.ErrorPageExtension and option != NOne:
            option.frame().setHtml(errorPage())
        else:
            QWebPage.extension(self, extension, option, output)

    # Convenience function.
    def setUserAgent(self, ua):
        self.page().setUserAgent(ua)

    # Returns whether the browser has loaded a content viewer.
    def isUsingContentViewer(self):
        return self._isUsingContentViewer

    # Checks whether the browser has loaded a content viewer.
    # This is necessary so that downloading the original file from
    # Google Docs Viewer doesn't loop back to Google Docs Viewer.
    def checkIfUsingContentViewer(self):
        for viewer in common.content_viewers:
            if viewer[0].replace("%s", "") in self.url().toString():
                self._isUsingContentViewer = True
                return
        self._isUsingContentViewer = False

    # Resets recorded content type.
    def resetContentType(self):
        self._contentType = None

    # Custom implementation of deleteLater that also removes
    # the WebView from common.webviews.
    def deleteLater(self):
        try: common.webviews.remove(self)
        except: pass
        QWebView.deleteLater(self)

    # If a request has finished and the request's URL is the current URL,
    # then set self._contentType.
    def ready(self, response):
        if self._contentType == None and response.url() == self.url():
            try: contentType = response.header(QNetworkRequest.ContentTypeHeader)
            except: contentType = None
            if contentType != None:
                self._contentType = contentType

    # This is a custom implementation of mousePressEvent.
    # It allows the user to Ctrl-click or middle-click links to open them in
    # new tabs.
    def mousePressEvent(self, ev):
        if self._statusBarMessage != "" and (((QCoreApplication.instance().keyboardModifiers() == Qt.ControlModifier) and not ev.button() == Qt.RightButton) or ev.button() == Qt.MidButton or ev.button() == Qt.MiddleButton):
            url = self._statusBarMessage
            ev.ignore()
            newWindow = self.createWindow(QWebPage.WebBrowserWindow)
            newWindow.load(QUrl(url))
        else:
            return QWebView.mousePressEvent(self, ev)

    # Creates an error page.
    def errorPage(self, *args, **kwargs):
        self.setHtml(network.errorPage(*args, **kwargs))

    # This loads a page from the cache if certain network errors occur.
    # If that can't be done either, it produces an error page.
    def finishLoad(self, ok=False):
        if not ok:
            success = False
            if not network.isConnectedToNetwork():
                success = self.loadPageFromCache(self._url)
            if not success:
                if not network.isConnectedToNetwork():
                    self.errorPage("Problem loading page", "No Internet connection", "Your computer is not connected to the Internet. You may want to try the following:", ["<b>Windows 7 or Vista:</b> Click the <i>Start</i> button, then click <i>Control Panel</i>. Type <b>network</b> into the search box, click <i>Network and Sharing Center</i>, click <i>Set up a new connection or network</i>, and then double-click <i>Connect to the Internet</i>. From there, follow the instructions. If the network is password-protected, you will have to enter the password.", "<b>Windows 8:</b> Open the <i>Settings charm</i> and tap or click the Network icon (shaped like either five bars or a computer screen with a cable). Select the network you want to join, then tap or click <i>Connect</i>.", "<b>Mac OS X:</b> Click the AirPort icon (the icon shaped like a slice of pie near the top right of your screen). From there, select the network you want to join. If the network is password-protected, enter the password.", "<b>Ubuntu (Unity and Xfce):</b> Click the Network Indicator (the icon with two arrows near the upper right of your screen). From there, select the network you want to join. If the network is password-protected, enter the password.", "<b>Other Linux:</b> Oh, come on. I shouldn't have to be telling you this.", "Alternatively, if you have access to a wired Ethernet connection, you can simply plug the cable into your computer."])
                #else:
                    #self.errorPage()
            else:
                self._cacheLoaded = True

    # Hacky custom implementation of QWebView.load(),
    # which can load a saved new tab page as well as
    # the settings dialog.
    def load(self, url):
        if type(url) is QListWidgetItem:
            url = QUrl.fromUserInput(url.text())
        self._cacheLoaded = False
        dirname = url.path()
        self._url = url.toString()
        if url.scheme() == "nimbus":
            x = common.htmlToBase64("<!DOCTYPE html><html><head><title>" + tr("Settings") + "</title></head><body><object type=\"application/x-qt-plugin\" classid=\"settingsDialog\" style=\"position: fixed; top: 0; left: 0; width: 100%; height: 100%;\"></object></body></html>")
            QWebView.load(self, QUrl(x))
            return
        if url.toString() == "about:blank":
            if os.path.exists(settings.new_tab_page):
                loadwin = QWebView.load(self, QUrl.fromUserInput(settings.new_tab_page))
            else:
                loadwin = QWebView.load(self, url)
        else:
            loadwin = QWebView.load(self, url)

    # Method to replace all <audio> and <video> tags with <embed> tags.
    # This is mainly a hack for Windows, where <audio> and <video> tags are not
    # properly supported under PyQt4.
    def replaceAVTags(self):
        if not settings.setting_to_bool("content/ReplaceHTML5MediaTagsWithEmbedTags"):
            return
        audioVideo = self.page().mainFrame().findAllElements("audio, video")
        for element in audioVideo:
            attributes = []
            if not "width" in element.attributeNames():
                attributes.append("width=352")
            if not "height" in element.attributeNames():
                attributes.append("height=240")
            if not "autostart" in element.attributeNames():
                attributes.append("autostart=false")
            attributes += ["%s=\"%s\"" % (attribute, element.attribute(attribute),) for attribute in element.attributeNames()]
            if element.firstChild() != None:
                attributes += ["%s=\"%s\"" % (attribute, element.firstChild().attribute(attribute),) for attribute in element.firstChild().attributeNames()]
            embed = "<embed %s></embed>" % (" ".join(attributes),)
            element.replace(embed)

    # Set status bar message.
    def setStatusBarMessage(self, link="", title="", content=""):
        self._statusBarMessage = link

    # Set load progress.
    def setLoadProgress(self, progress):
        self._loadProgress = progress

    # Set the window title. If the title is an empty string,
    # set it to "New Tab".
    def setWindowTitle(self, title):
        if len(title) == 0:
            title = tr("New Tab")
        QWebView.setWindowTitle(self, title)

    # Returns a devilish face if in incognito mode;
    # else page icon.
    def icon(self):
        if self.incognito:
            return common.complete_icon("face-devilish")
        return QWebView.icon(self)

    # Function to update proxy list.
    def updateProxy(self):
        proxyType = str(settings.settings.value("proxy/Type"))
        if proxyType == "None":
            proxyType = "No"
        port = settings.settings.value("proxy/Port")
        if port == None:
            port = common.default_port
        user = str(settings.settings.value("proxy/User"))
        if user == "":
            user = None
        password = str(settings.settings.value("proxy/Password"))
        if password == "":
            password = None
        self.page().networkAccessManager().setProxy(QNetworkProxy(eval("QNetworkProxy." + proxyType + "Proxy"), str(settings.settings.value("proxy/Hostname")), int(port), user, password))

    # Updates content settings based on settings.settings.
    def updateContentSettings(self):
        self.settings().setAttribute(self.settings().AutoLoadImages, settings.setting_to_bool("content/AutoLoadImages"))
        self.settings().setAttribute(self.settings().JavascriptEnabled, settings.setting_to_bool("content/JavascriptEnabled"))
        self.settings().setAttribute(self.settings().JavaEnabled, settings.setting_to_bool("content/JavaEnabled"))
        self.settings().setAttribute(self.settings().PrintElementBackgrounds, settings.setting_to_bool("content/PrintElementBackgrounds"))
        self.settings().setAttribute(self.settings().FrameFlatteningEnabled, settings.setting_to_bool("content/FrameFlatteningEnabled"))
        self.settings().setAttribute(self.settings().PluginsEnabled, settings.setting_to_bool("content/PluginsEnabled"))
        self.settings().setAttribute(self.settings().TiledBackingStoreEnabled, settings.setting_to_bool("content/TiledBackingStoreEnabled"))
        self.settings().setAttribute(self.settings().SiteSpecificQuirksEnabled, settings.setting_to_bool("content/SiteSpecificQuirksEnabled"))

    # Updates network settings based on settings.settings.
    def updateNetworkSettings(self):
        self.settings().setAttribute(self.settings().XSSAuditingEnabled, settings.setting_to_bool("network/XSSAuditingEnabled"))
        self.settings().setAttribute(self.settings().DnsPrefetchEnabled, settings.setting_to_bool("network/DnsPrefetchEnabled"))

    # Handler for unsupported content.
    # This is where the content viewers are loaded.
    def handleUnsupportedContent(self, reply):
        url2 = reply.url()
        url = url2.toString()

        # Make sure the file isn't local, that content viewers are
        # enabled, and private browsing isn't enabled.
        if not url2.scheme() == "file" and settings.setting_to_bool("content/UseOnlineContentViewers") and not self.incognito and not self.isUsingContentViewer():
            for viewer in common.content_viewers:
                try:
                    for extension in viewer[1]:
                        if url.lower().endswith(extension):
                            QWebView.load(self, QUrl(viewer[0] % (url,)))
                            return
                except:
                    pass

        self.downloadFile(reply.request())

    # Downloads a file.
    def downloadFile(self, request):

        if request.url() == self.url():

            # If the file type can be converted to plain text, use savePage
            # method instead.
            for mimeType in ("text", "svg", "html", "xml", "xhtml",):
                if mimeType in str(self._contentType):
                    self.savePage()
                    return

        # Get file name for destination.
        fname = QFileDialog.getSaveFileName(None, tr("Save As..."), os.path.join(os.path.expanduser("~"), request.url().toString().split("/")[-1]), tr("All files (*)"))
        if type(fname) is tuple:
            fname = fname[0]
        if fname:
            reply = self.page().networkAccessManager().get(request)
            
            # Create a DownloadBar instance and append it to list of
            # downloads.
            downloadDialog = DownloadBar(reply, fname, None)
            self.downloads.append(downloadDialog)

            # Emit signal.
            self.downloadStarted.emit(downloadDialog)

    # Loads a page from the offline cache.
    def loadPageFromCache(self, url):
        m = hashlib.md5()
        m.update(common.shortenURL(url).encode('utf-8'))
        h = m.hexdigest()
        try: f = open(os.path.join(settings.offline_cache_folder, h), "r")
        except: traceback.print_exc()
        else:
            try: self.setHtml(f.read())
            except: traceback.print_exc()
            f.close()
            return True
        return False

    # Saves a page to the offline cache.
    def savePageToCache(self):
        if not self.incognito:
            if not os.path.exists(settings.offline_cache_folder):
                try: os.mkdir(settings.offline_cache_folder)
                except: return
            content = self.page().mainFrame().toHtml()
            m = hashlib.md5()
            m.update(common.shortenURL(self.url().toString()).encode('utf-8'))
            h = m.hexdigest()
            try: f = open(os.path.join(settings.offline_cache_folder, h), "w")
            except: traceback.print_exc()
            else:
                try: f.write(content)
                except: traceback.print_exc()
                f.close()

    # Saves the current page.
    # It partially supports saving edits to a page,
    # but this is pretty hacky and doesn't work all the time.
    def savePage(self):
        content = self.page().mainFrame().toHtml()
        if self.url().toString() in ("about:blank", "", QUrl.fromUserInput(settings.new_tab_page).toString(),) and not self._cacheLoaded:
            fname = settings.new_tab_page
            content = content.replace("&lt;", "<").replace("&gt;", ">").replace("<body contenteditable=\"true\">", "<body>")
        else:
            fname = QFileDialog.getSaveFileName(None, tr("Save As..."), os.path.join(os.path.expanduser("~"), self.url().toString().split("/")[-1]), tr("All files (*)"))
        if type(fname) is tuple:
            fname = fname[0]
        if fname:
            try: f = open(fname, "w")
            except: pass
            else:
                try: f.write(content)
                except: pass
                f.close()
                if sys.platform.startswith("linux"):
                    subprocess.Popen(["notify-send", "--icon=emblem-downloads", tr("Download complete: %s") % (os.path.split(fname)[1],)])
                else:
                    common.trayIcon.showMessage(tr("Download complete"), os.path.split(fname)[1])

    # Adds a QUrl to the browser history.
    def addHistoryItem(self, url):
        addHistoryItem(url.toString())

    # Redefine createWindow. Emits windowCreated signal so that others
    # can utilize the newly-created WebView instance.
    def createWindow(self, type):
        webview = WebView(incognito=self.incognito, parent=self.parent())
        self.webViews.append(webview)
        self.windowCreated.emit(webview)
        return webview

    # Convenience function.
    # Opens a very simple find text dialog.
    def find(self):
        if type(self._findText) is not str:
            self._findText = ""
        find = QInputDialog.getText(None, tr("Find"), tr("Search for:"), QLineEdit.Normal, self._findText)
        if find:
            self._findText = find[0]
        else:
            self._findText = ""
        self.findText(self._findText, QWebPage.FindWrapsAroundDocument)

    # Convenience function.
    # Find next instance of text.
    def findNext(self):
        if not self._findText:
            self.find()
        else:
            self.findText(self._findText, QWebPage.FindWrapsAroundDocument)

    # Convenience function.
    # Find previous instance of text.
    def findPrevious(self):
        if not self._findText:
            self.find()
        else:
            self.findText(self._findText, QWebPage.FindWrapsAroundDocument | QWebPage.FindBackward)

    # Opens a print dialog to print page.
    def printPage(self):
        printer = QPrinter()
        self.page().mainFrame().render(printer.paintEngine().painter())
        printDialog = QPrintDialog(printer)
        printDialog.open()
        printDialog.accepted.connect(lambda: self.print(printer))
        printDialog.exec_()

    # Opens a print preview dialog.
    def printPreview(self):
        printer = QPrinter()
        self.page().mainFrame().render(printer.paintEngine().painter())
        printDialog = QPrintPreviewDialog(printer, self)
        printDialog.paintRequested.connect(lambda: self.print(printer))
        printDialog.exec_()
        printDialog.deleteLater()

# Extension button class.
class ExtensionButton(QToolButton):
    def __init__(self, script="", shortcut=None, parent=None):
        super(ExtensionButton, self).__init__(parent)
        if shortcut:
            self.setShortcut(QKeySequence.fromString(shortcut))
        settings.extension_buttons.append(self)
        self._parent = parent
        self.script = script
    def parentWindow(self):
        return self._parent
    def loadScript(self):
        try: exec(self.script)
        except:
            traceback.print_exc()
            self._parent.currentWidget().page().mainFrame().evaluateJavaScript(self.script)

# Custom MainWindow class.
# This contains basic navigation controls, a location bar, and a menu.
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # These are used to store where the mouse pressed down.
        # This is used in a hack to drag the window by the toolbar.
        self.mouseX = False
        self.mouseY = False

        # Add self to global list of windows.
        browser.windows.append(self)

        # Set window icon.
        self.setWindowIcon(common.app_icon)

        # List of closed tabs.
        self.closedTabs = []

        # List of sidebars.
        # Sidebars are part of the (incomplete) extensions API.
        self.sideBars = {}

        # Main toolbar.
        self.toolBar = custom_widgets.MenuToolBar(movable=False, contextMenuPolicy=Qt.CustomContextMenu, parent=self)
        self.addToolBar(self.toolBar)

        # Tab widget for tabbed browsing.
        self.tabs = QTabWidget(self)

        # Remove border around tabs.
        self.tabs.setDocumentMode(True)

        # Allow rearranging of tabs.
        self.tabs.setMovable(True)

        # Update tab titles and icons when the current tab is changed.
        self.tabs.currentChanged.connect(self.updateTabTitles)
        self.tabs.currentChanged.connect(self.updateTabIcons)

        # Hacky way of updating the location bar text when the tab is changed.
        self.tabs.currentChanged.connect(self.updateLocationText)

        # Allow closing of tabs.
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.removeTab)

        self.statusBar = status_bar.StatusBar(self)
        self.addToolBar(Qt.BottomToolBarArea, self.statusBar)
        self.addToolBarBreak(Qt.BottomToolBarArea)

        # Set tabs as central widget.
        self.setCentralWidget(self.tabs)

        # New tab action.
        newTabAction = QAction(common.complete_icon("list-add"), tr("New &Tab"), self)
        newTabAction.setShortcut("Ctrl+T")
        newTabAction.triggered.connect(lambda: self.addTab())

        # New private browsing tab action.
        newIncognitoTabAction = QAction(common.complete_icon("face-devilish"), tr("New &Incognito Tab"), self)
        newIncognitoTabAction.setShortcut("Ctrl+Shift+I")
        newIncognitoTabAction.triggered.connect(lambda: self.addTab(incognito=True))

        # This is used so that the new tab button looks halfway decent,
        # and can actually be inserted into the corner of the tab widget.
        newTabToolBar = QToolBar(movable=False, contextMenuPolicy=Qt.CustomContextMenu, parent=self)

        # We don't want this widget to have any decorations.
        newTabToolBar.setStyleSheet(common.blank_toolbar)

        newTabToolBar.addAction(newIncognitoTabAction)
        newTabToolBar.addAction(newTabAction)
        self.tabs.setCornerWidget(newTabToolBar, Qt.TopRightCorner)

        # These are hidden actions used for the Ctrl[+Shift]+Tab feature
        # you see in most browsers.
        nextTabAction = QAction(self)
        nextTabAction.setShortcut("Ctrl+Tab")
        nextTabAction.triggered.connect(self.nextTab)
        self.addAction(nextTabAction)

        previousTabAction = QAction(self)
        previousTabAction.setShortcut("Ctrl+Shift+Tab")
        previousTabAction.triggered.connect(self.previousTab)
        self.addAction(previousTabAction)

        # This is the Ctrl+W (Close Tab) shortcut.
        removeTabAction = QAction(self)
        removeTabAction.setShortcut("Ctrl+W")
        removeTabAction.triggered.connect(lambda: self.removeTab(self.tabWidget().currentIndex()))
        self.addAction(removeTabAction)

        # Dummy webpage used to provide navigation actions that conform to
        # the system's icon theme.
        self.actionsPage = QWebPage(self)

        # Regularly and forcibly enable and disable navigation actions
        # every few milliseconds.
        self.toggleActionsTimer = QTimer(self)
        self.toggleActionsTimer.timeout.connect(self.toggleActions)

        # Set up navigation actions.
        self.backAction = self.actionsPage.action(QWebPage.Back)
        self.backAction.setShortcut("Alt+Left")
        self.backAction.triggered.connect(self.back)
        self.toolBar.addAction(self.backAction)
        #self.toolBar.widgetForAction(self.backAction).setPopupMode(QToolButton.MenuButtonPopup)

        # This is a dropdown menu for the back history items, but due to
        # instability, it is currently disabled.
        self.backHistoryMenu = QMenu(self)
        self.backHistoryMenu.aboutToShow.connect(self.aboutToShowBackHistoryMenu)
        #self.backAction.setMenu(self.backHistoryMenu)

        self.forwardAction = self.actionsPage.action(QWebPage.Forward)
        self.forwardAction.setShortcut("Alt+Right")
        self.forwardAction.triggered.connect(self.forward)
        self.toolBar.addAction(self.forwardAction)
        #self.toolBar.widgetForAction(self.forwardAction).setPopupMode(QToolButton.MenuButtonPopup)

        # This is a dropdown menu for the forward history items, but due to
        # instability, it is currently disabled.
        self.forwardHistoryMenu = QMenu(self)
        self.forwardHistoryMenu.aboutToShow.connect(self.aboutToShowForwardHistoryMenu)
        #self.forwardAction.setMenu(self.forwardHistoryMenu)

        self.stopAction = self.actionsPage.action(QWebPage.Stop)
        self.stopAction.setShortcut("Esc")
        self.stopAction.triggered.connect(self.stop)
        self.toolBar.addAction(self.stopAction)

        self.reloadAction = self.actionsPage.action(QWebPage.Reload)
        self.reloadAction.setShortcuts(["F5", "Ctrl+R"])
        self.reloadAction.triggered.connect(self.reload)
        self.toolBar.addAction(self.reloadAction)

        # Go home button.
        self.homeAction = QAction(common.complete_icon("go-home"), tr("Go Home"), self)
        self.homeAction.setShortcut("Alt+Home")
        self.homeAction.triggered.connect(self.goHome)
        self.toolBar.addAction(self.homeAction)

        # Start timer to forcibly enable and disable navigation actions.
        self.toggleActionsTimer.start(8)

        # Location bar. Note that this is a combo box.
        # At some point, I should make a custom location bar
        # implementation that looks nicer.
        self.locationBar = QComboBox(self)

        # Load stored browser history.
        for url in data.history:
            self.locationBar.addItem(url)

        # Combo boxes are not normally editable by default.
        self.locationBar.setEditable(True)

        # We want the location bar to stretch to fit the toolbar,
        # so we set its size policy to that of a QLineEdit.
        self.locationBar.setSizePolicy(QLineEdit().sizePolicy())

        # Load a page when Enter is pressed.
        self.locationBar.lineEdit().returnPressed.connect(lambda: self.load(self.locationBar.lineEdit().text()))
        self.locationBar.view().activated.connect(lambda index: self.load(index.data()))

        # This is so that the location bar can shrink to a width
        # shorter than the length of its longest item.
        self.locationBar.setStyleSheet("""QComboBox {
min-width: 6em;
}""")
        self.toolBar.addWidget(self.locationBar)

        # Ctrl+L/Alt+D focuses the location bar.
        locationAction = QAction(self)
        locationAction.setShortcuts(["Ctrl+L", "Alt+D"])
        locationAction.triggered.connect(self.locationBar.setFocus)
        locationAction.triggered.connect(self.locationBar.lineEdit().selectAll)
        self.addAction(locationAction)

        # Extensions toolbar.
        self.extensionBar = QToolBar(self)
        self.extensionBar.setMovable(False)
        self.extensionBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.extensionBar.setStyleSheet("QToolBar { border: 0; border-right: 1px solid palette(dark); background: palette(window); }")
        self.addToolBar(Qt.LeftToolBarArea, self.extensionBar)
        self.extensionBar.hide()

        # Main menu.
        mainMenu = QMenu(self)

        # Add new tab actions to menu.
        mainMenu.addAction(newTabAction)
        mainMenu.addAction(newIncognitoTabAction)

        # Add new window action.
        newWindowAction = QAction(common.complete_icon("window-new"), tr("&New Window"), self)
        newWindowAction.setShortcut("Ctrl+N")
        newWindowAction.triggered.connect(self.addWindow)
        mainMenu.addAction(newWindowAction)

        # Add reopen tab action.
        reopenTabAction = QAction(common.complete_icon("edit-undo"), tr("&Reopen Tab"), self)
        reopenTabAction.setShortcut("Ctrl+Shift+T")
        reopenTabAction.triggered.connect(self.reopenTab)
        self.addAction(reopenTabAction)
        mainMenu.addAction(reopenTabAction)

        # Add reopen window action.
        reopenWindowAction = QAction(common.complete_icon("reopen-window"), tr("R&eopen Window"), self)
        reopenWindowAction.setShortcut("Ctrl+Shift+N")
        reopenWindowAction.triggered.connect(reopenWindow)
        self.addAction(reopenWindowAction)
        mainMenu.addAction(reopenWindowAction)

        mainMenu.addSeparator()

        # Save page action.
        savePageAction = QAction(common.complete_icon("document-save-as"), tr("Save Page &As..."), self)
        savePageAction.setShortcut("Ctrl+S")
        savePageAction.triggered.connect(lambda: self.tabWidget().currentWidget().downloadFile(QNetworkRequest(self.tabWidget().currentWidget().url())))
        mainMenu.addAction(savePageAction)

        mainMenu.addSeparator()

        # Add find text action.
        findAction = QAction(common.complete_icon("edit-find"), tr("&Find..."), self)
        findAction.setShortcut("Ctrl+F")
        findAction.triggered.connect(self.find)
        mainMenu.addAction(findAction)

        # Add find next action.
        findNextAction = QAction(common.complete_icon("media-seek-forward"), tr("Find Ne&xt"), self)
        findNextAction.setShortcut("Ctrl+G")
        findNextAction.triggered.connect(self.findNext)
        mainMenu.addAction(findNextAction)

        # Add find previous action.
        findPreviousAction = QAction(common.complete_icon("media-seek-backward"), tr("Find Pre&vious"), self)
        findPreviousAction.setShortcut("Ctrl+Shift+G")
        findPreviousAction.triggered.connect(self.findPrevious)
        mainMenu.addAction(findPreviousAction)

        mainMenu.addSeparator()

        # Add print preview action.
        printPreviewAction = QAction(common.complete_icon("document-print-preview"), tr("Print Previe&w"), self)
        printPreviewAction.setShortcut("Ctrl+Shift+P")
        printPreviewAction.triggered.connect(self.printPreview)
        mainMenu.addAction(printPreviewAction)

        # Add print page action.
        printAction = QAction(common.complete_icon("document-print"), tr("&Print..."), self)
        printAction.setShortcut("Ctrl+P")
        printAction.triggered.connect(self.printPage)
        mainMenu.addAction(printAction)

        # Add separator.
        mainMenu.addSeparator()

        # Add fullscreen button.
        self.toggleFullScreenButton = QAction(common.complete_icon("view-fullscreen"), tr("Toggle Fullscreen"), self)
        self.toggleFullScreenButton.setCheckable(True)
        self.toggleFullScreenButton.triggered.connect(lambda: self.setFullScreen(not self.isFullScreen()))
        self.toolBar.addAction(self.toggleFullScreenButton)
        self.toggleFullScreenButton.setVisible(False)

        # Add fullscreen action.
        self.toggleFullScreenAction = QAction(common.complete_icon("view-fullscreen"), tr("Toggle Fullscreen"), self)
        self.toggleFullScreenAction.setShortcut("F11")
        self.toggleFullScreenAction.setCheckable(True)
        self.toggleFullScreenAction.triggered.connect(lambda: self.setFullScreen(not self.isFullScreen()))
        self.addAction(self.toggleFullScreenAction)
        mainMenu.addAction(self.toggleFullScreenAction)

        mainMenu.addSeparator()

        # Add clear history action.
        clearHistoryAction = QAction(common.complete_icon("edit-clear"), tr("&Clear Data..."), self)
        clearHistoryAction.setShortcut("Ctrl+Shift+Del")
        clearHistoryAction.triggered.connect(self.clearHistory)
        mainMenu.addAction(clearHistoryAction)

        # Add settings dialog action.
        settingsAction = QAction(common.complete_icon("preferences-system"), tr("&Settings..."), self)
        settingsAction.setShortcuts(["Ctrl+,", "Ctrl+Alt+P"])
        settingsAction.triggered.connect(self.openSettings)
        mainMenu.addAction(settingsAction)

        mainMenu.addSeparator()

        # About Qt action.
        aboutQtAction = QAction(common.complete_icon("qt"), tr("About &Qt"), self)
        aboutQtAction.triggered.connect(QApplication.aboutQt)
        mainMenu.addAction(aboutQtAction)

        # About Nimbus action.
        aboutAction = QAction(common.complete_icon("help-about"), tr("A&bout Nimbus"), self)
        aboutAction.triggered.connect(lambda: QMessageBox.about(self, tr("About Nimbus"), tr("<h3>Nimbus</h3>Python 3/Qt 4-based Web browser.")))
        mainMenu.addAction(aboutAction)

        # Licensing information.
        licenseAction = QAction(tr("Credits && &Licensing"), self)
        licenseAction.triggered.connect(common.licenseDialog.show)
        mainMenu.addAction(licenseAction)

        mainMenu.addSeparator()

        # Quit action.
        quitAction = QAction(common.complete_icon("application-exit"), tr("Quit"), self)
        quitAction.setShortcut("Ctrl+Shift+Q")
        quitAction.triggered.connect(QCoreApplication.quit)
        mainMenu.addAction(quitAction)

        # Add main menu action/button.
        self.mainMenuAction = QAction(common.complete_icon("document-properties"), tr("&Menu"), self)
        self.mainMenuAction.setShortcuts(["Alt+M", "Alt+F"])
        self.mainMenuAction.setMenu(mainMenu)
        self.toolBar.addAction(self.mainMenuAction)
        self.toolBar.widgetForAction(self.mainMenuAction).setPopupMode(QToolButton.InstantPopup)
        self.mainMenuAction.triggered.connect(lambda: self.toolBar.widgetForAction(self.mainMenuAction).showMenu())

        # This is a dummy sidebar used to
        # dock extension sidebars with.
        # You will never actually see this sidebar.
        self.sideBar = QDockWidget(self)
        self.sideBar.setWindowTitle(tr("Sidebar"))
        self.sideBar.setMaximumWidth(320)
        self.sideBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.sideBar.setFeatures(QDockWidget.DockWidgetClosable)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.sideBar)
        self.sideBar.hide()

        # Load browser extensions.
        # Ripped off of Ricotta.
        self.reloadExtensions()

    # Returns the tab widget.
    def tabWidget(self):
        return self.tabs

    # Check if window has a sidebar.
    # Part of the extensions API.
    def hasSideBar(self, name):
        if name in self.sideBars.keys():
            return True
        return False

    # Toggles the sidebar with name name.
    # Part of the extensions API.
    def toggleSideBar(self, name):
        if self.hasSideBar(name):
            self.sideBars[name]["sideBar"].setVisible(not self.sideBars[name]["sideBar"].isVisible())
            if type(self.sideBars[name]["clip"]) is str:
                clip = self.sideBars[name]["clip"]
                if not clip in self.sideBars[name]["sideBar"].webView.url().toString():
                    self.sideBars[name]["sideBar"].webView.load(self.sideBars[name]["url"])

    # Adds a sidebar.
    # Part of the extensions API.
    def addSideBar(self, name="", url="about:blank", clip=None, ua=None):
        self.sideBars[name] = {"sideBar": QDockWidget(self), "url": QUrl(url), "clip": clip}
        self.sideBars[name]["sideBar"].setWindowTitle(name)
        self.sideBars[name]["sideBar"].setMaximumWidth(320)
        self.sideBars[name]["sideBar"].setContextMenuPolicy(Qt.CustomContextMenu)
        self.sideBars[name]["sideBar"].setFeatures(QDockWidget.DockWidgetClosable)
        self.sideBars[name]["sideBar"].webView = WebView()
        self.sideBars[name]["sideBar"].webView.windowCreated.connect(self.addTab)
        self.sideBars[name]["sideBar"].webView.setUserAgent(ua)
        self.sideBars[name]["sideBar"].webView.load(QUrl(url))
        self.sideBars[name]["sideBar"].setWidget(self.sideBars[name]["sideBar"].webView)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.sideBars[name]["sideBar"])
        self.tabifyDockWidget(self.sideBar, self.sideBars[name]["sideBar"])

    # This is so you can grab the window by its toolbar and move it.
    # It's an ugly hack, but it works.
    def mousePressEvent(self, ev):
        if ev.button() != Qt.LeftButton:
            return QMainWindow.mousePressEvent(self, ev)
        else:
            self.mouseX = ev.globalX()
            self.origX = self.x()
            self.mouseY = ev.globalY()
            self.origY = self.y()

    def mouseMoveEvent(self, ev):
        if self.mouseX and self.mouseY and not self.isMaximized():
            self.move(self.origX + ev.globalX() - self.mouseX,
self.origY + ev.globalY() - self.mouseY)

    # Deletes any closed windows above the reopenable window count,
    # and blanks all the tabs and sidebars.
    def closeEvent(self, ev):
        self.blankAll()
        for sidebar in self.sideBars.values():
            sidebar["sideBar"].webView.load(QUrl("about:blank"))
        if len(browser.windows) - 1 > settings.setting_to_int("general/ReopenableWindowCount"):
            for window in browser.windows:
                if not window.isVisible():
                    window.deleteLater()
                    browser.windows.pop(browser.windows.index(window))
                    break

    # Loads about:blank in all tabs when the window is closed.
    # This is a workaround to prevent audio and video from playing after
    # the window is closed.
    def blankAll(self):
        for index in range(0, self.tabWidget().count()):
            self.tabWidget().widget(index).load(QUrl("about:blank"))

    # Unblank all tabs.
    def deblankAll(self):
        for index in range(0, self.tabWidget().count()):
            if self.tabWidget().widget(index).url().toString() in ("about:blank", "", QUrl.fromUserInput(settings.new_tab_page).toString(),):
                self.tabWidget().widget(index).back()

    # Open settings dialog.
    def openSettings(self):
        if settings.setting_to_bool("general/OpenSettingsInTab"):
            self.addTab(url="nimbus://settings")
            self.tabWidget().setCurrentIndex(self.tabWidget().count()-1)
        else:
            settings.settingsDialog.reload()
            settings.settingsDialog.show()

    # Reload extensions.
    def reloadExtensions(self):

        # Hide extensions toolbar if there aren't any extensions.
        if settings.extensions_whitelist == None:
            self.extensionBar.hide()
            return
        elif len(settings.extensions_whitelist) == 0:
            self.extensionBar.hide()
            return

        for extension in settings.extensions:
            if extension not in settings.extensions_whitelist:
                continue
            extension_path = os.path.join(settings.extensions_folder, extension)

            if os.path.isdir(extension_path):
                script_path = os.path.join(extension_path, "script.py")
                if not os.path.isfile(script_path):
                    script_path = os.path.join(extension_path, "script.js")
                icon_path = os.path.join(extension_path, "icon.png")
                shortcut_path = os.path.join(extension_path, "shortcut.txt")
                if os.path.isfile(script_path):
                    f = open(script_path, "r")
                    script = copy.copy(f.read())
                    f.close()
                    shortcut = None
                    if os.path.exists(shortcut_path):
                        f = open(shortcut_path, "r")
                        shortcut = copy.copy(f.read().replace("\n", ""))
                        f.close()
                    newExtension = ExtensionButton(script, shortcut, self)
                    newExtension.setToolTip(extension.replace("_", " ").title() + ("" if not shortcut else "\n" + shortcut))
                    newExtension.clicked.connect(newExtension.loadScript)
                    self.extensionBar.show()
                    self.extensionBar.addWidget(newExtension)
                    if os.path.isfile(icon_path):
                        newExtension.setIcon(QIcon(icon_path))
                    else:
                        newExtension.setIcon(common.complete_icon("applications-other"))

    # Toggle all the navigation buttons.
    def toggleActions(self):
        try:
            self.backAction.setEnabled(self.tabWidget().currentWidget().pageAction(QWebPage.Back).isEnabled())
            self.forwardAction.setEnabled(self.tabWidget().currentWidget().pageAction(QWebPage.Forward).isEnabled())

            # This is a workaround so that hitting Esc will reset the location
            # bar text.
            self.stopAction.setEnabled(True)

            self.reloadAction.setEnabled(True)
        except:
            self.backAction.setEnabled(False)
            self.forwardAction.setEnabled(False)
            self.stopAction.setEnabled(False)
            self.reloadAction.setEnabled(False)

    # Navigation methods.
    def back(self):
        self.tabWidget().currentWidget().back()

    # This is used to refresh the back history items menu,
    # but it is unstable.
    def aboutToShowBackHistoryMenu(self):
        try:
            self.backHistoryMenu.clear()
            history = self.tabWidget().currentWidget().history()
            backItems = history.backItems(10)
            for item in range(0, len(backItems)):
                try:
                    action = custom_widgets.WebHistoryAction(item, backItems[item].icon(), backItems[item].title(), self.backHistoryMenu)
                    action.triggered2.connect(self.loadBackHistoryItem)
                    self.backHistoryMenu.addAction(action)
                except:
                    pass
        except:
            pass

    def loadBackHistoryItem(self, index):
        history = self.tabWidget().currentWidget().history()
        history.goToItem(history.backItems(10)[index])

    def forward(self):
        self.tabWidget().currentWidget().forward()

    def aboutToShowForwardHistoryMenu(self):
        try:
            self.forwardHistoryMenu.clear()
            history = self.tabWidget().currentWidget().history()
            forwardItems = history.forwardItems(10)
            for item in range(0, len(forwardItems)):
                try:
                    action = custom_widgets.WebHistoryAction(item, forwardItems[item].icon(), forwardItems[item].title(), self.forwardHistoryMenu)
                    action.triggered2.connect(self.loadForwardHistoryItem)
                    self.forwardHistoryMenu.addAction(action)
                except:
                    pass
        except:
            pass

    def loadForwardHistoryItem(self, index):
        history = self.tabWidget().currentWidget().history()
        history.goToItem(history.forwardItems(10)[index])

    def reload(self):
        self.tabWidget().currentWidget().reload()

    def stop(self):
        self.tabWidget().currentWidget().stop()
        self.locationBar.setEditText(self.tabWidget().currentWidget().url().toString())

    def goHome(self):
        self.tabWidget().currentWidget().load(QUrl.fromUserInput(settings.settings.value("general/Homepage")))

    # Find text/Text search methods.
    def find(self):
        self.tabWidget().currentWidget().find()

    def findNext(self):
        self.tabWidget().currentWidget().findNext()

    def findPrevious(self):
        self.tabWidget().currentWidget().findPrevious()

    # Page printing methods.
    def printPage(self):
        self.tabWidget().currentWidget().printPage()

    def printPreview(self):
        self.tabWidget().currentWidget().printPreview()

    # Clears the history after a prompt.
    def clearHistory(self):
        chistorydialog.display()

    # Method to load a URL.
    def load(self, url=False):
        if not url:
            url = self.locationBar.currentText()
        if "." in url or ":" in url or os.path.exists(url):
            self.tabWidget().currentWidget().load(QUrl.fromUserInput(url))
        else:
            self.tabWidget().currentWidget().load(QUrl(settings.settings.value("general/Search") % (url,)))

    # Status bar related methods.
    def setStatusBarMessage(self, message):
        try: self.statusBar.setStatusBarMessage(self.tabWidget().currentWidget()._statusBarMessage)
        except: self.statusBar.setStatusBarMessage("")

    def setProgress(self, progress):
        try: self.statusBar.setValue(self.tabWidget().currentWidget()._loadProgress)
        except: self.statusBar.setValue(0)

    # Fullscreen mode.
    def setFullScreen(self, fullscreen=False):
        if fullscreen:
            try: self.toggleFullScreenButton.setChecked(True)
            except: pass
            try: self.toggleFullScreenAction.setChecked(True)
            except: pass
            self.toggleFullScreenButton.setVisible(True)
            self.showFullScreen()
        else:
            try: self.toggleFullScreenButton.setChecked(False)
            except: pass
            try: self.toggleFullScreenAction.setChecked(False)
            except: pass
            self.toggleFullScreenButton.setVisible(False)
            self.showNormal()

    # Tab-related methods.
    def currentWidget(self):
        return self.tabWidget().currentWidget()

    def addWindow(self, url=None):
        addWindow(url)

    def addTab(self, webView=None, index=None, focus=True, **kwargs):
        # If a URL is specified, load it.
        if "incognito" in kwargs:
            webview = WebView(incognito=True, parent=self)
            if "url" in kwargs:
                webview.load(QUrl.fromUserInput(kwargs["url"]))

        elif "url" in kwargs:
            url = kwargs["url"]
            webview = WebView(incognito=not settings.setting_to_bool("data/RememberHistory"), parent=self)
            webview.load(QUrl.fromUserInput(url))

        # If a WebView object is specified, use it.
        elif webView != None:
            webview = webView

        # If nothing is specified, use a blank WebView.
        else:
            webview = WebView(incognito=not settings.setting_to_bool("data/RememberHistory"), parent=self)

        # Connect signals
        webview.loadProgress.connect(self.setProgress)
        webview.statusBarMessage.connect(self.setStatusBarMessage)
        webview.page().linkHovered.connect(self.setStatusBarMessage)
        webview.titleChanged.connect(self.updateTabTitles)
        webview.page().fullScreenRequested.connect(self.setFullScreen)
        webview.urlChanged.connect(self.updateLocationText)
        webview.iconChanged.connect(self.updateTabIcons)
        webview.windowCreated.connect(lambda webView: self.addTab(webView=webView, index=self.tabWidget().currentIndex()+1, focus=False))
        webview.downloadStarted.connect(self.addDownloadToolBar)

        # Add tab
        if type(index) is not int:
            self.tabWidget().addTab(webview, tr("New Tab"))
        else:
            self.tabWidget().insertTab(index, webview, tr("New Tab"))

        # Switch to new tab
        if focus:
            self.tabWidget().setCurrentIndex(self.tabWidget().count()-1)

        # Update icons so we see the globe icon on new tabs.
        self.updateTabIcons()

    # Goes to the next tab.
    # Loops around if there is none.
    def nextTab(self):
        if self.tabWidget().currentIndex() == self.tabWidget().count() - 1:
            self.tabWidget().setCurrentIndex(0)
        else:
            self.tabWidget().setCurrentIndex(self.tabWidget().currentIndex() + 1)

    # Goes to the previous tab.
    # Loops around if there is none.
    def previousTab(self):
        if self.tabWidget().currentIndex() == 0:
            self.tabWidget().setCurrentIndex(self.tabWidget().count() - 1)
        else:
            self.tabWidget().setCurrentIndex(self.tabWidget().currentIndex() - 1)

    # Update the titles on every single tab.
    def updateTabTitles(self):
        for index in range(0, self.tabWidget().count()):
            title = self.tabWidget().widget(index).windowTitle()
            self.tabWidget().setTabText(index, title[:24] + '...' if len(title) > 24 else title)
            if index == self.tabWidget().currentIndex():
                self.setWindowTitle(title + " - " + tr("Nimbus"))

    # Update the icons on every single tab.
    def updateTabIcons(self):
        for index in range(0, self.tabWidget().count()):
            try: icon = self.tabWidget().widget(index).icon()
            except: continue
            self.tabWidget().setTabIcon(index, icon)

    # Removes a tab at index.
    def removeTab(self, index):
        try:
            webView = self.tabWidget().widget(index)
            if webView.history().canGoBack() or webView.history().canGoForward() or webView.url().toString() not in ("about:blank", "", QUrl.fromUserInput(settings.new_tab_page).toString(),):
                self.closedTabs.append(webView)
                while len(self.closedTabs) > settings.setting_to_int("general/ReopenableTabCount"):
                    self.closedTabs[0].deleteLater()
                    try: common.webviews.remove(webView)
                    except: pass
                    self.closedTabs.pop(0)
                webView.load(QUrl("about:blank"))
            else:
                webView.deleteLater()
                try: common.webviews.remove(webView)
                except: pass
        except:
            traceback.print_exc()
        self.tabWidget().removeTab(index)
        if self.tabWidget().count() == 0:
            if settings.setting_to_bool("general/CloseWindowWithLastTab"):
                self.close()
            else:
                self.addTab(url="about:blank")

    # Reopens the last closed tab.
    def reopenTab(self):
        if len(self.closedTabs) > 0:
            webview = self.closedTabs.pop()
            self.addTab(webview)
            try:
                if webview.url().toString() in ("about:blank", "", QUrl.fromUserInput(settings.new_tab_page).toString(),):
                    webview.back()
            except: pass

    # This method is used to add a DownloadBar to the window.
    def addDownloadToolBar(self, toolbar):
        self.statusBar.addToolBar(toolbar)

    # Method to update the location bar text.
    def updateLocationText(self, url=None):
        try:
            if type(url) != QUrl:
                url = self.tabWidget().currentWidget().url()
            currentUrl = self.tabWidget().currentWidget().url()
            if url == currentUrl:
                self.locationBar.setEditText(currentUrl.toString())
        except:
            pass

# Redundancy is redundant.
def addWindow(url=None):
    win = MainWindow()
    if not url or url == None:
        win.addTab(url=settings.settings.value("general/Homepage"))
    else:
        win.addTab(url=url)
    win.show()

# Reopen window method.
def reopenWindow():
    for window in browser.windows[::-1]:
        if not window.isVisible():
            browser.windows.append(browser.windows.pop(browser.windows.index(window)))
            window.deblankAll()
            for sidebar in window.sideBars.values():
                sidebar["sideBar"].webView.back()
            if window.tabWidget().count() == 0:
                window.reopenTab()
            window.show()
            return

# Preparations to quit.
def prepareQuit():
    data.saveData()
    filtering.adblock_filter_loader.quit()
    filtering.adblock_filter_loader.wait()
    server_thread.httpd.shutdown()
    server_thread.quit()
    server_thread.wait()

# System tray icon.
class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, parent):
        super(SystemTrayIcon, self).__init__(common.app_icon, parent)

        # Set tooltip.
        self.setToolTip(tr("Nimbus"))

        # Set context menu.
        self.menu = QMenu(None)
        self.setContextMenu(self.menu)

        # New window action
        newWindowAction = QAction(common.complete_icon("window-new"), tr("&New Window"), self)
        newWindowAction.triggered.connect(addWindow)
        self.menu.addAction(newWindowAction)

        # Reopen window action
        reopenWindowAction = QAction(common.complete_icon("reopen-window"), tr("R&eopen Window"), self)
        reopenWindowAction.triggered.connect(reopenWindow)
        self.menu.addAction(reopenWindowAction)

        # Quit action
        quitAction = QAction(common.complete_icon("application-exit"), tr("Quit"), self)
        quitAction.triggered.connect(QCoreApplication.quit)
        self.menu.addAction(quitAction)

# DBus server.
if has_dbus:
    class DBusServer(dbus.service.Object):
        def __init__(self, bus=None):
            busName = dbus.service.BusName("org.nimbus.Nimbus", bus=bus)
            dbus.service.Object.__init__(self, busName, "/Nimbus")

        @dbus.service.method("org.nimbus.Nimbus", in_signature="s", out_signature="s")
        def addWindow(self, url=None):
            addWindow(url)
            return url

        @dbus.service.method("org.nimbus.Nimbus", in_signature="s", out_signature="s")
        def addTab(self, url="about:blank"):
            for window in browser.windows[::-1]:
                if window.isVisible():
                    window.addTab(url=url)
                    browser.windows[-1].activateWindow()
                    return url
            self.addWindow(url)
            browser.windows[-1].activateWindow()
            return url

# Main function to load everything.
def main():
    # Start DBus loop
    if has_dbus:
        mainloop = DBusQtMainLoop(set_as_default = True)
        dbus.set_default_main_loop(mainloop)

    # Create app.
    app = QApplication(sys.argv)
    app.installTranslator(translate.translator)

    # We want Nimbus to stay open when the last window is closed,
    # so we set this.
    app.setQuitOnLastWindowClosed(False)

    # If D-Bus is present...
    if has_dbus:
        bus = dbus.SessionBus()

    try: proxy = bus.get_object("org.nimbus.Nimbus", "/Nimbus")
    except: dbus_present = False
    else: dbus_present = True

    # If Nimbus detects the existence of another Nimbus process, it will
    # send all the requested URLs to the existing process and exit.
    if dbus_present:
        for arg in sys.argv[1:]:
            if "." in arg or ":" in arg:
                proxy.addTab(arg)
        return

    # Hack together the browser's icon. This needs to be improved.
    common.app_icon = common.complete_icon("nimbus")
    common.app_icon.addFile(common.icon("nimbus-16.png"))
    common.app_icon.addFile(common.icon("nimbus-22.png"))
    common.app_icon.addFile(common.icon("nimbus-24.png"))
    common.app_icon.addFile(common.icon("nimbus-32.png"))
    common.app_icon.addFile(common.icon("nimbus-48.png"))
    common.app_icon.addFile(common.icon("nimbus-64.png"))
    common.app_icon.addFile(common.icon("nimbus-72.png"))
    common.app_icon.addFile(common.icon("nimbus-80.png"))
    common.app_icon.addFile(common.icon("nimbus-128.png"))
    common.app_icon.addFile(common.icon("nimbus-256.png"))

    # Build the browser's default user agent.
    # This should be improved as well.
    webPage = QWebPage()
    nimbus_ua_sub = "Qt/" + common.qt_version + " Nimbus/" + common.app_version + " QupZilla/1.4.3"
    if common.qt_version.startswith("4"):
        common.defaultUserAgent = webPage.userAgentForUrl(QUrl.fromUserInput("google.com")).replace("Qt/" + common.qt_version, nimbus_ua_sub)
    else:
        common.defaultUserAgent = webPage.userAgentForUrl(QUrl.fromUserInput("google.com")).replace("Qt/" + common.qt_version, nimbus_ua_sub).replace("python", nimbus_ua_sub)
    webPage.deleteLater()
    del webPage
    del nimbus_ua_sub

    # Create tray icon.
    common.trayIcon = SystemTrayIcon(QCoreApplication.instance())
    common.trayIcon.show()

    # Creates a licensing information dialog.
    common.licenseDialog = custom_widgets.LicenseDialog()

    # Create instance of clear history dialog.
    global chistorydialog
    chistorydialog = clear_history_dialog.ClearHistoryDialog()

    # Set up settings dialog.
    settings.settingsDialog = WebView(incognito=True, parent=None)
    settings.settingsDialog.resize(560, 480)
    settings.settingsDialog.setWindowIcon(common.app_icon)
    settings.settingsDialog.setWindowFlags(Qt.Dialog)
    settings.settingsDialog.load(QUrl("nimbus://settings"))
    closeSettingsDialogAction = QAction(settings.settingsDialog)
    closeSettingsDialogAction.setShortcuts(["Esc", "Ctrl+W"])
    closeSettingsDialogAction.triggered.connect(settings.settingsDialog.hide)
    settings.settingsDialog.addAction(closeSettingsDialogAction)

    # Create DBus server
    if has_dbus:
        server = DBusServer(bus)

    # Load adblock rules.
    filtering.adblock_filter_loader.start()

    if not os.path.exists(settings.extensions_folder):
        shutil.copytree(common.extensions_folder, settings.extensions_folder)

    settings.reload_extensions()
    settings.reload_userscripts()

    server_thread.setDirectory(settings.extensions_folder)

    # Start extension server.
    server_thread.start()

    # On quit, save settings.
    app.aboutToQuit.connect(prepareQuit)

    # Load settings.
    data.loadData()

    if not "--daemon" in sys.argv:
        # Create instance of MainWindow.
        win = MainWindow()

        # Open URLs from command line.
        if len(sys.argv) > 1:
            for arg in sys.argv[1:]:
                if "." in arg or ":" in arg:
                    win.addTab(url=arg)

        if win.tabWidget().count() < 1:
            win.addTab(url=settings.settings.value("general/Homepage"))

        # Show window.
        win.show()

    # Start app.
    app.exec_()

# Start program
if __name__ == "__main__":
    try:
        main()
    except:
        traceback.print_exc()
