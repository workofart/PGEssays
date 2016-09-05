# -*- coding: utf-8 -*-
"""
Builds epub book out of Paul Graham's essays: http://paulgraham.com/articles.html
Original Author: Ola Sitarska <ola@sitarska.com>
Edited by: Henry Pan <hanxiangp@gmail.com>
Copyright: Licensed under the GPL-3 (http://www.gnu.org/licenses/gpl-3.0.html)
This script requires python-epub-library: http://code.google.com/p/python-epub-builder/
"""

import re, ez_epub, urllib2, genshi
from bs4 import BeautifulSoup
from tidylib import tidy_fragment
tidy_fragment.BASE_OPTIONS = {
    "output-xhtml": 1,     # XHTML instead of HTML4
    "indent": 0,           # Pretty; not too much of a performance hit
    "tidy-mark": 0,        # No tidy meta tag in output
    "wrap": 0,             # No wrapping
    "alt-text": "",        # Help ensure validation
    "doctype": 'strict',   # Little sense in transitional for tool-generated markup...
    "force-output": 1,     # May not get what you expect but you will get something
    }

def addSection(link, title):
    if not 'http' in link:
        page = urllib2.urlopen('http://www.paulgraham.com/'+link).read()
        soup = BeautifulSoup(page, "lxml")
        soup.prettify()
    else:
        page = urllib2.urlopen(link).read()

    section = ez_epub.Section()
    try:
        section.title = title
        print section.title

        if not 'http' in link:
            if len(soup.findAll('table', {'width':'435'})) != 0:
                font = str(soup.findAll('table', {'width':'435'})[0].findAll('font')[0]).strip("<font face=\"verdana\" size=\"2\">")
            elif len(soup.findAll('table', {'width':'374'})) != 0:
                font = str(soup.findAll('table', {'width':'374'})[0].findAll('font')[0]).strip("<font face=\"verdana\" size=\"2\">")
            if not 'Get funded by' in font and not 'Watch how this essay was' in font and not 'Like to build things?' in font and not len(font)<100:
                content = font
            else:
                content = ''
                for par in soup.findAll('p'):
                    content += str(par)
            for p in content.decode('utf-8').split("<br/><br/>"):
                p, error = tidy_fragment(p)
                if p == '</':
                    continue
                if p.__contains__("<xa"):
                    p = p.replace("<xa", "<a")
                section.text.append(genshi.core.Markup(p))
        else:
            for p in str(page).replace("\n","<br/>").split("<br/><br/>"):
                p, error = tidy_fragment(p)
                if p.__contains__("<xa"):
                    p = p.replace("<xa", "<a")
                section.text.append(genshi.core.Markup(p))
    except Exception, e:
        print str(e)
        pass
    return section


book = ez_epub.Book()
book.title = "Paul Graham's Essays"
book.authors = ['Paul Graham']

page = urllib2.urlopen('http://www.paulgraham.com/articles.html').read()
soup = BeautifulSoup(page)
soup.prettify()

links = soup.findAll('table', {'width': '435'})[1].findAll('a')
sections = []
for link in links:
    sections.append(addSection(link['href'], link.text))

book.sections = sections
book.make(book.title)