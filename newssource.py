# 
# This file describes the newssource object
# A newssource will include:
# - a url that is its source
# - a type (xml, html, rss)
# - a function used to process an element from the news source and extract its useful information
# - other bookkeeping information (like time last checked, last known element, etc)
#


import requests
from bs4 import BeautifulSoup
import json
from datetime import date
import time

# the following three parse functions operate on the response of an rss feed
# and they return a list (just an array) of newsitems from which to gather info

# Set speed to False for the temp urls
# True requires an extra hit to each responded item 
speed = True


class newsitem:
    def __init__(self, title_, url_, time_):
        self.title = title_
        self.url = url_
        self.time = time_
    
    def __str__(self):
        #return "{ title: " +  self.title + " ; url: " + self.url + " } "
        return "{ url: " + self.url + " } "

    def __repr__(self):
        return self.__str__()


class rssfeed:
    def __init__(self, sourceurl_, parsefn_):
        self.sourceurl = sourceurl_
        self.parsefn = parsefn_
        self.newslist = []

    def update(self):
        new_list = self.parsefn(self.sourceurl)
        for n in new_list:
            contained = False
            for o in self.newslist:
                if n.url == o.url:
                    contained = True

            if not contained:
                # here, we do some function to go grab the resource and process to input to our database
                pass
                


def parseXml(content):
    #print content
    list = []
    soup = BeautifulSoup(content, "xml")
    for item in soup.find_all("item"):
        link = item.find("link")
        title = item.find("title")
        if not speed:
            response = requests.request("GET",link.string)
            list.append(newsitem(title.string,response.url,date.today()))
        else:
            list.append(newsitem(title.string,link.string,date.today()))

    return list

def parseHtml_regitem(content):
    #print content
    list = []
    soup = BeautifulSoup(content, "xml")
    for item in soup.find_all("regularitem"):
        title = item.find("itemtitle")
        
        list.append(newsitem(title.string,link.string,date.today()))
    return list
        

def parseHtml(content):
    print content
    list = []
    soup = BeautifulSoup(content, 'xml')
    for item in soup.find_all("item"):
        title = item.find("title")
        link = item.find("link")
        response = requests.request("GET",link.string)
        list.append(newsitem(title.string,response.url,date.today()))
        #list.append(newsitem(title.string,link.string,date.today()))
    return list

def parseNyt(content):
    print content
    list = []
    soup = BeautifulSoup(content, 'xml')
    for item in soup.find_all("item"):
        print "item: ", item
       
        title = item.find("title")
        link = item.find("link")
        print title.string
        #print link["href"]
        ##response = requests.request("GET",link.string)
        #list.append(newsitem(title.string,response.url,date.today()))
        #list.append(newsitem(title.string,link["href"],date.today()))
        list.append(newsitem(title.string,link.string,date.today()))
        
    return list

def parseRss(content):
    pass



class Newssource:
    def __init__(self, url_, type_,parse_):
        self.url = url_
        self.type = type_
        self.parse = parse_
        self.last = ""

