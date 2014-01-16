#! /usr/bin/env python3

# ----------
# session.py
# ----------
# Author:      Daniel Sim (foxhead128)
# License:     See LICENSE.md for more details.
# Description: This is the module that contains stuff pertaining to session
#              management.

import os
import pickle
import settings
import traceback
import browser
from translate import tr
from mainwindow import MainWindow
try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QAction, QMainWindow, QPushButton, QInputDialog, QListWidget, QToolBar
except:
    from PySide.QtCore import Qt
    from PySide.QtWidgets import QAction, QMainWindow, QPushButton, QInputDialog, QListWidget, QToolBar

class SessionManager(QMainWindow):
    def __init__(self, parent=None):
        QListWidget.__init__(self, parent)
        self.setWindowTitle(tr("Saved Sessions"))
        self.setWindowFlags(Qt.Dialog)
        hideAction = QAction(self)
        hideAction.setShortcuts(["Esc", "Ctrl+W"])
        hideAction.triggered.connect(self.hide)
        self.addAction(hideAction)
        self.sessionList = QListWidget(self)
        self.sessionList.itemActivated.connect(self.loadSession)
        self.setCentralWidget(self.sessionList)
        self.toolBar = QToolBar(self)
        self.toolBar.setMovable(False)
        self.toolBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.addToolBar(Qt.BottomToolBarArea, self.toolBar)
        self.loadButton = QPushButton(tr("&Load"), self)
        self.loadButton.clicked.connect(lambda: self.loadSession(self.sessionList.currentItem()))
        self.toolBar.addWidget(self.loadButton)
        self.saveButton = QPushButton(tr("&Save"), self)
        self.saveButton.clicked.connect(saveSessionManually)
        self.toolBar.addWidget(self.saveButton)
    def show(self):
        self.sessionList.clear()
        if os.path.exists(settings.session_folder):
            sessions = os.listdir(settings.session_folder)
            for session in sessions:
                self.sessionList.addItem(session)
        QMainWindow.show(self)
    def loadSession(self, item):
        if os.path.exists(settings.session_folder):
            loadSession(os.path.join(settings.session_folder, item.text()))
        self.hide()

def saveSessionManually():
    sname = QInputDialog.getText(None, tr("Save Session"), tr("Enter a name here:"))
    if sname[1]:
        if not os.path.exists(settings.session_folder):
            os.makedirs(settings.session_folder)
        saveSession(os.path.join(settings.session_folder, sname[0]))

# Load session.
def loadSession(session_file=settings.session_file):
    try:
        if os.path.exists(session_file):
            f = open(session_file, "rb")
            session = pickle.load(f)
            f.close()
            for window in session:
                if len(window) == 0:
                    continue
                win = MainWindow()
                for tab in range(len(window)):
                    try:
                        incognito = bool(window[tab][2])
                    except:
                        traceback.print_exc()
                        incognito = False
                    win.addTab(index=tab, incognito=incognito)
                    if type(window[tab]) is tuple:
                        if tab < settings.setting_to_int("general/PinnedTabCount"):
                            win.tabWidget().widget(tab).page().loadHistory(window[tab][0])
                        else:    
                            win.tabWidget().widget(tab).loadHistory(window[tab][0], window[tab][1])
                    else:
                        win.tabWidget().widget(tab).loadHistory(window[tab])
                win.show()
    except:
        traceback.print_exc()

# Stores whether the session is being written to or not.
sessionLock = False

# Restore session.
def saveSession(session_file=settings.session_file):
    global sessionLock
    if not sessionLock:
        sessionLock = True
        session = []
        for window in browser.windows:
            session.append([])
            for tab in range(window.tabWidget().count()):
                session[-1].append((window.tabWidget().widget(tab).\
                                   saveHistory() if not\
                            window.tabWidget().widget(tab)._historyToBeLoaded\
                       else window.tabWidget().widget(tab)._historyToBeLoaded,
                       window.tabWidget().widget(tab).title(), window.tabWidget().widget(tab).incognito))
        try:
            f = open(session_file, "wb")
        except:
            sessionLock = False
            return
        pickle.dump(session, f)
        f.close()
        sessionLock = False
