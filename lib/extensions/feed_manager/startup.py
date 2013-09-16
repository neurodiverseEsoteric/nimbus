import json
try: common.feeds
except:
    feeds = data.data.value("data/Feeds")
    if not feeds:
        common.feeds = []
        data.data.setValue("data/Feeds", json.dumps(common.feeds))
        data.data.sync()
    else:
        common.feeds = json.loads(feeds)
self.toolBar.widgetForAction(self.feedMenuButton).setPopupMode(QToolButton.MenuButtonPopup)
self.feedMenuButton.setCheckable(True)
def toggleFeedsDock():
    try: browser.activeWindow().feedsDock
    except:
        mainWindow = browser.activeWindow()
        mainWindow.feedsDock = QDockWidget(mainWindow)
        mainWindow.feedsDock.setContextMenuPolicy(Qt.CustomContextMenu)
        mainWindow.feedsDock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        mainWindow.feedsList = QListWidget(browser.activeWindow().feedsDock)
        mainWindow.feedsDock.setWindowTitle("Feeds")
        mainWindow.feedsList.addItem("Add feed")
        for feed in common.feeds:
            mainWindow.feedsList.addItem(feed)
        mainWindow.feedsDock.setWidget(browser.activeWindow().feedsList)
        deleteAction = QAction(browser.activeWindow().feedsList)
        deleteAction.setShortcut("Del")
        mainWindow.feedsList.addAction(deleteAction)
        def removeBookmark():
            if browser.activeWindow().feedsList.hasFocus():
                import json
                currentItem = browser.activeWindow().feedsList.currentItem()
                url = currentItem.text()
                browser.activeWindow().feedsList.takeItem(browser.activeWindow().feedsList.row(currentItem))
                try: common.feeds.remove(url)
                except: pass
                data.data.setValue("data/Feeds", json.dumps(common.feeds))
                data.data.sync()
        deleteAction.triggered.connect(removeBookmark)
        def loadFeed(item):
            import json
            if item.text() == "Add feed":
                url = QInputDialog.getText(None, "Add Feed", "Enter a URL here:", QLineEdit.Normal, browser.activeWindow().tabWidget().currentWidget().url().toString())
                if url[1]:
                    browser.activeWindow().feedsList.addItem(url[0])
                    common.feeds.append(url[0])
                    data.data.setValue("data/Feeds", json.dumps(common.feeds))
                    data.data.sync()
            else:
                browser.activeWindow().tabs.currentWidget().load(QUrl.fromUserInput(item.text()))
        browser.activeWindow().feedsList.itemActivated.connect(loadFeed)
        mainWindow.addDockWidget(Qt.LeftDockWidgetArea, mainWindow.feedsDock)
        mainWindow.tabifyDockWidget(mainWindow.sideBar, mainWindow.feedsDock)
    else:
        browser.activeWindow().feedsDock.setVisible(not browser.activeWindow().feedsDock.isVisible())
        browser.activeWindow().feedsList.clear()
        browser.activeWindow().feedsList.addItem("Add feed")
        for feed in sorted(common.feeds):
            browser.activeWindow().feedsList.addItem(feed)
self.feedMenuButton.triggered.connect(toggleFeedsDock)
