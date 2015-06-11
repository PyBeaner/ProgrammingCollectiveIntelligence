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

if __name__ == "__main__":
    c = fisherclassifier(getwords)
    c.setdb("python_feed.db")
    read("python_search.xml",c)