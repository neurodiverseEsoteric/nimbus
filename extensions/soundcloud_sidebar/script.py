if not self.isCheckable():
    self.setCheckable(True)
    self.setChecked(True)
try: self.parentWindow().soundCloudDock
except:
    self.parentWindow().soundCloudDock = QDockWidget(self.parentWindow())
    self.parentWindow().soundCloudDock.setWindowTitle("SoundCloud")
    self.parentWindow().soundCloudDock.setMaximumWidth(320)
    self.parentWindow().soundCloudDock.setContextMenuPolicy(Qt.CustomContextMenu)
    self.parentWindow().soundCloudDock.setFeatures(QDockWidget.DockWidgetClosable)
    self.parentWindow().soundCloudView = WebView(self.parentWindow().soundCloudDock)
    self.parentWindow().soundCloudView.windowCreated.connect(browser.activeWindow().addTab)
    self.parentWindow().soundCloudView.load(QUrl("http://m.soundcloud.com/"))
    self.parentWindow().soundCloudDock.setWidget(self.parentWindow().soundCloudView)
    self.parentWindow().addDockWidget(Qt.LeftDockWidgetArea, self.parentWindow().soundCloudDock)
else:
    self.parentWindow().soundCloudDock.setVisible(not self.parentWindow().soundCloudDock.isVisible())
