#! /usr/bin/env python3

# ------------
# tray_icon.py
# ------------
# Author:      Daniel Sim (foxhead128)
# License:     See LICENSE.md for more details.
# Description: This module contains a system tray icon class, used by Nimbus
#              as it runs in the background.

# Import everything we need.
import common
import browser
import translate
import settings
import session
from translate import tr

# Extremely specific imports from PyQt5/PySide.
# We give PyQt5 priority because it supports Qt5.
if not common.pyqt4:
    from PyQt5.QtCore import pyqtSignal, Qt, QTimer, QSize
    Signal = pyqtSignal
    from PyQt5.QtGui import QCursor
    from PyQt5.QtWidgets import QWidget, QApplication, QMenu, QAction, QSystemTrayIcon, QDesktopWidget, QMessageBox, QToolButton, QToolBar, QLabel
else:
    try:
        from PyQt4.QtCore import pyqtSignal, Qt, QTimer, QSize
        Signal = pyqtSignal
        from PyQt4.QtGui import QWidget, QCursor, QApplication, QMenu, QAction, QSystemTrayIcon, QDesktopWidget, QMessageBox, QToolButton, QToolBar, QLabel
    except:
        from PySide.QtCore import Signal, Qt, QTimer, QSize
        from PySide.QtGui import QWidget, QCursor, QApplication, QMenu, QAction, QSystemTrayIcon, QDesktopWidget, QMessageBox, QToolButton, QToolBar, QLabel

class BackgroundToolBar(QToolBar):
    def __init__(self, *args, **kwargs):
        super(BackgroundToolBar, self).__init__(*args, **kwargs)
        self.setIconSize(QSize(22, 22))
        self.shownOnce = False
        self.desktopWidget = QDesktopWidget()
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint)
    def halfScreen(self):
        return int((self.desktopWidget.height()-self.height())/2)
    def show(self):
        super(BackgroundToolBar, self).show()
        if not self.shownOnce:
            self.move(self.desktopWidget.width()-self.width(), self.halfScreen())
            self.shownOnce = True
    def mousePressEvent(self, ev):
        if ev.button() != Qt.LeftButton:
            return QToolBar.mousePressEvent(self, ev)
        else:
            if not QApplication.instance().keyboardModifiers() in (Qt.ControlModifier, Qt.ShiftModifier, Qt.AltModifier):
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
        if self.x() + self.width() > self.desktopWidget.width():
            self.move(self.desktopWidget.width()-self.width(), self.y())
            if self.halfScreen() - 64 <= self.y() <= self.halfScreen() + 64:
                self.move(self.x(), self.halfScreen())
        elif self.x() < 0:
            self.move(0, self.y())
            if self.halfScreen() - 64 <= self.y() <= self.halfScreen() + 64:
                self.move(self.x(), self.halfScreen())
        return QToolBar.mouseReleaseEvent(self, ev)

# System tray icon.
class SystemTrayIcon(QSystemTrayIcon):
    newWindowRequested = Signal()
    windowReopenRequested = Signal()
    def __init__(self, parent):
        super(SystemTrayIcon, self).__init__(common.app_icon, parent)

        # Set tooltip.
        self.setToolTip(tr("Nimbus"))
        
        self.widget = QWidget(None)
        self.widget.resize(0, 0)
        self.widget.setWindowFlags(Qt.FramelessWindowHint)

        # Set context menu.
        self.menu = QMenu(None)
        self.setContextMenu(self.menu)

        self.activated.connect(self.showMenu)

        # New window action
        newWindowAction = QAction(common.complete_icon("window-new"), tr("&New Window"), self)
        newWindowAction.triggered.connect(self.newWindowRequested.emit)
        self.menu.addAction(newWindowAction)

        # Reopen window action
        reopenWindowAction = QAction(common.complete_icon("reopen-window"), tr("R&eopen Window"), self)
        reopenWindowAction.triggered.connect(self.reopenWindow)
        self.menu.addAction(reopenWindowAction)

        self.menu.addSeparator()

        self.sessionManager = session.SessionManager(None)

        # Load session action
        loadSessionAction = QAction(common.complete_icon("document-open"), tr("&Load Session..."), self)
        loadSessionAction.triggered.connect(self.loadSession)
        self.menu.addAction(loadSessionAction)

        # Save session action
        saveSessionAction = QAction(common.complete_icon("document-save-as"), tr("Sa&ve Session..."), self)
        saveSessionAction.triggered.connect(self.saveSession)
        self.menu.addAction(saveSessionAction)

        self.menu.addSeparator()

        # Settings action
        settingsAction = QAction(common.complete_icon("preferences-system"), tr("&Settings..."), self)
        settingsAction.triggered.connect(self.openSettings)
        self.menu.addAction(settingsAction)

        # Clippings manager
        clippingsAction = QAction(common.complete_icon("edit-paste"), tr("&Manage Clippings..."), self)
        clippingsAction.triggered.connect(self.openClippings)
        self.menu.addAction(clippingsAction)

        self.menu.addSeparator()

        # About Nimbus action.
        aboutAction = QAction(common.complete_icon("help-about"), tr("A&bout Nimbus"), self)
        aboutAction.triggered.connect(self.about)
        self.menu.addAction(aboutAction)

        # Quit action
        quitAction = QAction(common.complete_icon("application-exit"), tr("Quit"), self)
        quitAction.triggered.connect(QApplication.quit)
        self.menu.addAction(quitAction)

        if self.geometry().width() < 8:
            self.toolBar = BackgroundToolBar(None)
            self.toolBar.setWindowTitle(tr("Nimbus"))
            #self.toolBar.setStyleSheet("QToolBar{background:palette(window);border:0;}")
            self.button = QToolButton(self.toolBar)
            self.button.setIcon(common.app_icon)
            self.button.clicked.connect(self.showMenu)
            self.toolBar.addWidget(self.button)
            extender = QLabel(tr("Nimbus"), self.toolBar)
            self.toolBar.addWidget(extender)
            self.toolBar.hide()
            timer = QTimer(timeout=self.toggleButton, parent=self)
            timer.start(500)

    def toggleButton(self):
        if len(browser.windows) == 0:
            self.toolBar.show()
        else:
            self.toolBar.hide()

    # Show menu.
    def showMenu(self, reason=None):
        self.menu.show()
        if reason == QSystemTrayIcon.Trigger or not reason:
            y = QDesktopWidget()
            self.menu.move(min(QCursor.pos().x(), y.width() - self.menu.width()), min(QCursor.pos().y(), y.height() - self.menu.height()))
            y.deleteLater()

    # About.
    def about(self):
        try: parent = browser.windows[-1]
        except:
            parent = self.widget
            self.widget.show()
        QMessageBox.about(parent, tr("About Nimbus"),\
                          "<h3>" + tr("Nimbus") + " " +\
                          common.app_version +\
                          "</h3>" +\
                          tr("A Qt-based web browser made in Python."))
        self.widget.hide()

    # Reopen window.
    def reopenWindow(self):
        session.reopenWindow()

    # Open settings dialog.
    def openSettings(self):
        settings.settingsDialog.show()

    # Open clippings manager.
    def openClippings(self):
        settings.clippingsManager.show()

    def loadSession(self):
        self.sessionManager.show()

    def saveSession(self):
        session.saveSessionManually()
