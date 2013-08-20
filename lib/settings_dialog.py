#! /usr/bin/env python3

########################
## settings_dialog.py ##
########################

# Description:
# This module contains classes related to Nimbus' settings dialog.
# Each panel in the settings dialog is a subclass of a custom widget that
# can be used to make more panels.

import json
import common
import settings
import browser
import custom_widgets
import filtering
import data
import clear_history_dialog
from translate import tr
try:
    from PyQt4.QtCore import Qt, QUrl
    from PyQt4.QtGui import QWidget, QKeySequence, QIcon, QLabel, QMainWindow, QCheckBox, QTabWidget, QToolBar, QToolButton, QLineEdit, QVBoxLayout, QComboBox, QSizePolicy, QAction, QPushButton, QListWidget
except:
    from PySide.QtCore import Qt, QUrl
    from PySide.QtGui import QWidget, QKeySequence, QIcon, QLabel, QMainWindow, QCheckBox, QTabWidget, QToolBar, QToolButton, QLineEdit, QVBoxLayout, QComboBox, QSizePolicy, QAction, QPushButton, QListWidget

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
        homepageRow = custom_widgets.LineEditRow(tr("Homepage:"), self)
        self.homepageEntry = homepageRow.lineEdit
        self.layout().addWidget(homepageRow)

        # Default search.
        searchRow = custom_widgets.LineEditRow(tr("Search expression:"), self)
        self.searchEntry = searchRow.lineEdit
        self.layout().addWidget(searchRow)

        # Checkbox to toggle closing of window with last tab.
        self.closeWindowToggle = QCheckBox(tr("Close &window with last tab"), self)
        self.layout().addWidget(self.closeWindowToggle)

        self.settingsTabToggle = QCheckBox(tr("Open &settings in tab"), self)
        self.layout().addWidget(self.settingsTabToggle)

        self.reopenableTabCountRow = custom_widgets.SpinBoxRow(tr("Number of reopenable tabs:"), self)
        self.reopenableTabCount = self.reopenableTabCountRow.spinBox
        self.reopenableTabCount.setMaximum(9999)
        self.layout().addWidget(self.reopenableTabCountRow)

        self.reopenableWindowCountRow = custom_widgets.SpinBoxRow(tr("Number of reopenable windows:"), self)
        self.reopenableWindowCount = self.reopenableWindowCountRow.spinBox
        self.reopenableWindowCount.setMaximum(9999)
        self.layout().addWidget(self.reopenableWindowCountRow)

        self.layout().addWidget(custom_widgets.Expander(self))

    def loadSettings(self):
        self.homepageEntry.setText(str(settings.settings.value("general/Homepage")))
        self.searchEntry.setText(str(settings.settings.value("general/Search")))
        self.closeWindowToggle.setChecked(settings.setting_to_bool("general/CloseWindowWithLastTab"))
        self.settingsTabToggle.setChecked(settings.setting_to_bool("general/OpenSettingsInTab"))
        self.reopenableTabCount.setValue(settings.setting_to_int("general/ReopenableTabCount"))
        self.reopenableWindowCount.setValue(settings.setting_to_int("general/ReopenableWindowCount"))

    def saveSettings(self):
        settings.settings.setValue("general/Homepage", self.homepageEntry.text())
        settings.settings.setValue("general/Search", self.searchEntry.text())
        settings.settings.setValue("general/CloseWindowWithLastTab", self.closeWindowToggle.isChecked())
        settings.settings.setValue("general/OpenSettingsInTab", self.settingsTabToggle.isChecked())
        settings.settings.setValue("general/ReopenableWindowCount", self.reopenableWindowCount.text())
        settings.settings.setValue("general/ReopenableTabCount", self.reopenableTabCount.text())
        settings.settings.sync()

