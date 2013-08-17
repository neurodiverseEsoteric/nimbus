url = QUrl("http://m.wikipedia.org/")
if not self.isCheckable():
    self.setCheckable(True)
    self.setChecked(True)
try: self.parentWindow().wikipediaDock
except:
    self.parentWindow().wikipediaDock = QDockWidget(self.parentWindow())
    self.parentWindow().wikipediaDock.setWindowTitle("Wikipedia")
    self.parentWindow().wikipediaDock.setMaximumWidth(320)
    self.parentWindow().wikipediaDock.setContextMenuPolicy(Qt.CustomContextMenu)
    self.parentWindow().wikipediaDock.setFeatures(QDockWidget.DockWidgetClosable)
    self.parentWindow().wikipediaView = WebView(self.parentWindow().wikipediaDock)
    self.parentWindow().wikipediaView.windowCreated.connect(browser.activeWindow().addTab)
    self.parentWindow().wikipediaView.load(url)
    self.parentWindow().wikipediaDock.setWidget(self.parentWindow().wikipediaView)
    self.parentWindow().addDockWidget(Qt.LeftDockWidgetArea, self.parentWindow().wikipediaDock)
else:
    self.parentWindow().wikipediaDock.setVisible(not self.parentWindow().wikipediaDock.isVisible())
    if not "wikipedia" in self.parentWindow().wikipediaView.url().toString():
        self.parentWindow().wikipediaView.load(url)
