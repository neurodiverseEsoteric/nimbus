var nimbuskws = new Object();
nimbuskws['g '] = "http://www.google.com/search?q=\%s";
nimbuskws['i '] = "http://www.google.com/search?tbm=isch&q=\%s";
nimbuskws['m '] = "http://www.googlemusicsearch.com/search?q=\%s";
nimbuskws['b '] = "http://www.bing.com/search?q=\%s";
nimbuskws['y '] = "http://search.yahoo.com/search?p=\%s";
nimbuskws['d '] = "https://duckduckgo.com/?q=\%s";
nimbuskws['da '] = "http://www.deviantart.com/?q=\%s";
nimbuskws['w '] = "https://en.wikipedia.org/w/index.php?search=\%s&title=Special\%3ASearch";
var nimbussterms = "k";
while (nimbussterms == "k") {
    nimbussterms = prompt('Search (enter k for keywords):',"");
    if (nimbussterms == "k") {
        window.alert('Keywords:\nd: DuckDuckGo\nw: Wikipedia\nw: Yahoo\ng: Google Search\ni: Google Image Search\nm: Google Music Search\nb: Bing\ny: Yahoo\n\n');
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
            window.location.href=nimbuskws['d '].replace("\%s", nimbussterms.replace('g ', ""));
        }
    }
}
