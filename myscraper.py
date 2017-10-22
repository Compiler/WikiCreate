import sys
import re
from bs4 import BeautifulSoup, NavigableString
import urllib
import urllib2
import requests
import codecs
import operator

parser = 'lxml'


def get(title):
    url = 'http://en.wikipedia.org/wiki/' + urllib.quote(title)
    print 'URL to be searched:', url
    
    sourcecode = urllib.urlopen(url).read()
    soupobj = BeautifulSoup(sourcecode, parser) 
    something = soupobj.find("div", {'class':'mw-parser-output'})
    
    while something.next_element != 
if __name__ == '__main__':
    get('Rabin-Karp algorithm')
