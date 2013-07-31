#! /usr/bin/env python3

import sys
import os
import common
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QWidget, QVBoxLayout, QLabel, QMainWindow, QAction, QToolBar, QComboBox, QPushButton

class ClearHistoryDialog(QMainWindow):
    def __init__(self, parent=None):
        super(ClearHistoryDialog, self).__init__(parent)

        self.setWindowFlags(Qt.Dialog)
        self.setWindowModality(Qt.ApplicationModal)

        self.setWindowTitle("Clear History")

        closeWindowAction = QAction(self)
        closeWindowAction.setShortcuts(["Esc", "Ctrl+W", "Ctrl+Shift+Del"])
        closeWindowAction.triggered.connect(self.close)
        self.addAction(closeWindowAction)

        self.contents = QWidget()
        self.layout = QVBoxLayout()
        self.contents.setLayout(self.layout)
        self.setCentralWidget(self.contents)
        label = QLabel("What to clear:", self)
        self.layout.addWidget(label)
        self.dataType = QComboBox(self)
        self.dataType.addItem("History")
        self.dataType.addItem("Cookies")
        self.dataType.addItem("Cache")
        self.dataType.addItem("Persistent Storage")
        self.dataType.addItem("Everything")
        self.layout.addWidget(self.dataType)
        self.toolBar = QToolBar(self)
        self.toolBar.setStyleSheet(common.blank_toolbar)
        self.toolBar.setMovable(False)
        self.toolBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.addToolBar(Qt.BottomToolBarArea, self.toolBar)
        self.clearHistoryButton = QPushButton("Clear", self)
        self.clearHistoryButton.clicked.connect(self.clearHistory)
        self.toolBar.addWidget(self.clearHistoryButton)
        self.closeButton = QPushButton("Close", self)
        self.closeButton.clicked.connect(self.close)
        self.toolBar.addWidget(self.closeButton)

    def show(self):
        self.setVisible(True)

    def display(self):
        self.show()
        self.activateWindow()

    def clearHistory(self):
        clear_everything = (self.dataType.currentIndex() == 4)
        if self.dataType.currentIndex() == 0 or clear_everything:
            common.clearHistory()
        if self.dataType.currentIndex() == 1 or clear_everything:
            common.clearCookies()
        if self.dataType.currentIndex() == 2 or clear_everything:
            common.clearCache()
        if self.dataType.currentIndex() == 3 or clear_everything:
            webpageicondb = os.path.join(common.settings_folder, "WebpageIcons.db")
            if sys.platform.startswith("linux"):
                os.system("shred -v \"%s\"" % (webpageicondb,))
            try: os.remove(webpageicondb)
            except: pass
