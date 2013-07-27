#! /usr/bin/env python3

# Import everything we need.
import sys
import os
try:
    from abpy import Filter
except:
    class Filter(object):
        def __init__(self, rules):
            super(Filter, self).__init__()
        def match(self, url):
            return None
from PyQt4.QtCore import Qt, QSettings, QCoreApplication, pyqtSignal, QUrl, QByteArray, QFile, QIODevice
from PyQt4.QtGui import QApplication, QIcon, QMenu, QAction, QMainWindow, QToolBar, QToolButton, QComboBox, QLineEdit, QTabWidget, QPrinter, QPrintDialog, QPrintPreviewDialog, QInputDialog, QFileDialog, QProgressBar, QLabel
from PyQt4.QtNetwork import QNetworkCookieJar, QNetworkCookie, QNetworkAccessManager, QNetworkRequest
from PyQt4.QtWebKit import QWebView, QWebPage

# The folder that the app is stored in/
app_folder = os.path.dirname(os.path.realpath(__file__))
os.chdir(app_folder)

# Create a global settings manager.
settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "nimbus", "config", QCoreApplication.instance())

# This is a convenient variable for getting the settings folder.
settings_folder = os.path.dirname(settings.fileName())

# Adblock rules loading.
adblock_folder = os.path.join(settings_folder, "adblock")
easylist = os.path.join(app_folder, "easylist.txt")
adblock_rules = []

no_adblock = "--no-adblock" in sys.argv

# Load Adblock filters if Adblock is not disabled
if not no_adblock:
    # Load default easylist.
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

# Create filter.
adblock_filter = Filter(adblock_rules)

# Global cookiejar to store cookies.
cookieJar = QNetworkCookieJar(QCoreApplication.instance())

# Global list to store browser history.
history = []

# Add an item to the browser history.
def addHistoryItem(url):
    global history
    if not url in history and len(url) < 84:
        history.append(url)

def saveSettings():
    # Save cookies
    cookies = [cookie.toRawForm().data() for cookie in cookieJar.allCookies()]
    settings.setValue("cookies", cookies)

    # Save history
    settings.setValue("history", history)

    settings.sync()

def loadSettings():
    # Load history
    global history
    raw_history = settings.value("history")
    if type(raw_history) is list:
        history = settings.value("history")
    
    # Load cookies
    raw_cookies = settings.value("cookies")
    if type(raw_cookies) is list:
        cookies = [QNetworkCookie().parseCookies(QByteArray(cookie))[0] for cookie in raw_cookies]
        cookieJar.setAllCookies(cookies)

# Custom NetworkAccessManager class with support for ad-blocking.
class NetworkAccessManager(QNetworkAccessManager):
    def __init__(self, *args, **kwargs):
        super(NetworkAccessManager, self).__init__(*args, **kwargs)
    def createRequest(self, op, request, device=None):
        url = request.url().toString()
        x = adblock_filter.match(url)
        if x != None:
            return QNetworkAccessManager.createRequest(self, QNetworkAccessManager.GetOperation, QNetworkRequest(QUrl()))
        else:
            return QNetworkAccessManager.createRequest(self, op, request, device)

# Download progress bar
# Ripped off of Ryouko.
class DownloadProgressBar(QProgressBar):
    
    # Initialize
    def __init__(self, reply=False, destination=os.path.expanduser("~"), parent=None):
        super(DownloadProgressBar, self).__init__(parent)
        self.setWindowTitle(reply.request().url().toString().split("/")[-1])
        self.networkReply = reply
        self.destination = destination
        self.progress = [0, 0]
        if self.networkReply:
            self.networkReply.downloadProgress.connect(self.updateProgress)
            self.networkReply.finished.connect(self.finishDownload)
    
    # Finish download
    def finishDownload(self):
        if self.networkReply.isFinished():
            data = self.networkReply.readAll()
            f = QFile(self.destination)
            f.open(QIODevice.WriteOnly)
            f.writeData(data)
            f.flush()
            f.close()
            self.progress = [0, 0]

    # Update progress
    def updateProgress(self, received, total):
        self.setMaximum(total)
        self.setValue(received)
        self.progress[0] = received
        self.progress[1] = total
        self.show()

    # Abort download
    def abort(self):
        self.networkReply.abort()

