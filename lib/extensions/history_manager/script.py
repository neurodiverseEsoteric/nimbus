import json
history = data.data.value("data/History")
history = sorted(json.loads(history))
mainWindow = browser.activeWindow()
mainWindow.addTab()
links = ""
for item in history:
    links += "<a href='%s'>%s</a><br>" % (QUrl.fromUserInput(item).toString(),item)
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
mainWindow.tabWidget().currentWidget().setHtml(html)
