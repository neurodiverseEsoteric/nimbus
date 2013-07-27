#! /usr/bin/env python3

# Import everything we need.
import os
from PyQt4.QtCore import QCoreApplication, QSettings
from PyQt4.QtGui import QWidget, QHBoxLayout, QLabel, QSizePolicy

# Common settings manager.
settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "nimbus", "config", QCoreApplication.instance())

# This is a convenient variable that gets the settings folder on any platform.
settings_folder = os.path.dirname(settings.fileName())

# This stylesheet is applied to toolbars that 
blank_toolbar = "QToolBar { border: 0; background: transparent; }"

# Variables for convenience.
app_folder = os.path.dirname(os.path.realpath(__file__))
extensions_folder = os.path.join(app_folder, "extensions")
adblock_folder = os.path.join(settings_folder, "adblock")
easylist = os.path.join(app_folder, "easylist.txt")

# Row widget.
class Row(QWidget):
    def __init__(self, parent=None):
        super(Row, self).__init__(parent)
        newLayout = QHBoxLayout()
        self.setLayout(newLayout)
        self.layout().setContentsMargins(0,0,0,0)
    def addWidget(self, widget):
        self.layout().addWidget(widget)

class Expander(QLabel):
    def __init__(self, parent=None):
        super(Expander, self).__init__(parent)
        self.setText("")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
