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
self.addBookmarkButton = QToolButton(self)
self.addBookmarkButton.setText(tr("Add Bookmark"))
self.addBookmarkButton.setIcon(common.complete_icon("bookmark-add"))
self.toolBar.insertWidget(self.feedMenuButton, self.addBookmarkButton)
def addBookmark():
    url = QInputDialog.getText(None, "Add Bookmark", "Enter a URL here:", QLineEdit.Normal, browser.activeWindow().tabs.currentWidget().url().toString())
    if url[1]:
        common.bookmarks.append(url[0])
        data.data.setValue("data/Bookmarks", json.dumps(common.bookmarks))
        data.data.sync()
self.addBookmarkButton.clicked.connect(addBookmark)
