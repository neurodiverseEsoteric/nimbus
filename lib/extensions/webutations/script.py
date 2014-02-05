#!/usr/bin/env python

try: common.webutations
except: common.webutations = os.path.join(settings.extensions_folder, "webutations")
if not common.webutations in sys.path:
    sys.path.append(common.webutations)

import urllib.request
import io
from bs4 import BeautifulSoup

mainWindow = browser.activeWindow()
currentWidget = mainWindow.tabWidget().currentWidget()
host = currentWidget.url().host()
newurl = "http://www.webutations.net/go/review/" + host.replace("www.", "")
stdout_handle = os.popen("wget -S -O - " + newurl)
html = stdout_handle.read()

soup = BeautifulSoup(io.StringIO(html))
score = soup.find("span", {"class": "score"})
mx = soup.find("span", {"class": "max"})
scor = score.text + "/" + mx.text
print(scor)
currentWidget.page().mainFrame().evaluateJavaScript("\nwindow.alert(\'Webutation: " + scor + "\');")
