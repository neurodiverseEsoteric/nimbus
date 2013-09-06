#! /usr/bin/env python3

###############
## nimbus.py ##
###############

# Description:
# This is the core module that contains all the very specific components
# related to loading Nimbus.

# Import everything we need.
import sys
import os
import json
import copy
import traceback
import pickle

# This is a hack for installing Nimbus.
try: import common
except:
    try: import lib.common as common
    except:
        import nimbus.common as common
sys.path.append(common.app_folder)

import settings_dialog
import browser
import filtering
import translate
from translate import tr
import custom_widgets
import clear_history_dialog
import settings
if not os.path.isdir(settings.extensions_folder) or not os.path.isfile(settings.startpage):
    import shutil
import extension_server
import data
import search_manager
from nwebkit import *
from mainwindow import *
from tray_icon import *

# Python DBus
has_dbus = True
if not "-no-remote" in sys.argv:
    try:
        import dbus
        import dbus.service
        from dbus.mainloop.qt import DBusQtMainLoop
    except:
        has_dbus = False
else:
    has_dbus = False

# This was made for an attempt to compile Nimbus to CPython,
# but it is now useless.
try: exec
except:
    def exec(code):
        pass

# Extremely specific imports from PyQt4/PySide.
# We give PyQt4 priority because it supports Qt5.
try:
    from PyQt4.QtCore import Qt, QCoreApplication, QUrl, QTimer
    from PyQt4.QtGui import QApplication, QAction
    from PyQt4.QtWebKit import QWebPage
except:
    from PySide.QtCore import Qt, QCoreApplication, QUrl, QTimer
    from PySide.QtGui import QApplication, QAction
    from PySide.QtWebKit import QWebPage

# chdir to the app folder. This way, we won't have issues related to
# relative paths.
os.chdir(common.app_folder)

# Create extension server.
server_thread = extension_server.ExtensionServerThread()

# Redundancy is redundant.
def addWindow(url=None):
    win = MainWindow()
    if not url or url == None:
        win.addTab(url=settings.settings.value("general/Homepage"))
    else:
        win.addTab(url=url)
    win.show()

# Reopen window method.
def reopenWindow():
    if len(browser.closedWindows) > 0:
        session = browser.closedWindows.pop()
        win = MainWindow()
        win.loadSession(session)
        win.show()

# Load session.
def loadSession():
    if os.path.exists(settings.session_file):
        f = open(settings.session_file, "rb")
        session = pickle.load(f)
        f.close()
        for window in session:
            if len(window) == 0:
                continue
            win = MainWindow()
            for tab in range(len(window)):
                win.addTab(index=tab)
                win.tabWidget().widget(tab).loadHistory(window[tab])
            win.show()

# Stores whether the session is being written to or not.
sessionLock = False

# Restore session.
def saveSession():
    global sessionLock
    if not sessionLock:
        sessionLock = True
        session = []
        for window in browser.windows:
            session.append([])
            for tab in range(window.tabWidget().count()):
                session[-1].append(window.tabWidget().widget(tab).saveHistory())
        try:
            f = open(settings.session_file, "wb")
        except:
            sessionLock = False
            return
        pickle.dump(session, f)
        f.close()
        sessionLock = False

# Preparations to quit.
def prepareQuit():
    saveSession()
    data.saveData()
    filtering.adblock_filter_loader.quit()
    filtering.adblock_filter_loader.wait()
    server_thread.httpd.shutdown()
    server_thread.quit()
    server_thread.wait()

# DBus server.
if has_dbus:
    class DBusServer(dbus.service.Object):
        def __init__(self, bus=None):
            busName = dbus.service.BusName("org.nimbus.Nimbus", bus=bus)
            dbus.service.Object.__init__(self, busName, "/Nimbus")

        @dbus.service.method("org.nimbus.Nimbus", in_signature="s", out_signature="s")
        def addWindow(self, url=None):
            addWindow(url)
            return url

        @dbus.service.method("org.nimbus.Nimbus", in_signature="s", out_signature="s")
        def addTab(self, url="about:blank"):
            for window in browser.windows[::-1]:
                if window.isVisible():
                    window.addTab(url=url)
                    browser.windows[-1].activateWindow()
                    return url
            self.addWindow(url)
            browser.windows[-1].activateWindow()
            return url

