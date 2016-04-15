
#right now, this file just takes a file with a list of rss feeds and determines which can be parsed effectively using the xmlparse function. this should be enough to get going as there are 126 of them.


import requests
from bs4 import BeautifulSoup
import json
from datetime import date

import datetime, threading, time



import newssource
import request_parse
#from newssource import *
#from request_parse import *

headers = {'user-agent':'bt-rss-reader/0.1'}

TIMEOUT = 0.1
LST_FILE = "feeds.list"

# the following function applies each of the functions in fnlist
# and returns the function that achieved the max length
def apply_max(obj,fnlist):
    max = -1
    for fn in fnlist:
        tmp_result = fn(obj)
        tmp_count = len(tmp_result)
        if(tmp_count > max):
            retfn = fn
            max = tmp_count
            result = tmp_result
    return (result, retfn)

def parse_line(l):
    return l


'''
def test_new_candidate(line):
    response = requests.request("GET",url,headers=headers)
    (news,parsefn) = apply_max(response.text, [request_parse.parseXml, request_parse.parseHtml, request_parse.parseRss])
    if len(news) > 0:
        return 
'''
   

def write_error(errfile,data,err):
    errfile.write(data)
    #errfile.write(err)
 
# this function returns a list of feed objects
def import_feeds(source):

    feeds = []

    #xmlf = open("xmlwrite.list",'w')
    #noxmlf = open("noxml.list",'w')
    goodfeeds = open("goodfeeds.list",'w')
    badfeeds = open("badfeeds.list",'w')

    f = open(source,'r')
    for line in f.readlines():
    
        url = parse_line(line)
        print line
        
        if "nytimes" in line or "forbes" in line:
            #time.sleep(5)
            continue

        try:
            response = requests.request("GET",url,headers=headers,timeout = 0.1)
            (news,parsefn) = apply_max(response.text, [request_parse.parseXml, request_parse.parseHtml, request_parse.parseRss])
        except requests.exceptions.Timeout as e:
            write_error(badfeeds,url,e)
            continue
        except requests.exceptions.TooManyRedirects as e:
            write_error(badfeeds,url,e)
            continue
        except requests.exceptions.RequestException as e:
            write_error(badfeeds,url,e)
            continue

        print "len news: ",len(news)
        
        if len(news) > 0:
            feeds.append(newssource.rssfeed(url,parsefn))

            goodfeeds.write(line)
            #reghtml.write(line)
        else: # len(news) ==0
            badfeeds.write(line)
            #oparse.write(line)

    print "num feeds: ",len(feeds)
    #print feeds

    f.close()
    goodfeeds.close()
    badfeeds.close()

    return feeds

        
def update_items(lst):
    print lst
    for l in lst:
        print l
        l.update()



def do_every (interval, worker_func, args, iterations = 0):
    if iterations != 1:
        threading.Timer (
            interval,
            do_every,
            [interval, worker_func, args, 0 if iterations == 0 else iterations-1]
        ).start ()
        
        worker_func(*args)


#def periodic_update(update_obj):
#    next_call = time.time()
#    while True:
#        update_items(update_obj)
        #print datetime.datetime.now()
#        next_call = next_call+1;
#        time.sleep(next_call - time.time())

feeds = import_feeds(LST_FILE)
# call update_items every ten minutes
do_every (60, update_items, [feeds],3)

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
