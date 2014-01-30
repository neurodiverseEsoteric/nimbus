self.styleMenuButton = QAction(self)
self.styleMenuButton.setText(tr("User CSS Editor"))
self.styleMenuButton.setShortcut("Alt+E")
try: self.styleMenuButton.setIcon(QIcon(common.complete_icon("style")))
except: traceback.print_exc()
self.styleMenuButton.setCheckable(True)
self.toolBar.insertAction(self.feedMenuButton, self.styleMenuButton)
def togglestyleDock():
    try: browser.activeWindow().styleDock
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
        mainWindow.styleDock = QDockWidget(mainWindow)
        mainWindow.styleDock.setContextMenuPolicy(Qt.CustomContextMenu)
        mainWindow.styleDock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        mainWindow.styleEdit = QTextEdit(browser.activeWindow().styleDock)
        mainWindow.styleDock.setWindowTitle(tr("User CSS Editor"))
        mainWindow.styleDock.setWidget(browser.activeWindow().styleEdit)
        mainWindow.addDockWidget(Qt.RightDockWidgetArea, mainWindow.styleDock)
        def save():
            try: f = open(settings.user_css, "w")
            except: pass
            else:
                f.write(browser.activeWindow().styleEdit.toPlainText())
                f.close()
        browser.activeWindow().styleEdit.textChanged.connect(save)
    else:
        browser.activeWindow().styleDock.setVisible(not browser.activeWindow().styleDock.isVisible())
    u = ""
    try: f = open(settings.user_css, "r")
    except: pass
    else:
        u = f.read()
        f.close()
    browser.activeWindow().styleEdit.setPlainText(u)
self.styleMenuButton.triggered.connect(togglestyleDock)