# File download dialog
class DownloadBar(QToolBar):
    def __init__(self, reply, destination, parent=None):
        super(DownloadBar, self).__init__(parent)
        self.setMovable(False)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setStyleSheet("QToolBar { border: 0; background: palette(window); }")
        label = QLabel(self)
        self.addWidget(label)
        self.progressBar = DownloadProgressBar(reply, destination, self)
        self.progressBar.networkReply.finished.connect(self.close)
        self.progressBar.networkReply.finished.connect(self.deleteLater)
        self.addWidget(self.progressBar)
        label.setText(os.path.split(self.progressBar.destination)[1])
        abortAction = QAction(QIcon().fromTheme("process-stop"), "Abort", self)
        abortAction.triggered.connect(self.progressBar.abort)
        abortAction.triggered.connect(self.deleteLater)
        self.addAction(abortAction)

# Custom WebView class with support for ad-blocking, new tabs, and
# recording history.
class WebView(QWebView):
    
    # This is used to store references to webViews so that they don't
    # automatically get cleaned up.
    webViews = []
    
    # Downloads
    downloads = []
    
    # This is a signal used to inform everyone a new window was created.
    windowCreated = pyqtSignal(QWebView)
    downloadStarted = pyqtSignal(QToolBar)
    
    # Init.
    def __init__(self, *args, **kwargs):
        super(WebView, self).__init__(*args, **kwargs)
        
        # Persistant storage should be set to settings_folder
        self.settings().enablePersistentStorage(settings_folder)
        
        # This is used to store the text entered in using WebView.find()
        self._findText = False
        
        # Create a NetworkAccessmanager that supports ad-blocking and set it.
        self.nAM = NetworkAccessManager()
        self.page().setNetworkAccessManager(self.nAM)
        
        # Set the CookieJar
        self.page().networkAccessManager().setCookieJar(cookieJar)
        
        # Do this so that cookieJar doesn't die when WebView is deleted.
        cookieJar.setParent(QCoreApplication.instance())
        
        # Enable plugins.
        self.settings().setAttribute(self.settings().PluginsEnabled, True)
        
        # Forward unsupported content
        self.page().setForwardUnsupportedContent(True)
        self.page().unsupportedContent.connect(self.handleUnsupportedContent)
        self.page().downloadRequested.connect(self.downloadFile)
        
        # Connect signals.
        self.titleChanged.connect(self.setWindowTitle)
        self.urlChanged.connect(self.addHistoryItem)

    # Handle unsupported content
    def handleUnsupportedContent(self, reply):
        url = reply.url().toString()
        if not "file://" in url:
            for extension in (".doc", ".pdf", ".ps", ".gz"):
                if url.lower().endswith(extension):
                    self.load(QUrl("http://view.samurajdata.se/ps.php?url=" + url + "&submit=View!"))
                    return
        self.downloadFile(reply.request())

    # Download file
    def downloadFile(self, request):
        fname = QFileDialog.getSaveFileName(None, "Save As...", os.path.join(os.path.expanduser("~"), request.url().toString().split("/")[-1]), "All files (*)")
        if fname:
            reply = self.page().networkAccessManager().get(request)
            downloadDialog = DownloadBar(reply, fname, None)
            self.downloads.append(downloadDialog)
            self.downloadStarted.emit(downloadDialog)

    # Add history item to the browser history.
    def addHistoryItem(self, url):
        addHistoryItem(url.toString())
    
    # Redefine createWindow. Emits windowCreated signal for convenience.
    def createWindow(self, type):
        webview = WebView(self.parent())
        self.webViews.append(webview)
        self.windowCreated.emit(webview)
        return webview

    # Find text
    def find(self):
        if type(self._findText) is not str:
            self._findText = ""
        find = QInputDialog.getText(None, "Find", "Search for:", QLineEdit.Normal, self._findText)
        if find:
            self._findText = find[0]
        else:
            self._findText = ""
        self.findText(self._findText, QWebPage.FindWrapsAroundDocument)

    # Find next instance of text
    def findNext(self):
        if not self._findText:
            self.find()
        else:
            self.findText(self._findText, QWebPage.FindWrapsAroundDocument)

    # Find previous instance of text
    def findPrevious(self):
        if not self._findText:
            self.find()
        else:
            self.findText(self._findText, QWebPage.FindWrapsAroundDocument | QWebPage.FindBackward)

    # Print page.
    def printPage(self):
        printer = QPrinter()
        self.page().mainFrame().render(printer.paintEngine().painter())
        printDialog = QPrintDialog(printer)
        printDialog.open()
        printDialog.accepted.connect(lambda: self.print(printer))
        printDialog.exec_()

    # Show print preview dialog.
    def printPreview(self):
        printer = QPrinter()
        self.page().mainFrame().render(printer.paintEngine().painter())
        printDialog = QPrintPreviewDialog(printer, self)
        printDialog.paintRequested.connect(lambda: self.print(printer))
        printDialog.exec_()
        printDialog.deleteLater()

