#! /usr/bin/env python3

import common
from PyQt4.QtCore import Qt, QUrl
from PyQt4.QtGui import QWidget, QIcon, QLabel, QMainWindow, QCheckBox, QTabWidget, QToolBar, QToolButton, QLineEdit, QVBoxLayout, QComboBox, QSizePolicy, QAction, QPushButton, QListWidget

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

# General configuration panel
class GeneralSettingsPanel(SettingsPanel):
    def __init__(self, parent=None):
        super(GeneralSettingsPanel, self).__init__(parent)

        # Homepage row.
        homepageRow = common.LineEditRow("Homepage:", self)
        self.homepageEntry = homepageRow.lineEdit
        self.layout().addWidget(homepageRow)

        # Default search.
        searchRow = common.LineEditRow("Search expression:", self)
        self.searchEntry = searchRow.lineEdit
        self.layout().addWidget(searchRow)

        self.closeWindowToggle = QCheckBox("Close &window with last tab", self)
        self.layout().addWidget(self.closeWindowToggle)

        self.layout().addWidget(common.Expander(self))

    def loadSettings(self):
        self.homepageEntry.setText(str(common.settings.value("general/Homepage")))
        self.searchEntry.setText(str(common.settings.value("general/Search")))
        self.closeWindowToggle.setChecked(common.setting_to_bool("general/CloseWindowWithLastTab"))

    def saveSettings(self):
        common.settings.setValue("general/Homepage", self.homepageEntry.text())
        common.settings.setValue("general/Search", self.searchEntry.text())
        common.settings.setValue("general/CloseWindowWithLastTab", self.closeWindowToggle.isChecked())
        common.settings.sync()

# Content settings panel
class ContentSettingsPanel(SettingsPanel):
    def __init__(self, parent=None):
        super(ContentSettingsPanel, self).__init__(parent)

        # Checkbox to toggle auto loading of images.
        self.imagesToggle = QCheckBox("Automatically load &images", self)
        self.layout().addWidget(self.imagesToggle)

        # Checkbox to toggle Javascript.
        self.javascriptToggle = QCheckBox("Enable &Javascript", self)
        self.layout().addWidget(self.javascriptToggle)

        # Checkbox to toggle plugins.
        self.pluginsToggle = QCheckBox("Enable NPAPI &plugins", self)
        self.layout().addWidget(self.pluginsToggle)

        # Checkbox to toggle ad blocking.
        self.adblockToggle = QCheckBox("Enable ad &blocking", self)
        self.layout().addWidget(self.adblockToggle)

        # Checkbox to toggle handling of HTML5 audio and video using plugins.
        self.mediaToggle = QCheckBox("Use plugins to handle &HTML5 audio and video", self)
        self.layout().addWidget(self.mediaToggle)

        # Checkbox to toggle using Google Docs viewer.
        self.googleDocsToggle = QCheckBox("Use Google Docs &viewer to load unsupported content", self)
        self.layout().addWidget(self.googleDocsToggle)

        # Checkbox to toggle tiled backing.
        self.tiledBackingStoreToggle = QCheckBox("Enable &tiled backing store", self)
        self.layout().addWidget(self.tiledBackingStoreToggle)

        # Checkbox to toggle site specific quirks.
        self.siteSpecificQuirksToggle = QCheckBox("Enable site specific &quirks", self)
        self.layout().addWidget(self.siteSpecificQuirksToggle)

        self.layout().addWidget(common.Expander(self))

    def loadSettings(self):
        self.imagesToggle.setChecked(common.setting_to_bool("content/AutoLoadImages"))
        self.javascriptToggle.setChecked(common.setting_to_bool("content/JavascriptEnabled"))
        self.pluginsToggle.setChecked(common.setting_to_bool("content/PluginsEnabled"))
        self.adblockToggle.setChecked(common.setting_to_bool("content/AdblockEnabled"))
        self.mediaToggle.setChecked(common.setting_to_bool("content/ReplaceHTML5MediaTagsWithEmbedTags"))
        self.googleDocsToggle.setChecked(common.setting_to_bool("content/UseGoogleDocsViewer"))
        self.tiledBackingStoreToggle.setChecked(common.setting_to_bool("content/TiledBackingStoreEnabled"))
        self.siteSpecificQuirksToggle.setChecked(common.setting_to_bool("content/SiteSpecificQuirksEnabled"))

    def saveSettings(self):
        common.settings.setValue("content/AutoLoadImages", self.imagesToggle.isChecked())
        common.settings.setValue("content/JavascriptEnabled", self.javascriptToggle.isChecked())
        common.settings.setValue("content/PluginsEnabled", self.pluginsToggle.isChecked())
        common.settings.setValue("content/AdblockEnabled", self.adblockToggle.isChecked())
        common.settings.setValue("content/ReplaceHTML5MediaTagsWithEmbedTags", self.mediaToggle.isChecked())
        common.adblock_filter_loader.start()
        common.settings.setValue("content/UseGoogleDocsViewer", self.googleDocsToggle.isChecked())
        common.settings.setValue("content/TiledBackingStoreEnabled", self.tiledBackingStoreToggle.isChecked())
        common.settings.setValue("content/SiteSpecificQuirksEnabled", self.siteSpecificQuirksToggle.isChecked())
        common.settings.sync()

