name = QInputDialog.getText(self, "Name", "Enter the name of your app here:")
if name[1]:
    name = name[0]
    url = QInputDialog.getText(self, "URL", "Enter the URL of your app here:")
    if url[1]:
        url = url[0]
        common.app_maker_path = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.exists(common.app_maker_path):
            os.mkdir(common.app_maker_path)
        common.app_maker_icon_loader = WebView(None)
        common.app_maker_icon_loader.load(QUrl(url))
        common.app_maker_icon_loader.iconChanged.connect(lambda: common.app_maker_icon_loader.icon().pixmap(16, 16).save(os.path.join(common.app_maker_path, "icon.png")))
        common.app_maker_icon_loader.iconChanged.connect(common.app_maker_icon_loader.deleteLater)
        launcher_path = os.path.join(common.app_maker_path, name.lower().replace(" ", "_") + "_nimbus_app.desktop")
        try: f = open(launcher_path, "w")
        except: pass
        else:
            try: f.write("""#!/usr/bin/env xdg-open
[Desktop Entry]
Version=1.0
Terminal=false
Type=Application
Name=%(name)s
Exec=nimbus --app %(url)s
Icon=fh-nimbus
#StartupWMClass=drive.google.com""" % {"name": name, "url": url})
            except: pass
            f.close()
        os.system("chmod +x " + launcher_path)
