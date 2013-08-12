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
import base64
import urllib.request
import subprocess
import threading
import copy
import traceback
import hashlib
import common
import translate
from translate import tr
import custom_widgets
import clear_history_dialog
import status_bar
import extension_server
import settings_dialog

# Python DBus
has_dbus = True
try:
    import dbus
    import dbus.service
    from dbus.mainloop.qt import DBusQtMainLoop
except:
    has_dbus = False

# Extremely specific imports from PySide/PyQt4.
try:
    from PySide.QtCore import Qt, QCoreApplication, Signal, QUrl, QFile, QIODevice, QTimer
    from PySide.QtGui import QApplication, QKeySequence, QListWidget, QSpinBox, QListWidgetItem, QMessageBox, QIcon, QMenu, QAction, QMainWindow, QToolBar, QToolButton, QComboBox, QLineEdit, QTabWidget, QPrinter, QPrintDialog, QPrintPreviewDialog, QInputDialog, QFileDialog, QProgressBar, QLabel, QCalendarWidget, QSlider, QFontComboBox, QLCDNumber, QImage, QDateTimeEdit, QDial, QSystemTrayIcon
    from PySide.QtNetwork import QNetworkProxy, QNetworkRequest, QNetworkAccessManager
    from PySide.QtWebKit import QWebView, QWebPage
    pyside = True
except:
    from PyQt4.QtCore import Qt, QCoreApplication, pyqtSignal, QUrl, QFile, QIODevice, QTimer
    from PyQt4.QtGui import QApplication, QKeySequence, QListWidget, QSpinBox, QListWidgetItem, QMessageBox, QIcon, QMenu, QAction, QMainWindow, QToolBar, QToolButton, QComboBox, QLineEdit, QTabWidget, QPrinter, QPrintDialog, QPrintPreviewDialog, QInputDialog, QFileDialog, QProgressBar, QLabel, QCalendarWidget, QSlider, QFontComboBox, QLCDNumber, QImage, QDateTimeEdit, QDial, QSystemTrayIcon
    from PyQt4.QtNetwork import QNetworkProxy, QNetworkRequest, QNetworkAccessManager
    from PyQt4.QtWebKit import QWebView, QWebPage
    Signal = pyqtSignal
    pyside = False

# chdir to the app folder. This way, we won't have issues related to
# relative paths.
os.chdir(common.app_folder)

# Create extension server.
server_thread = extension_server.ExtensionServerThread()

