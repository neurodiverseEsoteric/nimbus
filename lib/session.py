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
    from PyQt4.QtCore import Qt
    from PyQt4.QtGui import QAction, QPushButton, QInputDialog, QListWidget
except:
    from PySide.QtCore import Qt
    from PySide.QtGui import QAction, QPushButton, QInputDialog, QListWidget

class SessionLoader(QListWidget):
    def __init__(self, parent=None):
        QListWidget.__init__(self, parent)
        self.setWindowTitle(tr("Saved Sessions"))
        self.setWindowFlags(Qt.Dialog)
        hideAction = QAction(self)
        hideAction.setShortcuts(["Esc", "Ctrl+W"])
        hideAction.triggered.connect(self.hide)
        self.addAction(hideAction)
        self.itemActivated.connect(self.loadSession)
    def show(self):
        self.clear()
        if os.path.exists(settings.session_folder):
            sessions = os.listdir(settings.session_folder)
            for session in sessions:
                self.addItem(session)
        QListWidget.show(self)
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
                    win.addTab(index=tab)
                    if type(window[tab]) is tuple:
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
                       window.tabWidget().widget(tab).title()))
        try:
            f = open(session_file, "wb")
        except:
            sessionLock = False
            return
        pickle.dump(session, f)
        f.close()
        sessionLock = False
