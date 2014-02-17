name = QInputDialog.getText(self, "Name", "Enter the name of your sidebar here:")
if name[1]:
    name = name[0]
    url = QInputDialog.getText(self, "URL", "Enter the URL of your sidebar here:")
    if url[1]:
        url = url[0]
        common.sidebar_maker_path = os.path.join(settings.extensions_folder, name.lower().replace(" ", "_") + "_sidebar")
        if not os.path.exists(common.sidebar_maker_path):
            os.mkdir(common.sidebar_maker_path)
        common.sidebar_maker_icon_loader = WebView(None)
        common.sidebar_maker_icon_loader.load(QUrl(url))
        common.sidebar_maker_icon_loader.iconChanged.connect(lambda: common.sidebar_maker_icon_loader.icon().pixmap(16, 16).save(os.path.join(common.sidebar_maker_path, "icon.png")))
        common.sidebar_maker_icon_loader.iconChanged.connect(common.sidebar_maker_icon_loader.deleteLater)
        try: f = open(os.path.join(common.sidebar_maker_path, "script.py"), "w")
        except: pass
        else:
            try: f.write("""name = "%(name)s"
url = "%(url)s"
clip = "%(clip)s"
ua = "Mozilla/5.0 (Linux; U; Android 2.3.5; en-us) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
style1 = os.path.join(settings.extensions_folder, self.name, "style.css")
style = style1 if os.path.isfile(style1) else None
if not self.isCheckable():
    self.setCheckable(True)
    self.setChecked(True)
if not self.parentWindow().hasSideBar(name):
    self.parentWindow().addSideBar(name, url, clip, ua, style=style)
else:
    self.parentWindow().toggleSideBar(name)""" % {"name": name, "url": url, "clip": url.split(".")[1]})
            except: pass
            f.close()
