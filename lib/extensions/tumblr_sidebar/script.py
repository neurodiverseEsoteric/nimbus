name = "Tumblr"
url = "http://www.tumblr.com/dashboard"
clip = "tumblr"
ua = "Mozilla/5.0 (Linux; U; Android 2.3.5; en-us) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
if not self.isCheckable():
    self.setCheckable(True)
    self.setChecked(True)
if not self.parentWindow().hasSideBar(name):
    self.parentWindow().addSideBar(name, url, clip, ua)
else:
    self.parentWindow().toggleSideBar(name)
