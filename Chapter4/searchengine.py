#! encoding=utf-8

from urllib import request
from bs4 import *
import sqlite3 as sqlite
import re

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
    def getentryid(self,table,field,value,createnew=False):
        cur = self.con.execute(
            "select rowid from %s where %s='%s'" % (table,field,value)
        )
        res = cur.fetchone()
        if not res:
            if(createnew):
                cur = self.con.execute(
                    "insert into %s (%s) values ('%s')" % (table,field,value)
                )
                return cur.lastrowid
        else:
            return res[0] # the first column is "rowid"

    # Index an individual page
    def addtoindex(self,url,soup):
        if(self.isindexed(url)):return
        print("Indexing %s" % url)

        # Get the individual words
        text = self.gettextonly(soup)
        words = self.separatewords(text)

        # Get the Url id
        urlid = self.getentryid("urllist","url",url,createnew=True)

        for i in range(len(words)):
            word = words[i]
            if word in ignorewords:continue
            wordid = self.getentryid("wordlist","word",word,True)
            self.con.execute(
                "insert into wordlocation(urlid,wordid,location) VALUES(%d,%d,%d)"
                %(urlid,wordid,i)
            )


    # Extract the text from an HTML page (no tags)
    def gettextonly(self,soup):
        v = soup.string
        if v==None:
            c = soup.contents
            resulttext = ""
            for t in c:
                subtext = self.gettextonly(t)
                resulttext+=subtext
            return resulttext
        else:
            return v.strip()

    # Separate the words by any non-whitespace character
    def separatewords(self,text):
        splitter = re.compile("\\W*")
        return [s.lower() for s in splitter.split(text) if s!=""]

    # return whether a url is indexed
    def isindexed(self,url):
        u = self.con.execute(
            "SELECT rowid from urllist where url='%s'" % url
        ).fetchone()
        if u!=None:
            # check if it's actually crawled
            v = self.con.execute(
                "select * from wordlocation where urlid=%d" % u[0]
            ).fetchone()
            if v!=None:return True
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

class searcher:
    def __init__(self,dbname):
        self.con = sqlite.connect(dbname)

    def __del__(self):
        self.con.close()

    def getmatchrows(self,query):
        # strings to build the query
        fieldList = "w0.urlid"
        tablelist = ""
        clauselist = ""
        wordids = []

        words = query.split(" ")
        tablenumber = 0

        for word in words:
            wordrow = self.con.execute(
                "select rowid from wordlist where word='%s'" % word
            ).fetchone()

            if wordrow!=None:
                wordid = wordrow[0]
                wordids.append(wordid)
                if tablenumber>0:
                    tablelist += ","
                    clauselist+= " and "
                    clauselist += 'w%d.urlid=w%d.urlid and ' % (tablenumber-1,tablenumber)
                fieldList += ",w%d.location" % tablenumber
                tablelist += "wordlocation w%d" % tablenumber
                clauselist+="w%d.wordid=%d" % (tablenumber,wordid)
                tablenumber+=1

        if not tablelist:
            print("nothing matched")
            return [],[]
        fullquery = "select %s from %s where %s" % (fieldList,tablelist,clauselist)
        print(fullquery)
        cur = self.con.execute(fullquery)
        rows = [row for row in cur]
        return rows,wordids

if(__name__=="__main__"):
    # pagelist = ["http://www.baidu.com"]
    # c = crawler("searchindex.db")
    # c.createindextables()
    # c.crawl(pagelist)

    s = searcher("searchindex.db")
    rows,wordids = s.getmatchrows("apple baidu")
    print(rows)