import sys
import re
from bs4 import BeautifulSoup, NavigableString
from multiprocessing.dummy import Pool
from multiprocessing import cpu_count

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
    if url not in global_link_hash:
        sourcecode = get_page(url)
        global_link_hash[title] = sourcecode
        global_link_hash[url] = sourcecode
    else:
        sourcecode = global_link_hash[url]
        
    try:
        soupobj = BeautifulSoup(sourcecode, parser)
    except:
        print 'failed to get soupobj'
        return {}



    main_name = soupobj.find("h1")
    main_name = main_name.text
    global_link_hash[main_name] = sourcecode 
    #print url, '->', main_name 
    
    
    redirect = soupobj.find('span', {'class':'mw-redirectedfrom'})
    doc_title = soupobj.find('title').text

    
    if redirect != None:
        redirect_from_name = (redirect.find('a', {'class':'mw-redirect'})).text
        #print url, ' redirected from ', redirect_from_name
    
    
    
    
    
    if category_filter(sourcecode) == BAD_LINK:
        #try to remove itself
        global_link_hash[url] = sourcecode
        global DELETE_COUNT
        DELETE_COUNT += 1
        return {} 
    
    
    if soupobj.find('div', {'class': 'mw-parser-output'}) == None:
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
        result = validate_link(final_link)
        if result[0] == GOOD_LINK:
            global_link_hash[final_link] = result[1]
            link_hash[final_link] = result[1] 


def get_page_name(link):
    
    if link not in global_link_hash:
        sourcecode = get_page(link)
    else:
        sourcecode = global_link_hash[link]
    soupobj = BeautifulSoup(sourcecode, parser)


    try:
        name = soupobj.find('h1').text
    except:
        name = 'N/A'
        print 'Error finding name of webpage using H1'
    #may need to remove soon
    if category_filter(sourcecode) == BAD_LINK:
        global_link_hash[name] = sourcecode 
        global DELETE_COUNT
        DELETE_COUNT+=1
    return (name, sourcecode)


def validate_link(link):
    #print 'validating', link 
    if link not in global_link_hash:
            name = get_page_name(link)
            if name[0] not in global_link_hash:
                global_link_hash[name] = name[1]
                #print 'Added', name[0], 'from', link
                return (GOOD_LINK, name[1])
            else:
                #print link, ' was not in global hash but', name[0], ' was.'
                return (BAD_LINK, name[1])
    return (BAD_LINK, -1)

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
    
    if current_depth not in hashes:
        hashes[current_depth] = [current_link]
    for link_key in current_level_hash.viewkeys():
        hashes[current_depth].append(link_key)
        build_tree(current_level_hash.get(link_key), depth, current_depth + 1, hashes)

    #print "finished depth ", current_depth



def write_to_file(name, hashes):

    fw = open(name, "w+")
    
    for key in hashes:
        for indice in range (len(hashes.get(key))):
            hash_link = hashes.get(key)[indice]
            final_string = re.sub('_', ' ', hash_link) 
            final_string = hash_link
            fw.write(final_string + "\n")
        fw.write("=\n")

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



global_start = 'Rabin-Karp algorithm'
def build_tree_iter(depth, starting_link):
    
    pool = Pool(cpu_count() * 2)
    current_depth = 1
    resulting_link_hash = {current_depth: pool.map(get_links, [starting_link])}
    if depth == 1:
        return resulting_link_hash
    
    
    for current_depth in range(1, depth):
        links = []
        something = resulting_link_hash.get(current_depth)
        for element in something: 
            for key in element.viewkeys():
                links.append(key)
        current_depth += 1
        if current_depth not in resulting_link_hash:
            resulting_link_hash[current_depth] = pool.map(get_links, links)
    return resulting_link_hash

def iter_write_to_file(file_name, l_format):
    fw = open(file_name, 'w+')
    depth = 1
    while depth in l_format:
        information = l_format.get(depth)
        for element in information:
            for key in element:
           
                fw.write(key)
                fw.write('\n')

        fw.write('=\n')
        
        depth+= 1
        
    fw.close()

if __name__ == '__main__':
    starting_link = 'Rabin-Karp algorithm'
    depth = 2
    start_time = timeit.default_timer()
    my_results = build_tree_iter(depth, starting_link)
    elapsed_time = timeit.default_timer() - start_time
    print 'Created a',depth, 'high tree in ', (elapsed_time / 60.0), 'minutes.'
    
    iter_write_to_file('wiki_data.txt', my_results)


    '''
    pool = Pool(cpu_count() * 2)

    resulting_hashes = pool.map(get_links, [starting_link])

    hashes ={} 
    next_seq = []
    for key in resulting_hashes:
        for mine in key.viewkeys():
            next_seq.append(mine)

        resulting_hashes.append(pool.map(get_links, next_seq[0:]))
    
    '''
    '''
    start_time = timeit.default_timer()
    build_tree(starting_link, 1, 1, hashes)
    elapsed_time = timeit.default_timer() - start_time
    

    print elapsed_time, ' to build tree'
    
    start_time = timeit.default_timer()
    write_to_file('wiki_data.txt', hashes)
    elapsed_time = timeit.default_timer() - start_time
    print elapsed_time, ' to write hashes to file'
    '''
    print 'Links duplicates caught: ', DELETE_COUNT
    
   


