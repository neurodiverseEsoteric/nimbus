url = QUrl("http://m.baidu.com/")
if not self.isCheckable():
    self.setCheckable(True)
    self.setChecked(True)
try: self.parentWindow().baiduDock
except:
    self.parentWindow().baiduDock = QDockWidget(self.parentWindow())
    self.parentWindow().baiduDock.setWindowTitle("Baidu")
    self.parentWindow().baiduDock.setMaximumWidth(320)
    self.parentWindow().baiduDock.setContextMenuPolicy(Qt.CustomContextMenu)
    self.parentWindow().baiduDock.setFeatures(QDockWidget.DockWidgetClosable)
    self.parentWindow().baiduView = WebView(self.parentWindow().baiduDock)
    self.parentWindow().baiduView.windowCreated.connect(browser.activeWindow().addTab)
    self.parentWindow().baiduView.load(url)
    self.parentWindow().baiduDock.setWidget(self.parentWindow().baiduView)
    self.parentWindow().addDockWidget(Qt.LeftDockWidgetArea, self.parentWindow().baiduDock)
else:
    self.parentWindow().baiduDock.setVisible(not self.parentWindow().baiduDock.isVisible())
    if not "baidu" in self.parentWindow().baiduView.url().toString():
        self.parentWindow().baiduView.load(url)
