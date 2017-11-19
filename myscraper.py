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

DELETE_COUNT = 0

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
        #url = title.encode('utf8')
        url = urllib.quote(title)
    except:
        #print 'Exception Caught trying to use urllib.quote(title)'
        #url = title.encode('utf8')
        
        url = re.sub(' ', '_', title)
     

    #print 'URL to be searched:', url
    
    sourcecode = get_page(url)
    	
    if category_filter(sourcecode) == -1:
        #try to remove itself
        if url.lower() in global_link_hash or title.lower() in global_link_hash:
            
            try:
                del global_link_hash[url.lower()]
                del global_link_hash[title.lower()]
            except:
                pass
            global DELETE_COUNT
            DELETE_COUNT += 1
        #return {}
    
    
    soupobj = BeautifulSoup(sourcecode, parser) 
    intro = soupobj.find("div", {'class':'mw-parser-output'}).findAll();
    link_hash = {}
    for element in intro:
        if element.name == 'h2': break;
        if element.name == 'p':
            links = element.findAll('a', attrs={'href' : re.compile('^/wiki/')})
            for valid_link in links:
                final_link = valid_link.get('href')[6:]
                if final_link.lower() not in global_link_hash: 
                    global_link_hash[final_link.lower()] = 1
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
                        see_also_section = soupobj.findAll(attrs={"id":'See_also'})#, {'class':'mw-headline'})
                        parent = see_also_section[0].parent
                        
                        link_section = parent.findNext('ul', attrs={'style':None}) 
                        links = link_section.findAll('a', attrs={'href' : re.compile('^/wiki/')})
                        for valid_link in links:
                            final_link = valid_link.get('href')[6:]
                            if final_link.lower() not in global_link_hash: 
                                global_link_hash[final_link.lower()] = 1
                                link_hash[final_link] = link_to_normal(final_link)
                            

    #else:
        #print 'No see also section exists\n\n'





    #add dictionary to end of global hash
    return link_hash

def category_filter(page_data):
    x=re.compile("^regions|ancient|countries|capitals|boroughs|towns|continents|provinces|numbers|sexual|states|cities|nations|stimulants|drugs|medicines$")
    soup = BeautifulSoup(page_data, 'lxml')
    links=[]
    i=1
    cat=soup.find('div',id="mw-normal-catlinks")
    for link in cat.findAll('a', attrs={'href': re.compile("^/wiki/Category")}):
                line=link.get('href')[15:]
                line=re.sub('_', ' ',line)
                if x.findall(line.lower())!=[]:
                    i=-1
    return i 

def link_to_normal(link):
    link_key = link
    link_key = re.sub('_', ' ', link_key)
    link_key = urllib.unquote(link_key)
    return link_key






category_check = re.compile("^:wikt|outline|portal|list|sexual|latin|history|glossary|index|book|wikipedia|wikibooks|image|file|help|template|category|special:|english|language|\(disambiguation\)$")
def build_tree(current_link, depth, current_depth, hashes):
    if current_depth > depth:
        return
    #print 'starting depth ', current_depth
    current_level_hash = get_links(current_link)
    
    hashes.append((str(current_depth) + ".) " + current_link, current_level_hash))
    for link_key in current_level_hash.viewkeys():
        build_tree(current_level_hash.get(link_key), depth, current_depth + 1, hashes)

    #print "finished depth ", current_depth









if __name__ == '__main__':
    starting_link = 'sex toy'
    
    

    fw = open("wiki_data.txt", "w+")
    
    hashes = []
    build_tree(starting_link, 2, 1, hashes)
    for index in range(len(hashes)):
        
        fw.write(re.sub('_', ' ', hashes[index][0]) + '\n')
        for key in hashes[index][1]:
            hash_link = hashes[index][1].get(key)
            final_string = re.sub('_', ' ', hash_link) 
            final_string = hash_link
            #print final_string
            fw.write(final_string + "\n")
        fw.write("\n")

    fw.close()
        
    print 'Links deleted: ', DELETE_COUNT



