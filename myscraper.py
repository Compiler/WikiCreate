import sys
import re
from bs4 import BeautifulSoup, NavigableString
import urllib
import urllib2
import requests
import codecs
import operator
from StringIO import StringIO
import gzip
parser = 'lxml'
global_link_hash = {}



def get_page(url):
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'MyTestScript/1.0 (contact at myscript@mysite.com)'), ('Accept-encoding', 'gzip')]
    resource = opener.open("http://en.wikipedia.org/wiki/" + url)
    if resource.info().get('Content-Encoding') == 'gzip':
        buf = StringIO( resource.read())
        f = gzip.GzipFile(fileobj=buf)
        return f.read()
    else:
        return resource.read()

def get_links(title):
    
    
    
    try:
        url = title.encode('utf8')
        url = urllib.quote(title)
    except:
        print 'Exception Caught trying to use urllib.quote(title)'
        url = title.encode('utf8')
        url = re.sub(' ', '_', url)
     

    print 'URL to be searched:', url
    
    #sourcecode = urllib.urlopen(url).read()
    sourcecode = get_page(url)
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
                    link_hash[final_link] = link_to_normal(final_link)






                    #########################
                    #See Also Section Scrape#
                    #########################

    mything = 'div-col columns column-count column-count-2'
    contents_section = soupobj.find("div", {'id' : 'toc'})
    if contents_section != None:
        #see_also_section = see_also_section.findAll()
        for element in contents_section.contents:
            if element.name == 'ul':
                contents_list = element.findAll('a', attrs={'href' : re.compile('^#')})
                for links in contents_list:
                    if links.get('href') == '#See_also':
                        print 'Page has see also\n\n'
                        see_also_section = soupobj.findAll(attrs={"id":'See_also'})#, {'class':'mw-headline'})
                        parent = see_also_section[0].parent
                        
                        link_section = parent.findNext('ul', attrs={'style':None}) 
                        links = link_section.findAll('a', attrs={'href' : re.compile('^/wiki/')})
                        for valid_link in links:
                            final_link = valid_link.get('href')[6:]
                            if final_link not in global_link_hash: 
                                global_link_hash[final_link] = 1
                                link_hash[final_link] = link_to_normal(final_link)
                            

        print '\n'
    else:
        print 'No see also section exists\n\n'





    #add dictionary to end of global hash
    return link_hash

def link_to_normal(link):
    link_key = link
    link_key = re.sub('_', ' ', link_key)
    link_key = urllib.unquote(link_key).decode('utf8')
    return link_key


if __name__ == '__main__':
    starting_link = 'Rabin-Karp algorithm'
    
    x=re.compile("^:wikt|outline|portal|list|sexual|latin|history|glossary|index|book|wikipedia|wikibooks|image|file|help|template|category|special:|english|language|\(disambiguation\)$")
    
    first_level_hash = get_links(starting_link)
    hashes = [(starting_link, first_level_hash)]

    for key in first_level_hash.viewkeys():
        print key, ' -> ', first_level_hash[key]
        print 'Getting links for ', key
        hashes.append((key, get_links(first_level_hash[key])))

    for index in range(len(hashes)):
        print '\n\nLinks for ', hashes[index][0],'\n', '='*30
        for key in hashes[index][1]:
           print hashes[index][1].get(key) 




        


