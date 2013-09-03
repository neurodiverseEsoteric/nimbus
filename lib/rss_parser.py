#! /usr/bin/env python3

try:
    import feedparser
    has_feedparser = True
except:
    has_feedparser = False

basic_html = """<!DOCTYPE html>
<html>
    <head>
        <title>%(title)s</title>
        <link rel="icon" href="%(icon)s"/>
        <style>
            .item {
                margin-bottom: 1em;
            }
        </style>
    </head>
    <body>
        <h1>%(title)s</h1>
        %(content)s
    </body>
</html>"""

def feedToHtml(url):
    if not has_feedparser:
        return ""
    else:
        d = feedparser.parse(url)
        try: feed_title = d.feed.title
        except: feed_title = "Untitled"
        try: icon = d.feed.icon
        except: icon = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3QgdBBMTEi/JQgAAABl0RVh0Q29tbWVudABDcmVhdGVkIHdpdGggR0lNUFeBDhcAAAAMSURBVAjXY/j//z8ABf4C/tzMWecAAAAASUVORK5CYII="
        items = []
        for entry in d.entries:
            try: content = entry.content
            except: content = ""
            try: link = entry.link
            except: link = ""
            try: title = entry.title
            except: title = ""
            try: author = entry.author
            except: author = "Anonymous"
            try: summary = entry.summary
            except: summary = ""
            try: tags = ", ".join([tag.term for tag in entry.tags])
            except: tags = "None"
            items.append("<div class=\"item\">%(content)s<h2><a href=\"%(link)s\">%(title)s by %(author)s</a></h2>%(summary)s<b>Tags:</b> %(tags)s</div>" % {"content": content, "link": link, "title": title, "author": author, "tags": tags, "summary": summary})
        return basic_html % {"title": feed_title, "icon": icon, "content": "<hr/>".join(items)}
