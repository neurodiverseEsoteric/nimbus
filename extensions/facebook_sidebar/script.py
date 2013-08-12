if not self.isCheckable():
    self.setCheckable(True)
    self.setChecked(True)
try: self._parent.facebookDock
except:
    try: from PySide.QtGui import QDockWidget
    except: from PyQt4.QtGui import QDockWidget
    self._parent.lastPassExtensionWidget = self
    self._parent.facebookDock = QDockWidget(self._parent)
    self._parent.facebookDock.setMaximumWidth(320)
    self._parent.facebookDock.setContextMenuPolicy(Qt.CustomContextMenu)
    self._parent.facebookDock.setFeatures(QDockWidget.DockWidgetClosable)
    self._parent.facebookView = WebView(self._parent.facebookDock)
    self._parent.facebookDock.setWindowTitle("Facebook")
    self._parent.facebookView.load(QUrl("https://m.facebook.com/"))
    self._parent.facebookDock.setWidget(self._parent.facebookView)
    self._parent.addDockWidget(Qt.LeftDockWidgetArea, self._parent.facebookDock)
else:
    self._parent.addDockWidget(Qt.LeftDockWidgetArea, self._parent.facebookDock)
    self._parent.facebookDock.setVisible(not self._parent.facebookDock.isVisible())