# Content settings panel
class ContentSettingsPanel(SettingsPanel):
    def __init__(self, parent=None):
        super(ContentSettingsPanel, self).__init__(parent)

        # Checkbox to toggle auto loading of images.
        self.imagesToggle = QCheckBox(tr("Automatically load &images"), self)
        self.layout().addWidget(self.imagesToggle)

        # Checkbox to toggle element backgrounds.
        self.elementBackgroundsToggle = QCheckBox(tr("Print e&lement backgrounds"), self)
        self.layout().addWidget(self.elementBackgroundsToggle)

        # Checkbox to toggle Javascript.
        self.javascriptToggle = QCheckBox(tr("Enable Java&Script"), self)
        self.layout().addWidget(self.javascriptToggle)

        # Checkbox to toggle Java.
        self.javaToggle = QCheckBox(tr("Enable &Java"), self)
        self.layout().addWidget(self.javaToggle)

        # Checkbox to toggle plugins.
        self.pluginsToggle = QCheckBox(tr("Enable &plugins"), self)
        self.layout().addWidget(self.pluginsToggle)

        # Checkbox to toggle handling of HTML5 audio and video using plugins.
        self.mediaToggle = QCheckBox(tr("Use plugins to handle &HTML5 audio and video"), self)
        self.layout().addWidget(self.mediaToggle)

        # Checkbox to toggle ad blocking.
        self.adblockToggle = QCheckBox(tr("Enable ad &blocking"), self)
        self.layout().addWidget(self.adblockToggle)

        # Checkbox to toggle hosts blocking.
        self.hostFilterToggle = QCheckBox(tr("Enable host &filtering"), self)
        self.layout().addWidget(self.hostFilterToggle)

        # Checkbox to toggle using online content viewers.
        self.contentViewersToggle = QCheckBox(tr("Use online content &viewers to load unsupported content"), self)
        self.layout().addWidget(self.contentViewersToggle)

        # Checkbox to toggle tiled backing.
        self.tiledBackingStoreToggle = QCheckBox(tr("Enable tiled backing store"), self)
        self.layout().addWidget(self.tiledBackingStoreToggle)

        self.frameFlattenToggle = QCheckBox(tr("Expand subframes to fit contents"), self)
        self.layout().addWidget(self.frameFlattenToggle)

        # Checkbox to toggle site specific quirks.
        self.siteSpecificQuirksToggle = QCheckBox(tr("Enable site specific &quirks"), self)
        self.layout().addWidget(self.siteSpecificQuirksToggle)

        self.layout().addWidget(custom_widgets.Expander(self))

    def loadSettings(self):
        self.imagesToggle.setChecked(settings.setting_to_bool("content/AutoLoadImages"))
        self.javascriptToggle.setChecked(settings.setting_to_bool("content/JavascriptEnabled"))
        self.javaToggle.setChecked(settings.setting_to_bool("content/JavaEnabled"))
        self.elementBackgroundsToggle.setChecked(settings.setting_to_bool("content/PrintElementBackgrounds"))
        self.pluginsToggle.setChecked(settings.setting_to_bool("content/PluginsEnabled"))
        self.adblockToggle.setChecked(settings.setting_to_bool("content/AdblockEnabled"))
        self.hostFilterToggle.setChecked(settings.setting_to_bool("content/HostFilterEnabled"))
        self.mediaToggle.setChecked(settings.setting_to_bool("content/ReplaceHTML5MediaTagsWithEmbedTags"))
        self.contentViewersToggle.setChecked(settings.setting_to_bool("content/UseOnlineContentViewers"))
        self.tiledBackingStoreToggle.setChecked(settings.setting_to_bool("content/TiledBackingStoreEnabled"))
        self.frameFlattenToggle.setChecked(settings.setting_to_bool("content/FrameFlatteningEnabled"))
        self.siteSpecificQuirksToggle.setChecked(settings.setting_to_bool("content/SiteSpecificQuirksEnabled"))

    def saveSettings(self):
        settings.settings.setValue("content/AutoLoadImages", self.imagesToggle.isChecked())
        settings.settings.setValue("content/JavascriptEnabled", self.javascriptToggle.isChecked())
        settings.settings.setValue("content/JavaEnabled", self.javaToggle.isChecked())
        settings.settings.setValue("content/PrintElementBackgrounds   ", self.elementBackgroundsToggle.isChecked())
        settings.settings.setValue("content/PluginsEnabled", self.pluginsToggle.isChecked())
        settings.settings.setValue("content/AdblockEnabled", self.adblockToggle.isChecked())
        settings.settings.setValue("content/HostFilterEnabled", self.hostFilterToggle.isChecked())
        settings.settings.setValue("content/ReplaceHTML5MediaTagsWithEmbedTags", self.mediaToggle.isChecked())
        filtering.adblock_filter_loader.start()
        settings.settings.setValue("content/UseOnlineContentViewers", self.contentViewersToggle.isChecked())
        settings.settings.setValue("content/TiledBackingStoreEnabled", self.tiledBackingStoreToggle.isChecked())
        settings.settings.setValue("content/FrameFlatteningEnabled", self.frameFlattenToggle.isChecked())
        settings.settings.setValue("content/SiteSpecificQuirksEnabled", self.siteSpecificQuirksToggle.isChecked())
        settings.settings.sync()

