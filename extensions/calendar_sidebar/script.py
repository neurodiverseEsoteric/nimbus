if not self.isCheckable():
    self.setCheckable(True)
    self.setChecked(True)
try: self.parentWindow().calendarDock
except:
    self.parentWindow().calendarDock = QDockWidget(self.parentWindow())
    self.parentWindow().calendarDock.setWindowTitle("Calendar")
    self.parentWindow().calendarDock.setContextMenuPolicy(Qt.CustomContextMenu)
    self.parentWindow().calendarDock.setFeatures(QDockWidget.DockWidgetClosable)
    self.parentWindow().calendarView = QCalendarWidget(self.parentWindow().calendarDock)
    self.parentWindow().calendarDock.setWidget(self.parentWindow().calendarView)
    self.parentWindow().addDockWidget(Qt.LeftDockWidgetArea, self.parentWindow().calendarDock)
else:
    self.parentWindow().calendarDock.setVisible(not self.parentWindow().calendarDock.isVisible())
