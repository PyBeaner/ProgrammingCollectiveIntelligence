import re
import math
import sqlite3 as sqlite

def getwords(doc):
    splitter = re.compile("\\W*")
    words = [w.lower() for w in splitter.split(doc)
             if len(w)>2 and len(w)<20]
    return dict([(w,1) for w in words])

def sampletrain(cl):
    cl.train('Nobody owns the water.','good')
    cl.train('the quick rabbit jumps fences','good')
    cl.train('buy pharmaceuticals now','bad')
    cl.train('make quick money at the online casino','bad')
    cl.train('the quick brown fox jumps','good')

class classifier:
    def __init__(self,getfeatures,filename=None):
        # count of feature/category
        self.fc = {}
        # count of document in each category
        self.cc = {}
        self.getfeatures = getfeatures

    def setdb(self,dbname):
        self.con = sqlite.connect(dbname)
        self.con.execute("create table if NOT EXISTS fc(feature,category,count)")
        self.con.execute("create table if NOT EXISTS cc(category,count)")

    # increase the count of a feature
    def incf(self,f,cat):
        # self.fc.setdefault(f,{})
        # self.fc[f].setdefault(cat,0)
        # self.fc[f][cat] += 1

        count = self.fcount(f,cat)
        if count==0:
            query = "insert into fc VALUES ('%s','%s',1)" % (f,cat)
        else:
            query = "update fc set count=%d where feature='%s' and category='%s'" % (count+1,f,cat)
        self.con.execute(query)

    # increase the count of a category
    def incc(self,cat):
        # self.cc.setdefault(cat,0)
        # self.cc[cat]+=1
        count = self.catcount(cat)
        if count==0:
            self.con.execute("insert into cc values('%s',1)" % (cat))
        else:
            self.con.execute("update cc set count=%d where category='%s'" %(count+1,cat))

    # the number of times a feature has appeared in a category
    def fcount(self,f,cat):
        # if f in self.fc and cat in self.fc[f]:
        #     return self.fc[f][cat]
        # return 0
        res = self.con.execute("select count from fc where feature='%s' and category='%s'" %(f,cat)).fetchone()
        if not res:return 0
        return res[0]

    def catcount(self,cat):
        # if cat in self.cc:
        #     return self.cc[cat]
        # return 0
        res = self.con.execute("select count from cc where category='%s'" % (cat)).fetchone()
        if not res:return 0
        return res[0]

    def totalcount(self):
        # return sum(self.cc.values())
        return self.con.execute("select sum(count) from cc").fetchone()[0]

    def categories(self):
        # return self.cc.keys()
        cur = self.con.execute("select category from cc")
        return [row[0] for row in cur]

    def train(self,item,cat):
        features = self.getfeatures(item)
        for f in features:
            self.incf(f,cat)
        self.incc(cat)
        self.con.commit()

    def fprob(self,f,cat):
        if self.catcount(cat)==0:return 0
        return self.fcount(f,cat)/self.catcount(cat)

    def weightedprob(self,f,cat,prf,weight=1.0,ap=0.5):
        basicprob = prf(f,cat)
        totals = sum([self.fcount(f,cat) for cat in self.categories()])
        bp = ((weight*ap)+(totals*basicprob))/(weight+totals)
        return bp

class naivebayes(classifier):
    def __init__(self,getfeatures):
        super(naivebayes,self).__init__(getfeatures)
        self.thresholds = {}

    def setthreshold(self,cat,t):
        self.thresholds[cat] = t

    def getthreshold(self,cat):
        if cat not in self.thresholds:return 1.0
        return self.thresholds[cat]

    # Guess category of a document
    def classify(self,item,default=None):
        probs = {}
        max = 0.0
        best = None
        for cat in self.categories():
            probs[cat] = self.prob(item,cat)
            if probs[cat]>max:
                max = probs[cat]
                best = cat

        for cat in probs:
            if cat==best:continue
            # if the best prob < its threshold * other category:
            # return default(unknown)
            if probs[cat]*self.getthreshold(best)>probs[best]:return default
        return best

    def docprob(self,item,cat):
        features = self.getfeatures(item)
        p = 1
        for f in features:
            p *= self.weightedprob(f,cat,self.fprob)
        return p

    def prob(self,item,cat):
        catprob = self.catcount(cat)/self.totalcount()
        docprob = self.docprob(item,cat)

        # Pr(A | B) = Pr(B | A) x Pr(A)/Pr(B)
        # Pr(B) is the same
        return catprob*docprob

class fisherclassifier(classifier):
    def __init__(self,getfeatures):
        super(fisherclassifier,self).__init__(getfeatures)
        self.minimums = {}

    def setminimum(self,cat,min):
        self.minimums[cat] = min

    def getminimum(self,cat):
        if cat not in self.minimums:return 0
        return self.minimums[cat]

    def classify(self,item,default=None):
        best = default
        max = 0.0
        for c in self.categories():
            p = self.fisherprob(item,c)
            if p>self.getminimum(c) and p>max:
                best = c
                max = p
        return best

    def cprob(self,f,cat):
        clf = self.fprob(f,cat)
        if clf==0:return 0
        freqsum = sum([self.fprob(f,cat) for cat in self.categories()])
        p = clf/freqsum
        return p

    # always between 0 and 1
    def fisherprob(self,item,cat):
        p = 1
        features = self.getfeatures(item)
        for f in features:
            p *= self.weightedprob(f,cat,self.cprob)
        fscore = -2 * math.log(p)
        return self.invchi2(fscore,len(features)*2)

    def invchi2(self, chi, df):
        m = chi/2.0
        sum = term = math.exp(-m)
        for i in range(1,int(df/2)):
            term*=m/i
            sum+=term
        return min(sum,1.0)

if __name__ == "__main__":
    c = classifier(getfeatures=getwords)
    c.setdb("test1.db")
    c.train('the quick brown fox jumps over the lazy dog','good')
    c.train('make quick money in the online casino','bad')
    # print(c.fprob("quick","good"))
    sampletrain(c)
    p = c.weightedprob("money","good",c.fprob)
    print(p)
    sampletrain(c)
    p = c.weightedprob("money","good",c.fprob)
    print(p)

    print("naive---")
    naive = naivebayes(getfeatures=getwords)
    naive.setdb("test1.db")
    sampletrain(naive)
    p = naive.prob("quick rabbit","good")
    print(p)
    p = naive.prob("quick rabbit","bad")
    print(p)

    print("classify---")
    cat = naive.classify("quick rabbit",default="unknown")
    print(cat)
    cat = naive.classify("quick money",default="unknown")
    print(cat)
    naive.setthreshold("bad",3.0)# avoid classify a good one as a bad one
    cat = naive.classify("quick money",default="unknown")
    print(cat)
    for i in range(10):sampletrain(naive)
    cat = naive.classify("quick money",default="unknown")
    print(cat)

    print("fisher----")
    finsher = fisherclassifier(getwords)
    finsher.setdb("test1.db")
    sampletrain(finsher)
    cat = finsher.classify("quick rabbit")
    print(cat)
    cat = finsher.classify("quick money")
    print(cat)
    finsher.setminimum("bad",0.8)
    cat = finsher.classify("quick money")
    print(cat)
    finsher.setminimum("good",0.8)
    cat = finsher.classify("quick rabbit")
    print(cat)