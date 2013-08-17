url = QUrl("http://mobile.weather.gov/")
if not self.isCheckable():
    self.setCheckable(True)
    self.setChecked(True)
try: self.parentWindow().weatherDock
except:
    self.parentWindow().weatherDock = QDockWidget(self.parentWindow())
    self.parentWindow().weatherDock.setWindowTitle("Weather")
    self.parentWindow().weatherDock.setMaximumWidth(320)
    self.parentWindow().weatherDock.setContextMenuPolicy(Qt.CustomContextMenu)
    self.parentWindow().weatherDock.setFeatures(QDockWidget.DockWidgetClosable)
    self.parentWindow().weatherView = WebView(self.parentWindow().weatherDock)
    self.parentWindow().weatherView.windowCreated.connect(browser.activeWindow().addTab)
    self.parentWindow().weatherView.load(url)
    self.parentWindow().weatherDock.setWidget(self.parentWindow().weatherView)
    self.parentWindow().addDockWidget(Qt.LeftDockWidgetArea, self.parentWindow().weatherDock)
else:
    self.parentWindow().weatherDock.setVisible(not self.parentWindow().weatherDock.isVisible())
    if not "weather" in self.parentWindow().weatherView.url().toString():
        self.parentWindow().weatherView.load(url)
