#! /usr/bin/env python3

# -------------
# mainwindow.py
# -------------
# Author:      Daniel Sim (foxhead128)
# License:     See LICENSE.md for more details.
# Description: Contains the main browser window interface.

# Import everything we need.
import os
import json
import copy
import common
import browser
import translate
from translate import tr
import custom_widgets
import settings
import status_bar
import data
from nwebkit import *
import traceback

# Extremely specific imports from PyQt5/PySide.
# We give PyQt5 priority because it supports Qt5.
try:
    from PyQt5.QtCore import Qt, QCoreApplication, QUrl, QTimer, QSize,\
                             QDateTime
    from PyQt5.QtGui import QKeySequence, QIcon
    from PyQt5.QtWidgets import QApplication, QDockWidget, QWidget, QHBoxLayout,\
                            QVBoxLayout,\
                            QMessageBox, QSizePolicy,\
                            QMenu, QAction, QMainWindow, QToolBar,\
                            QToolButton, QComboBox, QButtonGroup,\
                            QLabel
    from PyQt5.QtNetwork import QNetworkRequest
    from PyQt5.QtWebKitWidgets import QWebPage
except:
    try:
        from PyQt4.QtCore import Qt, QCoreApplication, QUrl, QTimer, QSize,\
                                 QDateTime
        from PyQt4.QtGui import QApplication, QDockWidget, QWidget, QHBoxLayout,\
                                QVBoxLayout,\
                                QKeySequence, QMessageBox, QSizePolicy, QIcon,\
                                QMenu, QAction, QMainWindow, QToolBar,\
                                QToolButton, QComboBox, QButtonGroup,\
                                QLabel
        from PyQt4.QtNetwork import QNetworkRequest
        from PyQt4.QtWebKit import QWebPage
    except:
        from PySide.QtCore import Qt, QCoreApplication, QUrl, QTimer, QSize,\
                                  QDateTime
        from PySide.QtGui import QApplication, QDockWidget, QWidget,\
                                 QVBoxLayout,\
                                 QHBoxLayout, QKeySequence, QMessageBox,\
                                 QSizePolicy, QIcon, QMenu, QAction,\
                                 QMainWindow, QToolBar, QToolButton, QComboBox,\
                                 QButtonGroup, QLabel
        from PySide.QtNetwork import QNetworkRequest
        from PySide.QtWebKit import QWebPage

tabbar_stylesheet = \
"""QTabBar { margin: 0; padding: 0; border-bottom: 0; }
   QTabBar::tab { border: 1px solid palette(dark);
                  border-%s: 0; margin: 0; padding: 4px;
                  background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 palette(window),
                                              stop: 1 palette(dark)); }
   QTabBar::tab:selected { background: qlineargradient(x1: 0, y1: 0,
                                                       x2: 0, y2: 1,
                                       stop: 0 palette(light),
                                       stop: 1 palette(window)); }"""

# Extension button class.
class ExtensionButton(QToolButton):
    def __init__(self, name=None, script="", etype="python", shortcut=None, parent=None):
        super(ExtensionButton, self).__init__(parent)
        self.name = "new-extension"
        if name:
            self.name = name
        if shortcut:
            self.setShortcut(QKeySequence.fromString(shortcut))
        self.etype = etype
        settings.extension_buttons.append(self)
        self._parent = parent
        self.script = script
    def parentWindow(self):
        return self._parent
    def loadScript(self):
        if self.etype == "python":
            try: exec(self.script)
            except:
                QMessageBox.information(self, tr("Error"), traceback.format_exc())
        else:
            self._parent.currentWidget().page().mainFrame().\
            evaluateJavaScript(self.script)

