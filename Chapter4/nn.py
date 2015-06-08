from math import tanh
import sqlite3 as sqlite


class searchnet:
    def __init__(self,dbname):
        self.con = sqlite.connect(dbname)

    def __del__(self):
        self.con.close()

    def maketables(self):
        self.con.execute("create table hiddennode(create_key)")
        self.con.execute("create table wordhidden(fromid,toid,strength)")
        self.con.execute("create table urlhidden(fromid,toid,strength)")

        self.con.commit()

    def getstrength(self,fromid,toid,layer):
        if layer==0:table="wordhidden"
        else:table="urlhidden"

        res = self.con.execute("select * from %s where fromid=%d and toid=%d" %(table,fromid,toid)).fetchone()
        if not res:
            if layer==0:return -0.2
            if layer==1:return 0
        return res[0]

    def setstrength(self,fromid,toid,layer,strength):
        if layer==0:table="wordhidden"
        else:table="urlhidden"

        res = self.con.execute("select * from %s where fromid=%d and toid=%d" %(table,fromid,toid)).fetchone()
        if not res:
            self.con.execute("insert into %s(fromid,toid,strength) VALUES(%d,%d,%f)" %(table,fromid,toid,strength))
        else:
            rowid = res[0]
            self.con.execute("update table %s set strength=%f where rowid=%d" % (table,strength,rowid))

    def generatehiddennode(self,wordids,urls):
        if len(wordids)>3:return
        createkey = "_".join([str(wi) for wi in wordids])
        res = self.con.execute("select * from hiddennode where create_key='%s'" % createkey).fetchone()
        if res:
            return
        cur = self.con.execute(
            "insert into hiddennode(create_key) values('%s')" % createkey
        )
        hiddenid = cur.lastrowid
        for wi in wordids:
            self.setstrength(wi,hiddenid,layer=0,strength=1.0/len(wordids))
        for url in urls:
            self.setstrength(hiddenid,url,layer=1,strength=0.1)

        self.con.commit()

    def getallhiddenids(self,wordids,urlids):
        ret = {}
        for wid in wordids:
            cur = self.con.execute("select toid from wordhidden where fromid=%d" % wid)
            for row in cur:ret[row[0]] = 1

        for uid in urlids:
            cur = self.con.execute("select fromid from urlhidden where toid=%d" % uid)
            for row in cur:ret[row[0]] = 1

        return ret.keys()

    def setupnetword(self,wordids,urlids):
        # self.wordids = wordids
        pass

if __name__=="__main__":
    s = searchnet("nn.db")
    s.maketables()
    wWorld,wRiver,wBank =101,102,103
    uWorldBank,uRiver,uEarth =201,202,203
    s.generatehiddennode([wWorld,wBank],[uWorldBank,uRiver,uEarth])
    for c in s.con.execute('select * from wordhidden'):
        print(c)
    for c in s.con.execute('select * from urlhidden'):
        print(c)
