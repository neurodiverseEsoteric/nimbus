history = data.history
mainWindow = browser.activeWindow()
mainWindow.addTab()
links = ""
sorted_history = sorted(history.items(), key=lambda x: (x[1]["last_visited"] if "last_visited" in x[1].keys() else 0), reverse=True)
for item in sorted_history:
    links += "\n        <a href='%s'>%s</a> (%s)<br>" % (QUrl.fromUserInput(item[0]).toString(),item[1]["title"],QDateTime.fromMSecsSinceEpoch(item[1]["last_visited"] if "last_visited" in item[1].keys() else 0).toString())
html = """<!DOCTYPE html>
<html>
    <head>
        <title>%s</title>
        <style type="text/css">
            body {
                font-family: sans-serif;
            }
        </style>
    </head>
    <body>
        <h1>%s</h1>%s    </body>
</html>""" % (tr("History"), tr("History"), links)
mainWindow.tabWidget().currentWidget().setHtml(html, QUrl("nimbus://history"))
