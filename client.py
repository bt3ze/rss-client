# an example to show how the feedreader works:

from newssource import newsitem
from feedreader import feedreader
from datetime import date
import json
import time
from utils import do_every, flatten
from functools import reduce
import ipaddress, sys
import threading, requests
from time import sleep

from flask import Flask
app = Flask(__name__)

'''
try:
    # this just tests that the input address is valid
    ipaddr = ipaddress.ip_address(sys.argv[1])
    
    dest_ip = sys.argv[1]
    dest_port = sys.argv[2]
except Exception as e:
    print(e)
    exit(1)
'''

dest_ip = sys.argv[1]
dest_port = sys.argv[2]

# this is a list of feeds that work when we request them
#LST_FILE = "goodfeeds.list"
#LST_FILE = "shortfeeds.list"
LST_FILE = "first_good_list.txt"

HOST="0.0.0.0"
PORT=5000


# there are three noteworthy objects for our rss reader:
# the "feedreader" iself
# the "rssfeed"
# and the "newsitem"

# to use the feedreader, simply pass it the filename containing a list of rss feeds.
# it will create an "rssfeed" that polls the source url and retrieves news stories


def send_to_db(data_,dest_ip,dest_port):
    try:
        r = requests.post("http://"+dest_ip+":"+dest_port+"/new",json=json.dumps(data_),headers=headers)
        print(r)
        return 1
    except Exception as e:
        print(e)
        return 0

#print("feeds: ",feeds)


def periodic_update(reader):
    # now we have a list of rssfeeds in the "feeds" variable
    # we can use them to get the news
    
    print("time: ",time.strftime("%H:%M:%S"))
    #newsitems = flatten(reader.fast_update())
    #reader.fast_dispatch(newsitems)
    
    responses = flatten(reader.fast_update_and_dispatch())
    print(responses)
    #items = [n['item'] for n in newsitems ]
    
    '''
    for i in range(0,len(items)):
        url = items[i].url
        digest = { "title":items[i].title, "url": url, "summary": items[i].article.summary, "keywords": items[i].article.keywords, "source": tldextract.extract( url ).domain }
        print(json.dumps(digest))
        send_to_db(digest)
    '''
    #print("\n\n\n end of round. \n\n\n")
    #return "Hello World"
        
#do_every(3600, periodic_update,[feeds],20)

#periodic_update(feeds)





reader = feedreader(LST_FILE,dest_ip, dest_port)

@app.route("/")
def startup():
    print("Start!")
    #reader = feedreader(LST_FILE,dest_ip, dest_port)
    #feeds = reader.feeds

    #do_every(3600, periodic_update,[reader],20)

    periodic_update(reader)
    return "Hello World!"

@app.route("/parseurl/<url>")
def parseurl(url):
    return "parse url " + url

@app.route("/addfeed/<url>")
def addfeed(url):
    return "add url" + url

if __name__ == "__main__":
    print ("Hello World! Test 123")
    
    def hit_port():
        response = requests.request("GET","http://"+HOST+":"+str(PORT))

    def periodic_func():
        sleep(30)
        do_every(7200,hit_port,[],200)

    thread = threading.Thread(target = periodic_func)
    thread.start()

    app.run(debug=True,host=HOST, port=PORT)   
    
    #feeds = reader.feeds

