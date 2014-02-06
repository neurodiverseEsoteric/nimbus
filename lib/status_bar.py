#! /usr/bin/env python3

# -------------
# status_bar.py
# -------------
# Author:      Daniel Sim (foxhead128)
# License:     See LICENSE.md for more details.
# Description: This is a browser status bar class.

from common import blank_toolbar
import custom_widgets
try:
    from PyQt5.QtCore import Qt, QSize
    from PyQt5.QtWidgets import QToolBar, QStatusBar, QFrame, QMainWindow, QLineEdit, QProgressBar, QSizeGrip
except:
    try:
        from PyQt4.QtCore import Qt, QSize
        from PyQt4.QtGui import QToolBar, QStatusBar, QFrame, QMainWindow, QLineEdit, QProgressBar, QSizeGrip
    except:
        from PySide.QtCore import Qt, QSize
        from PySide.QtGui import QToolBar, QStatusBar, QFrame, QMainWindow, QLineEdit, QProgressBar, QSizeGrip

class StatusBar(QToolBar):
    def __init__(self, parent=None):
        super(StatusBar, self).__init__(parent)
        if self.layoutDirection() == Qt.LeftToRight:
        	self.setLayoutDirection(Qt.RightToLeft)
        else:
        	self.setLayoutDirection(Qt.LeftToRight)
        self.setMovable(False)
        self.fullStatusBar = custom_widgets.Column(self)
        self.fullStatusBar.layout().setSpacing(0)
        self.addWidget(self.fullStatusBar)
        self.downloadsBar = QMainWindow(self)
        self.fullStatusBar.addWidget(self.downloadsBar)
        self.statusBar = QStatusBar(self)
        self.statusBar.setSizeGripEnabled(False)
        self.fullStatusBar.addWidget(self.statusBar)
        self.setStyleSheet(blank_toolbar + " QMainWindow { background: transparent; border: 0; }")
        self.progressBar = QProgressBar(self.statusBar)
        self.progressBar.setLayoutDirection(self.parent().layoutDirection())
        self.progressBar.hide()
        self.progressBar.setStyleSheet("min-height: 1em; max-height: 1em; min-width: 200px; max-width: 200px;")
        self.statusBar.addPermanentWidget(self.progressBar)
        self.widgetToolBar = QToolBar(self.statusBar)
        #self.widgetToolBar.setMaximumHeight(16)
        #self.widgetToolBar.setIconSize(QSize(16, 16))
        self.widgetToolBar.setMovable(False)
        self.widgetToolBar.setLayoutDirection(self.parent().layoutDirection())
        self.widgetToolBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.widgetToolBar.setStyleSheet("QToolBar { border: 0; background: transparent; } QToolButton { padding: 0; }")
        self.statusBar.addPermanentWidget(self.widgetToolBar)
    def addToolBar(self, toolbar):
        self.downloadsBar.addToolBar(toolbar)
    def setValue(self, value=0):
        if value in (0, 100):
            self.progressBar.hide()
        else:
            self.progressBar.show()
        self.progressBar.setValue(value)
    def statusBarMessage(self):
        return self.statusBar.currentMessage()
    def setStatusBarMessage(self, text=""):
        self.statusBar.showMessage(text)
    def addToolBar(self, toolbar):
        self.downloadsBar.addToolBar(toolbar)
