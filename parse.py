#
# these functions handle how we request information from the 
# rss feeds
# and will also handle how we parse individual news requests
#

import requests
from bs4 import BeautifulSoup
import json
from datetime import date

import newssource

# Set speed to False for the temp urls
# True requires an extra hit to each responded item 
speed = True


def get_rss_feed(url,parsefn):
    headers = {'user-agent':'bt-rss-reader/0.1'}
    try:
        response = requests.request("GET",url,headers=headers)
        #print (response.text)
    except requests.exceptions.Timeout as e:
        print(e)
        return ("",0)
    except requests.exceptions.TooManyRedirects as e:
        print(e)
        return ("",0)
    except requests.exceptions.RequestException as e:
        print(e)
        return ("",0)

    if parsefn == 0:
        return ("",0)
    return (response.url, parsefn(response.text))


# the following parse functions operate on the response of an rss feed
# and they return a list (just an array) of newsitems from which to gather info

def parseXml(content):
    #print content
    lst = []
    soup = BeautifulSoup(content, "xml")
    for item in soup.find_all("item"):
        link = item.find("link")
        title = item.find("title")
        if link != None:
            if not speed:
                response = requests.request("GET",link.string)
                lst.append(newssource.newsitem(title.string,response.url,date.today()))
            else:
                lst.append(newssource.newsitem(title.string,link.string,date.today()))
    return lst

def parseAtom(content):
    lst = []
    soup = BeautifulSoup(content, "xml")
    for item in soup.find_all("entry"):
        #print(item)
        link = item.find("link")
        title = item.find("title")
        #print(link.get("href"),title.string)
        if link != None:
            if not speed:
                response = requests.request("GET",link.get("href"))
                lst.append(newssource.newsitem(title.string,response.url,date.today()))
            else:
                lst.append(newssource.newsitem(title.string,link.get("href"),date.today()))
    return lst



def parseHtml_regitem(content):
    #print content
    list = []
    soup = BeautifulSoup(content, "xml")
    for item in soup.find_all("regularitem"):
        title = item.find("itemtitle")
        
        list.append(newssource.newsitem(title.string,link.string,date.today()))
    return list
        

def parseHtml(content):
    #print content
    list = []
    soup = BeautifulSoup(content, 'xml')
    for item in soup.find_all("item"):
        title = item.find("title")
        link = item.find("link")
        if link != None:
            if not speed:
                response = requests.request("GET",link.string)
                list.append(newssource.newsitem(title.string,response.url,date.today()))
            else: 
                list.append(newssource.newsitem(title.string,link.string,date.today()))
        #list.append(newsitem(title.string,link.string,date.today()))
    return list

def parseNyt(content):
    print (content)
    list = []
    soup = BeautifulSoup(content, 'xml')
    for item in soup.find_all("item"):
        print ("item: ", item)
       
        title = item.find("title")
        link = item.find("link")
        print (title.string)
        #print link["href"]
        ##response = requests.request("GET",link.string)
        #list.append(newsitem(title.string,response.url,date.today()))
        #list.append(newsitem(title.string,link["href"],date.today()))
        list.append(newssource.newsitem(title.string,link.string,date.today()))
        
    return list

def parseRss(content):
    return []

