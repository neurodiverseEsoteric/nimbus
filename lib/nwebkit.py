#! /usr/bin/env python3

# ----------
# nwebkit.py
# ----------
# Author:      Daniel Sim (foxhead128)
# License:     See LICENSE.md for more details.
# Description: This module mainly contains stuff related to QtWebKit.

# Import everything we need.
import sys
import os
import re
import subprocess
import browser
import urllib.parse
import hashlib
import common
import geolocation
import custom_widgets
import filtering
import translate
from translate import tr
import settings
import data
import network
import rss_parser
import view_source_dialog
if not sys.platform.startswith("linux"):
    import webbrowser

# Extremely specific imports from PyQt5/PySide.
# We give PyQt5 priority because it supports Qt5.
if not common.pyqt4:
    from PyQt5.QtCore import Qt, QSize, QObject, QCoreApplication, pyqtSignal, pyqtSlot, QUrl, QFile, QIODevice, QTimer, QByteArray, QDataStream, QDateTime, QPoint
    from PyQt5.QtGui import QIcon, QImage, QClipboard, QCursor
    from PyQt5.QtWidgets import QApplication, QListWidget, QSpinBox, QListWidgetItem, QMessageBox, QAction, QToolBar, QLineEdit, QInputDialog, QFileDialog, QProgressBar, QLabel, QCalendarWidget, QSlider, QFontComboBox, QLCDNumber, QDateTimeEdit, QDial, QSystemTrayIcon, QPushButton, QMenu, QDesktopWidget, QWidgetAction, QToolTip
    from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
    from PyQt5.QtNetwork import QNetworkProxy, QNetworkRequest
    from PyQt5.QtWebKit import QWebHistory
    from PyQt5.QtWebKitWidgets import QWebView, QWebPage
    Signal = pyqtSignal
    Slot = pyqtSlot
else:
    try:
        from PyQt4.QtCore import Qt, QSize, QObject, QCoreApplication, pyqtSignal, pyqtSlot, QUrl, QFile, QIODevice, QTimer, QByteArray, QDataStream, QDateTime, QPoint
        from PyQt4.QtGui import QApplication, QListWidget, QSpinBox, QListWidgetItem, QMessageBox, QIcon, QAction, QToolBar, QLineEdit, QPrinter, QPrintDialog, QPrintPreviewDialog, QInputDialog, QFileDialog, QProgressBar, QLabel, QCalendarWidget, QSlider, QFontComboBox, QLCDNumber, QImage, QDateTimeEdit, QDial, QSystemTrayIcon, QPushButton, QMenu, QDesktopWidget, QClipboard, QWidgetAction, QToolTip, QCursor
        from PyQt4.QtNetwork import QNetworkProxy, QNetworkRequest
        from PyQt4.QtWebKit import QWebView, QWebPage, QWebHistory
        Signal = pyqtSignal
        Slot = pyqtSlot
    except:
        from PySide.QtCore import Qt, QSize, QObject, QCoreApplication, Signal, Slot, QUrl, QFile, QIODevice, QTimer, QByteArray, QDataStream, QDateTime, QPoint
        from PySide.QtGui import QApplication, QListWidget, QSpinBox, QListWidgetItem, QMessageBox, QIcon, QAction, QToolBar, QLineEdit, QPrinter, QPrintDialog, QPrintPreviewDialog, QInputDialog, QFileDialog, QProgressBar, QLabel, QCalendarWidget, QSlider, QFontComboBox, QLCDNumber, QImage, QDateTimeEdit, QDial, QSystemTrayIcon, QPushButton, QMenu, QDesktopWidget, QClipboard, QWidgetAction, QToolTip, QCursor
        from PySide.QtNetwork import QNetworkProxy, QNetworkRequest
        from PySide.QtWebKit import QWebView, QWebPage, QWebHistory

