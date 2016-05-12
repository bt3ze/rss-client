
# this file implements a Feed Reader, which takes a list of rss feeds, determiens which can be parsed effectively, and periodically updates them


import requests
from datetime import date
import datetime, time
import newssource
import parse
import tldextract, json

from utils import threaded_map, apply_max, ret_max

import queue

#HEADERS = {'user-agent':'bt-rss-reader/0.1','Content-type':'application/json','Accept':'text/plain'}
HEADERS = {'Content-type':'application/json','Accept':'text/plain'}
#headers={}
TIMEOUT = 0.9
LST_FILE = "feeds.list"
DEBUG = False

def determine_parse_fn(feed_url):
    try:
        response = requests.request("GET",feed_url,headers=HEADERS,timeout = TIMEOUT)
        parsefn = ret_max(response.text, [parse.parseXml, parse.parseHtml, parse.parseRss])
        return parsefn
    except requests.exceptions.Timeout as e:
        if DEBUG:
            print(feed_url,e)
    except requests.exceptions.TooManyRedirects as e:
        if DEBUG:
            print(feed_url,e)
            #write_error(badfeeds,url,e)
    except requests.exceptions.RequestException as e:
        if DEBUG:
            print(feed_url,e)
            #write_error(badfeeds,url,e)
    return 0


def parse_line(l):
    return l

def write_error(errfile,data,err):
    errfile.write(data)
    #errfile.write(err)

# this function returns a list of feed objects
def import_feeds(source):

    feeds = []
    
    if DEBUG:
        goodfeeds = open("goodfeeds.list",'w')
        badfeeds = open("badfeeds.list",'w')

    f = open(source,'r')
    for line in f.readlines():
    
        url = parse_line(line)
        #print(line)
        
        if "nytimes" in line or "forbes" in line:
            continue

        try:
            response = requests.request("GET",url,headers=HEADERS,timeout = TIMEOUT)
            (news,parsefn) = apply_max(response.text, [parse.parseXml, parse.parseHtml, parse.parseRss])
        except requests.exceptions.Timeout as e:
            if DEBUG:
                write_error(badfeeds,url,e)
            continue
        except requests.exceptions.TooManyRedirects as e:
            if DEBUG:
                write_error(badfeeds,url,e)
            continue
        except requests.exceptions.RequestException as e:
            if DEBUG:
                write_error(badfeeds,url,e)
            continue

        #print("len news: ",len(news))
        if len(news) > 0:
            feeds.append(newssource.rssfeed(url,parsefn))
            if DEBUG:
                goodfeeds.write(line)
        else: # len(news) ==0
            if DEBUG:
                badfeeds.write(line)
            pass

    f.close()
    if DEBUG:
        goodfeeds.close()
        badfeeds.close()
    return feeds



class feedreader:
    def __init__(self, fname_, dest_db_, dest_port_):
        self.feeds = []
        self.fname = fname_
        self.feed_urls = []
        self.read_urls()
        self.construct_feeds()
        self.dest_db = dest_db_
        self.dest_port = dest_port_

    def read_urls(self):
        print("read urls")
        f = open(self.fname,'r')
        for line in f.readlines():
            url = parse_line(line)
            self.feed_urls.append(url)
            print(url),
        f.close()

    def construct_feeds_slow(self):
        #print("construct feeds",self.feed_urls)
        feeds = []
        
        for url in self.feed_urls:
            #print(url)
            parsefn = determine_parse_fn(url)
            #print(parsefn)
            feeds.append(newssource.rssfeed(url,parsefn))

        self.feeds = feeds


    def construct_feeds(self):
        print("construct feeds", self.feed_urls)        
        self.extend_feeds(self.feed_urls)

    def extend_feeds(self,urllist):
        def make_feeds(url_list):
            #print("make feeds")
            
            def make_newssource(url):
                parsefn = determine_parse_fn(url)
                #print(parsefn)
                n = newssource.rssfeed(url,parsefn)
                return n
        
            newssources = threaded_map(make_newssource,url_list)
            return newssources
        
        newfeeds = make_feeds(urllist)
        self.feeds.extend(newfeeds)
        self.feed_urls.extend(urllist)
    

    def fast_update(self):
        #print("fast update")

        def update_fn(item):
            return item.fast_update()
        
        # this should be returning an array of arrays of keyword,url,item objects
        return threaded_map(update_fn,self.feeds)


    def send_to_db(self,digest):
         try:
             r = requests.post("http://"+self.dest_db+":"+self.dest_port+"/new",json=json.dumps(digest),headers=HEADERS, timeout=TIMEOUT)
             print(r)
             return [1,digest["url"]]
         except Exception as e:
             print(e)
             return [0,digest["url"],e]


    def dispatch_fn(self,item):
        print(item)
        it = item['item']
        url = it.url
        
        if url == "0.0.0.0":
            print (json.dumps(item))
            return 0
        digest = { "title":it.title, "url": url, "summary": it.article.summary, "keywords": it.article.keywords, "source": tldextract.extract( url ).domain }
        print(json.dumps(digest))
        return self.send_to_db(digest)


    def fast_dispatch(self,items):
        return threaded_map(self.dispatch_fn,items)
        
        
    def fast_update_and_dispatch(self):
        def update_and_dispatch(item):
            newitems = item.fast_update()
            return threaded_map(self.dispatch_fn,newitems)
        
        return threaded_map(update_and_dispatch,self.feeds)
        #newitems = fast_update()
        #return fast_dispatch(newitems)

    def update(self):
        for feed in self.feeds:
            feed.update()
        
    def retrieve(self):
        self.feeds = import_feeds(self.fname)




