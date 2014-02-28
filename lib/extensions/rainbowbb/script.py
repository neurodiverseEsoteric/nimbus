name = os.path.join(settings.extensions_folder, self.name)
if not name in sys.path:
    sys.path.append(name)

from rainbowbb_gui import MainWindow

try: browser.activeWindow().rbbDock
except:
    mainWindow = browser.activeWindow()
    mainWindow.rbbDock = QDockWidget(mainWindow)
    mainWindow.rbbDock.setWindowTitle(tr("RainbowBB"))
    mainWindow.rbbDock.setContextMenuPolicy(Qt.CustomContextMenu)
    mainWindow.rbbDock.setFeatures(QDockWidget.DockWidgetClosable)
    mainWindow.rbbEdit = MainWindow(browser.activeWindow().rbbDock)
    mainWindow.rbbDock.setWidget(browser.activeWindow().rbbEdit)
    mainWindow.addDockWidget(Qt.BottomDockWidgetArea, mainWindow.rbbDock)
else:
    browser.activeWindow().rbbDock.setVisible(not browser.activeWindow().rbbDock.isVisible())
