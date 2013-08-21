if not self.isCheckable():
    self.setCheckable(True)
    self.setChecked(True)
import json
try: data.history
except:
    history = data.data.value("data/Bookmarks")
    if not history:
        data.history = []
        data.data.setValue("data/Bookmarks", json.dumps(data.history))
        data.data.sync()
    else:
        data.history = json.loads(history)
def reloadHistory():
    for window in browser.windows:
        try: window.historyList.clear()
        except: pass
    browser.activeWindow().locationBar.clear()
    for window in browser.windows:
        for history in data.history:
            try: window.historyList.addItem(history)
            except: pass
            window.locationBar.addItem(history)
try: browser.activeWindow().historyDock
except:
    mainWindow = browser.activeWindow()
    mainWindow.historyExtensionWidget = self
    mainWindow.historyDock = QDockWidget(mainWindow)
    mainWindow.historyDock.setContextMenuPolicy(Qt.CustomContextMenu)
    mainWindow.historyDock.setFeatures(QDockWidget.DockWidgetClosable)
    mainWindow.historyList = QListWidget(browser.activeWindow().historyDock)
    mainWindow.historyDock.setWindowTitle("History")
    #mainWindow.historyList.addItem("Add history")
    for history in data.history:
        mainWindow.historyList.addItem(history)
    mainWindow.historyDock.setWidget(browser.activeWindow().historyList)
    deleteAction = QAction(browser.activeWindow().historyList)
    deleteAction.setShortcut("Del")
    mainWindow.historyList.addAction(deleteAction)
    def removeHistoryItem():
        if browser.activeWindow().historyList.hasFocus():
            import json
            currentItem = browser.activeWindow().historyList.currentItem()
            url = currentItem.text()
            browser.activeWindow().historyList.takeItem(browser.activeWindow().historyList.row(currentItem))
            try: data.history.remove(url)
            except: pass
            data.data.setValue("data/Bookmarks", json.dumps(data.history))
            data.data.sync()
    deleteAction.triggered.connect(removeHistoryItem)
    deleteAction.triggered.connect(reloadHistory)
    def loadHistoryItem(item):
        import json
        if item.text() == "Add bookmark":
            url = QInputDialog.getText(None, "Add Bookmark", "Enter a URL here:", QLineEdit.Normal, browser.activeWindow().historyExtensionWidget.parentWindow().tabs.currentWidget().url().toString())
            if url[1]:
                browser.activeWindow().historyList.addItem(url[0])
                data.history.append(url[0])
                data.data.setValue("data/Bookmarks", json.dumps(data.history))
                data.data.sync()
        else:
            browser.activeWindow().tabs.currentWidget().load(QUrl.fromUserInput(item.text()))
    browser.activeWindow().historyList.itemActivated.connect(loadHistoryItem)
    mainWindow.addDockWidget(Qt.LeftDockWidgetArea, mainWindow.historyDock)
    mainWindow.tabifyDockWidget(mainWindow.sideBar, mainWindow.historyDock)
else:
    browser.activeWindow().historyDock.setVisible(not browser.activeWindow().historyDock.isVisible())
    reloadHistory()