# Data settings panel
class DataSettingsPanel(SettingsPanel):
    def __init__(self, parent=None):
        super(DataSettingsPanel, self).__init__(parent)

        # Clear history dialog.
        self.clearHistoryDialog = clear_history_dialog.ClearHistoryDialog(self)
        self.clearHistoryDialog.hide()

        self.showClearHistoryDialogButton = QPushButton(tr("Clear Data"), self)
        self.showClearHistoryDialogButton.clicked.connect(self.clearHistoryDialog.show)
        self.layout().addWidget(self.showClearHistoryDialogButton)

        # Remember history checkbox.
        self.rememberHistoryToggle = QCheckBox(tr("Remember &history"), self)
        self.layout().addWidget(self.rememberHistoryToggle)

        # Maximum cache size spinbox.
        self.maximumCacheSizeRow = custom_widgets.SpinBoxRow(tr("Maximum cache size:"), self)
        self.maximumCacheSizeRow.expander.setText(tr("MB"))
        self.maximumCacheSize = self.maximumCacheSizeRow.spinBox
        self.maximumCacheSize.setMaximum(20000)
        self.layout().addWidget(self.maximumCacheSizeRow)

        # Checkbox to toggle geolocation.
        self.geolocationToggle = QCheckBox(tr("Enable geo&location"), self)
        self.layout().addWidget(self.geolocationToggle)

        self.geolocationPermissionsRow = custom_widgets.Row(self)
        self.layout().addWidget(self.geolocationPermissionsRow)

        self.geolocationWhitelistColumn = custom_widgets.Column(self)
        self.geolocationPermissionsRow.addWidget(self.geolocationWhitelistColumn)

        self.geolocationWhitelistLabel = QLabel(tr("Allow these sites to track my location:"), self)
        self.geolocationWhitelistColumn.addWidget(self.geolocationWhitelistLabel)

        self.geolocationWhitelist = QListWidget(self)
        self.geolocationWhitelistColumn.addWidget(self.geolocationWhitelist)

        self.removeFromWhitelistButton = QPushButton(tr("Remove"))
        self.removeFromWhitelistButton.clicked.connect(lambda: self.geolocationWhitelist.takeItem(self.geolocationWhitelist.row(self.geolocationWhitelist.currentItem())))
        self.geolocationWhitelistColumn.addWidget(self.removeFromWhitelistButton)

        self.geolocationBlacklistColumn = custom_widgets.Column(self)
        self.geolocationPermissionsRow.addWidget(self.geolocationBlacklistColumn)

        self.geolocationBlacklistLabel = QLabel(tr("Prevent these sites from tracking my location:"), self)
        self.geolocationBlacklistColumn.addWidget(self.geolocationBlacklistLabel)

        self.geolocationBlacklist = QListWidget(self)
        self.geolocationBlacklistColumn.addWidget(self.geolocationBlacklist)

        self.removeFromBlacklistButton = QPushButton(tr("Remove"))
        self.removeFromBlacklistButton.clicked.connect(lambda: self.geolocationBlacklist.takeItem(self.geolocationBlacklist.row(self.geolocationBlacklist.currentItem())))
        self.geolocationBlacklistColumn.addWidget(self.removeFromBlacklistButton)

        self.removeAction = QAction(self)
        self.removeAction.setShortcut("Del")
        self.removeAction.triggered.connect(lambda: self.geolocationWhitelist.takeItem(self.geolocationWhitelist.row(self.geolocationWhitelist.currentItem())) if self.geolocationWhitelist.hasFocus() else self.geolocationBlacklist.takeItem(self.geolocationBlacklist.row(self.geolocationBlacklist.currentItem())))
        self.addAction(self.removeAction)

        self.layout().addWidget(custom_widgets.Expander(self))
    def loadSettings(self):
        self.maximumCacheSize.setValue(settings.setting_to_int("data/MaximumCacheSize"))
        self.rememberHistoryToggle.setChecked(settings.setting_to_bool("data/RememberHistory"))
        self.geolocationToggle.setChecked(settings.setting_to_bool("network/GeolocationEnabled"))
        self.geolocationWhitelist.clear()
        for url in data.geolocation_whitelist:
            self.geolocationWhitelist.addItem(url)
        self.geolocationBlacklist.clear()
        for url in data.geolocation_blacklist:
            self.geolocationBlacklist.addItem(url)
    def saveSettings(self):
        settings.settings.setValue("data/MaximumCacheSize", self.maximumCacheSize.value())
        settings.settings.setValue("data/RememberHistory", self.rememberHistoryToggle.isChecked())
        settings.settings.setValue("network/GeolocationEnabled", self.geolocationToggle.isChecked())
        while len(data.geolocation_whitelist) > 0:
            data.geolocation_whitelist.pop()
        data.geolocation_whitelist = [self.geolocationWhitelist.item(authority).text() for authority in range(0, self.geolocationWhitelist.count())]
        while len(data.geolocation_blacklist) > 0:
            data.geolocation_blacklist.pop()
        data.geolocation_blacklist = [self.geolocationBlacklist.item(authority).text() for authority in range(0, self.geolocationBlacklist.count())]
        data.saveData()

