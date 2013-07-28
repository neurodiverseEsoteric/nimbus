#! /usr/bin/env python3

# Import everything we need.
import sys
import os
import subprocess
import copy
import common
import status_bar
import extension_server
import settings_dialog

# To avoid warnings, we create this.
pdialog = None

# Extremely specific imports from PyQt4.
from PyQt4.QtCore import Qt, QCoreApplication, pyqtSignal, QUrl, QByteArray, QFile, QIODevice, QTimer
from PyQt4.QtGui import QApplication, QIcon, QMenu, QAction, QMainWindow, QToolBar, QToolButton, QComboBox, QLineEdit, QTabWidget, QPrinter, QPrintDialog, QPrintPreviewDialog, QInputDialog, QFileDialog, QProgressBar, QLabel
from PyQt4.QtNetwork import QNetworkCookie, QNetworkAccessManager, QNetworkRequest, QNetworkProxy
from PyQt4.QtWebKit import QWebView, QWebPage

# chdir to the app folder.
os.chdir(common.app_folder)

# Create extension server.
server_thread = extension_server.ExtensionServerThread()

# Create thread to load adblock filters.
adblock_filter_loader = common.AdblockFilterLoader()

# List of file extensions supported by Google Docs.
gdocs_extensions = (".doc", ".pdf", ".ppt", ".pptx", ".docx", ".xls", ".xlsx", ".pages", ".ai", ".psd", ".tiff", ".dxf", ".svg", ".eps", ".ps", ".ttf", ".xps", ".zip", ".rar")

# Global list to store browser history.
history = []

# Add an item to the browser history.
def addHistoryItem(url):
    global history
    if not url in history and len(url) < 84:
        history.append(url)

# This function saves the browser's settings.
def saveSettings():
    # Save history.
    global history
    history = [(item.partition("://")[-1] if "://" in item else item).replace(("www." if item.startswith("www.") else ""), "") for item in history]
    history = list(set(history))
    history.sort()
    common.settings.setValue("history", history)

    # Save cookies.
    cookies = [cookie.toRawForm().data() for cookie in common.cookieJar.allCookies()]
    common.settings.setValue("cookies", cookies)

    # Sync any unsaved settings.
    common.settings.sync()

# This function loads the browser's settings.
def loadSettings():
    # Load history.
    global history
    raw_history = common.settings.value("history")
    if type(raw_history) is list:
        history = common.settings.value("history")

    # Load cookies.
    raw_cookies = common.settings.value("cookies")
    if type(raw_cookies) is list:
        cookies = [QNetworkCookie().parseCookies(QByteArray(cookie))[0] for cookie in raw_cookies]
        common.cookieJar.setAllCookies(cookies)

# This function clears out the browsing history and cookies.
# Changes are written to the disk upon application quit.
def clearHistory():
    global history
    history = []
    common.cookieJar.setAllCookies([])

# Custom NetworkAccessManager class with support for ad-blocking.
class NetworkAccessManager(QNetworkAccessManager):
    def __init__(self, *args, **kwargs):
        super(NetworkAccessManager, self).__init__(*args, **kwargs)
    def createRequest(self, op, request, device=None):
        url = request.url().toString()
        x = common.adblock_filter.match(url)
        if x != None:
            return QNetworkAccessManager.createRequest(self, QNetworkAccessManager.GetOperation, QNetworkRequest(QUrl()))
        else:
            return QNetworkAccessManager.createRequest(self, op, request, device)

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
            f.writeData(data)
            f.flush()
            f.close()
            self.progress = [0, 0]
            if sys.platform.startswith("linux"):
                subprocess.Popen(["notify-send", "--icon=emblem-downloads", "Download complete: %s" % (self.windowTitle(),)])

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
        abortAction = QAction(QIcon().fromTheme("process-stop", QIcon(common.app_icon("process-stop.png"))), "Abort", self)
        abortAction.triggered.connect(self.progressBar.abort)
        abortAction.triggered.connect(self.deleteLater)
        self.addAction(abortAction)

