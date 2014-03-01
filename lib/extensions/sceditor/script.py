name = "SCEditor"
url = QUrl.fromUserInput(os.path.join(settings.extensions_folder, self.name, "index.html")).toString()
clip = "youtube"
if not self.isCheckable():
    self.setCheckable(True)
    self.setChecked(True)
if not self.parentWindow().hasSideBar(name):
    self.parentWindow().addSideBar(name, url, clip, toolbar=False)
    self.parentWindow().addDockWidget(Qt.BottomDockWidgetArea, self.parentWindow().getSideBar(name)["sideBar"])
    self.parentWindow().getSideBar(name)["radio"] = False
else:
    self.parentWindow().toggleSideBar(name)
