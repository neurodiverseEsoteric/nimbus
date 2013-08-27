name = QInputDialog.getText(self, "Name", "Enter the name of your sidebar here:")
if name[1]:
    name = name[0]
    url = QInputDialog.getText(self, "URL", "Enter the URL of your sidebar here:")
    if url[1]:
        url = url[0]
        path = os.path.join(settings.extensions_folder, name.lower() + "_sidebar")
        if not os.path.exists(path):
            os.mkdir(path)
        try: f = open(os.path.join(path, "script.py"), "w")
        except: pass
        else:
            try: f.write("""name = "%(name)s"
url = "%(url)s"
clip = "%(clip)s"
ua = None
if not self.isCheckable():
    self.setCheckable(True)
    self.setChecked(True)
if not self.parentWindow().hasSideBar(name):
    self.parentWindow().addSideBar(name, url, clip, ua)
else:
    self.parentWindow().toggleSideBar(name)""" % {"name": name, "url": url, "clip": url.split(".")[1]})
            except: pass
            f.close()
