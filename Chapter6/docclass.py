import re
import math

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

    # increase the count of a feature
    def incf(self,f,cat):
        self.fc.setdefault(f,{})
        self.fc[f].setdefault(cat,0)
        self.fc[f][cat] += 1

    # increase the count of a category
    def incc(self,cat):
        self.cc.setdefault(cat,0)
        self.cc[cat]+=1

    # the number of times a feature has appeared in a category
    def fcount(self,f,cat):
        if f in self.fc and cat in self.fc[f]:
            return self.fc[f][cat]
        return 0

    def catcount(self,cat):
        if cat in self.cc:
            return self.cc[cat]
        return 0

    def totalcount(self):
        return sum(self.cc.values())

    def categories(self):
        return self.cc.keys()

    def train(self,item,cat):
        features = self.getfeatures(item)
        for f in features:
            self.incf(f,cat)
        self.incc(cat)

if __name__ == "__main__":
    c = classifier(getfeatures=getwords)
    sampletrain(c)
    c.train('the quick brown fox jumps over the lazy dog','good')
    c.train('make quick money in the online casino','bad')
    print(c.fcount("quick","good"))
    print(c.fcount("quick","bad"))
