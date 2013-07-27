#! /usr/bin/env python3

# This is a browser status bar class.

import common
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QToolBar, QFrame, QHBoxLayout, QLineEdit, QProgressBar

class StatusBar(QToolBar):
    def __init__(self, parent=None):
        super(StatusBar, self).__init__(parent)
        self.setMovable(False)
        frame = QFrame(self)
        self.addWidget(frame)
        self.setStyleSheet(common.blank_toolbar + " QFrame { background: palette(window); border: 0; border-top: 1px solid palette(dark) }")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        frame.setLayout(layout)
        self.display = QLineEdit(self)
        self.display.setReadOnly(True)
        self.display.setFocusPolicy(Qt.NoFocus)
        self.display.setStyleSheet("QLineEdit { min-height: 1em; max-height: 1em; border: 0; background: transparent; }")
        frame.layout().addWidget(self.display)
        self.progressBar = QProgressBar(self)
        self.progressBar.hide()
        self.progressBar.setStyleSheet("min-height: 1em; max-height: 1em; min-width: 200px; max-width: 200px;")
        frame.layout().addWidget(self.progressBar)
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
