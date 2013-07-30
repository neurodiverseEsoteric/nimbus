#! /usr/bin/env python3

# This is a browser status bar class.

import common
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QToolBar, QFrame, QMainWindow, QLineEdit, QProgressBar

class StatusBar(QToolBar):
    def __init__(self, parent=None):
        super(StatusBar, self).__init__(parent)
        self.setMovable(False)
        self.fullStatusBar = common.Column(self)
        self.fullStatusBar.layout().setSpacing(0)
        self.addWidget(self.fullStatusBar)
        self.downloadsBar = QMainWindow(self)
        self.fullStatusBar.addWidget(self.downloadsBar)
        statusBar = common.Row(self)
        self.fullStatusBar.addWidget(statusBar)
        self.setStyleSheet(common.blank_toolbar.replace("}", " border-top: 1px solid palette(dark); }") + " QMainWindow { background: transparent; border: 0; }")
        self.display = QLineEdit(self)
        self.display.setReadOnly(True)
        self.display.setFocusPolicy(Qt.NoFocus)
        self.display.setStyleSheet("QLineEdit { min-height: 1em; max-height: 1em; border: 0; background: transparent; }")
        statusBar.addWidget(self.display)
        self.progressBar = QProgressBar(self)
        self.progressBar.hide()
        self.progressBar.setStyleSheet("min-height: 1em; max-height: 1em; min-width: 200px; max-width: 200px;")
        statusBar.addWidget(self.progressBar)
    def setValue(self, value=0):
        if value in (0, 100):
            self.progressBar.hide()
        else:
            self.progressBar.show()
        self.progressBar.setValue(value)
    def statusBarMessage(self):
        return self.display.text()
    def setStatusBarMessage(self, text=""):
        self.display.setText(text)
    def addToolBar(self, toolbar):
        self.downloadsBar.addToolBar(toolbar)
