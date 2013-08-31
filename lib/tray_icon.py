#! /usr/bin/env python3

###############
## nimbus.py ##
###############

# Description:
# This is the core module that contains all the very specific components
# related to loading Nimbus.

# Import everything we need.
import common
import translate
from translate import tr

# Extremely specific imports from PyQt4/PySide.
# We give PyQt4 priority because it supports Qt5.
try:
    from PyQt4.QtCore import pyqtSignal
    Signal = pyqtSignal
    from PyQt4.QtGui import QApplication, QMenu, QAction, QSystemTrayIcon
except:
    from PySide.QtCore import Signal
    from PySide.QtGui import QApplication, QMenu, QAction, QSystemTrayIcon

# System tray icon.
class SystemTrayIcon(QSystemTrayIcon):
    newWindowRequested = Signal()
    windowReopenRequested = Signal()
    def __init__(self, parent):
        super(SystemTrayIcon, self).__init__(common.app_icon, parent)

        # Set tooltip.
        self.setToolTip(tr("Nimbus"))

        # Set context menu.
        self.menu = QMenu(None)
        self.setContextMenu(self.menu)

        # New window action
        newWindowAction = QAction(common.complete_icon("window-new"), tr("&New Window"), self)
        newWindowAction.triggered.connect(self.newWindowRequested.emit)
        self.menu.addAction(newWindowAction)

        # Reopen window action
        reopenWindowAction = QAction(common.complete_icon("reopen-window"), tr("R&eopen Window"), self)
        reopenWindowAction.triggered.connect(self.windowReopenRequested.emit)
        self.menu.addAction(reopenWindowAction)

        # Quit action
        quitAction = QAction(common.complete_icon("application-exit"), tr("Quit"), self)
        quitAction.triggered.connect(QApplication.quit)
        self.menu.addAction(quitAction)