# Custom MainWindow class.
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        # Main toolbar
        self.toolBar = QToolBar(movable=False, contextMenuPolicy=Qt.CustomContextMenu, parent=self)
        self.addToolBar(self.toolBar)

        # Tab widget
        self.tabs = QTabWidget(self)
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(True)
        self.tabs.currentChanged.connect(self.updateTabTitles)
        self.tabs.currentChanged.connect(lambda: self.updateLocationText(self.tabs.currentWidget().url()))
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.removeTab)
        self.setCentralWidget(self.tabs)
        
        # New tab button
        newTabAction = QAction(QIcon().fromTheme("list-add"), "New &Tab", self)
        newTabAction.setShortcut("Ctrl+T")
        newTabAction.triggered.connect(lambda: self.addTab())
        newTabToolBar = QToolBar(movable=False, contextMenuPolicy=Qt.CustomContextMenu, parent=self)
        newTabToolBar.setStyleSheet("QToolBar { border: 0; background: transparent; }")
        newTabToolBar.addAction(newTabAction)
        self.tabs.setCornerWidget(newTabToolBar, Qt.TopRightCorner)
        
        # Remove tab action
        removeTabAction = QAction(self)
        removeTabAction.setShortcut("Ctrl+W")
        removeTabAction.triggered.connect(lambda: self.removeTab(self.tabs.currentIndex()))
        self.addAction(removeTabAction)

        # Back button
        backAction = QAction(QIcon().fromTheme("go-previous"), "Back", self)
        backAction.setShortcut("Alt+Left")
        backAction.triggered.connect(self.back)
        self.toolBar.addAction(backAction)
        
        # Forward button
        forwardAction = QAction(QIcon().fromTheme("go-next"), "Forward", self)
        forwardAction.setShortcut("Alt+Right")
        forwardAction.triggered.connect(self.forward)
        self.toolBar.addAction(forwardAction)
        
        # Stop button
        stopAction = QAction(QIcon().fromTheme("process-stop"), "Stop", self)
        stopAction.setShortcuts(["Esc"])
        stopAction.triggered.connect(self.stop)
        self.toolBar.addAction(stopAction)
        
        # Reload button
        reloadAction = QAction(QIcon().fromTheme("view-refresh"), "Reload", self)
        reloadAction.setShortcuts(["F5", "Ctrl+R"])
        reloadAction.triggered.connect(self.reload)
        self.toolBar.addAction(reloadAction)

        # Location bar
        self.locationBar = QComboBox(self)
        for url in history:
            self.locationBar.addItem(url)
        self.locationBar.setEditable(True)
        self.locationBar.setSizePolicy(QLineEdit().sizePolicy())
        self.locationBar.activated.connect(lambda: self.load(self.locationBar.currentText()))
        self.toolBar.addWidget(self.locationBar)
        
        # Focus location bar action
        locationAction = QAction(self)
        locationAction.setShortcuts(["Ctrl+L", "Alt+D"])
        locationAction.triggered.connect(self.locationBar.setFocus)
        locationAction.triggered.connect(self.locationBar.lineEdit().selectAll)
        self.addAction(locationAction)

        # Main menu
        mainMenu = QMenu(self)

        # Add new tab action
        mainMenu.addAction(newTabAction)
        
        # Add separator to menu
        mainMenu.addSeparator()

        # Find text action
        findAction = QAction("&Find...", self)
        findAction.setShortcut("Ctrl+F")
        findAction.triggered.connect(self.find)
        mainMenu.addAction(findAction)

        # Find next action
        findNextAction = QAction("Find Ne&xt", self)
        findNextAction.setShortcut("Ctrl+G")
        findNextAction.triggered.connect(self.findNext)
        mainMenu.addAction(findNextAction)

        # Find previous action
        findPreviousAction = QAction("Find Pre&vious", self)
        findPreviousAction.setShortcut("Ctrl+Shift+G")
        findPreviousAction.triggered.connect(self.findPrevious)
        mainMenu.addAction(findPreviousAction)

        # Add separator to menu
        mainMenu.addSeparator()

        # Print preview action
        printPreviewAction = QAction("Print Previe&w", self)
        printPreviewAction.setShortcut("Ctrl+Shift+P")
        printPreviewAction.triggered.connect(self.printPreview)
        mainMenu.addAction(printPreviewAction)

        # Print action
        printAction = QAction("&Print...", self)
        printAction.setShortcut("Ctrl+P")
        printAction.triggered.connect(self.printPage)
        mainMenu.addAction(printAction)

        # Main menu button
        self.mainMenuAction = QAction("&Menu", self)
        self.mainMenuAction.setShortcuts(["Alt+M", "Alt+F", "Alt+E"])
        self.mainMenuAction.setMenu(mainMenu)
        self.toolBar.addAction(self.mainMenuAction)
        self.toolBar.widgetForAction(self.mainMenuAction).setPopupMode(QToolButton.InstantPopup)
        self.mainMenuAction.triggered.connect(lambda: self.toolBar.widgetForAction(self.mainMenuAction).showMenu())
    
    # Go back
    def back(self):
        self.tabs.currentWidget().back()
    
    # Go forward
    def forward(self):
        self.tabs.currentWidget().forward()
    
    # Reload current page
    def reload(self):
        self.tabs.currentWidget().reload()
    
    # Stop loading current page
    def stop(self):
        self.tabs.currentWidget().stop()

    # Find text
    def find(self):
        self.tabs.currentWidget().find()

    # Find next instance of text
    def findNext(self):
        self.tabs.currentWidget().findNext()

    # Find previous instance of text
    def findPrevious(self):
        self.tabs.currentWidget().findPrevious()

    # Print current page
    def printPage(self):
        self.tabs.currentWidget().printPage()

    # Print current page
    def printPreview(self):
        self.tabs.currentWidget().printPreview()

    # Load a URL
    def load(self, url=False):
        if not url:
            url = self.locationBar.currentText()
        if "." in url or ":" in url:
            self.tabs.currentWidget().load(QUrl.fromUserInput(url))
        else:
            self.tabs.currentWidget().load(QUrl("https://duckduckgo.com/?q=" + url))
    
    # Add a tab
    def addTab(self, webView=None, **kwargs):
        # If a URL is specified, load it.
        if "url" in kwargs:
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
    
    # Add download toolbar
    def addDownloadToolBar(self, toolbar):
        self.addToolBar(Qt.BottomToolBarArea, toolbar)
    
    # Update location bar text.
    def updateLocationText(self, url):
        currentUrl = self.tabs.currentWidget().url()
        if url == currentUrl:
            self.locationBar.setEditText(currentUrl.toString())
    
    # Update tab titles.
    def updateTabTitles(self):
        for index in range(0, self.tabs.count()):
            title = self.tabs.widget(index).windowTitle()
            if len(title) == 0:
                title = "New Tab"
            self.tabs.setTabText(index, title[:24] + '...' if len(title) > 24 else title)
            if index == self.tabs.currentIndex():
                self.setWindowTitle(self.tabs.currentWidget().windowTitle())
    
    # Update tab icons.
    def updateTabIcons(self):
        for index in range(0, self.tabs.count()):
            icon = self.tabs.widget(index).icon()
            self.tabs.setTabIcon(index, icon)
            if index == self.tabs.currentIndex():
                self.setWindowIcon(self.tabs.widget(index).icon())
                
    # Remove a tab.
    def removeTab(self, index):
        self.tabs.widget(index).load(QUrl("about:blank"))
        self.tabs.removeTab(index)
        if self.tabs.count() == 0:
            if len(sys.argv) > 1:
                self.addTab(url=sys.argv[-1])
            else:
                self.addTab(url="duckduckgo.com")

# Main function to load everything.
def main():
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(saveSettings)
    loadSettings()
    win = MainWindow()
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if "." in arg or ":" in arg:
                win.addTab(url=arg)
    if win.tabs.count() == 0:
        win.addTab(url="about:blank")
    win.show()
    app.exec_()

# 
if __name__ == "__main__":
    main()