# Custom MainWindow class.
# This contains basic navigation controls, a location bar, and a menu.
class MainWindow(QMainWindow):
    def __init__(self, appMode=False, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # These are used to store where the mouse pressed down.
        # This is used in a hack to drag the window by the toolbar.
        self.mouseX = False
        self.mouseY = False
        
        self.appMode = bool(appMode)
        
        #self.setStyleSheet("* { font-family: Liberation Sans, sans; }")

        # Add self to global list of windows.
        browser.windows.append(self)

        # Set window icon.
        self.setWindowIcon(common.app_icon)

        # List of closed tabs.
        self.closedTabs = []

        # Extension list
        self._extensions = []

        # Stores whether the browser was maximized.
        self._wasMaximized = False

        # List of sidebars.
        # Sidebars are part of the (incomplete) extensions API.
        self.sideBars = {}


        # Tabs toolbar.
        self.tabsToolBar = custom_widgets.MenuToolBar(movable=False,\
                           contextMenuPolicy=Qt.CustomContextMenu,\
                           parent=self,
                           windowTitle=tr("Tabs"))
        self.addToolBar(self.tabsToolBar)
        self.addToolBarBreak(Qt.TopToolBarArea)

        # Main toolbar.
        self.toolBar = QToolBar(movable=False,\
                                contextMenuPolicy=Qt.CustomContextMenu,\
                                parent=self,
                                windowTitle=tr("Navigation Toolbar"))
        self.addToolBar(self.toolBar)
        if self.appMode:
            self.toolBar.setVisible(False)

        # Tab widget for tabbed browsing.
        self.tabs = custom_widgets.TabWidget(self)

        # Remove border around tabs.
        self.tabs.setDocumentMode(True)

        # Allow rearranging of tabs.
        self.tabs.setMovable(True)

        # Update tab titles and icons when the current tab is changed.
        #self.tabs.currentChanged.connect(self.updateTabTitles)
        self.tabs.currentChanged.connect(self.updateTabIcons)

        # Hacky way of updating the location bar text when the tab is changed.
        self.tabs.currentChanged.connect(self.updateLocationText)
        self.tabs.currentChanged.connect(self.updateLocationIcon)

        # Allow closing of tabs.
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.removeTab)

        self.statusBar = status_bar.StatusBar(self)
        self.statusBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.statusBar.setWindowTitle(tr("Status Bar"))
        self.addToolBar(Qt.BottomToolBarArea, self.statusBar)
        if self.appMode:
            self.statusBar.setVisible(False)
        self.addToolBarBreak(Qt.BottomToolBarArea)

        # Extensions toolbar.
        self.extensionBar = self.statusBar.widgetToolBar

        # Set tabs as central widget.
        self.setCentralWidget(self.tabs)

        self.tabsWidget = QWidget(self)
        tabsLayout = QHBoxLayout(self.tabsWidget)
        self.tabsWidget.setLayout(tabsLayout)
        self.tabsToolBar.addWidget(self.tabsWidget)
        self.tabsWidget.layout().setSpacing(0)
        self.tabsWidget.layout().setContentsMargins(0,0,0,0)
        self.tabsWidget.layout().addWidget(self.tabs.tabBar())
        self.tabs.tabBar().setExpanding(False)
        self.tabsToolBar.layout().setSpacing(0)
        self.tabsToolBar.layout().setContentsMargins(0,0,0,0)
        self.tabsToolBar.setStyleSheet("QToolBar { padding: 0; margin: 0; }")
        self.tabs.tabBar().setStyleSheet(tabbar_stylesheet % ("left" if self.layoutDirection() == Qt.LeftToRight else "right",))

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
        #newTabToolBar = QToolBar(movable=False, contextMenuPolicy=Qt.CustomContextMenu, parent=self)
        self.tabsToolBar.setIconSize(QSize(16, 16))

        # We don't want this widget to have any decorations.
        #newTabToolBar.setStyleSheet(common.blank_toolbar)

        self.tabsToolBar.addAction(newTabAction)

        self.tabsToolBar.addWidget(custom_widgets.HorizontalExpander(self.tabsToolBar))

        #self.tabsToolBar.addAction(newIncognitoTabAction)
        #self.tabsToolBar.addWidget(newTabToolBar)
        #self.tabs.setCornerWidget(newTabToolBar, Qt.TopRightCorner)

        tabsMenuAction = QAction(self)
        self.tabsToolBar.addAction(tabsMenuAction)
        self.tabsToolBar.widgetForAction(tabsMenuAction).setPopupMode(QToolButton.InstantPopup)
        self.tabsToolBar.widgetForAction(tabsMenuAction).setStyleSheet("QToolButton { max-width: 1em; }")
        #self.tabsToolBar.widgetForAction(tabsMenuAction).setArrowType(Qt.DownArrow)

        self.tabsMenu = QMenu(self)
        self.tabsMenu.aboutToShow.connect(self.aboutToShowTabsMenu)
        tabsMenuAction.setMenu(self.tabsMenu)

        # These are hidden actions used for the Ctrl[+Shift]+Tab feature
        # you see in most browsers.
        nextTabAction = QAction(self, triggered=self.nextTab, shortcut="Ctrl+Tab")
        self.addAction(nextTabAction)

        previousTabAction = QAction(self, triggered=self.previousTab, shortcut="Ctrl+Shift+Tab")
        self.addAction(previousTabAction)

        # This is the Ctrl+W (Close Tab) shortcut.
        removeTabAction = QAction(self, triggered=lambda: self.removeTab(self.tabWidget().currentIndex()), shortcut="Ctrl+W")
        self.addAction(removeTabAction)

        # Dummy webpage used to provide navigation actions that conform to
        # the system's icon theme.
        self.actionsPage = QWebPage(self)

        # Regularly and forcibly enable and disable navigation actions
        # every few milliseconds.
        self.toggleActionsTimer = QTimer(timeout=self.toggleActions, parent=self)
        self.dateTimeTimer = QTimer(timeout=self.updateDateTime, parent=self)

        # Set up navigation actions.
        self.backAction = self.actionsPage.action(QWebPage.Back)
        self.backAction.setShortcut("Alt+Left")
        self.backAction.triggered.connect(self.back)
        self.addAction(self.backAction)
        self.toolBar.addAction(self.backAction)
        self.toolBar.widgetForAction(self.backAction).setPopupMode(QToolButton.MenuButtonPopup)

        # This is a dropdown menu for the back history items, but due to
        # instability, it is currently disabled.
        self.backHistoryMenu = QMenu(aboutToShow=self.aboutToShowBackHistoryMenu, parent=self)
        self.backAction.setMenu(self.backHistoryMenu)

        self.forwardAction = self.actionsPage.action(QWebPage.Forward)
        self.forwardAction.setShortcut("Alt+Right")
        self.forwardAction.triggered.connect(self.forward)
        self.addAction(self.forwardAction)
        self.toolBar.addAction(self.forwardAction)
        self.toolBar.widgetForAction(self.forwardAction).setPopupMode(QToolButton.MenuButtonPopup)

        # This is a dropdown menu for the forward history items, but due to
        # instability, it is currently disabled.
        self.forwardHistoryMenu = QMenu(aboutToShow=self.aboutToShowForwardHistoryMenu, parent=self)
        self.forwardAction.setMenu(self.forwardHistoryMenu)

        self.upAction = QAction(self, triggered=self.up, icon=common.complete_icon("go-up"), text=tr("Go Up"))
        self.addAction(self.upAction)
        self.toolBar.addAction(self.upAction)
        self.toolBar.widgetForAction(self.upAction).setPopupMode(QToolButton.MenuButtonPopup)
        self.upAction.setVisible(False)

        self.upAction2 = QAction(self, triggered=self.up, shortcut="Alt+Up")
        self.addAction(self.upAction2)

        self.upMenu = QMenu(aboutToShow=self.aboutToShowUpMenu, parent=self)
        self.upAction.setMenu(self.upMenu)

        self.nextAction = QAction(self, triggered=self.next, icon=common.complete_icon("media-skip-forward"), text=tr("Go Next"))
        self.addAction(self.nextAction)
        self.toolBar.addAction(self.nextAction)

        self.stopAction = self.actionsPage.action(QWebPage.Stop)
        self.stopAction.triggered.connect(self.stop)
        self.stopAction.triggered.connect(lambda: self.stopAction.setEnabled(True))
        self.stopAction.triggered.connect(lambda: self.reloadAction.setEnabled(True))
        self.addAction(self.stopAction)
        self.toolBar.addAction(self.stopAction)

        self.stopAction2 = QAction(self, triggered=self.toggleFindToolBar, shortcut="Esc")
        self.addAction(self.stopAction2)

        self.reloadAction = self.actionsPage.action(QWebPage.Reload)
        self.reloadAction.triggered.connect(self.reload)
        self.reloadAction.triggered.connect(lambda: self.stopAction.setEnabled(True))
        self.reloadAction.triggered.connect(lambda: self.reloadAction.setEnabled(True))
        self.addAction(self.reloadAction)
        self.toolBar.addAction(self.reloadAction)

        self.reloadAction2 = QAction(self, triggered=self.reload)
        self.reloadAction2.setShortcuts(["F5", "Ctrl+R"])
        self.addAction(self.reloadAction2)

        # Go home button.
        self.homeAction = QAction(self, triggered=self.goHome, icon=common.complete_icon("go-home"), text=tr("Go Home"))
        self.addAction(self.homeAction)
        self.toolBar.addAction(self.homeAction)
        self.homeAction.setVisible(False)

        self.homeAction2 = QAction(self, triggered=self.goHome, shortcut="Alt+Home")
        self.addAction(self.homeAction2)

        # Start timer to forcibly enable and disable navigation actions.
        self.toggleActionsTimer.start(256)
        self.dateTimeTimer.start(500)

        # Location bar. Note that this is a combo box.
        # At some point, I should make a custom location bar
        # implementation that looks nicer.
        self.locationBar = custom_widgets.LocationBar(icon=None, parent=self)

        # Load stored browser history.
        if type(data.history) is list:
            for url in data.history:
                self.locationBar.addItem(url)
        else:
            for url in data.history.keys():
                self.locationBar.addItem(data.shortUrl(url))

        # Combo boxes are not normally editable by default.
        self.locationBar.setEditable(True)

        # We want the location bar to stretch to fit the toolbar,
        # so we set its size policy to expand.
        self.locationBar.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))

        # Load a page when Enter is pressed.
        self.locationBar.lineEdit().returnPressed.connect(lambda: self.load(self.locationBar.lineEdit().text()))
        self.locationBar.lineEdit().textChanged.connect(lambda x: self.tabWidget().currentWidget().setUrlText(x, emit=False))
        self.locationBar.view().activated.connect(lambda index: self.load(index.data()))

        # This is so that the location bar can shrink to a width
        # shorter than the length of its longest item.
        self.locationBar.setStyleSheet("QComboBox { min-width: 6em; }")
        self.toolBar.addWidget(self.locationBar)

        self.feedMenuButton = QAction(common.complete_icon("application-rss+xml"), tr("Feeds"), self)
        self.addAction(self.feedMenuButton)
        self.toolBar.addAction(self.feedMenuButton)
        self.toolBar.widgetForAction(self.feedMenuButton).setPopupMode(QToolButton.InstantPopup)
        self.toolBar.widgetForAction(self.feedMenuButton).setShortcut(QKeySequence.fromString("Ctrl+Alt+R"))
        self.feedMenuButton.setVisible(False)

        self.feedMenu = QMenu(self)
        self.feedMenu.aboutToShow.connect(self.aboutToShowFeedMenu)
        self.feedMenuButton.setMenu(self.feedMenu)

        self.searchEditButton = QAction(common.complete_icon("system-search"), tr("Manage Search Engines"), self)
        self.searchEditButton.setShortcut("Ctrl+K")
        self.searchEditButton.triggered.connect(common.searchEditor.show)
        self.addAction(self.searchEditButton)
        self.toolBar.addAction(self.searchEditButton)

        # Ctrl+L/Alt+D focuses the location bar.
        locationAction = QAction(self)
        locationAction.setShortcuts(["Ctrl+L", "Alt+D"])
        locationAction.triggered.connect(self.locationBar.setFocus)
        locationAction.triggered.connect(self.locationBar.lineEdit().selectAll)
        self.addAction(locationAction)

        self.extensionButtonGroup = QButtonGroup(self)
        self.extensionButtonGroup.setExclusive(True)

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

        # Save page action.
        savePageAction = QAction(common.complete_icon("document-save-as"), tr("Save Page &As..."), self)
        savePageAction.setShortcut("Ctrl+S")
        savePageAction.triggered.connect(lambda: self.tabWidget().currentWidget().downloadFile(QNetworkRequest(self.tabWidget().currentWidget().url())))
        mainMenu.addAction(savePageAction)

        mainMenu.addSeparator()

        viewMenu = QMenu(tr("Vi&ew"), self)
        mainMenu.addMenu(viewMenu)

        # Zoom actions.
        zoomInAction = QAction(common.complete_icon("zoom-in"), tr("Zoom In"), self)
        zoomInAction.triggered.connect(lambda: self.tabs.currentWidget().setZoomFactor(self.tabs.currentWidget().zoomFactor() + 0.1))
        zoomInAction.setShortcuts(["Ctrl+=", "Ctrl++"])
        viewMenu.addAction(zoomInAction)

        zoomOutAction = QAction(common.complete_icon("zoom-out"), tr("Zoom Out"), self)
        zoomOutAction.triggered.connect(lambda: self.tabs.currentWidget().setZoomFactor(self.tabs.currentWidget().zoomFactor() - 0.1))
        zoomOutAction.setShortcut("Ctrl+-")
        viewMenu.addAction(zoomOutAction)

        zoomOriginalAction = QAction(common.complete_icon("zoom-original"), tr("Reset Zoom"), self)
        zoomOriginalAction.triggered.connect(lambda: self.tabs.currentWidget().setZoomFactor(1.0))
        zoomOriginalAction.setShortcut("Ctrl+0")
        viewMenu.addAction(zoomOriginalAction)

        viewMenu.addSeparator()

        # Add separator.
        #self.tabsToolBar.addSeparator()

        # Displays the date and time while in fullscreen mode.
        self.dateTime = QAction(self)
        self.tabsToolBar.addAction(self.dateTime)
        self.tabsToolBar.widgetForAction(self.dateTime).setStyleSheet("QToolButton { font-family: monospace; border-radius: 3px; padding: 2px; background: palette(highlight); color: palette(highlighted-text); }")
        self.dateTime.setVisible(False)

        # Add fullscreen button.
        self.toggleFullScreenButton = QAction(common.complete_icon("view-fullscreen"), tr("Toggle Fullscreen"), self)
        self.toggleFullScreenButton.setCheckable(True)
        self.toggleFullScreenButton.triggered.connect(lambda: self.setFullScreen(not self.isFullScreen()))
        self.tabsToolBar.addAction(self.toggleFullScreenButton)
        self.toggleFullScreenButton.setVisible(False)

        # Add fullscreen action.
        self.toggleFullScreenAction = QAction(common.complete_icon("view-fullscreen"), tr("Toggle Fullscreen"), self)
        self.toggleFullScreenAction.setShortcuts(["F11", "Ctrl+Shift+F"])
        self.toggleFullScreenAction.setCheckable(True)
        self.toggleFullScreenAction.triggered.connect(lambda: self.setFullScreen(not self.isFullScreen()))
        self.addAction(self.toggleFullScreenAction)
        viewMenu.addAction(self.toggleFullScreenAction)

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

        historyMenu = QMenu(tr("&History"), self)
        historyMenu.setIcon(common.complete_icon("office-calendar"))
        mainMenu.addMenu(historyMenu)

        # Add reopen tab action.
        reopenTabAction = QAction(common.complete_icon("edit-undo"), tr("&Reopen Tab"), self)
        reopenTabAction.setShortcut("Ctrl+Shift+T")
        reopenTabAction.triggered.connect(self.reopenTab)
        self.addAction(reopenTabAction)
        historyMenu.addAction(reopenTabAction)

        # Add reopen window action.
        reopenWindowAction = QAction(common.complete_icon("reopen-window"), tr("R&eopen Window"), self)
        reopenWindowAction.setShortcut("Ctrl+Shift+N")
        reopenWindowAction.triggered.connect(self.reopenWindow)
        self.addAction(reopenWindowAction)
        historyMenu.addAction(reopenWindowAction)

        historyMenu.addSeparator()

        # Add clear history action.
        clearHistoryAction = QAction(common.complete_icon("edit-clear"), tr("&Clear Data..."), self)
        clearHistoryAction.setShortcut("Ctrl+Shift+Del")
        clearHistoryAction.triggered.connect(self.clearHistory)
        historyMenu.addAction(clearHistoryAction)

        # Add view source dialog action.
        viewSourceAction = QAction(tr("Page S&ource"), self)
        viewSourceAction.setShortcut("Ctrl+Alt+U")
        viewSourceAction.triggered.connect(lambda: self.tabWidget().currentWidget().viewSource())
        mainMenu.addAction(viewSourceAction)

        # Add settings dialog action.
        settingsAction = QAction(common.complete_icon("preferences-system"), tr("&Settings..."), self)
        settingsAction.setShortcut("Ctrl+,")
        settingsAction.triggered.connect(self.openSettings)
        mainMenu.addAction(settingsAction)

        clippingsAction = QAction(common.complete_icon("edit-paste"), tr("&Manage Clippings..."), self)
        clippingsAction.setShortcut("Ctrl+Shift+M")
        clippingsAction.triggered.connect(self.openClippings)
        mainMenu.addAction(clippingsAction)

        mainMenu.addSeparator()

        # About Qt action.
        aboutQtAction = QAction(common.complete_icon("qt"), tr("About &Qt"), self)
        aboutQtAction.triggered.connect(QApplication.aboutQt)
        mainMenu.addAction(aboutQtAction)

        # About Nimbus action.
        aboutAction = QAction(common.complete_icon("help-about"), tr("A&bout Nimbus"), self)
        aboutAction.triggered.connect(common.trayIcon.about)
        mainMenu.addAction(aboutAction)

        # Licensing information.
        licenseAction = QAction(tr("Credits && &Licensing"), self)
        licenseAction.triggered.connect(common.licenseDialog.show)
        mainMenu.addAction(licenseAction)

        mainMenu.addSeparator()

        # Quit action.
        quitAction = QAction(common.complete_icon("application-exit"),\
                             tr("Quit"), self)
        quitAction.setShortcut("Ctrl+Shift+Q")
        quitAction.triggered.connect(QCoreApplication.quit)
        mainMenu.addAction(quitAction)

        # Add main menu action/button.
        self.mainMenuAction =\
             QAction(tr("&Menu"), self)
        self.mainMenuAction.setShortcuts(["Alt+M", "Alt+F"])
        self.mainMenuAction.setMenu(mainMenu)
        self.addAction(self.mainMenuAction)
        if self.appMode:
            self.tabsToolBar.addSeparator()
            self.tabsToolBar.addAction(self.mainMenuAction)
            self.tabsToolBar.widgetForAction(self.mainMenuAction).\
                setPopupMode(QToolButton.InstantPopup)
        else:
            self.mainMenuAction.setIcon(common.complete_icon("document-properties"))
            self.toolBar.addAction(self.mainMenuAction)
            self.toolBar.widgetForAction(self.mainMenuAction).\
                setPopupMode(QToolButton.InstantPopup)
        self.mainMenuAction.triggered.\
             connect(lambda: (self.tabsToolBar if self.appMode else self.toolBar).\
             widgetForAction(self.mainMenuAction).showMenu())

        self.addToolBarBreak(Qt.TopToolBarArea)

        self.findToolBar = QToolBar(self)
        self.findToolBar.setStyleSheet("QToolBar{background: palette(window); border: 0; border-top: 1px solid palette(dark);}")
        self.findToolBar.setIconSize(QSize(16, 16))
        self.findToolBar.setMovable(False)
        self.findToolBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.addToolBar(Qt.BottomToolBarArea, self.findToolBar)
        self.findToolBar.hide()

        self.findBar = QLineEdit(self.findToolBar)
        self.findBar.returnPressed.connect(self.findEither)

        hideFindToolBarAction = QAction(self)
        hideFindToolBarAction.triggered.connect(self.findToolBar.hide)
        hideFindToolBarAction.setIcon(common.complete_icon("window-close"))

        self.findToolBar.addWidget(self.findBar)
        self.findToolBar.addAction(findPreviousAction)
        self.findToolBar.addAction(findNextAction)
        self.findToolBar.addAction(hideFindToolBarAction)
        
        # This is a dummy sidebar used to
        # dock extension sidebars with.
        # You will never actually see this sidebar.
        self.sideBar = QDockWidget(self)
        self.sideBar.setWindowTitle(tr("Sidebar"))
        self.sideBar.setMaximumWidth(320)
        self.sideBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.sideBar.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget((Qt.LeftDockWidgetArea if self.layoutDirection() == Qt.LeftToRight else Qt.RightDockWidgetArea), self.sideBar)
        self.sideBar.hide()

        # Load browser extensions.
        # Ripped off of Ricotta.
        self.reloadExtensions()
        self.loadStartupExtensions()

        # Tab hotkeys

        for tab in range(0, 8):
            exec("tab%sAction = QAction(self)" % (tab,))
            exec('tab%sAction.setShortcuts(["Ctrl+" + str(%s+1), "Alt+" + str(%s+1)])' % (tab,tab,tab))
            exec("tab%sAction.triggered.connect(lambda: browser.activeWindow().tabWidget().setCurrentIndex(%s))" % (tab,tab))
            exec('self.addAction(tab%sAction)' % (tab,))

        tabNineAction = QAction(self)
        tabNineAction.setShortcuts(["Ctrl+9", "Alt+9"])
        tabNineAction.triggered.connect(lambda: self.tabWidget().setCurrentIndex(self.tabWidget().count()-1))
        self.addAction(tabNineAction)

    # Redefine show function.
    def show(self):
        self.setVisible(True)
        self.tabs.setStyleSheet("QTabWidget::pane { top: -%s; } " %\
             (self.tabs.tabBar().height(),))

    # Returns the tab widget.
    def tabWidget(self):
        return self.tabs

    # Check if window has a sidebar.
    # Part of the extensions API.
    def hasSideBar(self, name):
        if name in self.sideBars.keys():
            return True
        return False

    def getSideBar(self, name):
        if self.hasSideBar(name):
            return self.sideBars[name]
        return None

    # Toggles the sidebar with name name.
    # Part of the extensions API.
    def toggleSideBar(self, name):
        for sidebar in self.sideBars:
            if sidebar != name:
                self.sideBars[sidebar]["sideBar"].setVisible(False)
        if self.hasSideBar(name):
            isVisible = not self.sideBars[name]["sideBar"].isVisible()
            self.sideBars[name]["sideBar"].\
                 setVisible(isVisible)
            if not isVisible:
                self.extensionButtonGroup.setExclusive(False)
                for extension in self._extensions:
                    if extension.isCheckable():
                        extension.setChecked(False)
                self.extensionButtonGroup.setExclusive(True)
            if type(self.sideBars[name]["clip"]) is str:
                clip = self.sideBars[name]["clip"]
                if not clip in self.sideBars[name]["sideBar"].\
                                     webView.url().toString():
                    self.sideBars[name]["sideBar"].\
                         webView.load(self.sideBars[name]["url"])

    # Adds a sidebar.
    # Part of the extensions API.
    def addSideBar(self, name="", url="about:blank", clip=None, ua=None, toolbar=True, script=None, style=None):
        self.sideBars[name] = {"sideBar": QDockWidget(self),\
                               "url": QUrl(url), "clip": clip}
        self.sideBars[name]["sideBar"].setWindowTitle(name)
        self.sideBars[name]["sideBar"].setMaximumWidth(320)
        self.sideBars[name]["sideBar"].\
             setContextMenuPolicy(Qt.CustomContextMenu)
        self.sideBars[name]["sideBar"].\
             setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.sideBars[name]["sideBar"].\
             webView = WebView(self.sideBars[name]["sideBar"])
        self.sideBars[name]["sideBar"].\
             webView.page().setUserScript(script)
        self.sideBars[name]["sideBar"].\
             webView.windowCreated.connect(self.addTab)
        if style:
            self.sideBars[name]["sideBar"].\
                 webView.settings().setUserStyleSheetUrl(QUrl.fromUserInput(str(style)))    
        self.sideBars[name]["sideBar"].\
             webView.setUserAgent(ua)
        self.sideBars[name]["sideBar"].\
             webView.load(QUrl(url))
        container = QWidget(self.sideBars[name]["sideBar"])
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        container.setLayout(layout)
        if toolbar:
            toolBar = QToolBar(container)
            toolBar.setIconSize(QSize(16, 16))
            toolBar.setMovable(False)
            toolBar.setContextMenuPolicy(Qt.CustomContextMenu)
            toolBar.addAction(self.sideBars[name]["sideBar"].webView.page().action(QWebPage.Back))
            toolBar.addAction(self.sideBars[name]["sideBar"].webView.page().action(QWebPage.Forward))
            toolBar.addAction(self.sideBars[name]["sideBar"].webView.page().action(QWebPage.Stop))
            toolBar.addAction(self.sideBars[name]["sideBar"].webView.page().action(QWebPage.Reload))
            container.layout().addWidget(toolBar)
        container.layout().addWidget(self.sideBars[name]\
                                   ["sideBar"].webView)
        self.sideBars[name]["sideBar"].setWidget(container)
        for sidebar in self.sideBars.values():
            sidebar["sideBar"].setVisible(False)
        self.addDockWidget((Qt.LeftDockWidgetArea if self.layoutDirection() == Qt.LeftToRight else Qt.RightDockWidgetArea),\
                           self.sideBars[name]["sideBar"])
        self.tabifyDockWidget(self.sideBar, self.sideBars[name]["sideBar"])
        self.sideBars[name]["sideBar"].setVisible(True)

    # This is so you can grab the window by its toolbar and move it.
    # It's an ugly hack, but it works.
    def mousePressEvent(self, ev):
        if ev.button() != Qt.LeftButton:
            return QMainWindow.mousePressEvent(self, ev)
        else:
            if not QCoreApplication.instance().keyboardModifiers() in (Qt.ControlModifier, Qt.ShiftModifier, Qt.AltModifier):
                QApplication.setOverrideCursor(Qt.SizeAllCursor)
            self.mouseX = ev.globalX()
            self.origX = self.x()
            self.mouseY = ev.globalY()
            self.origY = self.y()

    def mouseMoveEvent(self, ev):
        if self.mouseX and self.mouseY and not self.isMaximized():
            self.move(self.origX + ev.globalX() - self.mouseX,
self.origY + ev.globalY() - self.mouseY)

    def mouseReleaseEvent(self, ev):
        QApplication.restoreOverrideCursor()
        return QMainWindow.mouseReleaseEvent(self, ev)

    # Deletes any closed windows above the reopenable window count,
    # and blanks all the tabs and sidebars.
    def closeEvent(self, ev):
        window_session = {"tabs": [], "closed_tabs": self.closedTabs, "app_mode": self.appMode}
        for tab in range(self.tabWidget().count()):
            window_session["tabs"].append(self.tabWidget().widget(tab).saveHistory())
        browser.closedWindows.append(window_session)
        while len(browser.closedWindows) >\
               settings.setting_to_int("general/ReopenableWindowCount"):
            browser.closedWindows.pop(0)
        self.deleteLater()

    def deleteLater(self):
        try: browser.windows.remove(self)
        except: pass
        QMainWindow.deleteLater(self)

    # Open settings dialog.
    def openSettings(self):
        settings.settingsDialog.show()

    # Open clippings manager.
    def openClippings(self):
        settings.clippingsManager.show()

    # Loads startup extensions.
    def loadStartupExtensions(self):
        for extension in settings.extensions:
            if extension not in settings.extensions_whitelist:
                continue
            extension_path = os.path.join(settings.extensions_folder,\
                                          extension)

            if os.path.isdir(extension_path):
                script_path = os.path.join(extension_path, "startup.py")
                if os.path.isfile(script_path):
                    f = open(script_path, "r")
                    script = copy.copy(f.read())
                    f.close()
                    try: exec(script)
                    except: traceback.print_exc()

    # Reload extensions.
    def reloadExtensions(self):

        while len(self._extensions) > 0:
            self._extensions.pop()

        # Hide extensions toolbar if there aren't any extensions.
        self.extensionBar.hide()

        for extension in settings.extensions:
            if extension not in settings.extensions_whitelist:
                continue
            extension_path = os.path.join(settings.extensions_folder,\
                                          extension)

            if os.path.isdir(extension_path):
                script_path = os.path.join(extension_path, "script.py")
                etype = "python"
                if not os.path.isfile(script_path):
                    script_path = os.path.join(extension_path, "script.js")
                    etype = "js"
                icon_path = os.path.join(extension_path, "icon.png")
                shortcut_path = os.path.join(extension_path, "shortcut.txt")
                if os.path.isfile(script_path):
                    f = open(script_path, "r")
                    script = copy.copy(f.read())
                    f.close()
                    shortcut = None
                    if os.path.isfile(shortcut_path):
                        f = open(shortcut_path, "r")
                        shortcut = copy.copy(f.read().replace("\n", ""))
                        f.close()
                    newExtension = ExtensionButton(extension, script, etype, shortcut, self)
                    self.extensionButtonGroup.addButton(newExtension)
                    newExtension.setToolTip(extension.replace("_", " ").\
                                            title() +\
                                            ("" if not shortcut\
                                                else "\n" + shortcut))
                    newExtension.clicked.connect(newExtension.loadScript)
                    self.extensionBar.show()
                    self.extensionBar.addWidget(newExtension)
                    if os.path.isfile(icon_path):
                        newExtension.setIcon(QIcon(icon_path))
                    else:
                        newExtension.setIcon(common.complete_icon("applications-other"))
                    self._extensions.append(newExtension)

    # Updates the time.
    def updateDateTime(self):
        self.dateTime.setText(QDateTime.currentDateTime().toString())

    # Toggle all the navigation buttons.
    def toggleActions(self):
        try:
            self.backAction.setEnabled(self.tabWidget().currentWidget().\
                                       page().history().canGoBack())
            forwardEnabled = self.tabWidget().currentWidget().\
                             page().history().canGoForward()
            self.forwardAction.setEnabled(forwardEnabled)

            if not forwardEnabled:
                self.forwardAction.setShortcut("")
                self.nextAction.setShortcut("Alt+Right")
            else:
                self.forwardAction.setShortcut("Alt+Right")
                self.nextAction.setShortcut("")

            self.upAction.setEnabled(self.tabWidget().currentWidget().canGoUp())

            # This is a workaround so that hitting Esc will reset the location
            # bar text.
            self.stopAction.setVisible(self.tabWidget().currentWidget().\
                                       pageAction(QWebPage.Stop).isEnabled())
            self.stopAction.setEnabled(True)

            self.reloadAction.setVisible(self.tabWidget().currentWidget().\
                                         pageAction(QWebPage.Reload).\
                                         isEnabled())
            self.reloadAction.setEnabled(True)

            self.homeAction.setVisible(settings.\
                                       setting_to_bool\
                                       ("general/HomeButtonVisible"))
            self.upAction.setVisible(settings.\
                                     setting_to_bool\
                                     ("general/UpButtonVisible"))
            self.feedMenuButton.setVisible(settings.\
                                           setting_to_bool\
                                           ("general/FeedButtonVisible"))
        except:
            self.backAction.setEnabled(False)
            self.forwardAction.setEnabled(False)
            self.stopAction.setEnabled(False)
            self.reloadAction.setEnabled(False)
        self.toggleActions2()
        self.updateTabTitles()

    def toggleActions2(self):
        try: self.nextAction.setEnabled(bool(self.tabWidget().\
                                             currentWidget().canGoNext()))
        except: self.nextAction.setEnabled(False)

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
            for item in reversed(range(0, len(backItems))):
                try:
                    action = custom_widgets.\
                             WebHistoryAction(item,\
                                              backItems[item].title(),\
                                              self.backHistoryMenu)
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
                    action = custom_widgets.\
                             WebHistoryAction(item,
                                              forwardItems[item].title(),\
                                              self.forwardHistoryMenu)
                    action.triggered2.connect(self.loadForwardHistoryItem)
                    self.forwardHistoryMenu.addAction(action)
                except:
                    pass
        except:
            pass

    def loadForwardHistoryItem(self, index):
        history = self.tabWidget().currentWidget().history()
        history.goToItem(history.forwardItems(10)[index])

    def up(self):
        self.tabWidget().currentWidget().up()

    def next(self):
        self.tabWidget().currentWidget().next()

    def aboutToShowUpMenu(self):
        self.upMenu.clear()
        tab = self.tabWidget().currentWidget()
        components = tab.url().toString().split("/")
        for component in range(0, len(components)):
            if components[component] != "":
                try:
                    x = "/".join(components[:component])
                    if x != "":
                        action = custom_widgets.LinkAction(QUrl.fromUserInput(x),\
                                                           x,\
                                                           self.upMenu)
                        action.triggered2[QUrl].\
                        connect(self.tabWidget().currentWidget().load)
                        self.upMenu.addAction(action)
                except:
                    pass

    def reload(self):
        self.tabWidget().currentWidget().reload()

    def stop(self):
        self.tabWidget().currentWidget().stop()
        self.locationBar.setEditText(self.tabWidget().\
                                     currentWidget().url().toString())

    def goHome(self):
        self.tabWidget().currentWidget().load(QUrl.\
                                              fromUserInput(settings.\
                                              settings.\
                                              value("general/Homepage")))

    # About to show feed menu.
    def aboutToShowFeedMenu(self):
        self.feedMenu.clear()
        feeds = self.tabWidget().currentWidget().rssFeeds()
        if len(feeds) == 0:
            self.feedMenu.addAction("N/A")
        else:
            for title, feed in feeds:
                action = custom_widgets.LinkAction(feed, title, self.feedMenu)
                action.triggered2[str].connect(self.tabWidget().\
                                               currentWidget().load2)
                self.feedMenu.addAction(action)

    def toggleFindToolBar(self):
        if self.findBar.hasFocus():
            self.findToolBar.hide()
        else:
            self.stop()

    # Find text/Text search methods.
    def find(self):
        currentWidget = self.tabWidget().currentWidget()
        if type(currentWidget._findText) is not str:
            currentWidget._findText = ""
        self.findToolBar.show()
        self.findBar.setFocus()
        self.findBar.selectAll()
        #currentWidget.findText(currentWidget._findText, QWebPage.FindWrapsAroundDocument)

    def findEither(self):
        if not QCoreApplication.instance().keyboardModifiers() == Qt.ShiftModifier:
            self.findNext()
        else:
            self.findPrevious()

    def findNext(self):
        currentWidget = self.tabWidget().currentWidget()
        if not currentWidget._findText and self.findBar.text() == "":
            self.find()
        else:
            currentWidget._findText = self.findBar.text()
            currentWidget.findText(currentWidget._findText, QWebPage.FindWrapsAroundDocument)

    def findPrevious(self):
        currentWidget = self.tabWidget().currentWidget()
        if not currentWidget._findText and self.findBar.text() == "":
            self.find()
        else:
            currentWidget._findText = self.findBar.text()
            currentWidget.findText(currentWidget._findText, QWebPage.FindWrapsAroundDocument | QWebPage.FindBackward)

    # Page printing methods.
    def printPage(self):
        self.tabWidget().currentWidget().printPage()

    def printPreview(self):
        self.tabWidget().currentWidget().printPreview()

    # Clears the history after a prompt.
    def clearHistory(self):
        common.chistorydialog.display()

    # Method to load a URL.
    def load(self, url=False):
        if not url:
            url = self.locationBar.currentText()
        for keyword in common.search_engines.values()   :
            if type(url) is str:
                url3 = url
            else:
                try: url3 = url.toString()
                except: url3 = ""
            fkey = keyword[0] + " "
            if url3.startswith(fkey):
                self.tabWidget().currentWidget().load(QUrl(keyword[1]\
                                                           % (url3.\
                                                           replace(fkey,\
                                                           ""),)))
                return
        url2 = QUrl.fromUserInput(url)
        valid_url = (":" in url or os.path.exists(url) or url.count(".") > 2)
        this_tld = url2.topLevelDomain().upper()
        for tld in common.topLevelDomains():
            if tld in this_tld:
                valid_url = True
        if valid_url:
            self.tabWidget().currentWidget().load(QUrl.fromUserInput(url))
        else:
            self.tabWidget().currentWidget().load(QUrl(settings.\
                                                  settings.\
                                                  value("general/Search")\
                                                  % (url,)))

    # Status bar related methods.
    def setStatusBarMessage(self, message):
        try: self.statusBar.setStatusBarMessage(self.tabWidget().\
                                                currentWidget().\
                                                _statusBarMessage)
        except: self.statusBar.setStatusBarMessage("")

    def setProgress(self, progress):
        try: self.statusBar.setValue(self.tabWidget().\
                                     currentWidget()._loadProgress)
        except: self.statusBar.setValue(0)

    # Fullscreen mode.
    def setFullScreen(self, fullscreen=False):
        if fullscreen:
            try: self.toggleFullScreenButton.setChecked(True)
            except: pass
            try: self.toggleFullScreenAction.setChecked(True)
            except: pass
            self.toggleFullScreenButton.setVisible(True)
            self.dateTime.setVisible(True)
            self._wasMaximized = self.isMaximized()
            self.showFullScreen()
        else:
            try: self.toggleFullScreenButton.setChecked(False)
            except: pass
            try: self.toggleFullScreenAction.setChecked(False)
            except: pass
            self.toggleFullScreenButton.setVisible(False)
            self.dateTime.setVisible(False)
            if not self._wasMaximized:
                self.showNormal()
            else:
                self.showNormal()
                self.showMaximized()

    # Tab-related methods.
    def toggleTabsOnTop(self):
        if not settings.setting_to_bool("general/TabsOnTop"):
            settings.settings.setValue("general/TabsOnTop", True)
            for window in browser.windows:
                window.addToolBarBreak()
                window.addToolBar(window.toolBar)
                self.tabs.tabBar().setStyleSheet(tabbar_stylesheet)
        else:
            settings.settings.setValue("general/TabsOnTop", False)
            for window in browser.windows:
                window.addToolBarBreak()
                window.addToolBar(window.tabsToolBar)
                self.tabs.tabBar().setStyleSheet("")
        self.tabs.setStyleSheet("QTabWidget::pane { top: -%s; } " %\
             (self.tabs.tabBar().height(),))
        settings.settings.sync()

    def aboutToShowTabsMenu(self):
        self.tabsMenu.clear()
        for tab in range(self.tabWidget().count()):
            tabAction = custom_widgets.IndexAction(tab, self.tabWidget().widget(tab).shortWindowTitle(), self.tabsMenu)
            if tab == self.tabWidget().currentIndex():
                tabAction.setCheckable(True)
                tabAction.setChecked(True)
            tabAction.triggered2.connect(self.tabWidget().setCurrentIndex)
            self.tabsMenu.addAction(tabAction)
        self.tabsMenu.addSeparator()
        tabCountAction = QAction(self.tabsMenu)
        tabCountAction.setText(tr("You currently have %s tab(s) open") % (self.tabWidget().count(),))
        tabCountAction.setEnabled(False)
        self.tabsMenu.addAction(tabCountAction)

    def currentWidget(self):
        return self.tabWidget().currentWidget()

    def addWindow(self, url=None):
        win = MainWindow()
        if not url or url == None:
            win.addTab(url=settings.settings.value("general/Homepage"))
        else:
            win.addTab(url=url)
        win.show()

    def loadSession(self, session):
        for tab in range(len(session)):
            self.addTab(index=tab)
            if tab < settings.setting_to_int("general/PinnedTabCount"):
                try: self.tabWidget().widget(tab).page().loadHistory(session[tab])
                except: pass
            else:
                self.tabWidget().widget(tab).loadHistory(session[tab])

    def reopenWindow(self):
        common.trayIcon.reopenWindow()

    def addTab(self, webView=None, index=None, focus=True, incognito=None, **kwargs):
        # If a WebView object is specified, use it.
        if webView != None:
            webview = webView
        else:
            if incognito == True:
                webview = WebView(incognito=True, parent=self)
            elif incognito == False:
                webview = WebView(incognito=False, parent=self)
            else:
                webview = WebView(incognito=not settings.setting_to_bool("data/RememberHistory"), parent=self)

        if "url" in kwargs:
            url = kwargs["url"]
            webview.load(QUrl.fromUserInput(url))
        elif self.appMode == True:
            url = settings.settings.value("general/Homepage")
            webview.load(QUrl.fromUserInput(url))

        # Connect signals
        webview.loadProgress.connect(self.setProgress)
        webview.statusBarMessage.connect(self.setStatusBarMessage)
        webview.page().linkHovered.connect(self.setStatusBarMessage)
        webview.titleChanged.connect(self.updateTabTitles)
        webview.page().fullScreenRequested.connect(self.setFullScreen)
        webview.urlChanged.connect(self.updateLocationText)
        webview.urlChanged2.connect(self.updateLocationText)
        webview.iconChanged.connect(self.updateTabIcons)
        webview.iconChanged.connect(self.updateLocationIcon)
        webview.windowCreated.connect(lambda webView:\
                                      self.addTab(webView=webView,\
                                      index=self.tabWidget().\
                                            currentIndex()+1,\
                                      focus=False))
        webview.downloadStarted.connect(self.addDownloadToolBar)

        # Add tab
        if type(index) is not int:
            self.tabWidget().addTab(webview, tr("New Tab"))
        else:
            ptc = settings.setting_to_int("general/PinnedTabCount")
            if index < ptc:
                index = ptc
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
            self.tabWidget().setCurrentIndex(self.tabWidget().\
                                             currentIndex() - 1)

    # Update the titles on every single tab.
    def updateTabTitles(self):
        count = self.tabWidget().count()
        for index in range(0, count):
            title = (("[%s] " % (str(index+1),) if index < 8 else ("[9] " if index == count-1 else "")) if settings.setting_to_bool("general/TabHotkeysVisible") else "") + self.tabWidget().widget(index).shortWindowTitle()
            longtitle = self.tabWidget().widget(index).windowTitle()
            self.tabWidget().setTabText(index, "\u26bf" if index < settings.setting_to_int("general/PinnedTabCount") else title)
            if index == self.tabWidget().currentIndex():
                self.setWindowTitle(longtitle + " - " + tr("Nimbus"))

    # Update the icons on every single tab.
    def updateTabIcons(self):
        for index in range(0, self.tabWidget().count()):
            try: icon = self.tabWidget().widget(index).icon()
            except: continue
            self.tabWidget().setTabIcon(index, icon)

    # Removes a tab at index.
    def removeTab(self, index):
        if index < settings.setting_to_int("general/PinnedTabCount"):
            return
        elif self.tabWidget().count() == 1 and settings.setting_to_bool("general/CloseWindowWithLastTab"):
            self.close()
            return
        try:
            webView = self.tabWidget().widget(index)
            if webView.history().canGoBack() or\
            webView.history().canGoForward() or\
            webView.url().toString() not in\
            ("about:blank", "",\
             QUrl.fromUserInput(settings.new_tab_page).toString(),) or webView._historyToBeLoaded:
                self.closedTabs.append((webView.saveHistory(), index, webView.incognito))
                while len(self.closedTabs) >\
                settings.setting_to_int("general/ReopenableTabCount"):
                    self.closedTabs.pop(0)
            webView.deleteLater()
        except:
            pass
        self.tabWidget().removeTab(index)
        if self.tabWidget().count() == 0 and\
        not settings.setting_to_bool("general/CloseWindowWithLastTab"):
            self.addTab(url="about:blank")

    # Reopens the last closed tab.
    def reopenTab(self):
        if len(self.closedTabs) > 0:
            index = self.closedTabs[-1][1]
            try: incognito = self.closedTabs[-1][2]
            except: incognito = False
            self.addTab(index=index, incognito=incognito)
            self.tabWidget().setCurrentIndex(index)
            self.tabWidget().widget(index).loadHistory(self.closedTabs[-1][0])
            del self.closedTabs[-1]

    # This method is used to add a DownloadBar to the window.
    def addDownloadToolBar(self, toolbar):
        self.statusBar.addToolBar(toolbar)

    # Method to update the location bar text.
    def updateLocationText(self, url=None):
        try:
            if type(url) not in (QUrl, str):
                url = self.tabWidget().currentWidget()._urlText
            elif type(url) is QUrl:
                url = url.toString()
            self.locationBar.setEditText(url)
        except:
            pass

    def updateLocationIcon(self, url=None):
        try:
            if type(url) != QUrl:
                url = self.tabWidget().currentWidget().url()
            currentUrl = self.tabWidget().currentWidget().url()
            if url == currentUrl:
                self.locationBar.setIcon(self.tabs.currentWidget().icon())
        except:
            pass
