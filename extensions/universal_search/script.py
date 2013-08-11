import json
nimbuskws = common.settings.value("extensions/UniversalSearch")
if not nimbuskws:
    common.nimbuskws = {}
    common.nimbuskws['d '] = "https://duckduckgo.com/?q=%s"
    common.nimbuskws['w '] = "https://en.wikipedia.org/w/index.php?search=%s&title=Special%3ASearch"
    common.nimbuskws['wk '] = "http://en.wiktionary.org/w/index.php?search=%s&title=Special:Search"
    common.nimbuskws['g '] = "http://www.google.com/search?q=%s"
    common.nimbuskws['i '] = "http://www.google.com/search?tbm=isch&q=%s"
    common.nimbuskws['m '] = "http://www.googlemusicsearch.com/search?q=%s"
    common.nimbuskws['tr '] = "http://translate.google.com/#auto/en/%s"
    common.nimbuskws['t '] = "http://thesaurus.com/browse/%s"
    common.nimbuskws['b '] = "http://www.bing.com/search?q=%s"
    common.nimbuskws['y '] = "http://search.yahoo.com/search?p=%s"
    common.nimbuskws['da '] = "http://www.deviantart.com/?q=%s"
    common.nimbuskws['azl '] = "http://search.azlyrics.com/search.php?q=%s"
    common.nimbuskws['mtl '] = "http://www.metrolyrics.com/search?search=%s"
    common.nimbuskws['oca '] = "http://openclipart.org/search/?query=%s"
    common.settings.setValue("extensions/UniversalSearch", json.dumps(common.nimbuskws))
    common.settings.sync()
else:
    common.nimbuskws = json.loads(nimbuskws)
print(common.nimbuskws)
nimbussterms = "k"
while nimbussterms[0] in ("k", "r", "a"):
    nimbussterms = QInputDialog.getText(None, "Search", "Search (k for keywords/a to add a search/r to remove search):", QLineEdit.Normal, "")
    if nimbussterms[0] == "k":
        QMessageBox.warning(None, "Keywords", "<br/>".join(["<b>"+keyword.replace(" ", "</b>: ") + common.nimbuskws[keyword] for keyword in common.nimbuskws.keys()]), QMessageBox.Yes)
    elif nimbussterms[0] == "a":
        keyword = QInputDialog.getText(None, "Keyword", "Enter a keyword here:")
        if keyword[1]:
            expression = QInputDialog.getText(None, "Expression", "Enter an expression here (use %s for search terms):")
            if expression[1]:
                common.nimbuskws[keyword[0] + " "] = expression[0]
                common.settings.setValue("extensions/UniversalSearch", json.dumps(common.nimbuskws))
                common.settings.sync()
    elif nimbussterms[0] == "r":
        keyword = QInputDialog.getText(None, "Keyword", "Enter a keyword here:")
        if keyword[1]:
            try: del common.nimbuskws[keyword[0] + " "]
            except: pass
            common.settings.setValue("extensions/UniversalSearch", json.dumps(common.nimbuskws))
            common.settings.sync()
    elif nimbussterms[1]:
        for keyword in common.nimbuskws.keys():
            if nimbussterms[0].startswith(keyword):
                self._parent.tabs.currentWidget().load(QUrl(common.nimbuskws[keyword] % (nimbussterms[0].replace(keyword, ""),)))
                break