# Add an item to the browser history.
def addHistoryItem(url, title=None):
    if settings.setting_to_bool("data/RememberHistory"):
        url = url.split("#")[0]
        if len(url) <= settings.setting_to_int("data/MaximumURLLength"):
            data.history[url] = {"title": title, "last_visited" : QDateTime.currentDateTime().toMSecsSinceEpoch()}

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
        self.setIconSize(QSize(16, 16))
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setStyleSheet(common.blank_toolbar)
        label = QLabel(self)
        self.addWidget(label)
        self.progressBar = DownloadProgressBar(reply, destination, self)
        #self.progressBar.networkReply.finished.connect(self.close)
        #self.progressBar.networkReply.finished.connect(self.deleteLater)
        self.addWidget(self.progressBar)
        label.setText(os.path.split(self.progressBar.destination)[1])
        openFolderAction = QAction(common.complete_icon("document-open"), tr("Open containing folder"), self)
        openFolderAction.triggered.connect(lambda: os.system("xdg-open %s &" % (os.path.split(self.progressBar.destination)[0].split("://")[-1],)))
        self.addAction(openFolderAction)
        abortAction = QAction(QIcon().fromTheme("process-stop", QIcon(common.icon("process-stop.png"))), tr("Abort/Remove"), self)
        abortAction.triggered.connect(self.progressBar.abort)
        abortAction.triggered.connect(self.deleteLater)
        self.addAction(abortAction)

"""class JavaScriptBar(QToolBar):
    def __init__(self, frame=None, msg=None, parent=None):
        super(JavaScriptAlertBar, self).__init__(parent)
        self.setStyleSheet("QToolBar{background-color: #FFBF00;border:0;border-bottom:1px solid #FF7F00;}QToolBar,QLabel{color:#1A1A1A;}")
        self.setMovable(False)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
        e1 = custom_widgets.HorizontalExpander(self)
        self.addWidget(e1)
        
        self.toolBar = QToolBar(self)
        self.toolBar.setStyleSheet("QToolBar{background-color:transparent;border:0;padding:0;margin:0;}")
        self.addWidget(self.toolBar)
        
        e2 = custom_widgets.HorizontalExpander(self)
        self.addWidget(e2)

        self.button = QPushButton(self)
        self.button.setText(tr("OK"))
        self.button.clicked.connect(self.deleteLater)
        self.addWidget(self.button)

class JavaScriptAlertBar(JavaScriptBar):
    def __init__(self, *args, **kwargs):
        super(JavaScriptAlertBar, self).__init__(*args, **kwargs)"""

# Class for exposing fullscreen API to DOM.
class FullScreenRequester(QObject):
    fullScreenRequested = Signal(bool)
    @Slot(bool)
    def setFullScreen(self, fullscreen=False):
        self.fullScreenRequested.emit(fullscreen)

isOnlineTimer = QTimer()

