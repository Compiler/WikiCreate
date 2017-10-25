import sys
import re
from bs4 import BeautifulSoup, NavigableString
import urllib
import urllib2
import requests
import codecs
import operator

parser = 'lxml'
global_link_hash = {}

def get_links(title):
    url = 'http://en.wikipedia.org/wiki/' + urllib.quote(title)
    print 'URL to be searched:', url
    
    sourcecode = urllib.urlopen(url).read()
    soupobj = BeautifulSoup(sourcecode, parser) 
    intro = soupobj.find("div", {'class':'mw-parser-output'}).findAll();
    link_hash = {}
    for element in intro:
        if element.name == 'h2': break;
        if element.name == 'p':
            links = element.findAll('a', attrs={'href' : re.compile('^/wiki/')})
            for valid_link in links:
                final_link = valid_link.get('href')[6:]
                if final_link not in global_link_hash: 
                    global_link_hash[final_link] = 1
                    link_hash[final_link] = 1

    ##todo: add to link
    




    #add dictionary to end of global hash
    return link_hash

def link_to_normal(link):
    link_key = link
    link_key = final_link
    link_key = re.sub('_', ' ', link_key)
    link_key = urllib.unquote(link_key).decode('utf8')
    return link_key


if __name__ == '__main__':
    starting_link = 'Rabin-Karp algorithm'
    x=re.compile("^:wikt|outline|portal|list|sexual|latin|history|glossary|index|book|wikipedia|wikibooks|image|file|help|template|category|special:|english|language|\(disambiguation\)$")
    
    first_level_hash = get('Rabin-Karp algorithm')
    for v, k in first_level_hash.iteritems():
        print v, ' -> ', k

