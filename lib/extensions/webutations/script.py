try: common.webutations
except: common.webutations = os.path.join(settings.extensions_folder, self.name)
if not common.webutations in sys.path:
    sys.path.append(common.webutations)

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
if score and mx:
    scor = score.text + "/" + mx.text
else:
    scor = "Unknown domain"
#print(scor)
currentWidget.page().mainFrame().evaluateJavaScript("\nwindow.alert(\'Webutation: " + scor + "\');")
if not (score and mx):
    mainWindow.addTab(url=newurl)
