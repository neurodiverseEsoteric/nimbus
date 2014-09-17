mainWindow = browser.activeWindow()
try: mainWindow.counter
except:
    mainWindow.counter = 0
url = mainWindow.tabWidget().currentWidget().url().toString()
title = mainWindow.tabWidget().currentWidget().windowTitle()
if mainWindow.counter == 0:
    mainWindow.locationBar.setEditText("[url=%s]%s[/url]" % (url, title))
elif mainWindow.counter == 1:
    mainWindow.locationBar.setEditText("[url][img]%s[/img][/url]" % (url,))
#elif mainWindow.counter == 2:
#    mainWindow.locationBar.setEditText("[img]" + url + "[/img]")
mainWindow.counter += 1
if mainWindow.counter > 1:
    mainWindow.counter = 0
