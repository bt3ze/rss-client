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

dest_port = sys.argv[1]
dest_ips = sys.argv[2:]

# this is a list of feeds that work when we request them
LST_FILE = "goodfeeds.list"
#LST_FILE = "shortfeeds.list"
#LST_FILE = "first_good_list.txt"

HOST="0.0.0.0"
PORT=5000


# there are three noteworthy objects for our rss reader:
# the "feedreader" iself
# the "rssfeed"
# and the "newsitem"

# to use the feedreader, simply pass it the filename containing a list of rss feeds.
# it will create an "rssfeed" that polls the source url and retrieves news stories


def periodic_update(reader):
    # now we have a list of rssfeeds in the "feeds" variable
    # we can use them to get the news
    
    print("time: ",time.strftime("%H:%M:%S"))
    #newsitems = flatten(reader.fast_update())
    #reader.fast_dispatch(newsitems)
    
    responses = flatten(reader.fast_update_and_dispatch())
    print(responses)



reader = feedreader(LST_FILE,dest_ips, dest_port)

@app.route("/isalive")
def isalive():
    return "hello"

@app.route("/list_feeds")
def list_feeds():
    return str(reader.get_feeds())

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

@app.route("/addfeed/<path:code>")
def addfeed(code):
    reader.add_feed(code)
    return "add url " + code

@app.route("/removefeed/<path:code>")
def removefeed(code):
    return "remove feed: " + code + " " + str(reader.remove_feed(code))

if __name__ == "__main__":
    print ("Hello World! Test 123")
    
    def hit_port():
        response = requests.request("GET","http://"+HOST+":"+str(PORT))

    def periodic_func():
        sleep(30)
        do_every(7200,hit_port,[],200) #2 hours

    thread = threading.Thread(target = periodic_func)
    thread.start()
    
    app.run(debug=True,host=HOST, port=PORT)   
    
    #feeds = reader.feeds

