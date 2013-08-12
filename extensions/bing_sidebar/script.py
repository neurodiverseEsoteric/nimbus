if not self.isCheckable():
    self.setCheckable(True)
    self.setChecked(True)
try: self.parentWindow().bingDock
except:
    self.parentWindow().bingDock = QDockWidget(self.parentWindow())
    self.parentWindow().bingDock.setWindowTitle("Bing")
    self.parentWindow().bingDock.setMaximumWidth(320)
    self.parentWindow().bingDock.setContextMenuPolicy(Qt.CustomContextMenu)
    self.parentWindow().bingDock.setFeatures(QDockWidget.DockWidgetClosable)
    self.parentWindow().bingView = WebView(self.parentWindow().bingDock)
    self.parentWindow().bingView.windowCreated.connect(browser.activeWindow().addTab)
    self.parentWindow().bingView.load(QUrl("http://m.bing.com/"))
    self.parentWindow().bingDock.setWidget(self.parentWindow().bingView)
    self.parentWindow().addDockWidget(Qt.LeftDockWidgetArea, self.parentWindow().bingDock)
else:
    self.parentWindow().bingDock.setVisible(not self.parentWindow().bingDock.isVisible())
