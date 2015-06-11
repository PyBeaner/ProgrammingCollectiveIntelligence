import feedparser
import re
from docclass import *

# Takes a filename of URL of a blog feed and classifies the entries
def read(feed,classifier):
    # get feed entries loop over them
    f = feedparser.parse(feed)
    for entry in f["entries"]:
        print("\n")
        print("-----")
        print("Title:    "+str(entry['title'].encode("utf-8")))
        print("Publisher:"+str(entry["publisher"].encode("utf-8")))
        print("\n")
        print(entry["summary"].encode("utf-8"))

        fulltext = "%s\n%s\n%s" %(entry["title"],entry["publisher"],entry["summary"])
        print("Guess: "+str(classifier.classify(fulltext)))

        cat = input("Enter category: ")
        classifier.train(fulltext,cat)

def entryfeatures(entry):
    splitter = re.compile("\\W*")
    f = {}
    # Extract the title words and annotate
    titlewords = [s.lower() for s in splitter.split(entry["title"])
                  if len(s)>2 and len(s)<20]
    for w in titlewords:f["Title:"+w] = 1
    summarywords = [s.lower() for s in splitter.split(entry['summary'])
                  if len(s)>2 and len(s)<20]
    uc = 0
    for i in range(len(summarywords)):
        w = summarywords[i]
        f[w] = 1
        if w.isupper():uc+=1

        if i<len(summarywords)-1:
            twoword = " ".join(summarywords[i:i+1])
            f[twoword] = 1

    # Keep creator and publisher whole
    f['Publisher:'+entry['publisher']]=1
    # UPPERCASE is a virtual word flagging too much shouting
    if float(uc)/len(summarywords)>0.3: f['UPPERCASE']=1
    return f


if __name__ == "__main__":
    c = fisherclassifier(getwords)
    c.setdb("python_feed.db")
    read("python_search.xml",c)