# Network configuration panel
class NetworkSettingsPanel(SettingsPanel):
    def __init__(self, parent=None):
        super(NetworkSettingsPanel, self).__init__(parent)

        # Checkbox to toggle DNS prefetching.
        self.dnsPrefetchingToggle = QCheckBox(tr("Enable DNS &prefetching"), self)
        self.layout().addWidget(self.dnsPrefetchingToggle)

        # Checkbox to toggle XSS auditing.
        self.xssAuditingToggle = QCheckBox(tr("Enable &XSS auditing"), self)
        self.layout().addWidget(self.xssAuditingToggle)

        # Proxy label.
        proxyLabel = QLabel(tr("<b>Proxy configuration</b>"))
        self.layout().addWidget(proxyLabel)

        # Type row.
        typeRow = custom_widgets.Row(self)
        self.layout().addWidget(typeRow)

        # Create a nice label.
        typeLabel = QLabel(tr("Type:"), self)
        typeRow.addWidget(typeLabel)

        # Combo box to select proxy type.
        self.proxySelect = QComboBox(self)
        self.proxySelect.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.proxySelect.addItem("None")
        self.proxySelect.addItem('Socks5')
        self.proxySelect.addItem('Http')
        typeRow.addWidget(self.proxySelect)

        # Hostname and port row.
        self.hostNamePortRow = custom_widgets.Row()
        self.layout().addWidget(self.hostNamePortRow)

        # Hostname row.
        self.hostNameRow = custom_widgets.LineEditRow(tr("Hostname:"), self)
        self.hostNameEntry = self.hostNameRow.lineEdit
        self.hostNamePortRow.addWidget(self.hostNameRow)

        # Port row.
        self.portRow = custom_widgets.SpinBoxRow(tr("Port:"), self)
        self.portRow.expander.hide()
        self.portEntry = self.portRow.spinBox
        self.portEntry.setMaximum(99999)
        self.hostNamePortRow.addWidget(self.portRow)

        # User row.
        self.userRow = custom_widgets.LineEditRow(tr("User:"), self)
        self.userEntry = self.userRow.lineEdit
        self.layout().addWidget(self.userRow)

        # Password row.
        self.passwordRow = custom_widgets.LineEditRow(tr("Password:"), self)
        self.passwordEntry = self.passwordRow.lineEdit
        self.passwordEntry.setEchoMode(QLineEdit.Password)
        self.layout().addWidget(self.passwordRow)

        # Add an expander.
        expander = custom_widgets.Expander(self)
        self.layout().addWidget(expander)

    def loadSettings(self):
        self.hostNameEntry.setText(str(settings.settings.value("proxy/Hostname")))
        self.userEntry.setText(str(settings.settings.value("proxy/User")))
        self.passwordEntry.setText(str(settings.settings.value("proxy/Password")))
        self.xssAuditingToggle.setChecked(settings.setting_to_bool("network/XSSAuditingEnabled"))
        self.dnsPrefetchingToggle.setChecked(settings.setting_to_bool("network/DnsPrefetchingEnabled"))
        port = settings.setting_to_int("proxy/Port")
        if port == "None":
            port = str(settings.default_port)
        self.portEntry.setValue(port)
        for index in range(0, self.proxySelect.count()):
            if self.proxySelect.itemText(index) == settings.settings.value("proxy/Type"):
                self.proxySelect.setCurrentIndex(index)
                break

    def saveSettings(self):
        settings.settings.setValue("proxy/Hostname", self.hostNameEntry.text())
        proxyType = self.proxySelect.currentText()
        if proxyType == "None":
            proxyType = "No"
        settings.settings.setValue("network/XSSAuditingEnabled", self.xssAuditingToggle.isChecked())
        settings.settings.setValue("network/DnsPrefetchingEnabled", self.dnsPrefetchingToggle.isChecked())
        settings.settings.setValue("proxy/Type", proxyType)
        settings.settings.setValue("proxy/Port", self.portEntry.value())
        settings.settings.setValue("proxy/User", self.userEntry.text())
        settings.settings.setValue("proxy/Password", self.passwordEntry.text())
        settings.settings.sync()

