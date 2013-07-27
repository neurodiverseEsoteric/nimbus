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
from PyQt4.QtCore import Qt, QSettings, QCoreApplication, pyqtSignal, QUrl, QByteArray
from PyQt4.QtGui import QApplication, QIcon, QAction, QMainWindow, QToolBar, QComboBox, QLineEdit, QTabWidget
from PyQt4.QtNetwork import QNetworkCookieJar, QNetworkCookie, QNetworkAccessManager, QNetworkRequest
from PyQt4.QtWebKit import QWebView

# The folder that the app is stored in/
app_folder = os.path.dirname(os.path.realpath(__file__))
os.chdir(app_folder)

# Create a global settings manager.
settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "nimbus", "config", QCoreApplication.instance())

# This is a convenient variable for getting the settings folder.
settings_folder = os.path.dirname(settings.fileName())

# AdBlock rules loading.
adblock_folder = os.path.join(settings_folder, "adblock")
easylist = os.path.join(app_folder, "easylist.txt")
adblock_rules = []

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
    if not url in history and len(url) < 129:
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

# Custom WebView class with support for ad-blocking, new tabs, and
# recording history.
class WebView(QWebView):
    webViews = []
    windowCreated = pyqtSignal(QWebView)
    def __init__(self, *args, **kwargs):
        super(WebView, self).__init__(*args, **kwargs)
        self.settings().enablePersistentStorage(settings_folder)
        
        # Create a NetworkAccessmanager that supports ad-blocking and set it.
        self.nAM = NetworkAccessManager()
        self.page().setNetworkAccessManager(self.nAM)
        
        # Set the CookieJar
        self.page().networkAccessManager().setCookieJar(cookieJar)
        
        # Do this so that cookieJar doesn't die when WebView is deleted.
        cookieJar.setParent(QCoreApplication.instance())
        
        self.settings().setAttribute(self.settings().PluginsEnabled, True)
        self.titleChanged.connect(self.setWindowTitle)
        self.urlChanged.connect(self.addHistoryItem)
    def addHistoryItem(self, url):
        addHistoryItem(url.toString())
    def createWindow(self, type):
        webview = WebView(self.parent())
        self.webViews.append(webview)
        self.windowCreated.emit(webview)
        return webview

# Custom MainWindow class.
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.toolBar = QToolBar(movable=False, contextMenuPolicy=Qt.CustomContextMenu, parent=self)
        self.addToolBar(self.toolBar)
                
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
        
        # Tab widget
        self.tabs = QTabWidget(self)
        self.tabs.setDocumentMode(True)
        self.tabs.currentChanged.connect(self.updateTabTitles)
        self.tabs.currentChanged.connect(lambda: self.updateLocationText(self.tabs.currentWidget().url()))
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.removeTab)
        self.setCentralWidget(self.tabs)
        
        # New tab button
        newTabAction = QAction(QIcon().fromTheme("list-add"), "New Tab", self)
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
    
    # Load a URL
    def load(self, url=False):
        if not url:
            url = self.locationBar.currentText()
        self.tabs.currentWidget().load(QUrl.fromUserInput(url))
    
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
        
        # Add tab
        self.tabs.addTab(webview, "New Tab")
        
        # Switch to new tab
        self.tabs.setCurrentIndex(self.tabs.count()-1)
        
        # Update icons so we see the globe icon on new tabs.
        self.updateTabIcons()
    
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
            win.addTab(url=arg)
    else:
        win.addTab(url="duckduckgo.com")
    win.show()
    app.exec_()

# 
if __name__ == "__main__":
    main()
