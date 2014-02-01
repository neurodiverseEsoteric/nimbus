self.notePadMenuButton = QAction(self)
self.notePadMenuButton.setText(tr("Notepad"))
self.notePadMenuButton.setShortcut("Ctrl+Shift+E")
try: self.notePadMenuButton.setIcon(QIcon(common.complete_icon("accessories-text-editor")))
except: traceback.print_exc()
self.notePadMenuButton.setCheckable(True)
self.toolBar.insertAction(self.feedMenuButton, self.notePadMenuButton)
def togglenotePadDock():
    try: browser.activeWindow().notePadDock
    except:
        try:
            from PyQt5.QtGui import QTextDocument
            from PyQt5.QtWidgets import QTextEdit
        except:
            try:
                from PyQt4.QtGui import QTextEdit, QTextDocument
            except:
                from PySide.QtGui import QTextEdit, QTextDocument
        mainWindow = browser.activeWindow()
        mainWindow.notePadDock = QDockWidget(mainWindow)
        mainWindow.notePadDock.setContextMenuPolicy(Qt.CustomContextMenu)
        mainWindow.notePadDock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        mainWindow.notePadEdit = QTextEdit(browser.activeWindow().notePadDock)
        mainWindow.notePadEdit.setAcceptRichText(False)
        mainWindow.notePadEdit.setFontFamily("monospace")
        mainWindow.notePadDock.setWindowTitle(tr("Notepad"))
        mainWindow.notePadDock.setWidget(browser.activeWindow().notePadEdit)
        mainWindow.addDockWidget(Qt.RightDockWidgetArea, mainWindow.notePadDock)
        def save():
            try: f = open(os.path.join(settings.settings_folder, "notes.txt"), "w")
            except: pass
            else:
                f.write(browser.activeWindow().notePadEdit.toPlainText())
                f.close()
        browser.activeWindow().notePadEdit.textChanged.connect(save)
    else:
        browser.activeWindow().notePadDock.setVisible(not browser.activeWindow().notePadDock.isVisible())
    u = ""
    try: f = open(os.path.join(settings.settings_folder, "notes.txt"), "r")
    except: pass
    else:
        u = f.read()
        f.close()
    browser.activeWindow().notePadEdit.setPlainText(u)
    try:
        browser.activeWindow().feedsDock.hide()
        browser.activeWindow().styleDock.hide()
        browser.activeWindow().feedMenuButton.setChecked(False)
        browser.activeWindow().styleMenuButton.setChecked(False)
    except: pass
self.notePadMenuButton.triggered.connect(togglenotePadDock)
