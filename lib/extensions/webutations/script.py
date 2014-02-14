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
sources = ["google-safebrowsing", "antivirus", "norton-safeweb", "webutation-reviews", "wot", "wikipedia", "child-safety"]
data = []
for source in sources:
    try: data.append(soup.find("dt", {"id": source}).find("span", {"class": "pull-right"})["class"])
    except: data.append("Unknown")
if score and mx:
    scor = score.text + "/" + mx.text
    try: data = [source[1].split("-")[-1].title() if len(source[1].split("-")[-1]) > 2 else "Safe" for source in data]
    except: pass
else:
    scor = "Unknown domain"
print(data + [scor,])
QMessageBox.information(self, tr("Webutation"), "Google Safebrowsing: %s\nWebsite Antivirus: %s\nNorton Safeweb: %s\n\nWebutation Reviews: %s\nWOT (Web of Trust): %s\nWikipedia Trust Links: %s\nG-Rated / Child Safety: %s\n\n" "Webutation: %s" % tuple(data + [scor,]))
if not (score and mx):
    mainWindow.addTab(url=newurl)