# Extension configuration panel
class ExtensionsSettingsPanel(SettingsPanel):
    def __init__(self, parent=None):
        super(ExtensionsSettingsPanel, self).__init__(parent)

        # List row
        listRow = custom_widgets.Row(self)
        self.layout().addWidget(listRow)

        # Extensions whitelist.
        whitelistColumn = custom_widgets.Column(self)
        listRow.addWidget(whitelistColumn)
        whitelistColumn.addWidget(QLabel(tr("Enabled extensions:"), self))
        self.whitelist = QListWidget(self)
        self.whitelist.itemActivated.connect(self.disableExtension)
        whitelistColumn.addWidget(self.whitelist)

        # Extensions blacklist.
        blacklistColumn = custom_widgets.Column(self)
        listRow.addWidget(blacklistColumn)
        blacklistColumn.addWidget(QLabel(tr("Disabled extensions:"), self))
        self.blacklist = QListWidget(self)
        self.blacklist.itemActivated.connect(self.enableExtension)
        blacklistColumn.addWidget(self.blacklist)

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
        settings.reload_extensions()
        self.whitelist.clear()
        for extension in settings.extensions_whitelist:
            self.whitelist.addItem(extension)
        self.blacklist.clear()
        for extension in settings.extensions_blacklist:
            self.blacklist.addItem(extension)

    def saveSettings(self):
        settings.settings.setValue("extensions/Whitelist", json.dumps([self.whitelist.item(extension).text() for extension in range(0, self.whitelist.count())]))
        settings.reload_extensions()
        settings.settings.sync()

# Main settings dialog
class SettingsDialog(QWidget):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)

        # Set layout.
        _layout = QVBoxLayout(self)
        _layout.setContentsMargins(0,0,0,0)
        self.setLayout(_layout)

        # Set window title.
        self.setWindowTitle(tr("Settings"))

        # Tab widget
        self.tabs = QTabWidget(self)
        self.layout().addWidget(self.tabs)

        self.tabs.addTab(GeneralSettingsPanel(self), tr("&General"))
        self.tabs.addTab(ContentSettingsPanel(self), tr("&Content"))
        self.tabs.addTab(DataSettingsPanel(self), tr("&Data && Privacy"))
        self.tabs.addTab(NetworkSettingsPanel(self), tr("&Network"))
        self.tabs.addTab(ExtensionsSettingsPanel(self), tr("&Extensions"))

        # Toolbar
        self.toolBar = QToolBar(self)
        self.toolBar.setMovable(False)
        self.toolBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.toolBar.setStyleSheet(common.blank_toolbar)
        self.layout().addWidget(self.toolBar)

        # Apply button
        applyButton = QPushButton(tr("&Apply"), self)
        applyButton.clicked.connect(self.saveSettings)
        self.toolBar.addWidget(applyButton)

        # Reload settings button
        reloadButton = QPushButton(tr("&Reload"), self)
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
        settings.reset_extensions()
        for window in browser.windows:
            window.reloadExtensions()
        for webview in common.webviews:
            webview.updateProxy()
            webview.updateNetworkSettings()
            webview.updateContentSettings()

class SettingsDialogWrapper(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        _layout = QVBoxLayout(self)
        _layout.setContentsMargins(0,0,0,0)
        _layout.setSpacing(0)
        self.setLayout(_layout)
        self.settingsDialog = SettingsDialog(self)
        self.layout().addWidget(self.settingsDialog)