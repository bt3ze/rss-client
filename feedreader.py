
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
HEADERS = {'user-agent':'Bot - bt-rss-reader/0.1; bterner@umail.ucsb.edu','Content-type':'application/json','Accept':'text/plain'}
#headers={}
TIMEOUT = 0.9
LST_FILE = "feeds.list"
DEBUG = False

def determine_parse_fn(feed_url):
    try:
        response = requests.request("GET",feed_url,headers=HEADERS,timeout = TIMEOUT)
        #print("url: ",response.url)
        #print(response.text)
        #parsefn = ret_max(response.text, [parse.parseXml, parse.parseAtom, parse.parseHtml, parse.parseRss])
        parsefn = ret_max(response.text, [parse.parseXml, parse.parseAtom])
        url = response.url
        if url.endswith('%0A'):
            url = url[:-3]
        return (url,parsefn)
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
    return ("",0)


def parse_line(l):
    return l

def write_error(errfile,data,err):
    errfile.write(data)
    #errfile.write(err)



class feedreader:
    def __init__(self, fname_, dest_dbs_, dest_port_):
        self.feeds = []
        self.fname = fname_
        self.feed_urls = []
        self.read_urls()
        self.construct_feeds()
        self.dest_dbs = dest_dbs_
        self.dest_port = dest_port_

    def get_feeds(self):
        return self.feeds

    def add_feed(self,url):
        if url not in self.feed_urls:
            self.extend_feeds([url])
            return True
        return False

    def remove_feed(self,url):
        removed = False
        for f in self.feeds:
            if f.sourceurl == url:
                self.feeds.remove(f)
                removed = True
                break
            
        return removed

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
            (realurl, parsefn) = determine_parse_fn(url)
            #print(parsefn)
            if(parsefn != 0):
                feeds.append(newssource.rssfeed(realurl,parsefn))

        self.feeds = feeds


    def construct_feeds(self):
        print("construct feeds", self.feed_urls)        
        self.extend_feeds(self.feed_urls)

    def extend_feeds(self,urllist):
        def make_feeds(url_list):
            #print("make feeds")
            #feeds = []
            
            def make_newssource(url):
                (realurl, parsefn) = determine_parse_fn(url)
                print("url :" +url +"\nrealurl: " + realurl + "\nparsefn : " + str(parsefn))
                #print(parsefn)
                if parsefn==0:
                    return {'news':None,'url':"",'err':1}
                
                n = newssource.rssfeed(realurl,parsefn)
                return {'news':n,'url':url,'realurl': realurl,'err':0}
                                
            newssources = threaded_map(make_newssource,url_list,num_t=20)
            return newssources
        
        newfeeds = filter(lambda x: x['err'] == 0, make_feeds(urllist))

        #for n in newsfeeds:
        #    if n.err != 1:
        #        nfeeds.append(n.news)
        #        nurls.append(n.url)
        nfeeds = [n['news'] for n in newfeeds]
        nurls = [n['url'] for n in newfeeds]
        nrurls = [n['realurl'] for n in newfeeds]
        self.feeds.extend(nfeeds)
        self.feed_urls.extend(nurls)
        self.feed_urls.extend(nrurls)
    

    def fast_update(self):
        #print("fast update")

        def update_fn(item):
            return item.fast_update()
        
        # this should be returning an array of arrays of keyword,url,item objects
        return threaded_map(update_fn,self.feeds)


    def send_to_db(self,digest):
        def sendfn(dest_db, dest_port,digest):
            try:
                r1 = requests.post("http://"+dest_db+":"+dest_port+"/new",json=json.dumps(digest),headers=HEADERS, timeout=TIMEOUT)
                print(r1)
                return [1,digest["url"],dest_db]
            except Exception as e:
                print(e)
                return [0,digest["url"],dest_db,e]

        results = list( map(lambda x: sendfn(x,self.dest_port,digest), self.dest_dbs) )
        return results


    def dispatch_fn(self,item):
        if item['errcode'] != 0:
            print(item)
            #print (json.dumps(item))
            return item
        else:
            it = item['item']
            url = it.url
            digest = { "title":it.title, "url": url, "summary": it.article.summary, "keywords": it.article.keywords, "source": tldextract.extract( url ).domain }
            #print(json.dumps(digest))
            try: 
                print(digest)
            except Exception as e:
                print(e)
            return self.send_to_db(digest)


    def fast_dispatch(self,items):
        return threaded_map(self.dispatch_fn,items)
        
        
    def fast_update_and_dispatch(self):
        def update_and_dispatch(feed):
            #newsitems = feed.fast_update()
            newsitems = list(feed.update())
            #print (newsitems)
            return threaded_map(self.dispatch_fn,newsitems)
        
        return threaded_map(update_and_dispatch,self.feeds)
        #newitems = fast_update()
        #return fast_dispatch(newitems)

    def update(self):
        for feed in self.feeds:
            feed.update()

'''
    def retrieve(self):
        self.feeds = import_feeds(self.fname)
'''