# Main function to load everything.
def main():
    # Start DBus loop
    if has_dbus:
        mainloop = DBusQtMainLoop(set_as_default = True)
        dbus.set_default_main_loop(mainloop)

    # Create app.
    app = QApplication(sys.argv)
    app.installTranslator(translate.translator)

    # We want Nimbus to stay open when the last window is closed,
    # so we set this.
    app.setQuitOnLastWindowClosed(False)

    # If D-Bus is present...
    if has_dbus:
        bus = dbus.SessionBus()

    try: proxy = bus.get_object("org.nimbus.Nimbus", "/Nimbus")
    except: dbus_present = False
    else: dbus_present = True

    # If Nimbus detects the existence of another Nimbus process, it will
    # send all the requested URLs to the existing process and exit.
    if dbus_present:
        for arg in sys.argv[1:]:
            if "." in arg or ":" in arg:
                proxy.addTab(arg)
        if len(sys.argv) < 2:
            proxy.addWindow()
        return

    # Hack together the browser's icon. This needs to be improved.
    common.app_icon = common.complete_icon("nimbus")
    common.app_icon.addFile(common.icon("nimbus-16.png"))
    common.app_icon.addFile(common.icon("nimbus-22.png"))
    common.app_icon.addFile(common.icon("nimbus-24.png"))
    common.app_icon.addFile(common.icon("nimbus-32.png"))
    common.app_icon.addFile(common.icon("nimbus-48.png"))
    common.app_icon.addFile(common.icon("nimbus-64.png"))
    common.app_icon.addFile(common.icon("nimbus-72.png"))
    common.app_icon.addFile(common.icon("nimbus-80.png"))
    common.app_icon.addFile(common.icon("nimbus-128.png"))
    common.app_icon.addFile(common.icon("nimbus-256.png"))

    app.setWindowIcon(common.app_icon)

    common.searchEditor = search_manager.SearchEditor()

    # Build the browser's default user agent.
    # This should be improved as well.
    webPage = QWebPage()
    nimbus_ua_sub = "Qt/" + common.qt_version + " Nimbus/" + common.app_version + " QupZilla/1.4.3"
    ua = webPage.userAgentForUrl(QUrl.fromUserInput("google.com"))
    if common.qt_version.startswith("4") or not "python" in ua:
        common.defaultUserAgent = ua.replace("Qt/" + common.qt_version, nimbus_ua_sub)
    else:
        common.defaultUserAgent = ua.replace("python", nimbus_ua_sub)
    webPage.deleteLater()
    del webPage
    del ua
    del nimbus_ua_sub

    # Create tray icon.
    common.trayIcon = SystemTrayIcon(QCoreApplication.instance())
    common.trayIcon.newWindowRequested.connect(addWindow)
    common.trayIcon.windowReopenRequested.connect(reopenWindow)
    common.trayIcon.show()

    # Creates a licensing information dialog.
    common.licenseDialog = custom_widgets.LicenseDialog()

    # Create instance of clear history dialog.
    global chistorydialog
    chistorydialog = clear_history_dialog.ClearHistoryDialog()

    # Set up settings dialog.
    settings.settingsDialog = settings_dialog.SettingsDialog()
    settings.settingsDialog.setWindowFlags(Qt.Dialog)
    closeSettingsDialogAction = QAction(settings.settingsDialog)
    closeSettingsDialogAction.setShortcuts(["Esc", "Ctrl+W"])
    closeSettingsDialogAction.triggered.connect(settings.settingsDialog.hide)
    settings.settingsDialog.addAction(closeSettingsDialogAction)

    # Create DBus server
    if has_dbus:
        server = DBusServer(bus)

    # Load adblock rules.
    filtering.adblock_filter_loader.start()

    if not os.path.isdir(settings.extensions_folder):
        try: shutil.copytree(common.extensions_folder, settings.extensions_folder)
        except: pass
    if not os.path.isfile(settings.startpage):
        try: shutil.copy2(common.startpage, settings.startpage)
        except: pass

    settings.reload_extensions()
    settings.reload_userscripts()

    server_thread.setDirectory(settings.extensions_folder)

    # Start extension server.
    server_thread.start()

    # On quit, save settings.
    app.aboutToQuit.connect(prepareQuit)

    # Load settings.
    data.loadData()

    sessionSaver = QTimer(QCoreApplication.instance())
    sessionSaver.timeout.connect(saveSession)
    sessionSaver.timeout.connect(data.saveData)
    sessionSaver.start(30000)

    if not "--daemon" in sys.argv and os.path.exists(settings.session_file):
        loadSession()
    if (not "--daemon" in sys.argv and len(browser.windows) == 0) or len(sys.argv[1:]) > 0:
        # Create instance of MainWindow.
        win = MainWindow()

        # Open URLs from command line.
        if len(sys.argv[1:]) > 0:
            for arg in sys.argv[1:]:
                if "." in arg or ":" in arg:
                    win.addTab(url=arg)

        if win.tabWidget().count() < 1:
            win.addTab(url=settings.settings.value("general/Homepage"))

        # Show window.
        win.show()

    # Start app.
    app.exec_()

# Start program
if __name__ == "__main__":
    try:
        main()
    except:
        traceback.print_exc()
