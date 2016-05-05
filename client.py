# an example to show how the feedreader works:

from newssource import newsitem
from feedreader import feedreader
from datetime import date
import time
from utils import do_every, flatten
from functools import reduce

from flask import Flask
app = Flask(__name__)


# this is a list of feeds that work when we request them
#LST_FILE = "goodfeeds.list"
LST_FILE = "shortfeeds.list"


# there are three noteworthy objects for our rss reader:
# the "feedreader" iself
# the "rssfeed"
# and the "newsitem"

# to use the feedreader, simply pass it the filename containing a list of rss feeds.
# it will create an "rssfeed" that polls the source url and retrieves news stories




#print("feeds: ",feeds)

def periodic_update(reader):
    # now we have a list of rssfeeds in the "feeds" variable
    # we can use them to get the news
    print("time: ",time.strftime("%H:%M:%S"))
    newsitems = flatten(reader.fast_update())
    items = [n['item'] for n in newsitems ]
    texts = [n.article.text for n in items]
    #size = reduce(lambda a,b: a + len(b.html), [n['item'] for n in newsitems ],0)
    size = reduce(lambda a,b: a + len(b), texts,0)
    print("\n\n\n end of round. size: " + str(size) + " \n\n\n")
    #print ([i.html for i in items])
    #print (items)
    #print (texts)
    #print("\n\n\n end of round. \n\n\n")

        
#do_every(3600, periodic_update,[feeds],20)

#periodic_update(feeds)


@app.route("/")
def startup():
    print("Hello World!")
    reader = feedreader(LST_FILE)
    #feeds = reader.feeds
    periodic_update(reader)
    return "Hello World!"

@app.route("/parseurl/<url>")
def parseurl(url):
    return "parse url " + url


if __name__ == "__main__":
    app.run(debug=True)
