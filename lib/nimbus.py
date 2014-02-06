#! /usr/bin/env python3

# ---------
# nimbus.py
# ---------
# Author:      Daniel Sim (foxhead128)
# License:     See LICENSE.md for more details.
# Description: This is the core module that contains all the very
#              specific components related to loading Nimbus.

# Import everything we need.
import sys
import os
import json
import copy

# This is a hack for installing Nimbus.
try: import common
except:
    try: import lib.common as common
    except:
        import nimbus.common as common
sys.path.append(common.app_folder)

from session import *
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

# This was made for an attempt to compile Nimbus to CPython,
# but it is now useless.
try: exec
except:
    def exec(code):
        pass

# Extremely specific imports from PyQt5/PySide.
# We give PyQt5 priority because it supports Qt5.
try:
    from PyQt5.QtCore import Qt, QCoreApplication, QUrl, QTimer
    from PyQt5.QtWidgets import QApplication, QAction
    from PyQt5.QtWebKit import QWebSettings
    from PyQt5.QtWebKitWidgets import QWebPage

    # Python DBus
    has_dbus = False
    if not "-no-remote" in sys.argv:
        try:
            import dbus
            import dbus.service
            from dbus.mainloop.pyqt5 import DBusQtMainLoop
            has_dbus = True
        except:
            pass
except:
    try:
        from PyQt4.QtCore import Qt, QCoreApplication, QUrl, QTimer
        from PyQt4.QtGui import QApplication, QAction
        from PyQt4.QtWebKit import QWebPage, QWebSettings

        # Python DBus
        has_dbus = False
        if not "-no-remote" in sys.argv:
            try:
                import dbus
                import dbus.service
                from dbus.mainloop.qt import DBusQtMainLoop
                has_dbus = True
            except:
                pass
    except:
        from PySide.QtCore import Qt, QCoreApplication, QUrl, QTimer
        from PySide.QtGui import QApplication, QAction
        from PySide.QtWebKit import QWebPage, QWebSettings


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

        @dbus.service.method("org.nimbus.Nimbus", in_signature="s",\
                             out_signature="s")
        def addWindow(self, url=None):
            addWindow(url)
            return url

        @dbus.service.method("org.nimbus.Nimbus", in_signature="s",\
                             out_signature="s")
        def addTab(self, url="about:blank"):
            if url == "--app":
                win = MainWindow()
                win.toolBar.setVisible(False)
                win.statusBar.setVisible(False)
                win.addTab(url="about:blank")
                win.show()
                return url
            else:
                for window in browser.windows[::-1]:
                    if window.isVisible():
                        window.addTab(url=url)
                        if window.tabWidget().widget(0).url().toString() == "about:blank":
                            window.removeTab(0)
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

    # If Nimbus detects the existence of another Nimbus process, it
    # will send all the requested URLs to the existing process and
    # exit.
    if dbus_present:
        for arg in sys.argv[1:]:
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
    common.createUserAgent()

    # Create tray icon.
    common.trayIcon = SystemTrayIcon(QCoreApplication.instance())
    common.trayIcon.newWindowRequested.connect(addWindow)
    #common.trayIcon.windowReopenRequested.connect(reopenWindow)
    common.trayIcon.show()

    # Creates a licensing information dialog.
    common.licenseDialog = custom_widgets.LicenseDialog()

    # Create instance of clear history dialog.
    common.chistorydialog = clear_history_dialog.ClearHistoryDialog()

    QWebSettings.globalSettings().setAttribute(QWebSettings.globalSettings().DeveloperExtrasEnabled, True)

    uc = QUrl.fromUserInput(settings.user_css)
    QWebSettings.globalSettings().setUserStyleSheetUrl(uc)
    print(QWebSettings.globalSettings().userStyleSheetUrl())
    print("Nyahahaha!")

    # Set up settings dialog.
    settings.settingsDialog = settings_dialog.SettingsDialog()
    settings.settingsDialog.setWindowFlags(Qt.Dialog)
    closeSettingsDialogAction = QAction(settings.settingsDialog)
    closeSettingsDialogAction.setShortcuts(["Esc", "Ctrl+W"])
    closeSettingsDialogAction.triggered.connect(settings.settingsDialog.hide)
    settings.settingsDialog.addAction(closeSettingsDialogAction)

    # Set up clippings manager.
    settings.clippingsManager = settings_dialog.ClippingsPanel()
    settings.clippingsManager.setWindowFlags(Qt.Dialog)
    closeClippingsManagerAction = QAction(settings.clippingsManager)
    closeClippingsManagerAction.setShortcuts(["Esc", "Ctrl+W"])
    closeClippingsManagerAction.triggered.connect(settings.clippingsManager.hide)
    settings.clippingsManager.addAction(closeClippingsManagerAction)

    # Create DBus server
    if has_dbus:
        server = DBusServer(bus)

    # Load adblock rules.
    filtering.adblock_filter_loader.start()

    if not os.path.isdir(settings.extensions_folder):
        try: shutil.copytree(common.extensions_folder,\
                             settings.extensions_folder)
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
    if not "--daemon" in sys.argv and len(sys.argv[1:]) > 0:
        # Create instance of MainWindow.
        if len(browser.windows) > 0:
            win = browser.windows[-1]
        else:
            win = MainWindow()

        if "--app" in sys.argv:
            win.toolBar.setVisible(False)
            win.statusBar.setVisible(False)

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
    main()
