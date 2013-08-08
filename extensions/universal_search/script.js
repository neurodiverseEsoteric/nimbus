var nimbuskws = new Object();
nimbuskws['d '] = "https://duckduckgo.com/?q=\%s";
nimbuskws['w '] = "https://en.wikipedia.org/w/index.php?search=\%s&title=Special\%3ASearch";
nimbuskws['wk '] = "http://en.wiktionary.org/w/index.php?search=\%s&title=Special:Search";
nimbuskws['g '] = "http://www.google.com/search?q=\%s";
nimbuskws['i '] = "http://www.google.com/search?tbm=isch&q=\%s";
nimbuskws['m '] = "http://www.googlemusicsearch.com/search?q=\%s";
nimbuskws['tr '] = "http://translate.google.com/#auto/en/\%s";
nimbuskws['t '] = "http://thesaurus.com/browse/\%s";
nimbuskws['b '] = "http://www.bing.com/search?q=\%s";
nimbuskws['y '] = "http://search.yahoo.com/search?p=\%s";
nimbuskws['da '] = "http://www.deviantart.com/?q=\%s";
var nimbussterms = "k";
while (nimbussterms == "k") {
    nimbussterms = prompt('Search (enter k for keywords):',"");
    if (nimbussterms == "k") {
        window.alert('Keywords:\nd: DuckDuckGo\nw: Wikipedia\nwk: Wiktionary\ng: Google Search\ni: Google Image Search\nm: Google Music Search\ntr: Google Translate\nt: Thesaurus.com\nb: Bing\ny: Yahoo\nda: deviantART');
    }
    else {
        var kwfalse = true;
        for (var nimbuskw in nimbuskws) {
            if (nimbussterms.indexOf(nimbuskw) == 0) {
                window.location.href=nimbuskws[nimbuskw].replace("\%s", nimbussterms.replace(nimbuskw, ""));
                kwfalse = false;
                break;
            }
        }
        if (kwfalse) {
            window.location.href=nimbuskws['d '].replace("\%s", nimbussterms.replace('d ', ""));
        }
    }
}
