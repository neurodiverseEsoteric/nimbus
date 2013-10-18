import json
try: common.bookmarks
except:
    bookmarks = data.data.value("data/Bookmarks")
    if not bookmarks:
        bookmarks = common.settings.value("extensions/Bookmarks")
    if not bookmarks:
        common.bookmarks = []
        data.data.setValue("data/Bookmarks", json.dumps(common.bookmarks))
        data.data.sync()
    else:
        common.bookmarks = json.loads(bookmarks)
name = "Bookmarks"
clip = "about:blank"
ua = None
if not self.isCheckable():
    self.setCheckable(True)
    self.setChecked(True)
if not self.parentWindow().hasSideBar(name):
    self.parentWindow().addSideBar(name, "about:blank", clip, ua)
else:
    self.parentWindow().toggleSideBar(name)
    html = """<!DOCTYPE html>
<html>
    <body>
        %s
    </body>
</html>""" % ("\n".join(["<a target=\"_blank\" href=\"%s\">%s</a>" % (url, url) for url in common.bookmarks]),)
    print(html)
    self.parentWindow().getSideBar(name).webView.setHtml(html)
