import urllib2
import csv
import re
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool  # This is a thread-based Pool
from multiprocessing import cpu_count
import timeit
import gzip
from StringIO import StringIO

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



def crawlToCSV(URLrecord):
    print 'trying', URLrecord
    OpenSomeSiteURL = get_page(URLrecord)#urllib2.urlopen(URLrecord)
    soupobj = BeautifulSoup(OpenSomeSiteURL, "lxml")

    #main_name = Soup_SomeSite.find("h2")
    #trTags = tbodyTags.find_all("tr", class_="result-item ")
    
    placeHolder = {} 
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


    return link_hash

def validate_links_and_populate(links, link_hash):
    
    for valid_link in links:
        final_link = valid_link.get('href')[6:]
        final_link = re.sub(' ', '_', final_link)
        if final_link not in link_hash:
        #if validate_link(final_link) == GOOD_LINK:
            #global_link_hash[final_link] = GOOD_LINK
            print 'added', final_link
            link_hash[final_link] = 1


if __name__ == "__main__":
    fileName = "Religion"
    
    
    pool = Pool(cpu_count() * 2)  # Creates a Pool with cpu_count * 2 threads.
    
    
    
    #with open('output.txt', "rb") as f:
    
    results = pool.map(crawlToCSV, [fileName])  # results is a list of all the placeHolder lists returned from each call to crawlToCSV
    


    writeFile = open('out.txt', 'w+')

    
    for i in range(0, 2):
        appender = []
        for result in results:
            for key in result.viewkeys():
                writeFile.write(key + '\n')
                appender.append(key)
        writeFile.write("=\n")
        #if isinstance(results, dict):
        results = pool.map(crawlToCSV, appender)
        


    writeFile.close()
    
    print 'done'










