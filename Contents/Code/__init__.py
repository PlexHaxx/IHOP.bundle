# -*- coding: utf-8 -*-
PREFIX = "/video/ihop"
NAME = "IHOP Plugin"

MAXRESULTS = 50

IHOP_FEED_URL = "http://feed.theplatform.com/f/IfSiAC/5ct7EYhhJs9Z/"
IHOP_FEED_QUERY = "?q=%s&range=%s-%s&=&sort=pubDate|desc&count=true"
IHOP_FEED_FILT_ARTIST = "&byCustomValue={ihopkc$worshipLeader}{%s}"
IHOP_JAVASCRIPT_URL = "http://cdn.ihopkc.org.edgesuite.net/wp-content/themes/ihopkc_theme/_js/ihopkc-main.min.js"

RE_WLEADER = Regex('e.worshipLeaders\[0\]\.toLowerCase\(\)\)return"";var t\=(\[[a-zA-Z0-9\a\A\s",]+\]);')

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0'
TITLE = L('IHOP')
ICON = 'icon-default.png'
ART = 'art-default.jpg'
VIDEOS = 'icon-videos.png'

####################################################################################################
def Start():
    #HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = USER_AGENT
    Log.Debug("Starting the IHOP Plugin")
    Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

@route(PREFIX + '/thumb')
def GetThumb(url):
    Log.Debug(url)
    if url:
        data = HTTP.Request(url, cacheTime = CACHE_1WEEK).content
        return DataObject(data, 'image/jpeg')
    else:
        return Redirect(R(VIDEOS))

@indirect
def PlayVideo(url):
    return IndirectResponse(VideoClipObject, key=url)

def createEpisodeObject(url, title, summary, thumburl, rating_key, originally_available_at=None, duration=None, include_container=False):
    container = Container.MP4
    video_codec = VideoCodec.H264
    audio_codec = AudioCodec.AAC
    audio_channels = 2

    track_object = VideoClipObject(
        key = Callback(
            createEpisodeObject,
            url=url,
            title=title,
            summary=summary,
            thumburl=thumburl,
            rating_key=rating_key,
            originally_available_at=originally_available_at,
            duration=duration,
            include_container=True
        ),
        rating_key = rating_key,
        title = title,
        summary = summary,
        # thumb = thumb,
        thumb=Callback(GetThumb, url=thumburl),
        originally_available_at = originally_available_at,
        duration = duration,
        items = [
            MediaObject(
                parts = [
                    PartObject(key=Callback(PlayVideo, url=url))
                ],
                container = container,
                video_codec = video_codec,
                audio_codec = audio_codec,
                audio_channels = audio_channels,
            )
        ]
    )

    if include_container:
        return ObjectContainer(objects=[track_object])
    else:
        return track_object

@route(PREFIX + '/worshiper')
def WorshipLeaderMenu(artist=None):
    if artist:
        URL = IHOP_FEED_URL + IHOP_FEED_QUERY % (IHOP_FEED_FILT_ARTIST % artist.replace(" ", "+"), 0, MAXRESULTS)
    else:
        URL = IHOP_FEED_URL
    container = Container.MP4
    video_codec = VideoCodec.H264
    audio_codec = AudioCodec.AAC
    audio_channels = 2
    Log.Debug(URL)
    data = JSON.ObjectFromURL(URL)
    Log.Debug(data)
    if not artist:
        oc = ObjectContainer(title2=data["title"]+" - " + L("All Videos"))
    else:
        oc = ObjectContainer(title2=data["title"]+" - " + artist)
    oc.art = R(ART)
    oc.view_group = "Details"
    for ent in data.get('entries', []):
        if "content" not in ent:
            continue
        video_url = ""
        title = "%s - %s - %s" % (ent.get("title"), ', '.join(ent.get('ihopkc$setType',[''])), ', '.join(ent.get('ihopkc$worshipLeader',[''])))
        duration = 0
        for c in ent.get("content"):
            if c.get("contentType") == "video":
                video_url = c.get('downloadUrl')
                duration = c.get('duration')
                break
        if video_url:
            Log.Debug(video_url)
            oc.add(createEpisodeObject(
                url = video_url,
                title = title,
                summary = title,
                originally_available_at=Datetime.FromTimestamp(ent.get("added")/1000),
                duration = int(duration*1000),
                rating_key = ent.get("guid"),
                thumburl = ent.get("defaultThumbnailUrl"),
            ))
    return oc

@handler(PREFIX, NAME, R(ART), R(ICON))
def MainMenu():
    oc = ObjectContainer(no_cache = True)
    oc.art = R(ART)
    Log.Debug("Load Main Menu")
    wleaders = []
    try:
        Log.Debug("Loading Worship Leaders")
        IHOP_JAVASCRIPT_RAW = HTTP.Request(IHOP_JAVASCRIPT_URL).content
        #Log.Debug(IHOP_JAVASCRIPT_RAW)
        wleaders_match = RE_WLEADER.search(IHOP_JAVASCRIPT_RAW).groups()[0]
        Log.Debug("Got response: %s" % wleaders_match)
        wleaders = JSON.ObjectFromString(wleaders_match)
    except Exception, exc:
        Log.Exception(exc)

    Log.Debug(str(wleaders))
    oc.add(DirectoryObject(key=Callback(WorshipLeaderMenu), title = L("All Videos"), thumb = R(VIDEOS)))
    for wleader in wleaders:
        Log.Debug("Adding Worship Leader: %s" % wleader)
        oc.add(DirectoryObject(key = Callback(WorshipLeaderMenu, artist=wleader), title = wleader, thumb = R(VIDEOS)))
    return oc