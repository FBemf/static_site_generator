""" Generates RSS & Atom feeds
"""

import datetime

from feedgen.feed import FeedGenerator

def makeFeed(*, feedConfig, siteConfig, pages, groups=None, atomFile=None, rssFile=None):
    fg = FeedGenerator()

    fg.id = feedConfig.id
    fg.title = siteConfig.title
    fg.updated = max(pages, key=lambda x: x.date if x.date else datetime.datetime(1970, 1, 1))
    if siteConfig.author:
        fg.author(siteConfig.author)
    if feedConfig.link:
        fg.link(feedConfig.link)
    if feedConfig.icon:
        fg.subtitle(feedConfig.icon)
    if feedConfig.contributor:
        fg.contributor(feedConfig.contributor)
    if feedConfig.logo:
        fg.subtitle(feedConfig.logo)
    if siteConfig.rights:
        fg.subtitle(siteConfig.rights)
    if siteConfig.subtitle:
        fg.subtitle(siteConfig.subtitle)
    if feedConfig.language:
        fg.language(siteConfig.language)

    for page in pages:
        if groups:
            if page.group not in groups:
                continue
        fe = fg.add_entry()
        if page.id:
            fe.id(page.feed_id)
        else:
            fe.id(joinUrl(feedConfig.id, page.url))
        fe.title(page.title)
        fe.updated(page.updated if page.updated else page.date)

        fe.author(page.author if page.author else siteConfig.author)
        fe.content(page.content)
        if page.summary:
            fe.summary(page.summary)
        if page.contributor:
            fe.contributor(page.contributor)
        fe.published(page.date)
        if page.rights:
            fe.rights(page.rights)
        elif siteConfig.rights:
            fe.rights(siteConfig.rights)
    
    if atomFile:
        fg.atom_file(atomFile)
    if rssFile:
        fg.rss_file(rssFile)
    if not (atomFile or rssFile):
        raise RuntimeError("You must provide either an atom or an rss output file")

def joinUrl(a, b):
    while a[-1] == '/':
        a = a[:-1]
    while b[0] == '/':
        b = b[1:]
    return a + "/" + b