# Custom WebView class with support for ad-blocking, new tabs, downloads,
# recording history, and more.
class WebView(QWebView):

    # This is used to store references to webViews so that they don't
    # automatically get cleaned up.
    webViews = []

    # Downloads
    downloads = []

    # This is a signal used to inform everyone a new window was created.
    windowCreated = pyqtSignal(QWebView)

    # This is a signal used to tell everyone a download has started.
    downloadStarted = pyqtSignal(QToolBar)

    # Initialize class.
    def __init__(self, *args, incognito=False, **kwargs):
        super(WebView, self).__init__(*args, **kwargs)

        # Add this webview to the list of webviews.
        common.webviews.append(self)

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

        # Create a NetworkAccessmanager that supports ad-blocking and set it.
        self.nAM = NetworkAccessManager()
        self.page().setNetworkAccessManager(self.nAM)

        # Enable Web Inspector
        self.settings().setAttribute(self.settings().DeveloperExtrasEnabled, True)

        self.updateProxy()

        # What to do if private browsing is not enabled.
        if not self.incognito:
            # Set persistent storage path to settings_folder.
            self.settings().enablePersistentStorage(common.settings_folder)

            # Set the CookieJar.
            self.page().networkAccessManager().setCookieJar(common.cookieJar)

            # Do this so that cookieJar doesn't get deleted along with WebView.
            common.cookieJar.setParent(QCoreApplication.instance())

            # Forward unsupported content.
            # Since this uses Google's servers, it is disabled in
            # private browsing mode.
            self.page().setForwardUnsupportedContent(True)
            self.page().unsupportedContent.connect(self.handleUnsupportedContent)

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

        # Enable Netscape plugins.
        self.settings().setAttribute(self.settings().PluginsEnabled, True)

        # This is what Nimbus should do when faced with a file to download.
        self.page().downloadRequested.connect(self.downloadFile)

        # Connect signals.
        self.titleChanged.connect(self.setWindowTitle)
        self.iconChanged.connect(self.setWindowIcon)
        self.page().linkHovered.connect(self.setStatusBarMessage)
        self.statusBarMessage.connect(self.setStatusBarMessage)
        self.loadProgress.connect(self.setLoadProgress)

        # PyQt4 doesn't support <audio> and <video> tags on Windows.
        # This is a little hack to work around it.
        if sys.platform.startswith("win"):
            self.loadFinished.connect(self.replaceAVTags)

        self.setWindowTitle("")

    # Method to replace all <audio> and <video> tags with <embed> tags.
    def replaceAVTags(self):
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
            title = "New Tab"
        QWebView.setWindowTitle(self, title)

    def icon(self):
        if self.incognito:
            return common.complete_icon("face-devilish")
        return QWebView.icon(self)

    # Function to update proxy list.
    def updateProxy(self):
        proxyType = str(common.settings.value("proxy/type"))
        if proxyType == "None":
            proxyType = "No"
        port = common.settings.value("proxy/port")
        if port == None:
            port = common.default_port
        user = str(common.settings.value("proxy/user"))
        if user == "":
            user = None
        password = str(common.settings.value("proxy/password"))
        if password == "":
            password = None
        self.page().networkAccessManager().setProxy(QNetworkProxy(eval("QNetworkProxy." + proxyType + "Proxy"), str(common.settings.value("proxy/hostname")), int(port), user, password))

    # Handler for unsupported content.
    def handleUnsupportedContent(self, reply):
        url = reply.url().toString()

        if not "file://" in url: # Make sure the file isn't local.
            
            # Check to see if the file can be loaded in Google Docs viewer.
            for extension in gdocs_extensions:
                if url.lower().endswith(extension):
                    self.load(QUrl("https://docs.google.com/viewer?embedded=true&url=" + url))
                    return
        
        self.downloadFile(reply.request())

    # Download file.
    def downloadFile(self, request):

        # Get file name for destination.
        fname = QFileDialog.getSaveFileName(None, "Save As...", os.path.join(os.path.expanduser("~"), request.url().toString().split("/")[-1]), "All files (*)")
        if fname:
            reply = self.page().networkAccessManager().get(request)
            
            # Create a DownloadBar instance and append it to list of
            # downloads.
            downloadDialog = DownloadBar(reply, fname, None)
            self.downloads.append(downloadDialog)

            # Emit signal.
            self.downloadStarted.emit(downloadDialog)

    # Save current page.
    def savePage(self):
        fname = QFileDialog.getSaveFileName(None, "Save As...", os.path.join(os.path.expanduser("~"), self.url().toString().split("/")[-1]), "All files (*)")
        if fname:
            content = self.page().mainFrame().toHtml()
            try: f = open(fname, "w")
            except: pass
            else:
                try: f.write(content)
                except: pass
                f.close()

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
        find = QInputDialog.getText(None, "Find", "Search for:", QLineEdit.Normal, self._findText)
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
    def __init__(self, script="", parent=None):
        super(ExtensionButton, self).__init__(parent)
        common.extension_buttons.append(self)
        self._parent = parent
        self.script = script
    def loadScript(self):
        self._parent.currentWidget().page().mainFrame().evaluateJavaScript(self.script)

