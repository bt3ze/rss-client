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
        return "{ url: " + self.url + "; title: " + self.title + " } "
        
    def __repr__(self):
        return self.__str__()

    def retrieve(self):
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
            return self
        

class rssfeed:
    def __init__(self, sourceurl_, parsefn_):
        self.sourceurl = sourceurl_
        self.parsefn = parsefn_
        self.fetched_urls = deque([],maxlen=URL_LIST_SIZE)

    def __str__(self):
        return "feed: { url: " + self.sourceurl + " ; parsefn: " + str(self.parsefn) + " } "

    def __repr__(self):
        return self.__str__()

    def get_news(self):
        news = parse.get_rss_feed(self.sourceurl, self.parsefn)
        return news
    

    def update(self):
        def fetch_fn(news_item):
            if news_item.url in self.fetched_urls:
                pass
            else:
                self.fetched_urls.append(news_item.url)
                news_item.retrieve()
            #print ("update keywords: ",news_item.keywords)

        new_list = self.get_news()        
        return map(fetch_fn,new_list)
    
    def fast_update(self):
        def fetch_fn(news_item):
            if news_item.url in self.fetched_urls:
                pass
            else:
                success = news_item.retrieve()
                if success == 0:
                    print ("retrieve failed: ",news_item.url)
                else:
                    self.fetched_urls.append(news_item.url)
                    #print ("update keywords: ",news_item.keywords)
                    return { "url": news_item.url, "keywords": news_item.keywords, "item":news_item }

        #print("Fast Update!")
        new_list = self.get_news()
        return threaded_map(fetch_fn,new_list)
