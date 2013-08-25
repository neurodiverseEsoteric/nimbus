#! /usr/bin/env python3

import common
import settings
import os
import json
from translate import tr
try:
    from PyQt4.QtCore import Qt, pyqtSignal
    from PyQt4.QtGui import QMainWindow, QAction, QMessageBox, QToolBar, QLineEdit, QLabel, QPushButton, QListWidget, QInputDialog, QCursor, QDesktopWidget
    Signal = pyqtSignal
except:
    from PySide.QtCore import Qt, Signal
    from PySide.QtGui import QMainWindow, QAction, QMessageBox, QToolBar, QLineEdit, QLabel, QPushButton, QListWidget, QInputDialog, QCursor, QDesktopWidget

def unicode(*args, **kwargs):
    return str(*args, **kwargs)

class SearchManager(object):
    def __init__(self):
        self.reload_()
        self.searchEngines = common.search_engines
        self.currentSearch = ""
    def reload_(self):
        search_engines = settings.settings.value("SearchEngines")
        if not search_engines:
            common.search_engines = {}
            common.search_engines['DuckDuckGo'] = ["d", "https://duckduckgo.com/?q=%s"]
            common.search_engines['Wikipedia'] = ["w", "https://en.wikipedia.org/w/index.php?search=%s&title=Special:Search"]
            common.search_engines['Wiktionary'] = ["wk", "http://en.wiktionary.org/w/index.php?search=%s&title=Special:Search"]
            common.search_engines['Google'] = ["g", "http://www.google.com/search?client=nimbus&q=%s"]
            common.search_engines['Google Image Search'] = ["i", "http://www.google.com/search?client=nimbus&tbm=isch&q=%s"]
            common.search_engines['Google Music Search'] = ["m", "http://www.googlemusicsearch.com/search?q=%s"]
            common.search_engines['Google Translate'] = ["tr", "http://translate.google.com/#auto/en/%s"]
            common.search_engines['Thesaurus.com'] = ["t", "http://thesaurus.com/browse/%s"]
            common.search_engines['Bing'] = ["b", "http://www.bing.com/search?q=%s"]
            common.search_engines['Yahoo'] = ["y", "http://search.yahoo.com/search?p=%s"]
            common.search_engines['deviantART'] = ["da", "http://www.deviantart.com/?q=%s"]
            common.search_engines['A-Z Lyrics'] = ["azl", "http://search.azlyrics.com/search.php?q=%s"]
            common.search_engines['MetroLyrics'] = ["mtl", "http://www.metrolyrics.com/search?search=%s"]
            common.search_engines['Openclipart'] = ["oca", "http://openclipart.org/search/?query=%s"]
            settings.settings.setValue("SearchEngines", json.dumps(common.search_engines))
            settings.settings.sync()
        else:
            common.search_engines = json.loads(search_engines)
    def add(self, name, expression, keyword=""):
        try:
            common.search_engines[name] = [keyword, expression]
        except:
            traceback.print_exc()
    def change(self, name):
        try: self.currentSearch = common.search_engines[name][1]
        except: pass
        else:
            settings.settings.setValue("general/Search", self.currentSearch)
    def remove(self, name):
        try: del common.search_engines[name]
        except: pass
        settings.settings.setValue("SearchEngines", json.dumps(common.search_engines))
        settings.settings.sync()

class SearchEditor(QMainWindow):
    searchChanged = Signal(str)
    searchManager = SearchManager()
    def __init__(self, parent=None):
        super(SearchEditor, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.parent = parent
        self.setWindowTitle(tr('Search Editor'))
        self.styleSheet = "QMainWindow { background: palette(window); border: 1px solid palette(dark); }"
        self.setStyleSheet(self.styleSheet)
        try: self.setWindowIcon(common.app_icon)
        except: pass

        closeWindowAction = QAction(self)
        closeWindowAction.setShortcuts(["Ctrl+W", "Ctrl+Shift+K"])
        closeWindowAction.triggered.connect(self.close)
        self.addAction(closeWindowAction)

        self.entryBar = QToolBar(self)
        self.entryBar.setStyleSheet(common.blank_toolbar)
        self.entryBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.entryBar.setMovable(False)
        self.addToolBar(self.entryBar)

        eLabel = QLabel(" " + tr('New expression:'), self)
        self.entryBar.addWidget(eLabel)
        self.expEntry = QLineEdit(self)
        self.expEntry.returnPressed.connect(self.addSearch)
        self.entryBar.addWidget(self.expEntry)
        self.addSearchButton = QPushButton(common.complete_icon("list-add"), "", self)
        self.addSearchButton.clicked.connect(self.addSearch)
        self.entryBar.addWidget(self.addSearchButton)

        self.engineList = QListWidget(self)
        self.engineList.itemClicked.connect(self.applySearch)
        self.engineList.itemActivated.connect(self.applySearch)
        self.engineList.itemActivated.connect(self.close)
        self.setCentralWidget(self.engineList)

        self.takeSearchAction = QAction(self)
        self.takeSearchAction.triggered.connect(self.takeSearch)
        self.takeSearchAction.setShortcut("Del")
        self.addAction(self.takeSearchAction)

        self.hideAction = QAction(self)
        self.hideAction.triggered.connect(self.hide)
        self.hideAction.setShortcut("Esc")
        self.addAction(self.hideAction)

        self.reload_()

    def show(self):
        self.setVisible(True)
        y = QDesktopWidget()
        self.move(max(0, QCursor.pos().x() - self.width()), min(QCursor.pos().y(), y.height() - self.height()))
        y.deleteLater()

    def primeDisplay(self):
        self.reload_()
        self.expEntry.setFocus()

    def focusOutEvent(self, e):
        e.accept()
        self.hide()

    def reload_(self):
        self.engineList.clear()
        for name in self.searchManager.searchEngines:
            keyword = "None"
            if self.searchManager.searchEngines[name][0] != "":
                keyword = self.searchManager.searchEngines[name][0]
            self.engineList.addItem("%s\nKeyword: %s" % (name, keyword))
        for item in range(0, self.engineList.count()):
            if self.searchManager.searchEngines[unicode(self.engineList.item(item).text()).split("\n")[0]][1] == self.searchManager.currentSearch:
                self.engineList.setCurrentItem(self.engineList.item(item))
                self.searchChanged.emit(str(unicode(self.engineList.item(item).text()).split("\n")[0]))
                break

    def addSearch(self):
        if "%s" in self.expEntry.text():
            name = QInputDialog.getText(self, tr('Query'), tr('Enter a name here:'))
            if name and name != "":
                keyword = QInputDialog.getText(self, tr('Query'), tr('Enter a keyword here:'))
                self.searchManager.add(name, self.expEntry.text(), keyword)
            self.reload_()
        else:
            QMessageBox.warning(self, tr('Error'), tr('Search expression must contain a <b>%s</b> to indicate the search terms.'))

    def applySearch(self, item=False, old=False):
        if item:
            try: unicode(item.text()).split("\n")[0]
            except:
                notificationMessage(tr('searchError'))
            else:
                self.searchManager.change(unicode(item.text()).split("\n")[0])
        if item != None:
            self.searchChanged.emit(str(unicode(item.text()).split("\n")[0]))

    def takeSearch(self):
        self.searchManager.remove(unicode(self.engineList.currentItem().text()).split("\n")[0])
        self.reload_()