# Add an item to the browser history.
def addHistoryItem(url):
    if not url in common.history and len(url) < 84 and common.setting_to_bool("data/RememberHistory"):
        common.history.append(url)

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
            self.nAM = common.networkAccessManager
            self.page().setNetworkAccessManager(self.nAM)
            self.nAM.setParent(QCoreApplication.instance())
        else:
            self.nAM = common.incognitoNetworkAccessManager
            self.page().setNetworkAccessManager(self.nAM)
            self.nAM.setParent(QCoreApplication.instance())
        self.nAM.finished.connect(self.requestFinished)

        # Enable Web Inspector
        self.settings().setAttribute(self.settings().DeveloperExtrasEnabled, True)

        self.updateProxy()
        self.updateNetworkSettings()
        self.updateContentSettings()

        # What to do if private browsing is not enabled.
        if not self.incognito:
            # Set persistent storage path to settings_folder.
            self.settings().enablePersistentStorage(common.settings_folder)

            # Set the CookieJar.
            self.page().networkAccessManager().setCookieJar(common.cookieJar)

            # Do this so that cookieJar doesn't get deleted along with WebView.
            common.cookieJar.setParent(QCoreApplication.instance())

            # Recording history should only be done in normal browsing mode.
            self.urlChanged.connect(self.addHistoryItem)

        # What to do if private browsing is enabled.
        else:
            # Global incognito cookie jar, so that logins are preserved
            # between incognito tabs.
            self.page().networkAccessManager().setCookieJar(common.incognitoCookieJar)
            common.incognitoCookieJar.setParent(QCoreApplication.instance())

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
        self.loadFinished.connect(self.replaceAVTags)
        self.loadFinished.connect(self.savePageToCache)

        self.setWindowTitle("")

        self.load(QUrl("about:blank"))

    def deleteLater(self):
        try: common.webviews.remove(self)
        except: pass
        QWebView.deleteLater(self)

    def mousePressEvent(self, ev):
        if self._statusBarMessage != "" and (((QCoreApplication.instance().keyboardModifiers() == Qt.ControlModifier) and not ev.button() == Qt.RightButton) or ev.button() == Qt.MidButton or ev.button() == Qt.MiddleButton):
            url = self._statusBarMessage
            ev.ignore()
            newWindow = self.createWindow(QWebPage.WebBrowserWindow)
            newWindow.load(QUrl(url))
        else:
            return QWebView.mousePressEvent(self, ev)

    # This loads a page from the cache if certain network errors occur.
    def requestFinished(self, reply):
        if reply.error() in (3,4,104,) and not self._cacheLoaded:
            self._cacheLoaded = True
            self.loadPageFromCache(self._url)

    def load(self, url):
        if type(url) is QListWidgetItem:
            url = QUrl.fromUserInput(url.text())
        self._cacheLoaded = False
        dirname = url.path()
        self._url = url.toString()
        if url.scheme() == "nimbus":
            x = "data:text/html;charset=utf-8;base64," + base64.b64encode(("<!DOCTYPE html><html><head><title>" + tr("Settings") + "</title></head><body><object type=\"application/x-qt-plugin\" classid=\"settingsDialog\" style=\"position: fixed; top: 0; left: 0; width: 100%; height: 100%;\"></object></body></html>".replace('\n', '')).encode('utf-8')).decode('utf-8')
            QWebView.load(self, QUrl(x))
            return
        if url.toString() == "about:blank":
            if os.path.exists(common.new_tab_page):
                loadwin = QWebView.load(self, QUrl.fromUserInput(common.new_tab_page))
            else:
                loadwin = QWebView.load(self, url)
        else:
            loadwin = QWebView.load(self, url)

    # Method to replace all <audio> and <video> tags with <embed> tags.
    def replaceAVTags(self):
        if not common.setting_to_bool("content/ReplaceHTML5MediaTagsWithEmbedTags"):
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

    def setStatusBarMessage(self, link="", title="", content=""):
        self._statusBarMessage = link

    def setLoadProgress(self, progress):
        self._loadProgress = progress

    def setWindowTitle(self, title):
        if len(title) == 0:
            title = tr("New Tab")
        QWebView.setWindowTitle(self, title)

    def icon(self):
        if self.incognito:
            return common.complete_icon("face-devilish")
        return QWebView.icon(self)

    # Function to update proxy list.
    def updateProxy(self):
        proxyType = str(common.settings.value("proxy/Type"))
        if proxyType == "None":
            proxyType = "No"
        port = common.settings.value("proxy/Port")
        if port == None:
            port = common.default_port
        user = str(common.settings.value("proxy/User"))
        if user == "":
            user = None
        password = str(common.settings.value("proxy/Password"))
        if password == "":
            password = None
        self.page().networkAccessManager().setProxy(QNetworkProxy(eval("QNetworkProxy." + proxyType + "Proxy"), str(common.settings.value("proxy/Hostname")), int(port), user, password))

    def updateContentSettings(self):
        self.settings().setAttribute(self.settings().AutoLoadImages, common.setting_to_bool("content/AutoLoadImages"))
        self.settings().setAttribute(self.settings().JavascriptEnabled, common.setting_to_bool("content/JavascriptEnabled"))
        self.settings().setAttribute(self.settings().JavaEnabled, common.setting_to_bool("content/JavaEnabled"))
        self.settings().setAttribute(self.settings().PrintElementBackgrounds, common.setting_to_bool("content/PrintElementBackgrounds"))
        self.settings().setAttribute(self.settings().FrameFlatteningEnabled, common.setting_to_bool("content/FrameFlatteningEnabled"))
        self.settings().setAttribute(self.settings().PluginsEnabled, common.setting_to_bool("content/PluginsEnabled"))
        self.settings().setAttribute(self.settings().TiledBackingStoreEnabled, common.setting_to_bool("content/TiledBackingStoreEnabled"))
        self.settings().setAttribute(self.settings().SiteSpecificQuirksEnabled, common.setting_to_bool("content/SiteSpecificQuirksEnabled"))

    def updateNetworkSettings(self):
        self.settings().setAttribute(self.settings().XSSAuditingEnabled, common.setting_to_bool("network/XSSAuditingEnabled"))
        self.settings().setAttribute(self.settings().DnsPrefetchEnabled, common.setting_to_bool("network/DnsPrefetchEnabled"))

    # Handler for unsupported content.
    def handleUnsupportedContent(self, reply):
        url2 = reply.url()
        url = url2.toString()

        # Make sure the file isn't local, that content viewers are
        # enabled, and private browsing isn't enabled.
        if not url2.scheme() == "file" and common.setting_to_bool("content/UseOnlineContentViewers") and not self.incognito:
            for viewer in common.content_viewers:
                try:
                    for extension in viewer[1]:
                        if url.lower().endswith(extension):
                            QWebView.load(self, QUrl(viewer[0] % (url,)))
                            return
                except:
                    pass

        self.downloadFile(reply.request())

    # Download file.
    def downloadFile(self, request):

        if request.url() == self.url():

            try: contentMimeType = urllib.request.urlopen(request.url().toString()).info()
            except: contentMimeType = "None"
            else: contentMimeType = str(contentMimeType["Content-Type"])

            # If the file type can be converted to plain text, use savePage
            # method instead.
            for mimeType in ("text", "svg", "html", "xml", "xhtml",):
                if mimeType in contentMimeType:
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

    def loadPageFromCache(self, url):
        m = hashlib.md5()
        m.update(common.shortenURL(url).encode('utf-8'))
        h = m.hexdigest()
        try: f = open(os.path.join(common.offline_cache_folder, h), "r")
        except: traceback.print_exc()
        else:
            try: self.setHtml(f.read())
            except: traceback.print_exc()
            f.close()

    def savePageToCache(self):
        if not self.incognito:
            if not os.path.exists(common.offline_cache_folder):
                try: os.mkdir(common.offline_cache_folder)
                except: return
            content = self.page().mainFrame().toHtml()
            m = hashlib.md5()
            m.update(common.shortenURL(self.url().toString()).encode('utf-8'))
            h = m.hexdigest()
            try: f = open(os.path.join(common.offline_cache_folder, h), "w")
            except: traceback.print_exc()
            else:
                try: f.write(content)
                except: traceback.print_exc()
                f.close()

    # Save current page.
    def savePage(self):
        content = self.page().mainFrame().toHtml()
        if self.url().toString() in ("about:blank", "", QUrl.fromUserInput(common.new_tab_page).toString(),) and not self._cacheLoaded:
            fname = common.new_tab_page
            content = content.replace("&lt;", "<").replace("&gt;", ">").replace("<body contenteditable=\"true\">", "<body>")
        else:
            fname = QFileDialog.getSaveFileName(None, tr("Save As..."), os.path.join(os.path.expanduser("~"), self.url().toString().split("/")[-1]), tr("All files (*)"))
        if fname:
            if type(fname) is tuple:
                fname = fname[0]
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

    # Add history item to the browser history.
    def addHistoryItem(self, url):
        addHistoryItem(url.toString())

    # Redefine createWindow. Emits windowCreated signal so that others
    # can utilize the newly-created WebView instance.
    def createWindow(self, type):
        webview = WebView(incognito=self.incognito, parent=self.parent())
        self.webViews.append(webview)
        self.windowCreated.emit(webview)
        return webview

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

    # Find next instance of text.
    def findNext(self):
        if not self._findText:
            self.find()
        else:
            self.findText(self._findText, QWebPage.FindWrapsAroundDocument)

    # Find previous instance of text.
    def findPrevious(self):
        if not self._findText:
            self.find()
        else:
            self.findText(self._findText, QWebPage.FindWrapsAroundDocument | QWebPage.FindBackward)

    # Open print dialog to print page.
    def printPage(self):
        printer = QPrinter()
        self.page().mainFrame().render(printer.paintEngine().painter())
        printDialog = QPrintDialog(printer)
        printDialog.open()
        printDialog.accepted.connect(lambda: self.print(printer))
        printDialog.exec_()

    # Open print preview dialog.
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
        common.extension_buttons.append(self)
        self._parent = parent
        self.script = script
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
        self.mouseX = False
        self.mouseY = False

        # Add self to global list of windows.
        common.windows.append(self)

        # Set window icon.
        self.setWindowIcon(common.app_icon)

        # List of closed tabs.
        self.closedTabs = []

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
        removeTabAction.triggered.connect(lambda: self.removeTab(self.tabs.currentIndex()))
        self.addAction(removeTabAction)

        # Dummy webpage used to provide navigation actions that conform to
        # the system's icon theme.
        self.actionsPage = QWebPage(self)

        # Regularly toggle navigation actions every few milliseconds.
        self.toggleActionsTimer = QTimer(self)
        self.toggleActionsTimer.timeout.connect(self.toggleActions)

        # Set up navigation actions.
        self.backAction = self.actionsPage.action(QWebPage.Back)
        self.backAction.setShortcut("Alt+Left")
        self.backAction.triggered.connect(self.back)
        self.toolBar.addAction(self.backAction)

        self.forwardAction = self.actionsPage.action(QWebPage.Forward)
        self.forwardAction.setShortcut("Alt+Right")
        self.forwardAction.triggered.connect(self.forward)
        self.toolBar.addAction(self.forwardAction)

        self.stopAction = self.actionsPage.action(QWebPage.Stop)
        self.stopAction.setShortcut("Esc")
        self.stopAction.triggered.connect(self.stop)
        self.toolBar.addAction(self.stopAction)

        self.reloadAction = self.actionsPage.action(QWebPage.Reload)
        self.reloadAction.setShortcuts(["F5", "Ctrl+R"])
        self.reloadAction.triggered.connect(self.reload)
        self.toolBar.addAction(self.reloadAction)

        self.homeAction = QAction(common.complete_icon("go-home"), tr("Go Home"), self)
        self.homeAction.setShortcut("Alt+Home")
        self.homeAction.triggered.connect(self.goHome)
        self.toolBar.addAction(self.homeAction)

        # Start timer.
        self.toggleActionsTimer.start(8)

        # Location bar. Note that this is a combo box.
        self.locationBar = QComboBox(self)

        # Load stored browser history.
        for url in common.history:
            self.locationBar.addItem(url)

        # Combo boxes are not normally editable by default.
        self.locationBar.setEditable(True)

        # We want the location bar to stretch to fit the toolbar,
        # so we set its size policy to that of a QLineEdit.
        self.locationBar.setSizePolicy(QLineEdit().sizePolicy())

        # Load a page when Enter is pressed.
        self.locationBar.lineEdit().returnPressed.connect(lambda: self.load(self.locationBar.lineEdit().text()))
        self.locationBar.view().activated.connect(lambda index: self.load(index.data()))

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
        savePageAction.triggered.connect(lambda: self.tabs.currentWidget().downloadFile(QNetworkRequest(self.tabs.currentWidget().url())))
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

        # Add clear history action.
        clearHistoryAction = QAction(common.complete_icon("edit-clear"), tr("&Clear Data..."), self)
        clearHistoryAction.setShortcut("Ctrl+Shift+Del")
        clearHistoryAction.triggered.connect(self.clearHistory)
        mainMenu.addAction(clearHistoryAction)

        # Add settings dialog action.
        settingsAction = QAction(common.complete_icon("preferences-system"), tr("&Settings..."), self)
        settingsAction.setShortcuts(["Ctrl+,", "Ctrl+Alt+P"])
        settingsAction.triggered.connect(self.openSettings)
        settingsAction.triggered.connect(lambda: self.tabs.setCurrentIndex(self.tabs.count()-1))
        mainMenu.addAction(settingsAction)

        mainMenu.addSeparator()

        # About Qt action.
        aboutQtAction = QAction(common.complete_icon("qt"), tr("About &Qt"), self)
        aboutQtAction.triggered.connect(QApplication.aboutQt)
        mainMenu.addAction(aboutQtAction)

        # About Nimbus action.
        aboutAction = QAction(common.complete_icon("help-about"), tr("A&bout Nimbus"), self)
        aboutAction.triggered.connect(lambda: QMessageBox.about(self, tr("Nimbus"), tr("<h3>Nimbus</h3>Python 3/Qt 4-based web browser.")))
        mainMenu.addAction(aboutAction)

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

        # Load browser extensions.
        # Ripped off of Ricotta.
        self.reloadExtensions()

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

    # Blank all tabs when window is closed.
    def closeEvent(self, ev):
        self.blankAll()
        if len(common.windows) - 1 > common.setting_to_int("general/ReopenableWindowCount"):
            for window in common.windows:
                if not window.isVisible():
                    window.deleteLater()
                    common.windows.pop(common.windows.index(window))
                    break

    # Open settings dialog.
    def openSettings(self):
        if common.setting_to_bool("general/OpenSettingsInTab"):
            self.addTab(url="nimbus://settings")
        else:
            common.settingsDialog.reload()
            common.settingsDialog.show()

    # Reload extensions.
    def reloadExtensions(self):

        # Hide extensions toolbar if there aren't any extensions.
        if common.extensions_whitelist == None:
            self.extensionBar.hide()
            return
        elif len(common.extensions_whitelist) == 0:
            self.extensionBar.hide()
            return

        for extension in common.extensions:
            if extension not in common.extensions_whitelist:
                continue
            extension_path = os.path.join(common.extensions_folder, extension)
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
            self.backAction.setEnabled(self.tabs.currentWidget().pageAction(QWebPage.Back).isEnabled())
            self.forwardAction.setEnabled(self.tabs.currentWidget().pageAction(QWebPage.Forward).isEnabled())

            # This is a workaround so that hitting Esc will reset the location
            # bar text.
            self.stopAction.setEnabled(True)

            self.reloadAction.setEnabled(True)
        except:
            self.backAction.setEnabled(False)
            self.forwardAction.setEnabled(False)
            self.stopAction.setEnabled(False)
            self.reloadAction.setEnabled(False)

    # Blank all tabs.
    def blankAll(self):
        for index in range(0, self.tabs.count()):
            self.tabs.widget(index).load(QUrl("about:blank"))

    def deblankAll(self):
        for index in range(0, self.tabs.count()):
            if self.tabs.widget(index).url().toString() in ("about:blank", "", QUrl.fromUserInput(common.new_tab_page).toString(),):
                self.tabs.widget(index).back()

    # Navigation methods.
    def back(self):
        self.tabs.currentWidget().back()

    def forward(self):
        self.tabs.currentWidget().forward()

    def reload(self):
        self.tabs.currentWidget().reload()

    def stop(self):
        self.tabs.currentWidget().stop()
        self.locationBar.setEditText(self.tabs.currentWidget().url().toString())

    def goHome(self):
        self.tabs.currentWidget().load(QUrl.fromUserInput(common.settings.value("general/Homepage")))

    # Find text/Text search methods.
    def find(self):
        self.tabs.currentWidget().find()

    def findNext(self):
        self.tabs.currentWidget().findNext()

    def findPrevious(self):
        self.tabs.currentWidget().findPrevious()

    # Page printing methods.
    def printPage(self):
        self.tabs.currentWidget().printPage()

    def printPreview(self):
        self.tabs.currentWidget().printPreview()

    # Clears the history after a prompt.
    def clearHistory(self):
        chistorydialog.display()

    # Method to load a URL.
    def load(self, url=False):
        if not url:
            url = self.locationBar.currentText()
        if "." in url or ":" in url or os.path.exists(url):
            self.tabs.currentWidget().load(QUrl.fromUserInput(url))
        else:
            self.tabs.currentWidget().load(QUrl(common.settings.value("general/Search") % (url,)))

    # Status bar related methods.
    def setStatusBarMessage(self, message):
        try: self.statusBar.setStatusBarMessage(self.tabs.currentWidget()._statusBarMessage)
        except: self.statusBar.setStatusBarMessage("")

    def setProgress(self, progress):
        try: self.statusBar.setValue(self.tabs.currentWidget()._loadProgress)
        except: self.statusBar.setValue(0)

    # Tab-related methods.
    def currentWidget(self):
        return self.tabs.currentWidget()

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
            webview = WebView(incognito=not common.setting_to_bool("data/RememberHistory"), parent=self)
            webview.load(QUrl.fromUserInput(url))

        # If a WebView object is specified, use it.
        elif webView != None:
            webview = webView

        # If nothing is specified, use a blank WebView.
        else:
            webview = WebView(incognito=not common.setting_to_bool("data/RememberHistory"), parent=self)

        # Connect signals
        webview.loadProgress.connect(self.setProgress)
        webview.statusBarMessage.connect(self.setStatusBarMessage)
        webview.page().linkHovered.connect(self.setStatusBarMessage)
        webview.titleChanged.connect(self.updateTabTitles)
        webview.urlChanged.connect(self.updateLocationText)
        webview.iconChanged.connect(self.updateTabIcons)
        webview.windowCreated.connect(lambda webView: self.addTab(webView=webView, index=self.tabs.currentIndex()+1, focus=False))
        webview.downloadStarted.connect(self.addDownloadToolBar)

        # Add tab
        if type(index) is not int:
            self.tabs.addTab(webview, tr("New Tab"))
        else:
            self.tabs.insertTab(index, webview, tr("New Tab"))

        # Switch to new tab
        if focus:
            self.tabs.setCurrentIndex(self.tabs.count()-1)

        # Update icons so we see the globe icon on new tabs.
        self.updateTabIcons()

    def nextTab(self):
        if self.tabs.currentIndex() == self.tabs.count() - 1:
            self.tabs.setCurrentIndex(0)
        else:
            self.tabs.setCurrentIndex(self.tabs.currentIndex() + 1)

    def previousTab(self):
        if self.tabs.currentIndex() == 0:
            self.tabs.setCurrentIndex(self.tabs.count() - 1)
        else:
            self.tabs.setCurrentIndex(self.tabs.currentIndex() - 1)

    def updateTabTitles(self):
        for index in range(0, self.tabs.count()):
            title = self.tabs.widget(index).windowTitle()
            self.tabs.setTabText(index, title[:24] + '...' if len(title) > 24 else title)
            if index == self.tabs.currentIndex():
                self.setWindowTitle(title + " - " + tr("Nimbus"))

    def updateTabIcons(self):
        for index in range(0, self.tabs.count()):
            try: icon = self.tabs.widget(index).icon()
            except: continue
            self.tabs.setTabIcon(index, icon)

    def removeTab(self, index):
        try:
            webView = self.tabs.widget(index)
            if webView.history().canGoBack() or webView.history().canGoForward() or webView.url().toString() not in ("about:blank", "", QUrl.fromUserInput(common.new_tab_page).toString(),):
                self.closedTabs.append(webView)
                while len(self.closedTabs) > common.setting_to_int("general/ReopenableTabCount"):
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
        self.tabs.removeTab(index)
        if self.tabs.count() == 0:
            if common.setting_to_bool("general/CloseWindowWithLastTab"):
                self.close()
            else:
                self.addTab(url="about:blank")

    def reopenTab(self):
        if len(self.closedTabs) > 0:
            webview = self.closedTabs.pop()
            self.addTab(webview)
            try:
                if webview.url().toString() in ("about:blank", "", QUrl.fromUserInput(common.new_tab_page).toString(),):
                    webview.back()
            except: pass

    # This method is used to add a DownloadBar to the window.
    def addDownloadToolBar(self, toolbar):
        self.statusBar.addToolBar(toolbar)

    # Method to update the location bar text.
    def updateLocationText(self, url=None):
        try:
            if type(url) != QUrl:
                url = self.tabs.currentWidget().url()
            currentUrl = self.tabs.currentWidget().url()
            if url == currentUrl:
                self.locationBar.setEditText(currentUrl.toString())
        except:
            pass