# Custom MainWindow class.
# This contains basic navigation controls, a location bar, and a menu.
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Add self to global list of windows.
        common.windows.append(self)

        # Set window icon.
        self.setWindowIcon(common.complete_icon("internet-web-browser"))

        # List of closed tabs.
        self.closedTabs = []

        # Main toolbar.
        self.toolBar = QToolBar(movable=False, contextMenuPolicy=Qt.CustomContextMenu, parent=self)
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
        self.tabs.currentChanged.connect(lambda: self.updateLocationText(self.tabs.currentWidget().url()))

        # Allow closing of tabs.
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.removeTab)

        self.statusBar = status_bar.StatusBar(self)
        self.addToolBar(Qt.BottomToolBarArea, self.statusBar)
        self.addToolBarBreak(Qt.BottomToolBarArea)

        # Set tabs as central widget.
        self.setCentralWidget(self.tabs)

        # New tab action.
        newTabAction = QAction(common.complete_icon("list-add"), "New &Tab", self)
        newTabAction.setShortcut("Ctrl+T")
        newTabAction.triggered.connect(lambda: self.addTab())

        # New private browsing tab action.
        newIncognitoTabAction = QAction(common.complete_icon("face-devilish"), "New &Incognito Tab", self)
        newIncognitoTabAction.setShortcut("Ctrl+Shift+N")
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

        # Start timer.
        self.toggleActionsTimer.start(8)

        # Location bar. Note that this is a combo box.
        self.locationBar = QComboBox(self)

        # Load stored browser history.
        for url in history:
            self.locationBar.addItem(url)

        # Combo boxes are not normally editable by default.
        self.locationBar.setEditable(True)

        # We want the location bar to stretch to fit the toolbar,
        # so we set its size policy to that of a QLineEdit.
        self.locationBar.setSizePolicy(QLineEdit().sizePolicy())

        # Load a page when Enter is pressed.
        self.locationBar.activated.connect(lambda: self.load(self.locationBar.currentText()))

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
        self.extensionBar.setStyleSheet("QToolBar { border: 0; border-right: 1px solid palette(dark); background: transparent; }")
        self.addToolBar(Qt.LeftToolBarArea, self.extensionBar)
        self.extensionBar.hide()

        # Main menu.
        mainMenu = QMenu(self)

        # Add new tab actions to menu.
        mainMenu.addAction(newTabAction)
        mainMenu.addAction(newIncognitoTabAction)

        # Add new window action.
        newWindowAction = QAction(common.complete_icon("window-new"), "&New Window", self)
        newWindowAction.setShortcut("Ctrl+N")
        newWindowAction.triggered.connect(self.addWindow)
        mainMenu.addAction(newWindowAction)

        # Add reopen tab action.
        reopenTabAction = QAction(common.complete_icon("edit-undo"), "&Reopen Tab", self)
        reopenTabAction.setShortcut("Ctrl+Shift+T")
        reopenTabAction.triggered.connect(self.reopenTab)
        self.addAction(reopenTabAction)
        mainMenu.addAction(reopenTabAction)

        mainMenu.addSeparator()

        # Save page action.
        savePageAction = QAction(common.complete_icon("document-save-as"), "Save Page &As...", self)
        savePageAction.setShortcut("Ctrl+S")
        savePageAction.triggered.connect(lambda: self.tabs.currentWidget().savePage())
        mainMenu.addAction(savePageAction)

        mainMenu.addSeparator()

        # Add find text action.
        findAction = QAction(common.complete_icon("edit-find"), "&Find...", self)
        findAction.setShortcut("Ctrl+F")
        findAction.triggered.connect(self.find)
        mainMenu.addAction(findAction)

        # Add find next action.
        findNextAction = QAction(common.complete_icon("media-seek-forward"), "Find Ne&xt", self)
        findNextAction.setShortcut("Ctrl+G")
        findNextAction.triggered.connect(self.findNext)
        mainMenu.addAction(findNextAction)

        # Add find previous action.
        findPreviousAction = QAction(common.complete_icon("media-seek-backward"), "Find Pre&vious", self)
        findPreviousAction.setShortcut("Ctrl+Shift+G")
        findPreviousAction.triggered.connect(self.findPrevious)
        mainMenu.addAction(findPreviousAction)

        mainMenu.addSeparator()

        # Add print preview action.
        printPreviewAction = QAction(common.complete_icon("document-print-preview"), "Print Previe&w", self)
        printPreviewAction.setShortcut("Ctrl+Shift+P")
        printPreviewAction.triggered.connect(self.printPreview)
        mainMenu.addAction(printPreviewAction)

        # Add print page action.
        printAction = QAction(common.complete_icon("document-print"), "&Print...", self)
        printAction.setShortcut("Ctrl+P")
        printAction.triggered.connect(self.printPage)
        mainMenu.addAction(printAction)

        # Add separator.
        mainMenu.addSeparator()

        # Add clear history action.
        clearHistoryAction = QAction(common.complete_icon("edit-clear"), "&Clear Recent History...", self)
        clearHistoryAction.setShortcut("Ctrl+Shift+Del")
        clearHistoryAction.triggered.connect(clearHistory)
        mainMenu.addAction(clearHistoryAction)

        # Add settings dialog action.
        settingsAction = QAction(common.complete_icon("preferences-system"), "&Settings...", self)
        settingsAction.setShortcuts(["Ctrl+,", "Ctrl+Alt+P"])
        settingsAction.triggered.connect(lambda: self.tabs.addTab(pdialog, "Settings"))
        settingsAction.triggered.connect(lambda: self.tabs.setCurrentIndex(self.tabs.count()-1))
        mainMenu.addAction(settingsAction)

        # Add main menu action/button.
        self.mainMenuAction = QAction(common.complete_icon("document-properties"), "&Menu", self)
        self.mainMenuAction.setShortcuts(["Alt+M", "Alt+F"])
        self.mainMenuAction.setMenu(mainMenu)
        self.toolBar.addAction(self.mainMenuAction)
        self.toolBar.widgetForAction(self.mainMenuAction).setPopupMode(QToolButton.InstantPopup)
        self.mainMenuAction.triggered.connect(lambda: self.toolBar.widgetForAction(self.mainMenuAction).showMenu())

        # Load browser extensions.
        # Ripped off of Ricotta.
        self.reloadExtensions()

    def reloadExtensions(self):

        # Hide extensions toolbar if there aren't any extensions.
        if len(common.settings.value("extensions/whitelist")) == 0:
            self.extensionBar.hide()
            return

        for extension in common.extensions:
            if extension not in common.settings.value("extensions/whitelist"):
                continue
            extension_path = os.path.join(common.extensions_folder, extension)
            if os.path.isdir(extension_path):
                script_path = os.path.join(extension_path, "script.js")
                icon_path = os.path.join(extension_path, "icon.png")
                if os.path.isfile(script_path):
                    f = open(script_path, "r")
                    script = copy.copy(f.read())
                    f.close()
                    newExtension = ExtensionButton(script, self)
                    newExtension.setToolTip(extension.title())
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

            self.reloadAction.setEnabled(self.tabs.currentWidget().pageAction(QWebPage.Reload).isEnabled())
        except:
            self.backAction.setEnabled(False)
            self.forwardAction.setEnabled(False)
            self.stopAction.setEnabled(False)
            self.reloadAction.setEnabled(False)

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

    # Method to load a URL.
    def load(self, url=False):
        if not url:
            url = self.locationBar.currentText()
        if "." in url or ":" in url:
            self.tabs.currentWidget().load(QUrl.fromUserInput(url))
        else:
            self.tabs.currentWidget().load(QUrl(common.settings.value("search") % (url,)))

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

    def addWindow(self):
        win = MainWindow()
        win.addTab(url="about:blank")
        win.show()

    def addTab(self, webView=None, **kwargs):
        # If a URL is specified, load it.
        if "incognito" in kwargs:
            webview = WebView(incognito=True, parent=self)
            if "url" in kwargs:
                webview.load(QUrl.fromUserInput(kwargs["url"]))

        elif "url" in kwargs:
            url = kwargs["url"]
            webview = WebView(self)
            webview.load(QUrl.fromUserInput(url))

        # If a WebView object is specified, use it.
        elif webView != None:
            webview = webView

        # If nothing is specified, use a blank WebView.
        else:
            webview = WebView(self)

        # Connect signals
        webview.loadProgress.connect(self.setProgress)
        webview.statusBarMessage.connect(self.setStatusBarMessage)
        webview.page().linkHovered.connect(self.setStatusBarMessage)
        webview.titleChanged.connect(self.updateTabTitles)
        webview.urlChanged.connect(self.updateLocationText)
        webview.iconChanged.connect(self.updateTabIcons)
        webview.windowCreated.connect(self.addTab)
        webview.downloadStarted.connect(self.addDownloadToolBar)

        # Add tab
        self.tabs.addTab(webview, "New Tab")

        # Switch to new tab
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
                self.setWindowTitle(title + " - Nimbus")

    def updateTabIcons(self):
        for index in range(0, self.tabs.count()):
            try: icon = self.tabs.widget(index).icon()
            except: continue
            self.tabs.setTabIcon(index, icon)

    def removeTab(self, index):
        try:
            if self.tabs.widget(index).history().canGoBack() or self.tabs.widget(index).history().canGoForward() or self.tabs.widget(index).url().toString() not in ("about:blank", ""):
                self.closedTabs.append(self.tabs.widget(index))
            self.tabs.widget(index).load(QUrl("about:blank"))
        except:
            pass
        self.tabs.removeTab(index)
        if self.tabs.count() == 0:
            self.close()

    def reopenTab(self):
        if len(self.closedTabs) > 0:
            self.addTab(self.closedTabs.pop())
            try: self.tabs.widget(self.tabs.count() - 1).back()
            except: pass

    # This method is used to add a DownloadBar to the window.
    def addDownloadToolBar(self, toolbar):
        self.statusBar.addToolBar(toolbar)

    # Method to update the location bar text.
    def updateLocationText(self, url):
        currentUrl = self.tabs.currentWidget().url()
        if url == currentUrl:
            self.locationBar.setEditText(currentUrl.toString())

# Main function to load everything.
def main():

    # Create app.
    app = QApplication(sys.argv)

    # Load adblock rules.
    adblock_filter_loader.start()

    # Start extension server.
    server_thread.start()

    # On quit, save settings.
    app.aboutToQuit.connect(saveSettings)

    # Load settings.
    loadSettings()

    # Create instance of MainWindow.
    win = MainWindow()

    # Create instance of SettingsDialog.
    global pdialog
    pdialog = settings_dialog.SettingsDialog()

    # Open URLs from command line.
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if "." in arg or ":" in arg:
                win.addTab(url=arg)

    # If there aren't any tabs, open homepages.
    if win.tabs.count() == 0:
        win.addTab(url=common.settings.value("homepage"))
    if win.tabs.count() == 0:
        win.addTab(url="about:blank")

    # Show window.
    win.show()

    # Start app.
    app.exec_()

# Start program
if __name__ == "__main__":
    main()
