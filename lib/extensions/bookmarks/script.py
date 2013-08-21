if not self.isCheckable():
    self.setCheckable(True)
    self.setChecked(True)
import json
try: common.bookmarks
except:
    bookmarks = data.data.value("data/Bookmarks")
    if not bookmarks:
        bookmarks = common.settings.value("extensions/Bookmarks")
    if not bookmarks:
        common.bookmarks = []
        data.data.setValue("data/Bookmarks", json.dumps(common.bookmarks))
        data.data.sync()
    else:
        common.bookmarks = json.loads(bookmarks)
try: browser.activeWindow().bookmarksDock
except:
    mainWindow = browser.activeWindow()
    mainWindow.bookmarksExtensionWidget = self
    mainWindow.bookmarksDock = QDockWidget(mainWindow)
    mainWindow.bookmarksDock.setContextMenuPolicy(Qt.CustomContextMenu)
    mainWindow.bookmarksDock.setFeatures(QDockWidget.DockWidgetClosable)
    mainWindow.bookmarksList = QListWidget(browser.activeWindow().bookmarksDock)
    mainWindow.bookmarksDock.setWindowTitle("Bookmarks")
    mainWindow.bookmarksList.addItem("Add bookmark")
    for bookmark in common.bookmarks:
        mainWindow.bookmarksList.addItem(bookmark)
    mainWindow.bookmarksDock.setWidget(browser.activeWindow().bookmarksList)
    deleteAction = QAction(browser.activeWindow().bookmarksList)
    deleteAction.setShortcut("Del")
    mainWindow.bookmarksList.addAction(deleteAction)
    def removeBookmark():
        if browser.activeWindow().bookmarksList.hasFocus():
            import json
            currentItem = browser.activeWindow().bookmarksList.currentItem()
            url = currentItem.text()
            browser.activeWindow().bookmarksList.takeItem(browser.activeWindow().bookmarksList.row(currentItem))
            try: common.bookmarks.remove(url)
            except: pass
            data.data.setValue("data/Bookmarks", json.dumps(common.bookmarks))
            data.data.sync()
    deleteAction.triggered.connect(removeBookmark)
    def loadBookmark(item):
        import json
        if item.text() == "Add bookmark":
            url = QInputDialog.getText(None, "Add Bookmark", "Enter a URL here:", QLineEdit.Normal, browser.activeWindow().bookmarksExtensionWidget.parentWindow().tabs.currentWidget().url().toString())
            if url[1]:
                browser.activeWindow().bookmarksList.addItem(url[0])
                common.bookmarks.append(url[0])
                data.data.setValue("data/Bookmarks", json.dumps(common.bookmarks))
                data.data.sync()
        else:
            browser.activeWindow().tabs.currentWidget().load(QUrl.fromUserInput(item.text()))
    browser.activeWindow().bookmarksList.itemActivated.connect(loadBookmark)
    mainWindow.addDockWidget(Qt.LeftDockWidgetArea, mainWindow.bookmarksDock)
    mainWindow.tabifyDockWidget(mainWindow.sideBar, mainWindow.bookmarksDock)
else:
    browser.activeWindow().bookmarksDock.setVisible(not browser.activeWindow().bookmarksDock.isVisible())
    browser.activeWindow().bookmarksList.clear()
    browser.activeWindow().bookmarksList.addItem("Add bookmark")
    for bookmark in common.bookmarks:
        browser.activeWindow().bookmarksList.addItem(bookmark)
