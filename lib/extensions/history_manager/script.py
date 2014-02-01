history = data.history
mainWindow = browser.activeWindow()
mainWindow.addTab()
links = ""
for item in sorted(history.keys()):
    links += "<a href='%s'>%s</a><br>" % (QUrl.fromUserInput(item).toString(),history[item]["title"])
html = """<!DOCTYPE html>
<html>
    <head>
        <title>%s</title>
    </head>
    <body>
        <h1>%s</h1>
        %s
    </body>
</html>""" % (tr("History"), tr("History"), links)
mainWindow.tabWidget().currentWidget().setHtml(html, QUrl("nimbus://history"))
