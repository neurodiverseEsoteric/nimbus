#! /usr/bin/env python3

import common
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QWidget, QLabel, QMainWindow, QTabWidget, QToolBar, QToolButton, QLineEdit, QVBoxLayout, QComboBox, QSizePolicy, QAction, QPushButton

# Basic settings panel.
class SettingsPanel(QWidget):
    def __init__(self, parent=None):
        super(SettingsPanel, self).__init__(parent)
        # Create layout.
        newLayout = QVBoxLayout()
        self.setLayout(newLayout)
        self.layout().setContentsMargins(4,4,4,4)
    def saveSettings(self):
        pass

# Proxy configuration panel
class ProxyConfigPanel(SettingsPanel):
    def __init__(self, parent=None):
        super(ProxyConfigPanel, self).__init__(parent)

        # Proxy label.
        proxyLabel = QLabel("<b>Proxy configuration</b>")
        self.layout().addWidget(proxyLabel)

        # Type row.
        typeRow = common.Row(self)
        self.layout().addWidget(typeRow)

        # Create a nice label.
        typeLabel = QLabel("Type:", self)
        typeRow.addWidget(typeLabel)

        # Combo box to select proxy type.
        self.proxySelect = QComboBox(self)
        self.proxySelect.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.proxySelect.addItem("None")
        self.proxySelect.addItem('Socks5')
        self.proxySelect.addItem('Http')
        typeRow.addWidget(self.proxySelect)

        # Hostname row.
        hostNameRow = common.Row(self)
        self.layout().addWidget(hostNameRow)

        # Create amnother nice label.
        hostNameLabel = QLabel("Hostname:", self)
        hostNameRow.addWidget(hostNameLabel)

        self.hostNameEntry = QLineEdit(self)
        hostNameRow.addWidget(self.hostNameEntry)

        # Add an expander.
        expander = common.Expander(self)
        self.layout().addWidget(expander)

        self.loadSettings()

    def loadSettings(self):
        self.hostNameEntry.setText(str(common.settings.value("proxy/hostname")))
        for index in range(0, self.proxySelect.count()):
            if self.proxySelect.itemText(index) == common.settings.value("proxy/type"):
                self.proxySelect.setCurrentIndex(index)
                break

    def saveSettings(self):
        common.settings.setValue("proxy/hostname", self.hostNameEntry.text())
        common.settings.setValue("proxy/type", self.proxySelect.currentText())
        common.settings.sync()

# Main settings dialog
class SettingsDialog(QMainWindow):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)

        # Set window title.
        self.setWindowTitle("Settings")

        # Add action to hide dialog.
        hideAction = QAction(self)
        hideAction.setShortcut("Esc")
        hideAction.triggered.connect(self.hide)
        self.addAction(hideAction)

        # Tab widget
        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)

        self.tabs.addTab(ProxyConfigPanel(self), "Network")

        # Toolbar
        self.toolBar = QToolBar(self)
        self.toolBar.setMovable(False)
        self.toolBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.toolBar.setStyleSheet(common.blank_toolbar)
        self.addToolBar(Qt.BottomToolBarArea, self.toolBar)

        # Apply button
        applyButton = QPushButton("&Apply", self)
        applyButton.clicked.connect(self.saveSettings)
        self.toolBar.addWidget(applyButton)
    # Method to save all settings.
    def saveSettings(self):
        for index in range(0, self.tabs.count()):
            self.tabs.widget(index).saveSettings()
