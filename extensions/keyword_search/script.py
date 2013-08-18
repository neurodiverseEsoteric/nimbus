import json
nimbuskws = common.settings.value("extensions/KeywordSearch")
if not nimbuskws:
    common.nimbuskws = {}
    common.nimbuskws['d '] = "https://duckduckgo.com/?q=%s"
    common.nimbuskws['w '] = "https://en.wikipedia.org/w/index.php?search=%s&title=Special:Search"
    common.nimbuskws['wk '] = "http://en.wiktionary.org/w/index.php?search=%s&title=Special:Search"
    common.nimbuskws['g '] = "http://www.google.com/search?client=nimbus&q=%s"
    common.nimbuskws['i '] = "http://www.google.com/search?client=nimbus&tbm=isch&q=%s"
    common.nimbuskws['m '] = "http://www.googlemusicsearch.com/search?q=%s"
    common.nimbuskws['tr '] = "http://translate.google.com/#auto/en/%s"
    common.nimbuskws['t '] = "http://thesaurus.com/browse/%s"
    common.nimbuskws['b '] = "http://www.bing.com/search?q=%s"
    common.nimbuskws['y '] = "http://search.yahoo.com/search?p=%s"
    common.nimbuskws['da '] = "http://www.deviantart.com/?q=%s"
    common.nimbuskws['azl '] = "http://search.azlyrics.com/search.php?q=%s"
    common.nimbuskws['mtl '] = "http://www.metrolyrics.com/search?search=%s"
    common.nimbuskws['oca '] = "http://openclipart.org/search/?query=%s"
    common.settings.setValue("extensions/KeywordSearch", json.dumps(common.nimbuskws))
    common.settings.sync()
else:
    common.nimbuskws = json.loads(nimbuskws)
nimbussterms = "k"
while nimbussterms[0] in ("k", "r", "a"):
    nimbussterms = QInputDialog.getText(None, "Search", "<b>k</b> to list all keywords<br/><b>a</b> to add a search<br/><b>r</b> to remove search<br/><br/>Enter your search here:", QLineEdit.Normal, "")
    all_searches = ["<b>"+keyword.replace(" ", "</b>: ") + common.nimbuskws[keyword] for keyword in common.nimbuskws.keys()]
    if nimbussterms[0] == "k":
        QMessageBox.warning(None, "Keywords", "<br/>".join(all_searches), QMessageBox.Ok)
    elif nimbussterms[0] == "a":
        keyword = QInputDialog.getText(None, "Add Search", "Enter a keyword to be added:")
        if keyword[1]:
            expression = QInputDialog.getText(None, "Add Search", "Use <b>%s</b> for search terms.<br/>Enter an expression to be added:")
            if expression[1]:
                common.nimbuskws[keyword[0] + " "] = expression[0]
                common.settings.setValue("extensions/KeywordSearch", json.dumps(common.nimbuskws))
                common.settings.sync()
    elif nimbussterms[0] == "r":
        keyword = QInputDialog.getText(None, "Remove Search", "Enter a keyword to be removed:")
        if keyword[1]:
            try: del common.nimbuskws[keyword[0] + " "]
            except: pass
            common.settings.setValue("extensions/KeywordSearch", json.dumps(common.nimbuskws))
            common.settings.sync()
    elif nimbussterms[1]:
        for keyword in common.nimbuskws.keys():
            if nimbussterms[0].startswith(keyword):
                self._parent.tabs.currentWidget().load(QUrl(common.nimbuskws[keyword] % (nimbussterms[0].replace(keyword, ""),)))
                break
