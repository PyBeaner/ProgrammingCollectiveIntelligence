from urllib import request
from bs4 import *
import sqlite3 as sqlite

ignorewords = {'the',"of","to","and","a","in","is","it"}


class crawler:
    # Initialize the crawler with the name of database
    def __init__(self,dbname):
        self.con = sqlite.connect(dbname)

    def __del__(self):
        self.con.close()

    def dbcommit(self):
        self.con.commit()

    # Auxilliary function for getting an entry id and adding
    # it if it's not present
    def getentryid(self,table,field,value,createnew=True):
        return None

    # Index an individual page
    def addtoindex(self,url,soup):
        print("Indexing %s" % url)

    # Extract the text from an HTML page (no tags)
    def gettextonly(self,soup):
        return None

    # Separate the words by any non-whitespace character
    def separatewords(self,text):
        return None

    # return whether a url is indexed
    def isindexed(self,url):
        return False

    # add a link between two pages
    def addlinkref(self,urlFrom,urlTo,linkText):
        pass

    # Starting with a list of pages, do a breadth
    # first search to the given depth, indexing pages
    # as we go
    def crawl(self,pages,depth=2):
        for i in range(depth):
            newpages = set()
            for page in pages:
                try:
                    c = request.urlopen(page)
                except Exception as e:
                    print("Could not open %s" % page)
                    print("Due to:"+e.__str__())
                    continue
                soup = BeautifulSoup(c.readall())
                self.addtoindex(page,soup)

                links = soup("a")
                for link in links:
                    if "href" in dict(link.attrs):
                        url = request.urljoin(page,link["href"])
                        if url.find("'")!=-1:continue
                        url = url.split("#")[0]# remove url portion
                        if url[0:4]=="http" and not self.isindexed(url):
                            newpages.add(url)

                        linkText = self.gettextonly(link)
                        self.addlinkref(page,url,linkText)
                self.dbcommit()
            pages = newpages

    # Create the database tables
    def createindextables(self):
        self.con.execute("create table urllist(url)")
        self.con.execute("create table wordlist(word)")
        self.con.execute("create table wordlocation(urlid,wordid,location)")
        self.con.execute("create table link(fromid integer,toid integer)")
        self.con.execute("create table linkwords(wordid,linkid)")

        self.con.execute("create index wordidx on wordlist(word)")
        self.con.execute("create index urlidx on urllist(url)")
        self.con.execute("create index wordurlidx on wordlocation(wordid)")
        self.con.execute("create index urltoidx on link(toid)")
        self.con.execute("create index urlfromidx on link(fromid)")
        self.con.commit()

if(__name__=="__main__"):
    pagelist = ["http://www.baidu.com"]
    c = crawler("")
    c.crawl(pagelist)