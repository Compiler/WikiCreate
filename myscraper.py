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
import timeit




parser = 'lxml'
global_link_hash = {}

DELETE_COUNT = 0

BAD_LINK = -3
GOOD_LINK = 4

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



def validate(title):
    if title in global_link_hash:
        return BAD_LINK
    return GOOD_LINK

def get_links(title):
    
    
    
    
    url = re.sub(' ', '_', title)
    sourcecode = get_page(url)
    soupobj = BeautifulSoup(sourcecode, parser)
    
    main_name = soupobj.find("h1")
    main_name = main_name.text
    print url, '->', main_name 
    
    global_link_hash[main_name] = GOOD_LINK
    global_link_hash[title] = GOOD_LINK
    global_link_hash[url] = GOOD_LINK
    
    redirect = soupobj.find('span', {'class':'mw-redirectedfrom'})
    doc_title = soupobj.find('title').text

    
    if redirect != None:
        redirect_from_name = (redirect.find('a', {'class':'mw-redirect'})).text
        print url, ' redirected from ', redirect_from_name
    
    
    
    
    
    if category_filter(sourcecode) == BAD_LINK:
        #try to remove itself
        global_link_hash[url] = BAD_LINK
        global DELETE_COUNT
        DELETE_COUNT += 1
        return {} 
    
    

    intro = soupobj.find("div", {'class':'mw-parser-output'}).findAll();
    link_hash = {}
    for element in intro:
        if element.name == 'h2': break;
        if element.name == 'p':
            links = element.findAll('a', attrs={'href' : re.compile('^/wiki/')})
            validate_links_and_populate(links, link_hash)






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
                        validate_links_and_populate(links, link_hash)

    #else:
        #print 'No see also section exists\n\n'





    #add dictionary to end of global hash
    return link_hash

def validate_links_and_populate(links, link_hash):
    
    for valid_link in links:
        final_link = valid_link.get('href')[6:]
        final_link = re.sub(' ', '_', final_link)
        if validate_link(final_link) == GOOD_LINK:
            global_link_hash[final_link] = GOOD_LINK
            link_hash[final_link] = link_to_normal(final_link)


def get_page_name(link):

    sourcecode = get_page(link)
    soupobj = BeautifulSoup(sourcecode, parser)


    try:
        name = soupobj.find('h1').text
    except:
        name = 'N/A'
        print 'Error finding name of webpage using H1'
    #may need to remove soon
    if category_filter(sourcecode) == BAD_LINK:
        global_link_hash[name] = BAD_LINK
        global DELETE_COUNT
        DELETE_COUNT+=1
    return name


def validate_link(link):
    
    if link not in global_link_hash:
            name = get_page_name(link)
            if name not in global_link_hash:
                global_link_hash[name] = GOOD_LINK
                print 'Added', name, 'from', link
                return GOOD_LINK
            else:
                print link, ' was not in global hash but', name, ' was.'
    return BAD_LINK

def category_filter(page_data):
    x=re.compile("^regions|ancient|countries|capitals|boroughs|towns|continents|provinces|numbers|sexual|states|cities|nations|stimulants|drugs|medicines$")
    soup = BeautifulSoup(page_data, 'lxml')
    cat=soup.find('div',id="mw-normal-catlinks")
    if cat != None:
        for link in cat.findAll('a', attrs={'href': re.compile("^/wiki/Category")}):
            line=link.get('href')[15:]
            if x.findall(line.lower())!=[]:
                global_link_hash[line] = BAD_LINK
                global DELETE_COUNT
                DELETE_COUNT += 1
                return BAD_LINK
    return GOOD_LINK 

def link_to_normal(link):
    link_key = link
    link_key = re.sub('_', ' ', link_key)
    link_key = urllib.unquote(link_key)
    return link_key






category_check = re.compile("^:wikt|outline|portal|list|sexual|latin|history|glossary|index|book|wikipedia|wikibooks|image|file|help|template|category|special:|english|language|\(disambiguation\)$")
def build_tree(current_link, depth, current_depth, hashes):
    if current_depth > depth:
        return
    
    #print '-' * (current_depth**2), '>' , current_link
    current_level_hash = get_links(current_link)
    
    hashes.append((str(current_depth) + ".) " + current_link, current_level_hash))
    for link_key in current_level_hash.viewkeys():    
        build_tree(current_level_hash.get(link_key), depth, current_depth + 1, hashes)

    #print "finished depth ", current_depth


def validate_depth(hashes, depth):
    pass




def write_to_file(name, hashes):

    fw = open(name, "w+")
    
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


def write_global_sorted_to_file(name):
    fw = open(name, 'w+')

    all_links = global_link_hash.keys()
    all_links.sort()

    for element in all_links:
        if global_link_hash.get(element) == BAD_LINK:
            fw.write('**BAD LINK**\t\t')
        fw.write(element + '\n')
        

    fw.close()

def write_hashes_sorted_to_file(name, hashes):
    fw = open(name, 'w+')

    all_links = []

    for index in range(len(hashes)):
        pass        

if __name__ == '__main__':
    starting_link = 'religion'
    
    hashes = []
    
    start_time = timeit.default_timer()
    build_tree(starting_link, 2, 1, hashes)
    elapsed_time = timeit.default_timer() - start_time
    

    print elapsed_time, ' to build tree'
    
    start_time = timeit.default_timer()
    write_to_file('wiki_data.txt', hashes)
    elapsed_time = timeit.default_timer() - start_time
    print elapsed_time, ' to write hashes to file'
    
    print 'Links duplicates caught: ', DELETE_COUNT
    
   


