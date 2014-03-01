#! /usr/bin/env python3

# -----------------
# search_manager.py
# -----------------
# Author:      Daniel Sim (foxhead128)
# License:     See LICENSE.md for more details.
# Description: This module contains a dialog that allows easy management of
#              search engines. It was ported over from Ryouko
#              (http://github.com/foxhead128/ryouko).

import common
import settings
import os
import json
import custom_widgets
from translate import tr
if not common.pyqt4:
    from PyQt5.QtCore import Qt, pyqtSignal, QSize
    from PyQt5.QtGui import QCursor
    from PyQt5.QtWidgets import QMainWindow, QAction, QMessageBox, QToolBar, QLabel, QToolButton, QListWidget, QInputDialog, QDesktopWidget
    Signal = pyqtSignal
else:
    try:
        from PyQt4.QtCore import Qt, pyqtSignal, QSize
        from PyQt4.QtGui import QMainWindow, QAction, QMessageBox, QToolBar, QLabel, QToolButton, QListWidget, QInputDialog, QCursor, QDesktopWidget
        Signal = pyqtSignal
    except:
        from PySide.QtCore import Qt, Signal, QSize
        from PySide.QtGui import QMainWindow, QAction, QMessageBox, QToolBar, QLabel, QToolButton, QListWidget, QInputDialog, QCursor, QDesktopWidget

def unicode(*args, **kwargs):
    return str(*args, **kwargs)

class SearchManager(object):
    def __init__(self):
        self.reload_()
        self.searchEngines = common.search_engines
        self.currentSearch = ""
    def reload_(self):
        try: search_engines = settings.settings.value("SearchEngines")
        except: pass
        if not search_engines:
            common.search_engines = {}
            common.search_engines['DuckDuckGo'] = ["d", "https://duckduckgo.com/?q=%s"]
            common.search_engines['Wikipedia'] = ["w", "https://en.wikipedia.org/w/index.php?search=%s&title=Special:Search"]
            common.search_engines['Wiktionary'] = ["wk", "http://en.wiktionary.org/w/index.php?search=%s&title=Special:Search"]
            common.search_engines['Wikimedia Commons'] = ["wc", "http://commons.wikimedia.org/w/index.php?search=%s&title=Special:Search"]
            common.search_engines['Google'] = ["g", "http://www.google.com/search?client=nimbus&q=%s"]
            common.search_engines['Google Image Search'] = ["i", "http://www.google.com/search?client=nimbus&tbm=isch&q=%s"]
            common.search_engines['Google Music Search'] = ["m", "http://www.googlemusicsearch.com/search?q=%s"]
            common.search_engines['Google Translate'] = ["tr", "http://translate.google.com/#auto/en/%s"]
            common.search_engines['Thesaurus.com'] = ["t", "http://thesaurus.com/browse/%s"]
            common.search_engines['Bing'] = ["b", "http://www.bing.com/search?q=%s"]
            common.search_engines['Baidu'] = ["ba", "http://www.baidu.com/s?wd=%s"]
            common.search_engines['Yahoo'] = ["y", "http://search.yahoo.com/search?p=%s"]
            common.search_engines['YouTube'] = ["yt", "http://www.youtube.com/results?search_query=%s"]
            common.search_engines["GitHub"] = ["gh", "https://github.com/search?q=%s&ref=cmdform"]
            common.search_engines["Stack Overflow"] = ["so", "http://stackoverflow.com/search?q=%s"]
            common.search_engines["Wolfram|Alpha"] = ["wa", "http://www.wolframalpha.com/input/?i=%s"]
            common.search_engines['deviantART'] = ["da", "http://www.deviantart.com/?q=%s"]
            common.search_engines["TV Tropes"] = ["tv", "http://tvtropes.org/pmwiki/search_result.php?cx=partner-pub-6610802604051523:amzitfn8e7v&cof=FORID:10&ie=ISO-8859-1&q=%s"]
            common.search_engines['A-Z Lyrics'] = ["azl", "http://search.azlyrics.com/search.php?q=%s"]
            common.search_engines['MetroLyrics'] = ["mtl", "http://www.metrolyrics.com/search?search=%s"]
            common.search_engines['Openclipart'] = ["oca", "http://openclipart.org/search/?query=%s"]
            common.search_engines['Safebooru'] = ["sb", "http://safebooru.org/index.php?page=post&s=list&tags=%s"]
            common.search_engines['Gigablast'] = ["gb", "https://www.gigablast.com/search?q=%s"]
            settings.settings.setValue("SearchEngines", json.dumps(common.search_engines))
            settings.settings.sync()
        else:
            common.search_engines = json.loads(search_engines)
    def add(self, name, expression, keyword=""):
        try:
            common.search_engines[name] = [keyword, expression]
            settings.settings.setValue("SearchEngines", json.dumps(common.search_engines))
            settings.settings.sync()
        except:
            pass
    def change(self, name):
        try: self.currentSearch = common.search_engines[name][1]
        except: pass
        else:
            settings.settings.setValue("general/Search", self.currentSearch)
            settings.settings.setValue("SearchEngines", json.dumps(common.search_engines))
            settings.settings.sync()
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
        self.entryBar.setIconSize(QSize(16, 16))
        self.entryBar.setStyleSheet(common.blank_toolbar)
        self.entryBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.entryBar.setMovable(False)
        self.addToolBar(self.entryBar)

        eLabel = QLabel(" " + tr('New expression:'), self)
        self.entryBar.addWidget(eLabel)
        self.expEntry = custom_widgets.LineEdit(self)
        self.expEntry.returnPressed.connect(self.addSearch)
        self.entryBar.addWidget(self.expEntry)
        self.addSearchButton = QToolButton(self)
        self.addSearchButton.setText(tr("Add"))
        self.addSearchButton.setIcon(common.complete_icon("list-add"))
        self.addSearchButton.clicked.connect(self.addSearch)
        self.entryBar.addWidget(self.addSearchButton)

        self.engineList = QListWidget(self)
        self.engineList.setAlternatingRowColors(True)
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
        keys = self.searchManager.searchEngines.keys()
        if type(keys) is not list:
            keys = [key for key in keys]
        for name in sorted(keys):
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
            if name[1] and name[0] != "":
                name = name[0]
                keyword = QInputDialog.getText(self, tr('Query'), tr('Enter a keyword here:'))[0]
                self.searchManager.add(name, self.expEntry.text(), keyword)
                self.expEntry.clear()
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
