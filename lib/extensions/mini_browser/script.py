name = "Mini Browser"
url = ""
clip = ""
ua = "Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19"
if not self.isCheckable():
    self.setCheckable(True)
    self.setChecked(True)
if not self.parentWindow().hasSideBar(name):
    self.parentWindow().addSideBar(name, url, clip, ua)
    container = self.parentWindow().getSideBar(name)["sideBar"].widget()
    toolBar = self.parentWindow().getSideBar(name)["sideBar"].toolBar
    self.parentWindow().miniLocationBar = QLineEdit(container)
    focusMiniLocationBarAction = QAction(self.parentWindow())
    focusMiniLocationBarAction.setShortcuts(["Alt+Shift+L", "Alt+Shift+D"])
    focusMiniLocationBarAction.triggered.connect(self.parentWindow().miniLocationBar.setFocus)
    focusMiniLocationBarAction.triggered.connect(self.parentWindow().miniLocationBar.selectAll)
    self.parentWindow().addAction(focusMiniLocationBarAction)
    toolBar.addWidget(self.parentWindow().miniLocationBar)
    self.parentWindow().miniLocationBar.returnPressed.connect(lambda: browser.activeWindow().getSideBar("Mini Browser")["sideBar"].webView.load(QUrl.fromUserInput(browser.activeWindow().miniLocationBar.text())))
    self.parentWindow().getSideBar("Mini Browser")["sideBar"].webView.urlChanged.connect(lambda x: browser.activeWindow().miniLocationBar.setText(x.toString()))
else:
    self.parentWindow().toggleSideBar(name)
