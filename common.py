#! /usr/bin/env python3

# Import everything we need.
import os
from PyQt4.QtCore import QCoreApplication, QSettings
from PyQt4.QtGui import QWidget, QHBoxLayout, QLabel, QSizePolicy, QLineEdit

default_settings = {"proxy/type": "None",
                    "proxy/hostname": "",
                    "proxy/port": 8080,
                    "proxy/user": "",
                    "proxy/password": "",
                    "homepage": "https://github.com/foxhead128/nimbus",
                    "search": "https://duckduckgo.com/?q=%s"}
default_port = default_settings["proxy/port"]

# Common settings manager.
settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "nimbus", "config", QCoreApplication.instance())

for setting, value in default_settings.items():
    if settings.value(setting) == None:
        settings.setValue(setting, value)

settings.sync()

# This is a convenient variable that gets the settings folder on any platform.
settings_folder = os.path.dirname(settings.fileName())

# This stylesheet is applied to toolbars that are blank.
blank_toolbar = "QToolBar { border: 0; background: transparent; }"

# Stores webviews.
webviews = []

# Stores browser windows.
windows = []

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

class LineEditRow(Row):
    def __init__(self, text="Enter something here:", parent=None):
        super(LineEditRow, self).__init__(parent)
        self.label = QLabel(text, self)
        self.addWidget(self.label)
        self.lineEdit = QLineEdit(self)
        self.addWidget(self.lineEdit)

class Expander(QLabel):
    def __init__(self, parent=None):
        super(Expander, self).__init__(parent)
        self.setText("")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
