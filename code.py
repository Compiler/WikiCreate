import sys
import re
from bs4 import BeautifulSoup, NavigableString
import requests
#import pprint
import urllib
import urllib2
import codecs
import operator
from StringIO import StringIO
import gzip

def getPage(url):
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'MyTestScript/1.0 (contact at myscript@mysite.com)'), ('Accept-encoding', 'gzip')]
    resource = opener.open("http://en.wikipedia.org/wiki/" + url)
    if resource.info().get('Content-Encoding') == 'gzip':
        buf = StringIO( resource.read())
        f = gzip.GzipFile(fileobj=buf)
        return f.read()
    else:
        return resource.read()

def cat(title):
    x=re.compile("^regions|ancient|countries|capitals|boroughs|towns|continents|provinces|numbers|sexual|states|cities|nations|stimulants|drugs|medicines$")
    article = urllib.quote(title)
    data=getPage(article)
    soup = BeautifulSoup(data, 'lxml')
    links=[]
    i=1
    cat=soup.find('div',id="mw-normal-catlinks")
    for link in cat.findAll('a', attrs={'href': re.compile("^/wiki/Category")}):
                line=link.get ('href')[15:]
                line=re.sub('_', ' ',line)
                #line=urllib.unquote(line).decode('utf8')
                if x.findall(line.lower())==[]:
                    i*=1
                else:
                    i=0
    return i
    
def alllinks(title):
    i=0
    links=[]
    x=re.compile("^:wikt|portal|index|latin|list|wikipedia|book|wikibooks|image|file|help|template|category|special:|\(disambiguation\)$")
    #article = urllib.quote(title)
    article=re.sub(' ','_', title)
##    opener = urllib2.build_opener()
##    opener.addheaders = [('User-agent', 'Mozilla/5.0')] #wikipedia needs this
    try:
##        resource = opener.open("http://en.wikipedia.org/wiki/" + article)
##        data = resource.read()
##        resource.close()
        data=getPage(article)
        soup = BeautifulSoup(data, 'lxml')
        para=soup.find('div',id="mw-content-text")
        for link in para.findAll('a', attrs={'href': re.compile("^/wiki/")}):
            line=link.get('href')[6:]
            #line=re.sub('/wiki/', '', line)
            line=re.sub('_', ' ',line)
            
            if x.findall(line.lower())==[]:
                if  line.lower() not in (y.lower() for y in links):
                    links.append(line)
                    #print line
                    i=i+1
    except:
        i=0
    return i

def get_links(title):
    x=re.compile("^:wikt|outline|portal|list|sexual|latin|history|glossary|index|book|wikipedia|wikibooks|image|file|help|template|category|special:|english|language|\(disambiguation\)$")
    article = urllib.quote(title)
    print article
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')] #wikipedia needs this
    print 'open'
    resource = opener.open("http://en.wikipedia.org/wiki/" + article)
    data = resource.read()
    print 'read'
    resource.close()
##    data=getPage(article)
    soup = BeautifulSoup(data, 'lxml')
    links=[]
    links1=[]
    j=0
    #para1=soup.find('div',id="bodyContent").p
    #para1=soup.findAll("p")[0]
    '''para1=soup.find('div',id="mw-content-text").p
    for link in para1.findAll('a', attrs={'href': re.compile("^/wiki/")}):
        line=link.get ('href')[6:]
        #line=re.sub('/wiki/', '', line)
        line=re.sub('_', ' ',line)
        line=urllib.unquote(line).decode('utf8')
        line=line.split('|')[0]
        line=line.split('#')[0]
        #links.append(line)
        if x.findall(line.lower())==[]:
            if  line.lower() not in (y.lower() for y in links):
                links.append(line)'''
    for tag in soup.find('div',id="mw-content-text").findAll():
        if tag.name == 'h2':
            break
        if tag.name == 'p':
            for link in tag.findAll('a', attrs={'href': re.compile("^/wiki/")}):
                line=link.get ('href')[6:]
                line=re.sub('_', ' ',line)
                line=urllib.unquote(line).decode('utf8')
                line=line.split('|')[0]
                line=line.split('#')[0]
                if x.findall(line.lower())==[]:
                    if  line.lower() not in (y.lower() for y in links):
                        links.append(line)
    try:
        link=soup.find('a', {'title':'Edit section: See also'})['href']
        resource2 = opener.open("http://en.wikipedia.org/"+link)
        data2 = resource2.read()
        resource2.close()
        soup2 = BeautifulSoup(data2)
        content= soup2.find('textarea', {"id": "wpTextbox1"}).renderContents()
        m = re.findall(r"\[\[(.*?)\]\]", content)
        for i in m:
            i=urllib.unquote(i).decode('utf8')
            i=i.split('|')[0]
            i=i.split('#')[0]
            if x.findall(i.lower())==[]:
                if  i.lower() not in (y.lower() for y in links):
                    #i=urllib.unquote(i).decode('utf8')
                    #links.append(urllib.unquote(i).decode('utf8'))
                    links.append(i)

    except:
        j=j+1
    return links


if __name__ == '__main__':
    ###  enter a valid wikipedia title - e.x. 'Marketing' and the search level: 2 for links under the links
    #For example 
    #
    #   python Links.py 'marketing' 1 

    fw=open("imunsuredude.txt","w+")
    #title=str(sys.argv[1])
    #level=int(sys.argv[2])
    #title="rabin karp algorithm"
    title = "online shopping"
    level=2
    i=0
    links=[title]
    link2=[title]
    #gl=[]
    
    print 'link output: ' , links;
    while (i<level):
        this_level=[]
        for link in links:
            print 'singular links: ', link
            try:
                #this_level.extend(get_links(link))
                '''gl=get_links(link)
                print gl'''
                linksofcurrent = get_links(link)
                print 'first level:' , linksofcurrent
                for k in get_links(link):
                    if k not in this_level:
                         if  k.lower() not in (y.lower() for y in link2):
                             if cat(k)==1:
                                this_level.append(k)                     
            except:
                print 'Couldn\'t pursue %s. Most likely an encoding problem' %(link)
        links=this_level
        
        #link2+=links
        #link2+='='
        pair={}
        for j in links:
            c=urllib.unquote(j)
            n=alllinks(j)
            pair[c] = n
        sorted_pair=sorted(pair.iteritems(), key=operator.itemgetter(1), reverse=True)
        for m in sorted_pair:
            #print urllib.unquote(m[0])
            #print urllib.unquote(m[0]).decode('utf8')
            print m[0]
            link2+=[m[0]]
            #print m[1]
        link2+='='    
        print("====")
        i+=1
    
    for i in link2: fw.write(i+'\n')
    #fw.write(str(link2))
    #pprint.pprint(links)
    #print(link2)
    print 'There are %s links %s node(s) away from %s' %(len(links),level,title)
    fw.close()
