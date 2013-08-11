import json
try: common.bookmarksDock.deleteLater()
except: pass
try: from PySide.QtGui import QDockWidget
except: from PyQt4.QtGui import QDockWidget
common.bookmarkExtensionWidget = self
mainWindow = common.bookmarkExtensionWidget._parent
bookmarks = common.settings.value("extensions/Bookmarks")
if not bookmarks:
    common.bookmarks = []
    common.settings.setValue("extensions/Bookmarks", json.dumps(common.bookmarks))
    common.settings.sync()
else:
    common.bookmarks = json.loads(bookmarks)
nimbussterms = "k"
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
        common.settings.setValue("extensions/Bookmarks", json.dumps(common.bookmarks))
        common.settings.sync()
deleteAction.triggered.connect(removeBookmark)
def loadBookmark(item):
    import json
    if item.text() == "Add bookmark":
        url = QInputDialog.getText(None, "Add Bookmark", "Enter a URL here:", QLineEdit.Normal, common.bookmarkExtensionWidget._parent.tabs.currentWidget().url().toString())
        if url[1]:
            common.bookmarksWidget.addItem(url[0])
            common.bookmarks.append(url[0])
            common.settings.setValue("extensions/Bookmarks", json.dumps(common.bookmarks))
            common.settings.sync()
    else:
        common.bookmarkExtensionWidget._parent.tabs.currentWidget().load(QUrl.fromUserInput(item.text()))
common.bookmarksWidget.itemActivated.connect(loadBookmark)
mainWindow.addDockWidget(Qt.LeftDockWidgetArea, common.bookmarksDock)
