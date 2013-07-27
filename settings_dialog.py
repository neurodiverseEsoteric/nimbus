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
    def loadSettings(self):
        pass
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
        self.hostNameRow = common.LineEditRow("Hostname:", self)
        self.hostNameEntry = self.hostNameRow.lineEdit
        self.layout().addWidget(self.hostNameRow)

        # Port row.
        self.portRow = common.LineEditRow("Port:", self)
        self.portRow.lineEdit.setInputMask("99999")
        self.portEntry = self.portRow.lineEdit
        self.layout().addWidget(self.portRow)

        # User row.
        self.userRow = common.LineEditRow("User:", self)
        self.userEntry = self.userRow.lineEdit
        self.layout().addWidget(self.userRow)

        # Password row.
        self.passwordRow = common.LineEditRow("Password:", self)
        self.passwordEntry = self.passwordRow.lineEdit
        self.layout().addWidget(self.passwordRow)

        # Add an expander.
        expander = common.Expander(self)
        self.layout().addWidget(expander)

    def loadSettings(self):
        self.hostNameEntry.setText(str(common.settings.value("proxy/hostname")))
        port = str(common.settings.value("proxy/port"))
        if port == "None":
            port = str(common.default_port)
        self.portEntry.setText(port)
        for index in range(0, self.proxySelect.count()):
            if self.proxySelect.itemText(index) == common.settings.value("proxy/type"):
                self.proxySelect.setCurrentIndex(index)
                break

    def saveSettings(self):
        common.settings.setValue("proxy/hostname", self.hostNameEntry.text())
        proxyType = self.proxySelect.currentText()
        if proxyType == "None":
            proxyType = "No"
        common.settings.setValue("proxy/type", proxyType)
        common.settings.setValue("proxy/port", int(self.portEntry.text()))
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

        # Apply button
        cancelButton = QPushButton("&Cancel", self)
        cancelButton.clicked.connect(self.loadSettings)
        cancelButton.clicked.connect(self.hide)
        self.toolBar.addWidget(cancelButton)

        # Load settings
        self.loadSettings()
    
    # Method to load all settings.
    def loadSettings(self):
        for index in range(0, self.tabs.count()):
            self.tabs.widget(index).loadSettings()
    
    # Method to save all settings.
    def saveSettings(self):
        for index in range(0, self.tabs.count()):
            self.tabs.widget(index).saveSettings()