# Redundancy is redundant.
def addWindow(url=None):
    win = MainWindow()
    if url == None:
        win.addTab(url=common.settings.value("general/Homepage"))
    else:
        win.addTab(url=url)
    win.show()

# Reopen window method.
def reopenWindow():
    for window in common.windows[::-1]:
        if not window.isVisible():
            common.windows.append(common.windows.pop(common.windows.index(window)))
            window.deblankAll()
            if window.tabs.count() == 0:
                window.reopenTab()
            window.show()
            return

# Preparations to quit.
def prepareQuit():
    common.saveData()
    common.adblock_filter_loader.quit()
    common.adblock_filter_loader.wait()
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
            for window in common.windows[::-1]:
                if window.isVisible():
                    window.addTab(url=url)
                    common.windows[-1].activateWindow()
                    return url
            self.addWindow(url)
            common.windows[-1].activateWindow()
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

    # Create tray icon.
    common.trayIcon = SystemTrayIcon(QCoreApplication.instance())
    common.trayIcon.show()

    # Create instance of clear history dialog.
    global chistorydialog
    chistorydialog = clear_history_dialog.ClearHistoryDialog()

    # Set up settings dialog.
    common.settingsDialog = WebView(incognito=True, parent=None)
    common.settingsDialog.resize(560, 480)
    common.settingsDialog.setWindowIcon(common.app_icon)
    common.settingsDialog.setWindowFlags(Qt.Dialog)
    common.settingsDialog.load(QUrl("nimbus://settings"))
    closeSettingsDialogAction = QAction(common.settingsDialog)
    closeSettingsDialogAction.setShortcuts(["Esc", "Ctrl+W"])
    closeSettingsDialogAction.triggered.connect(common.settingsDialog.hide)
    common.settingsDialog.addAction(closeSettingsDialogAction)

    # Create DBus server
    if has_dbus:
        server = DBusServer(bus)

    # Load adblock rules.
    common.adblock_filter_loader.start()

    # Start extension server.
    server_thread.start()

    # On quit, save settings.
    app.aboutToQuit.connect(prepareQuit)

    # Load settings.
    common.loadData()

    if not "--daemon" in sys.argv:
        # Create instance of MainWindow.
        win = MainWindow()

        # Open URLs from command line.
        if len(sys.argv) > 1:
            for arg in sys.argv[1:]:
                if "." in arg or ":" in arg:
                    win.addTab(url=arg)

        if win.tabs.count() < 1:
            win.addTab(url=common.settings.value("general/Homepage"))

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