def setNavigatorOnline():
    script = "window.navigator.onLine = " + str(network.isConnectedToNetwork()).lower() + ";"
    for window in browser.windows:
        for tab in range(window.tabWidget().count()):
            try:
                window.tabWidget().widget(tab).page().mainFrame().evaluateJavaScript(script)
                window.tabWidget().widget(tab).page().mainFrame().evaluateJavaScript("if (window.onLine) {\n" + \
                                            "   document.dispatchEvent(window.nimbus.onLineEvent);\n" + \
                                            "}")
                window.tabWidget().widget(tab).page().mainFrame().evaluateJavaScript("if (!window.onLine) {\n" + \
                                            "   document.dispatchEvent(window.nimbus.offLineEvent);\n" + \
                                            "}")
            except:
                pass

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

    fullScreenRequested = Signal(bool)
    def __init__(self, *args, **kwargs):
        super(WebPage, self).__init__(*args, **kwargs)

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
        self.loadFinished.connect(self.doRedirectHack)
        self.loadFinished.connect(self.checkForNavigatorGeolocation)
        self.loadFinished.connect(self.loadUserScripts)

        # Custom userscript.
        self.userScript = ""

        # This stores the user agent.
        self._userAgent = ""
        self._fullScreen = False

        # Start self.isOnlineTimer.
        if not isOnlineTimer.isActive():
            isOnlineTimer.timeout.connect(setNavigatorOnline)
            isOnlineTimer.start(5000)

        # Set user agent to default value.
        self.setUserAgent()

    def setUserScript(self, script):
        if script:
            self.userScript = script

    # Performs a hack on Google pages to change their URLs.
    def doRedirectHack(self):
        links = self.mainFrame().findAllElements("a")
        for link in links:
            try: href = link.attribute("href")
            except: pass
            else:
                for gurl in ("/url?q=", "?redirect="):
                    if href.startswith(gurl):
                        url = href.replace(gurl, "").split("&")[0]
                        url = urllib.parse.unquote(url)
                        link.setAttribute("href", url)
                    elif gurl in href:
                        url = href.split(gurl)[-1]
                        url = urllib.parse.unquote(url)
                        link.setAttribute("href", url)
                    elif "#post" in href:
                        try: class_ = link.attribute("class")
                        except: class_ = ""
                        if not "postcounter" in class_:
                            url = "-".join(href.split("-")[:-1])
                            postnumber = href.split("#")[-1]
                            url = url + "-" + postnumber + ".html"
                            link.setAttribute("href", url)

    # Loads history.
    def loadHistory(self, history):
        out = QDataStream(history, QIODevice.ReadOnly)
        out.__rshift__(self.history())

    def saveHistory(self):
        byteArray = QByteArray()
        out = QDataStream(byteArray, QIODevice.WriteOnly)
        out.__lshift__(self.history())
        return byteArray

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
            if settings.setting_to_bool("content/HostFilterEnabled") or settings.setting_to_bool("content/AdblockEnabled"):
                self.mainFrame().evaluateJavaScript("""var __NimbusAdRemoverQueries = %s;
for (var i=0; i<__NimbusAdRemoverQueries.length; i++) {
    var cl = document.querySelectorAll(__NimbusAdRemoverQueries[i]);
    for (var j=0; j<cl.length; j++) {
        cl[j].style.display = "none";
    }
}
delete __NimbusAdRemoverQueries;""" % (settings.adremover_filters,))
            self.mainFrame().evaluateJavaScript(self.userScript)
            for userscript in settings.userscripts:
                for match in userscript["match"]:
                    try:
                        if match == "*":
                            r = True
                        else:
                            r = re.match(match, self.mainFrame().url().toString())
                        if r:
                            self.mainFrame().evaluateJavaScript(userscript["content"])
                            break
                    except:
                        pass

    # Returns user agent string.
    def userAgentForUrl(self, url):
        if ("app.box" in url.authority() or "ppirc" in url.authority() or "google" in url.authority() or "blackboard" in url.authority()) and not "android" in self._userAgent.lower():
            return QWebPage.userAgentForUrl(self, url) + " Chrome/22." + common.qt_version + " Nimbus/" + common.app_version
        elif not "github" in url.authority():
            return self._userAgent
        # This is a workaround for GitHub not loading properly
        # with the default Nimbus user agent.
        else:
            return QWebPage.userAgentForUrl(self, url)

    # Convenience function.
    def setUserAgent(self, ua=None):
        try:
            if type(ua) is str:
                self._userAgent = ua
            else:
                self._userAgent = common.defaultUserAgent
        except:
            pass

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
        if feature == self.Notifications and frame == self.mainFrame():
            self.setFeaturePermission(frame, feature, self.PermissionGrantedByUser)
        elif feature == self.Geolocation and frame == self.mainFrame() and settings.setting_to_bool("network/GeolocationEnabled") and not authority in data.geolocation_blacklist:
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

    # This stores the directory you last saved a file in.
    saveDirectory = os.path.expanduser("~")

    # This is used to store references to webViews so that they don't
    # automatically get cleaned up.
    webViews = []

    # Downloads
    downloads = []

    sourceDialogs = []

    # This is a signal used to inform everyone a new window was created.
    windowCreated = Signal(QWebView)
    
    # Requests tab
    tabRequested = Signal(QWebView)

    # This is a signal used to tell everyone a download has started.
    downloadStarted = Signal(QToolBar)
    urlChanged2 = Signal(QUrl)

    nextExpressions = ("start=", "offset=", "page=", "first=", "pn=", "=",)

    # Initialize class.
    def __init__(self, *args, incognito=False, sizeHint=None, minimumSizeHint=None, forceBlankPage=False, **kwargs):
        super(WebView, self).__init__(*args, **kwargs)

        self._sizeHint = sizeHint
        self._minimumSizeHint = minimumSizeHint

        # Add this webview to the list of webviews.
        common.webviews.append(self)

        # These are used to store the current url.
        self._url = ""
        self._urlText = ""
        self._oldURL = ""

        #self.disconnected = False

        self.isLoading = False

        self._html = ""

        self._changeCanGoNext = False

        self._cacheLoaded = False

        # Private browsing.
        self.incognito = incognito

        # Stores the mime type of the current page.
        self._contentType = None
        self._contentTypes = {}

        # This is used to store the text entered in using WebView.find(),
        # so that WebView.findNext() and WebView.findPrevious() work.
        self._findText = False

        # This is used to store the current status message.
        self._statusBarMessage = ""
        self.statusMessageDisplay = QLabel(self)
        self.statusMessageDisplay.setStyleSheet("QLabel { border-radius: 4px; padding: 2px; background: palette(highlight); color: palette(highlighted-text); }")
        self.statusMessageDisplay.hide()

        # This is used to store the current page loading progress.
        self._loadProgress = 0

        # Stores if window was maximized.
        self._wasMaximized = False

        # Stores next page.
        self._canGoNext = False

        # This stores the link last hovered over.
        self._hoveredLink = ""

        # Stores history to be loaded.
        self._historyToBeLoaded = None

        # Temporary title.
        self._tempTitle = None

        self.setPage(WebPage(self))

        # Create a NetworkAccessmanager that supports ad-blocking and set it.
        if not self.incognito:
            self.nAM = network.network_access_manager
        else:
            self.nAM = network.incognito_network_access_manager
        self.page().setNetworkAccessManager(self.nAM)
        self.nAM.setParent(QCoreApplication.instance())

        self.updateProxy()
        self.updateNetworkSettings()
        self.updateContentSettings()

        # What to do if private browsing is not enabled.
        if not self.incognito:
            # Set persistent storage path to settings_folder.
            self.settings().enablePersistentStorage(settings.settings_folder)

            # Do this so that cookie_jar doesn't get deleted along with WebView.
            network.cookie_jar.setParent(QCoreApplication.instance())

        # What to do if private browsing is enabled.
        else:
            # Global incognito cookie jar, so that logins are preserved
            # between incognito tabs.
            network.incognito_cookie_jar.setParent(QCoreApplication.instance())

            # Enable private browsing for QWebSettings.
            self.settings().setAttribute(self.settings().PrivateBrowsingEnabled, True)

        # Handle unsupported content.
        self.page().setForwardUnsupportedContent(True)
        self.page().unsupportedContent.connect(self.handleUnsupportedContent)

        # This is what Nimbus should do when faced with a file to download.
        self.page().downloadRequested.connect(self.downloadFile)

        # Connect signals.
        self.page().linkHovered.connect(self.setStatusBarMessage)

        # PyQt5 doesn't support <audio> and <video> tags on Windows.
        # This is a little hack to work around it.
        self.page().networkAccessManager().finished.connect(self.ready)
        #self.loadFinished.connect(lambda: print("\n".join(self.rssFeeds()) + "\n"))

        # Check if content viewer.
        self._isUsingContentViewer = False

        self.setWindowTitle("")

        self.clippingsMenu = QMenu(self)

        self.init()

        if os.path.exists(settings.new_tab_page) and not forceBlankPage:
            self.load(QUrl("about:blank"))

    def wheelEvent(self, *args, **kwargs):
        super(WebView, self).wheelEvent(*args, **kwargs)
        self.statusMessageDisplay.hide()

    def disconnect(self, *args, **kwargs):
        super(WebView, self).disconnect(*args, **kwargs)
        self.init()
        #self.disconnected = True
        common.disconnected.append(self)

    def init(self):
        self.urlChanged.connect(self.setUrlText)
        if not self.incognito:
            self.urlChanged.connect(self.addHistoryItem)
            self.urlChanged.connect(lambda: self.setChangeCanGoNext(True))
        self.titleChanged.connect(self.setWindowTitle2)
        self.titleChanged.connect(self.updateHistoryTitle)
        self.titleChanged.connect(self.setWindowTitle2)
        self.titleChanged.connect(self.updateHistoryTitle)
        self.statusBarMessage.connect(self.setStatusBarMessage)
        self.loadProgress.connect(self.setLoadProgress)
        self.loadStarted.connect(self.setLoading)
        self.loadFinished.connect(self.unsetLoading)
        self.loadStarted.connect(self.resetContentType)
        self.loadFinished.connect(self.replaceAVTags)
        self.loadFinished.connect(self.setCanGoNext)
        self.loadFinished.connect(self.savePageToCache)
        self.loadStarted.connect(self.checkIfUsingContentViewer)
        self.loadFinished.connect(self.finishLoad)

    def requestTab(self):
        self.tabRequested.emit(self)

    def minimumSizeHint(self):
        if not type(self._minimumSizeHint) is QSize:
            return super(WebView, self).minimumSizeHint()
        return self._minimumSizeHint

    def sizeHint(self):
        if not type(self._sizeHint) is QSize:
            return super(WebView, self).sizeHint()
        return self._sizeHint

    def updateHistoryTitle(self, title):
        url = self.url().toString().split("#")[0]
        if url in data.history.keys():
            data.history[url]["title"] = (title if len(title) > 0 else tr("(Untitled)"))

    def setUrlText(self, text, emit=True):
        if type(text) is QUrl:
            text = text.toString()
        self._urlText = str(text)
        if emit:
            self.urlChanged2.emit(QUrl(self._urlText))

    def setLoading(self):
        self.isLoading = True
        self.iconChanged.emit()

    def unsetLoading(self):
        self.isLoading = False
        self.iconChanged.emit()

    def setWindowTitle2(self, text):
        if text == "" and self.url().toString() not in ("", "about:blank"):
            pass
        else:
            self.setWindowTitle(text)

    def contextMenuEvent(self, ev):
        if QCoreApplication.instance().keyboardModifiers() in (Qt.ControlModifier, Qt.ShiftModifier, Qt.AltModifier) and len(data.clippings) > 0:
            menu = self.clippingsMenu
            menu.clear()
            openInDefaultBrowserAction = QAction(tr("Open in Default Browser"), menu)
            openInDefaultBrowserAction.triggered.connect(self.openInDefaultBrowser)
            menu.addAction(openInDefaultBrowserAction)
            if self._statusBarMessage == "":
                openInDefaultBrowserAction.setEnabled(False)
            menu.addSeparator()
            for clipping in data.clippings:
                a = custom_widgets.LinkAction(data.clippings[clipping], clipping, menu)
                a.triggered2.connect(QApplication.clipboard().setText)
                a.triggered2.connect(lambda: self.page().action(QWebPage.Paste).trigger())
                menu.addAction(a)
            menu.show()
            y = QDesktopWidget()
            menu.move(min(ev.globalX(), y.width()-menu.width()), min(ev.globalY(), y.height()-menu.height()))
            y.deleteLater()
        else:
            super(WebView, self).contextMenuEvent(ev)

    def shortWindowTitle(self):
        title = self.windowTitle()
        return title[:24] + '...' if len(title) > 24 else title

    def viewSource(self):
        sourceDialog = view_source_dialog.ViewSourceDialog(None)
        for sd in self.sourceDialogs:
            try: sd.doNothing()
            except: self.sourceDialogs.remove(sd)
        self.sourceDialogs.append(sourceDialog)
        sourceDialog.setPlainText(self.page().mainFrame().toHtml())
        sourceDialog.show()

    # Enables fullscreen in web app mode.
    def enableWebAppMode(self):
        self.isWebApp = True
        fullScreenAction = QAction(self)
        fullScreenAction.setShortcut("F11")
        fullScreenAction.triggered.connect(self.toggleFullScreen)
        self.addAction(fullScreenAction)

    # Sends a request to become fullscreen.
    def toggleFullScreen(self):
        if not self.isFullScreen():
            self._wasMaximized = self.isMaximized()
            self.showFullScreen()
        else:
            if not self._wasMaximized:
                self.showNormal()
            else:
                self.showNormal()
                self.showMaximized()

    def saveHtml(self):
        self._html = self.page().mainFrame().toHtml()

    def restoreHtml(self):
        self.setHtml(self._html)

    def deleteLater(self):
        try: common.webviews.remove(self)
        except: pass
        try: self.page().networkAccessManager().finished.disconnect(self.ready)
        except: pass
        QWebView.deleteLater(self)

    def paintEvent(self, ev):
        if self._historyToBeLoaded:
            self.page().loadHistory(self._historyToBeLoaded)
            self._historyToBeLoaded = None
        QWebView.paintEvent(self, ev)

    def loadHistory(self, history, title=None):
        self._historyToBeLoaded = history
        out = QDataStream(history, QIODevice.ReadOnly)
        if title:
            self._tempTitle = title
        else:
            page = QWebPage(None)
            history = page.history()
            out.__rshift__(history)
            self._tempTitle = history.currentItem().title()
        self.titleChanged.emit(str(self._tempTitle))
        try: page.deleteLater()
        except: pass

    def title(self):
        if not self._tempTitle:
            return QWebView.title(self)
        else:
            return self._tempTitle

    def saveHistory(self):
        if self._historyToBeLoaded:
            return self._historyToBeLoaded
        return self.page().saveHistory()

    def setChangeCanGoNext(self, true=False):
        self._changeCanGoNext = true

    def canGoUp(self):
        components = self.url().toString().split("/")
        urlString = self.url().toString()
        if len(components) < 2 or (urlString.count("/") < 4 and not "///" in urlString and urlString.startswith("file://")) or (len(components) < 5 and not urlString.startswith("file://") and components[-1] == ""):
            return False
        return True

    def up(self):
        components = self.url().toString().split("/")
        urlString = self.url().toString()
        if urlString.count("/") < 4 and "///" in urlString:
            self.load(QUrl("file:///"))
            return
        self.load(QUrl.fromUserInput("/".join(components[:(-1 if components[-1] != "" else -2)])))

    def rssFeeds(self):
        feed_urls = []
        links = self.page().mainFrame().findAllElements("[type=\"application/rss+xml\"], [type=\"application/atom+xml\"]")
        for element in links:
            if element.hasAttribute("title") and element.hasAttribute("href"):
                feed_urls.append((element.attribute("title"), element.attribute("href")))
            elif element.hasAttribute("href"):
                feed_urls.append((element.attribute("href"), element.attribute("href")))
        return feed_urls

    def setCanGoNext(self):
        if not self._changeCanGoNext:
            return
        else:
            self._changeCanGoNext = False
        url_parts = self.url().toString().split("/")
        fail = []
        for part in range(len(url_parts)):
            try: int(url_parts[part])
            except: pass
            else:
                fail.append(part)
        if len(fail) == 1:
            url_parts[fail[0]] = str(int(url_parts[fail[0]]) + 1)
            self._canGoNext = "/".join(url_parts)
            return
        anchors = self.page().mainFrame().findAllElements("a")
        for anchor in anchors:
            for attribute in anchor.attributeNames():
                try:
                    if attribute.lower() == "rel" and anchor.attribute(attribute).lower() == "next":
                        try:
                            self._canGoNext = anchor.attribute("href")
                            return
                        except:
                            pass
                except:
                    pass
        success = False
        for rstring in self.nextExpressions[:-1]:
            for times in reversed(range(1, 11)):
                try: thisPageNumber = int(re.search("%s%s" % (rstring, "[\d]" * times), self.url().toString().lower()).group().replace(rstring, ""))
                except: pass
                else:
                    success = True
                    break
        if not success:
            thisPageNumber = 0
        for rstring in self.nextExpressions:
            for anchor in anchors:
                for attribute in anchor.attributeNames():
                    try:
                        for times in reversed(range(1, 11)):
                            try: thatPageNumber = int(re.search("%s%s" % (rstring, "[\d]" * times), anchor.attribute(attribute).lower()).group().replace(rstring, ""))
                            except: pass
                            else: break
                        if thatPageNumber > thisPageNumber:
                            try:
                                self._canGoNext = anchor.attribute("href")
                                return
                            except:
                                pass
                    except:
                        pass
        for rstring in ("start=", "offset=", "page=", "="):
            for anchor in anchors:
                for attribute in anchor.attributeNames():
                    if re.search("%s[\d*]" % (rstring,), anchor.attribute(attribute).lower()):
                        try:
                            self._canGoNext = anchor.attribute("href")
                            return
                        except:
                            pass
        for anchor in anchors:
            for attribute in anchor.attributeNames():
                try:
                    if attribute.lower() in ("class", "rel", "id") and "next" in anchor.attribute(attribute).lower():
                        try:
                            self._canGoNext = anchor.attribute("href")
                            return
                        except:
                            pass
                except:
                    pass
        for anchor in anchors:
            if "next" in anchor.toPlainText().lower():
                try:
                    self._canGoNext = anchor.attribute("href")
                    return
                except:
                    pass
        self._canGoNext = False

    def canGoNext(self):
        return self._canGoNext

    def next(self):
        href = self.canGoNext()
        if href:
            self.page().mainFrame().evaluateJavaScript("window.location.href = \"%s\";" % (href,))

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
    def setUserAgent(self, ua=None):
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
        if self._oldURL != self._url:
            self._contentTypes = {}
            self._oldURL = self._url

    # Custom implementation of deleteLater that also removes
    # the WebView from common.webviews.
    def deleteLater(self):
        try: common.webviews.remove(self)
        except: pass
        QWebView.deleteLater(self)

    # If a request has finished and the request's URL is the current URL,
    # then set self._contentType.
    def ready(self, response):
        try:
            if self._contentType == None and response.url() == self.url():
                try: contentType = response.header(QNetworkRequest.ContentTypeHeader)
                except: contentType = None
                if contentType != None:
                    self._contentType = contentType
                html = self.page().mainFrame().toHtml()
                if "xml" in str(self._contentType) and ("<rss" in html or ("<feed" in html and "atom" in html)):
                    try: self.setHtml(rss_parser.feedToHtml(html), self.url())
                    except: pass
        except:
            pass

    # This is a custom implementation of mousePressEvent.
    # It allows the user to Ctrl-click or middle-click links to open them in
    # new tabs.
    def mousePressEvent(self, ev):
        if self._statusBarMessage != "" and (((QCoreApplication.instance().keyboardModifiers() == Qt.ControlModifier) and not ev.button() == Qt.RightButton) or ev.button() == Qt.MidButton or ev.button() == Qt.MiddleButton):
            url = self._statusBarMessage
            ev.ignore()
            newWindow = self.createWindow(QWebPage.WebBrowserWindow)
            newWindow.load(QUrl(url))
        elif self._statusBarMessage != "" and (((QCoreApplication.instance().keyboardModifiers() == Qt.ShiftModifier) and not ev.button() == Qt.RightButton)):
            self.openInDefaultBrowser(self._statusBarMessage)
        else:
            return QWebView.mousePressEvent(self, ev)

    def openInDefaultBrowser(self, url=None):
        if type(url) is QUrl:
            url = url.toString()
        elif not url:
            url = self._statusBarMessage
        if sys.platform.startswith("linux"):
            subprocess.Popen(["xdg-open", url])
        else:
            webbrowser.open(url)

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
        if sys.platform.startswith("win"):
            components = []
            print(url.toString().split("/"))
            for component in url.toString().split("/"):
                if len(component) == 2 and component.endswith(":"):
                    pass
                else:
                    components.append(component)
            print(components)
            url = QUrl("/".join(components))
        self._cacheLoaded = False
        dirname = url.path()
        self._url = url.toString()
        if url.toString() == "about:blank":
            if os.path.exists(settings.new_tab_page):
                loadwin = QWebView.load(self, QUrl.fromUserInput(settings.new_tab_page))
            else:
                loadwin = QWebView.load(self, url)
        else:
            loadwin = QWebView.load(self, url)

    def load2(self, url):
        self.page().mainFrame().evaluateJavaScript("window.location.href = \"%s\"" % (url,))

    # Method to replace all <audio> and <video> tags with <embed> tags.
    # This is mainly a hack for Windows, where <audio> and <video> tags are not
    # properly supported under PyQt5.
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
        if not settings.setting_to_bool("general/StatusBarVisible") and len(self._statusBarMessage) > 0:
            self.statusMessageDisplay.hide()
            self.statusMessageDisplay.setText(self._statusBarMessage)
            self.statusMessageDisplay.show()
            self.statusMessageDisplay.move(QPoint(0, self.height()-self.statusMessageDisplay.height()))
            opposite = QCursor.pos().x() in tuple(range(self.statusMessageDisplay.mapToGlobal(QPoint(0,0)).x(), self.statusMessageDisplay.mapToGlobal(QPoint(0,0)).x() + self.statusMessageDisplay.width())) and QCursor.pos().y() in tuple(range(self.statusMessageDisplay.mapToGlobal(QPoint(0,0)).y(), self.statusMessageDisplay.mapToGlobal(QPoint(0,0)).y() + self.statusMessageDisplay.height()))
            self.statusMessageDisplay.move(QPoint(0 if not opposite else self.width()-self.statusMessageDisplay.width(), self.height()-self.statusMessageDisplay.height()))
            self.repaint()
        elif len(self._statusBarMessage) == 0:
            self.statusMessageDisplay.hide()
            self.repaint()

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
        if self.isLoading:
            return common.complete_icon("image-loading")
        elif self.incognito:
            return common.complete_icon("face-devilish")
        icon = QWebView.icon(self)
        if icon.pixmap(QSize(16, 16)).width() == 0:
            return common.complete_icon("text-html")
        else:
            return icon

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
        self.settings().setAttribute(self.settings().JavascriptCanOpenWindows, settings.setting_to_bool("content/JavascriptCanOpenWindows"))
        self.settings().setAttribute(self.settings().JavascriptCanCloseWindows, settings.setting_to_bool("content/JavascriptCanCloseWindows"))
        self.settings().setAttribute(self.settings().JavascriptCanAccessClipboard, settings.setting_to_bool("content/JavascriptCanAccessClipboard"))
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
        fileName = request.url().toString().split("?")[0].split("/")
        fileName = fileName[-1 if fileName[-1] != "" else -2]
        upperFileName = fileName.upper()
        for extension in common.tlds:
            if upperFileName.endswith(extension):
                fileName = fileName + ".html"
        try: ext = "." + self._contentTypes[request.url().toString()].split("/")[-1].split(";")[0]
        except: ext = ".html"
        fname = QFileDialog.getSaveFileName(None, tr("Save As..."), os.path.join(self.saveDirectory, fileName + (ext if not "." in fileName else "")), tr("All files (*)"))
        if type(fname) is tuple:
            fname = fname[0]
        if fname:
            self.saveDirectory = os.path.split(fname)[0]
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
        except: pass
        else:
            try: self.setHtml(f.read(), QUrl(url))
            except: pass
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
            except: pass
            else:
                try: f.write(content)
                except: pass
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
            fileName = self.url().toString().split("?")[0].split("/")
            fileName = fileName[-1 if fileName[-1] != "" else -2]
            upperFileName = fileName.upper()
            for extension in common.tlds:
                if upperFileName.endswith(extension):
                    fileName = fileName + ".html"
            try: ext = "." + self._contentTypes[self.url().toString()].split("/")[-1].split(";")[0]
            except: ext = ".html"
            fname = QFileDialog.getSaveFileName(None, tr("Save As..."), os.path.join(self.saveDirectory, fileName + (ext if not "." in fileName else "")), tr("All files (*)"))
        if type(fname) is tuple:
            fname = fname[0]
        if fname:
            self.saveDirectory = os.path.split(fname)[0]
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
        addHistoryItem(url.toString(), self.windowTitle())

    # Redefine createWindow. Emits windowCreated signal so that others
    # can utilize the newly-created WebView instance.
    def createWindow(self, type):
        webview = WebView(incognito=self.incognito)
        self.webViews.append(webview)
        #webview.show()
        self.windowCreated.emit(webview)
        return webview

    # Convenience function.
    # Sets the zoom factor.
    def zoom(self):
        zoom = QInputDialog.getDouble(self, tr("Zoom"), tr("Set zoom factor:"), self.zoomFactor())
        if zoom[1]:
            self.setZoomFactor(zoom[0])

    # Convenience function.
    # Opens a very simple find text dialog.
    def find(self):
        if type(self._findText) is not str:
            self._findText = ""
        find = QInputDialog.getText(self, tr("Find"), tr("Search for:"), QLineEdit.Normal, self._findText)
        if find[1]:
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

class WebViewAction(QWidgetAction):
    def __init__(self, *args, incognito=False, **kwargs):
        super(WebViewAction, self).__init__(*args, **kwargs)
        self.webView = WebView(incognito=incognito, sizeHint=QSize(1, 320), minimumSizeHint=QSize(0,0))
        self.webView.setUserAgent(common.mobileUserAgent)
        self.setDefaultWidget(self.webView)
    def load(self, *args, **kwargs):
        self.webView.load(*args, **kwargs)
    def back(self, *args, **kwargs):
        self.webView.back(*args, **kwargs)
    def forward(self, *args, **kwargs):
        self.webView.forward(*args, **kwargs)
    def reload(self, *args, **kwargs):
        self.webView.reload(*args, **kwargs)
    def stop(self, *args, **kwargs):
        self.webView.stop(*args, **kwargs)
