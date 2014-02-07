name = "PPIrC Web IRC"
url = "http://webchat.ppirc.net/"
clip = "ppirc"
ua = "Mozilla/5.0 (Linux; U; Android 2.3.5; en-us; HTC Vision Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
style = os.path.join(settings.extensions_folder, self.name, "style.css")
if not self.isCheckable():
    self.setCheckable(True)
    self.setChecked(True)
if not self.parentWindow().hasSideBar(name):
    self.parentWindow().addSideBar(name, url, clip, ua, style=style)
else:
    self.parentWindow().toggleSideBar(name)
