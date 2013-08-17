url = QUrl("https://m.facebook.com/")
if not self.isCheckable():
    self.setCheckable(True)
    self.setChecked(True)
try: self.parentWindow().facebookDock
except:
    self.parentWindow().facebookDock = QDockWidget(self.parentWindow())
    self.parentWindow().facebookDock.setWindowTitle("Facebook")
    self.parentWindow().facebookDock.setMaximumWidth(320)
    self.parentWindow().facebookDock.setContextMenuPolicy(Qt.CustomContextMenu)
    self.parentWindow().facebookDock.setFeatures(QDockWidget.DockWidgetClosable)
    self.parentWindow().facebookView = WebView(self.parentWindow().facebookDock)
    self.parentWindow().facebookView.windowCreated.connect(browser.activeWindow().addTab)
    self.parentWindow().facebookView.load(url)
    self.parentWindow().facebookDock.setWidget(self.parentWindow().facebookView)
    self.parentWindow().addDockWidget(Qt.LeftDockWidgetArea, self.parentWindow().facebookDock)
else:
    self.parentWindow().facebookDock.setVisible(not self.parentWindow().facebookDock.isVisible())
    if not "facebook" in self.parentWindow().facebookView.url().toString():
        self.parentWindow().facebookView.load(url)