# Network configuration panel
class NetworkSettingsPanel(SettingsPanel):
    def __init__(self, parent=None):
        super(NetworkSettingsPanel, self).__init__(parent)

        # Checkbox to toggle DNS prefetching.
        self.dnsPrefetchingToggle = QCheckBox("Enable DNS &prefetching")
        self.layout().addWidget(self.dnsPrefetchingToggle)

        # Checkbox to toggle XSS auditing.
        self.xssAuditingToggle = QCheckBox("Enable &XSS auditing")
        self.layout().addWidget(self.xssAuditingToggle)

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
        self.hostNameEntry.setText(str(common.settings.value("proxy/Hostname")))
        self.userEntry.setText(str(common.settings.value("proxy/User")))
        self.passwordEntry.setText(str(common.settings.value("proxy/Password")))
        self.xssAuditingToggle.setChecked(common.setting_to_bool("network/XSSAuditingEnabled"))
        self.dnsPrefetchingToggle.setChecked(common.setting_to_bool("network/DnsPrefetchingEnabled"))
        port = str(common.settings.value("proxy/Port"))
        if port == "None":
            port = str(common.default_port)
        self.portEntry.setText(port)
        for index in range(0, self.proxySelect.count()):
            if self.proxySelect.itemText(index) == common.settings.value("proxy/Type"):
                self.proxySelect.setCurrentIndex(index)
                break

    def saveSettings(self):
        common.settings.setValue("proxy/Hostname", self.hostNameEntry.text())
        proxyType = self.proxySelect.currentText()
        if proxyType == "None":
            proxyType = "No"
        common.settings.setValue("network/XSSAuditingEnabled", self.xssAuditingToggle.isChecked())
        common.settings.setValue("network/DnsPrefetchingEnabled", self.dnsPrefetchingToggle.isChecked())
        common.settings.setValue("proxy/Type", proxyType)
        common.settings.setValue("proxy/Port", int(self.portEntry.text()))
        common.settings.setValue("proxy/User", self.userEntry.text())
        common.settings.setValue("proxy/Password", self.passwordEntry.text())
        common.settings.sync()

# Extension configuration panel
class ExtensionsSettingsPanel(SettingsPanel):
    def __init__(self, parent=None):
        super(ExtensionsSettingsPanel, self).__init__(parent)

        # List row
        listRow = common.Row(self)
        self.layout().addWidget(listRow)

        # Extensions whitelist.
        whitelistColumn = common.Column(self)
        listRow.addWidget(whitelistColumn)
        whitelistColumn.addWidget(QLabel("Enabled extensions:", self))
        self.whitelist = QListWidget(self)
        self.whitelist.itemActivated.connect(self.disableExtension)
        whitelistColumn.addWidget(self.whitelist)

        # Extensions blacklist.
        blacklistColumn = common.Column(self)
        listRow.addWidget(blacklistColumn)
        blacklistColumn.addWidget(QLabel("Disabled extensions:", self))
        self.blacklist = QListWidget(self)
        self.blacklist.itemActivated.connect(self.enableExtension)
        blacklistColumn.addWidget(self.blacklist)

        self.layout().addWidget(common.Expander(self))

    def disableExtension(self, item):
        name = item.text()
        self.blacklist.addItem(name)
        self.blacklist.sortItems(Qt.AscendingOrder)
        self.whitelist.takeItem(self.whitelist.row(item))
        self.whitelist.sortItems(Qt.AscendingOrder)

    def enableExtension(self, item):
        name = item.text()
        self.whitelist.addItem(name)
        self.whitelist.sortItems(Qt.AscendingOrder)
        self.blacklist.takeItem(self.blacklist.row(item))
        self.blacklist.sortItems(Qt.AscendingOrder)

    def loadSettings(self):
        self.whitelist.clear()
        for extension in common.settings.value("extensions/Whitelist"):
            self.whitelist.addItem(extension)
        self.blacklist.clear()
        for extension in common.extensions_blacklist:
            self.blacklist.addItem(extension)

    def saveSettings(self):
        common.settings.setValue("extensions/Whitelist", [self.whitelist.item(extension).text() for extension in range(0, self.whitelist.count())])
        common.reload_extensions_blacklist()
        common.settings.sync()

# Main settings dialog
class SettingsDialog(QMainWindow):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)

        # Set window title.
        self.setWindowTitle("Settings")

        # Tab widget
        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)

        self.tabs.addTab(GeneralSettingsPanel(self), "&General")
        self.tabs.addTab(ContentSettingsPanel(self), "&Content")
        self.tabs.addTab(NetworkSettingsPanel(self), "&Network")
        self.tabs.addTab(ExtensionsSettingsPanel(self), "&Extensions")

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

        # Reload settings button
        reloadButton = QPushButton("&Reload", self)
        reloadButton.clicked.connect(self.loadSettings)
        self.toolBar.addWidget(reloadButton)

        # Load settings
        self.loadSettings()

    def url(self):
        return QUrl("")

    def icon(self):
        return common.complete_icon("preferences-system")

    # Method to load all settings.
    def loadSettings(self):
        for index in range(0, self.tabs.count()):
            self.tabs.widget(index).loadSettings()
    
    # Method to save all settings.
    def saveSettings(self):
        for index in range(0, self.tabs.count()):
            self.tabs.widget(index).saveSettings()
        common.reset_extensions()
        for window in common.windows:
            window.reloadExtensions()
        for webview in common.webviews:
            webview.updateProxy()
            webview.updateNetworkSettings()
            webview.updateContentSettings()
