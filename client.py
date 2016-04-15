
#right now, this file just takes a file with a list of rss feeds and determines which can be parsed effectively using the xmlparse function. this should be enough to get going as there are 126 of them.


import requests
from bs4 import BeautifulSoup
import json
from datetime import date
import time

from newssource import *


headers = {'user-agent':'bt-rss-reader/0.1'}

f = open("feeds.list",'r')
xmlf = open("xmlwrite.list",'w')
noxmlf = open("noxml.list",'w')

newsitems = []

for line in f.readlines():
    url = line
    print line
    if "rss.nytimes" in line:
        time.sleep(5)
    response = requests.request("GET",url,headers=headers)
    news = parseXml(response.text)
    if len(news) > 0:
        xmlf.write(line)
        #reghtml.write(line)
        newsitems.append(news)

    else: # len(news) ==0
        noxmlf.write(line)
        #oparse.write(line)

    print len(news)


# now we can do something with the newsitems, like check if they have been updated recently or something





#    print 

#print news

#for line in f.readlines():
#    url = line
#    response = requests.request("GET",url,headers=headers)
#    news = parseXml(response.text)

#f = open("noxml2.list",'r')
#reghtml = open("reghtml.list",'w')
#oparse = open("otherparse.list",'

#url = "http://rss.nytimes.com/services/xml/rss/nyt/Arts.xml"
#url = "http://chicagotribune.feedsportal.com/c/34253/f/669303/index.rss"
#url = "http://feeds.theguardian.com/theguardian/world/rss"
#url = "http://rss.nytimes.com/services/xml/rss/nyt/Arts.xml"
#url = "http://rss.nytimes.com/services/xml/rss/nyt/Environment.xml"
#response = requests.request("GET",url,headers=headers)
#news = parseNyt(response.text)
#print news
#print len(news)
