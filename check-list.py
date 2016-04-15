#
# This file reads in  a list of urls,
# then outputs them as json-encoded 
# objects which include url of the feed
# and its type (xml, etc)
#


import requests
import bs4
import json
#import urllib2
from sys import argv


print "begin processing rss streams"

xml_feeds = []


f = open(argv[1],'r')
w = open('valid.list','w')

xmlf = open('xmlfeeds.list','w')
htmlf = open('htmlfeeds.list','w')
rssf = open('rssfeeds.list','w')
otherf = open('otherfeeds.list','w')

for line in f:
    response = requests.request('GET',line)
    print line, response.status_code, response.encoding, response.headers['Content-Type'], response.history, response.links, response.url
    
    sc = response.status_code
    
    if not (sc == 404  or sc==503): 
        w.write(line)
        #w.write('\n')
    
        ct = response.headers['Content-Type']

        print ct
        print "validboo"

        if 'text/html' in ct: #ct == 'text/html;' or  ct == 'text/html':        
            htmlf.write(response.url)
            htmlf.write('\n')
            print "html feed"

        elif 'text/xml' in ct: #ct == 'text/xml;' or ct == 'text/xml':
            xmlf.write(response.url)
            xmlf.write('\n')
            print "xml feed"

        elif 'rss' in ct:
            rssf.write(response.url)
            rssf.write('\n')
            print "rss feed"

        else:
            otherf.write(response.url)
            otherf.write('\n')
            print "other feed"

f.close()
w.close()
htmlf.close()
xmlf.close()
rssf.close()
otherf.close()
