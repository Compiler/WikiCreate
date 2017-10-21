import sys
import re
from bs4 import BeautifulSoup, NavigableString
import urllib
import urllib2
import codecs
import operator





def compare(titles):
    x=re.compile("^:wikt|outline|portal|list|sexual|latin|history|glossary|index|book|wikipedia|wikibooks|image|file|help|template|category|special:|english|language|\(disambiguation\)$")
    articles = [None] * len(titles)
    for i in range(0, len(titles)):
        articles[i] = urllib.quote(titles[i])
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')] #wik	
    print 'something'
    for i in range(0, len(articles)):
	
	print '\n\n', titles[i], ': '
        articles[i] = articles[i].replace('%20', '_');
        print articles[i]
        wholeurl = "https://en.wikipedia.org/wiki/" + articles[i];
        print wholeurl
	resource = opener.open(wholeurl)
        #print resource
        data = resource.read()
	#print data
        resource.close()
##    data=getPage(article)
    soup = BeautifulSoup(data)
    links=[]
    links1=[]


if __name__ == '__main__':
    compare(['online shopping', 'rabin-karp algorithm']) 
