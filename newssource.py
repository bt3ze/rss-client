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


import request_parse


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

    def __str__(self):
        nlist = ""
        for n in self.newslist:
            nlist += " " + n
        nlist = nlist[:-1]

        return "feed: { url: " + self.sourceurl + " ; parsefn: " + str(self.parsefn) +\
            " newslist: [ " + nlist + " ] } "

    def __repr__(self):
        return self.__str__()

    def get_news(self):
        return get_news_items(self.sourceurl, self.parsefn)

    def update(self):
        print self.__str__()
        '''
        new_list = get_news_items(self.sourceurl, self.parsefn)
        for n in new_list:
            contained = False
            for o in self.newslist:
                if n.url == o.url:
                    contained = True

            if not contained:
                # here, we do some function to go grab the resource and process to input to our database
                pass
        '''        
