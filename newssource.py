# 
# This file describes the newssource object
# A newssource will include:
# - a url that is its source
# - a type (xml, html, rss)
# - a function used to process an element from the news source and extract its useful information
# - other bookkeeping information (like time last checked, last known element, etc)
#


from newspaper import Article
import parse
from utils import threaded_map
from collections import deque

URL_LIST_SIZE = 50


class newsitem:
    def __init__(self, title_, url_, time_):
        self.title = title_
        self.url = url_
        self.time = time_
        self.article = Article(self.url)
        self.retrieved = False
        self.keywords = []

    def __str__(self):
        #return "{ title: " +  self.title + " ; url: " + self.url + " } "
        if self.title == None or self.url == None:
            return "{ url: 0.0.0.0; title: bad newsitem }"
        return "{ url: " + self.url + "; title: " + self.title + " } "
        
    def __repr__(self):
        return self.__str__()

    def retrieve(self):
        if self.url.endswith(".mp3"):
            print ("error: attempting to download mp3")
            #self.retrieved = True
            return 0
        if not self.retrieved:
            print("retrieve: ",self.url)
            a = self.article
            a.download()
            if a.html == "":
                print("error: download failed")
                return 0
            a.parse()
            a.nlp()
            self.retrieved = 1
            #print(self.article.keywords)
            
            self.keywords = self.article.keywords
            #print(self.keywords)
            return self
        else:
            return 0
        

class rssfeed:
    def __init__(self, sourceurl_, parsefn_):
        self.sourceurl = sourceurl_
        self.parsefn = parsefn_
        self.fetched_urls = deque([],maxlen=URL_LIST_SIZE)

    def __str__(self):
        if self.sourceurl == None or self.parsefn == None:
            return "feed: { url: bad feed, parsefn: bad feed }"
        return "feed: { url: " + self.sourceurl + " ; parsefn: " + str(self.parsefn) + " } "

    def __repr__(self):
        return self.__str__()

    def get_news(self):
        print(self.sourceurl)
        print(self.parsefn)
        (a,news) = parse.get_rss_feed(self.sourceurl, self.parsefn)
        return news
    

    def update(self):
        def fetch_fn(news_item):
            if news_item.url in self.fetched_urls:
                return {'url':"0.0.0.0",'error':"status already fetched", 'errcode':1}
                #pass
            else:
                success = news_item.retrieve()
                if success == 0:
                    print ("retrieve failed: ",news_item.url)
                    return {"url":"0.0.0.0", 'error':"retrieve failed", 'errcode':2, "item": news_item}
                else:
                    self.fetched_urls.append(news_item.url)
                    print ("update keywords: ",news_item.keywords)
                    return { "url": news_item.url, "keywords": news_item.keywords, "item":news_item, 'errcode':0 }

        new_list = self.get_news()        
        return map(fetch_fn,new_list)
    
        
    def fast_update(self):
        def fetch_fn(news_item):
            if news_item.url in self.fetched_urls:
                return {'url':"0.0.0.0",'error':"status already fetched", 'errcode':1}
                #pass
            else:
                success = news_item.retrieve()
                if success == 0:
                    print ("retrieve failed: ",news_item.url)
                    return {"url":"0.0.0.0", 'error':"retrieve failed", 'errcode':2, "item": news_item}
                else:
                    self.fetched_urls.append(news_item.url)
                    print ("update keywords: ",news_item.keywords)
                    return { "url": news_item.url, "keywords": news_item.keywords, "item":news_item, 'errcode':0 }

        #print("Fast Update!")
        new_list = self.get_news()
        return threaded_map(fetch_fn,new_list)


        
