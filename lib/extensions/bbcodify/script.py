mainWindow = browser.activeWindow()
try: mainWindow.counter
except:
    mainWindow.counter = 0
url = mainWindow.tabWidget().currentWidget().url().toString()
title = mainWindow.tabWidget().currentWidget().windowTitle()
if mainWindow.counter == 0:
    mainWindow.locationBar.setEditText("[URL=%s]%s[/URL]" % (url, title))
elif mainWindow.counter == 1:
    mainWindow.locationBar.setEditText("[IMG]%s[/IMG]" % (url,))
elif mainWindow.counter == 2:
    mainWindow.locationBar.setEditText("[URL=%s][IMG]%s[/IMG][/URL]" % (url, url))
mainWindow.counter += 1
if mainWindow.counter > 2:
    mainWindow.counter = 0
