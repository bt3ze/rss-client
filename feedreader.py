
# this file implements a Feed Reader, which takes a list of rss feeds, determiens which can be parsed effectively, and periodically updates them


import requests
from datetime import date
import datetime, time
import newssource
import parse

from utils import threaded_map, apply_max, ret_max

import queue

HEADERS = {'user-agent':'bt-rss-reader/0.1'}
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
    def __init__(self, fname_):
        self.feeds = []
        self.fname = fname_
        self.feed_urls = []
        self.read_urls()
        self.construct_feeds()


    def read_urls(self):
        #print("read urls")
        f = open(self.fname,'r')
        for line in f.readlines():
            url = parse_line(line)
            self.feed_urls.append(url)
            #print(url),
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
        #print("construct feeds", self.feed_urls)        
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

    
    def update(self):
        for feed in self.feeds:
            feed.update()
        
    def retrieve(self):
        self.feeds = import_feeds(self.fname)




