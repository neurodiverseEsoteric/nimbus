import json
try: common.bookmarksDock.deleteLater()
except: pass
common.bookmarkExtensionWidget = self
mainWindow = common.bookmarkExtensionWidget._parent
bookmarks = common.data.value("data/Bookmarks")
if not bookmarks:
    bookmarks = common.settings.value("extensions/Bookmarks")
if not bookmarks:
    common.bookmarks = []
    common.data.setValue("data/Bookmarks", json.dumps(common.bookmarks))
    common.data.sync()
else:
    common.bookmarks = json.loads(bookmarks)
common.bookmarksDock = QDockWidget(mainWindow)
common.bookmarksDock.setContextMenuPolicy(Qt.CustomContextMenu)
common.bookmarksDock.setFeatures(QDockWidget.DockWidgetClosable)
common.bookmarksWidget = QListWidget(common.bookmarksDock)
common.bookmarksDock.setWindowTitle("Bookmarks")
common.bookmarksWidget.addItem("Add bookmark")
for bookmark in common.bookmarks:
    common.bookmarksWidget.addItem(bookmark)
common.bookmarksDock.setWidget(common.bookmarksWidget)
deleteAction = QAction(common.bookmarksWidget)
deleteAction.setShortcut("Del")
common.bookmarksWidget.addAction(deleteAction)
def removeBookmark():
    if common.bookmarksWidget.hasFocus():
        import json
        currentItem = common.bookmarksWidget.currentItem()
        url = currentItem.text()
        common.bookmarksWidget.takeItem(common.bookmarksWidget.row(currentItem))
        try: common.bookmarks.remove(url)
        except: pass
        common.data.setValue("data/Bookmarks", json.dumps(common.bookmarks))
        common.data.sync()
deleteAction.triggered.connect(removeBookmark)
def loadBookmark(item):
    import json
    if item.text() == "Add bookmark":
        url = QInputDialog.getText(None, "Add Bookmark", "Enter a URL here:", QLineEdit.Normal, common.bookmarkExtensionWidget._parent.tabs.currentWidget().url().toString())
        if url[1]:
            common.bookmarksWidget.addItem(url[0])
            common.bookmarks.append(url[0])
            common.data.setValue("data/Bookmarks", json.dumps(common.bookmarks))
            common.data.sync()
    else:
        common.bookmarkExtensionWidget._parent.tabs.currentWidget().load(QUrl.fromUserInput(item.text()))
common.bookmarksWidget.itemActivated.connect(loadBookmark)
mainWindow.addDockWidget(Qt.LeftDockWidgetArea, common.bookmarksDock)
