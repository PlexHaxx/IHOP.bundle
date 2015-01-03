# -*- coding: utf-8 -*-
PREFIX = "/video/ihop"
NAME = "IHOP Plugin"

MAXRESULTS = 50

IHOP_FEED_URL = "http://feed.theplatform.com/f/IfSiAC/5ct7EYhhJs9Z/"
IHOP_FEED_QUERY = "?q=%s&range=0-%s&=&sort=pubDate|desc&count=true"
IHOP_FEED_FILT = "&byCustomValue={ihopkc$setType}{Intercession}"
IHOP_JAVASCRIPT_URL = "http://cdn.ihopkc.org.edgesuite.net/wp-content/themes/ihopkc_theme/_js/ihopkc-main.min.js"

RE_WLEADER = Regex("""e.worshipLeaders\[0\]\.toLowerCase\(\)\)return"";var t\=(\[[a-zA-Z0-9\a\A\s",]+\]);""")

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0'
TITLE = L('IHOP')
ICON = 'icon-default.png'

####################################################################################################
def Start():
    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = USER_AGENT
    Log.Debug("Starting the IHOP Plugin")

@handler(PREFIX, NAME)
def MainMenu():
    Log.Debug("Load Main Menu")
    wleaders = []
    try:
        Log.Debug("Loading Worship Leaders")
        IHOP_JAVASCRIPT_RAW = HTTP.Request(IHOP_JAVASCRIPT_URL).content
        wleaders = JSON.ObjectFromString(RE_WLEADER.search(IHOP_JAVASCRIPT_RAW).group(0))
        Log.Debug(str(wleaders))
    except:
        pass

@route(PREFIX + '/worshiper')
def WorshipLeaderMenu(channel):
    pass