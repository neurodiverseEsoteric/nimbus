if not self.isCheckable():
    self.setCheckable(True)
    self.setChecked(True)
try: self.parent().facebookDock
except:
    def addTab(webView):
        for window in common.windows[::-1]:
            if window.isActiveWindow():
                window.addTab(webView=webView, focus=True)
    self.addTab = addTab
    try: from PySide.QtGui import QDockWidget
    except: from PyQt4.QtGui import QDockWidget
    self.parent().lastPassExtensionWidget = self
    self.parent().facebookDock = QDockWidget(self.parent())
    self.parent().facebookDock.setWindowTitle("Facebook")
    self.parent().facebookDock.setMaximumWidth(320)
    self.parent().facebookDock.setContextMenuPolicy(Qt.CustomContextMenu)
    self.parent().facebookDock.setFeatures(QDockWidget.DockWidgetClosable)
    self.parent().facebookView = WebView(self.parent().facebookDock)
    self.parent().facebookView.windowCreated.connect(addTab)
    self.parent().facebookView.load(QUrl("https://m.facebook.com/"))
    self.parent().facebookDock.setWidget(self.parent().facebookView)
    self.parent().addDockWidget(Qt.LeftDockWidgetArea, self.parent().facebookDock)
else:
    self.parent().addDockWidget(Qt.LeftDockWidgetArea, self.parent().facebookDock)
    self.parent().facebookDock.setVisible(not self.parent().facebookDock.isVisible())
