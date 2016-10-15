#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmcgui, xbmc, xbmcaddon
import os,sys
from traceback import format_exc
from datetime import datetime
import time

try:
    from multiprocessing.pool import ThreadPool as Pool
    supportsPool = True
except Exception: 
    supportsPool = False

try:
    import simplejson as json
except Exception:
    import json

ADDON_ID = "script.skin.helper.widgets"
ADDON = xbmcaddon.Addon(ADDON_ID)
WINDOW = xbmcgui.Window(10000)
SETTING = ADDON.getSetting

FIELDS_BASE = ["dateadded", "file", "lastplayed","plot", "title", "art", "playcount"]
FIELDS_FILE = FIELDS_BASE + ["streamdetails", "director", "resume", "runtime"]
FIELDS_MOVIES = FIELDS_FILE + ["plotoutline", "sorttitle", "cast", "votes", "showlink", "top250", "trailer", "year", "country", "studio", "set", "genre", "mpaa", "setid", "rating", "tag", "tagline", "writer", "originaltitle", "imdbnumber"]
FIELDS_TVSHOWS = FIELDS_BASE + ["sorttitle", "mpaa", "premiered", "year", "episode", "watchedepisodes", "votes", "rating", "studio", "season", "genre", "cast", "episodeguide", "tag", "originaltitle", "imdbnumber"]
FIELDS_EPISODES = FIELDS_FILE + ["cast", "productioncode", "rating", "votes", "episode", "showtitle", "tvshowid", "season", "firstaired", "writer", "originaltitle"]
FIELDS_MUSICVIDEOS = FIELDS_FILE + ["genre", "artist", "tag", "album", "track", "studio", "year"]
FIELDS_FILES = FIELDS_FILE + ["plotoutline", "sorttitle", "cast", "votes", "trailer", "year", "country", "studio", "genre", "mpaa", "rating", "tagline", "writer", "originaltitle", "imdbnumber", "premiered","episode", "showtitle","firstaired","watchedepisodes","duration"]
FIELDS_SONGS = ["artist","displayartist", "title", "rating", "fanart", "thumbnail", "duration", "playcount", "comment", "file", "album", "lastplayed", "genre", "musicbrainzartistid", "track"]
FIELDS_ALBUMS = ["title", "fanart", "thumbnail", "genre", "displayartist", "artist", "genreid", "musicbrainzalbumartistid", "year", "rating", "artistid", "musicbrainzalbumid", "theme", "description", "type", "style", "playcount", "albumlabel", "mood"]
FIELDS_PVR = ["art", "channel", "directory", "endtime", "file", "genre", "icon", "playcount", "plot", "plotoutline", "resume", "runtime", "starttime", "streamurl", "title"]

FILTER_UNWATCHED = {"operator":"lessthan", "field":"playcount", "value":"1"}
FILTER_WATCHED = {"operator":"isnot", "field":"playcount", "value":"0"}
FILTER_RATING = {"operator":"greaterthan","field":"rating", "value":"7"}
FILTER_INPROGRESS = {"operator":"true", "field":"inprogress", "value":""}

def log_msg(msg, loglevel = xbmc.LOGNOTICE):
    if isinstance(msg, unicode):
        msg = msg.encode('utf-8')
    xbmc.log("Skin Helper Widgets --> %s" %msg, level=loglevel)

def set_kodi_json(method,params):
    json_response = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method" : "%s", "params": %s, "id":1 }' %(method, try_encode(params)))
    jsonobject = json.loads(json_response.decode('utf-8','replace'))
    return jsonobject

def get_kodi_json(jsonmethod, sortby=None, filters=None, fields=None, 
        limits=None, returntype=None, opt_params=None, sortorder="descending"):
    kodi_json = {}
    kodi_json["jsonrpc"] = "2.0"
    kodi_json["method"] = jsonmethod
    if opt_params:
        kodi_json["params"] = opt_params
    else:
        kodi_json["params"] = {}
    kodi_json["id"] = 1
    if sortby:
        kodi_json["params"]["sort"] = { "order": sortorder, "method": sortby }
    if filters:
        if len(filters) > 1:
            kodi_json["params"]["filter"] = {}
            kodi_json["params"]["filter"]["and"] = filters
        else:
            kodi_json["params"]["filter"] = filters[0]
    if fields:
        kodi_json["params"]["properties"] = fields
    if limits:
        kodi_json["params"]["limits"] = { "start": limits[0], "end": limits[1] }
    json_response = xbmc.executeJSONRPC(try_encode(json.dumps(kodi_json))).decode('utf-8','replace')
    json_object = json.loads(json_response)
    result = {}
    if 'result' in json_object:
        if returntype and returntype in json_object['result']:
            #returntype specified, return immediately
            result = json_object['result'][returntype]
        else:
            #no returntype specified, we'll have to look for it
            for key, value in json_object['result'].iteritems():
                if not key=="limits" and (isinstance(value, list) or isinstance(value,dict)):
                    result = value
    return result

def try_encode(text, encoding="utf-8"):
    try:
        return text.encode(encoding,"ignore")
    except Exception:
        return text

def try_decode(text, encoding="utf-8"):
    try:
        return text.decode(encoding,"ignore")
    except Exception:
        return text

def create_listitem(item,asTuple=True):

    try:
        liz = xbmcgui.ListItem(label=item.get("label",""),label2=item.get("label2",""))
        liz.setProperty('IsPlayable', item.get('IsPlayable','true'))
        liz.setPath(item.get('file'))

        nodetype = "Video"
        if item["type"] in ["song","album","artist"]:
            nodetype = "Music"

        #extra properties
        for key, value in item["extraproperties"].iteritems():
            liz.setProperty(key, value)

        #video infolabels
        if nodetype == "Video":
            infolabels = {
                "title": item.get("title"),
                "size": item.get("size"),
                "genre": item.get("genre"),
                "year": item.get("year"),
                "top250": item.get("top250"),
                "tracknumber": item.get("tracknumber"),
                "rating": item.get("rating"),
                "playcount": item.get("playcount"),
                "overlay": item.get("overlay"),
                "cast": item.get("cast"),
                "castandrole": item.get("castandrole"),
                "director": item.get("director"),
                "mpaa": item.get("mpaa"),
                "plot": item.get("plot"),
                "plotoutline": item.get("plotoutline"),
                "originaltitle": item.get("originaltitle"),
                "sorttitle": item.get("sorttitle"),
                "duration": item.get("duration"),
                "studio": item.get("studio"),
                "tagline": item.get("tagline"),
                "writer": item.get("writer"),
                "tvshowtitle": item.get("tvshowtitle"),
                "premiered": item.get("premiered"),
                "status": item.get("status"),
                "code": item.get("imdbnumber"),
                "aired": item.get("aired"),
                "credits": item.get("credits"),
                "album": item.get("album"),
                "artist": item.get("artist"),
                "votes": item.get("votes"),
                "trailer": item.get("trailer"),
                "progress": item.get('progresspercentage')
            }
            if "DBID" in item["extraproperties"] and item["type"] not in ["tvrecording","tvchannel","favourite"]:
                infolabels["mediatype"] = item["type"]
                infolabels["dbid"] = item["extraproperties"]["DBID"]
            if "date" in item: infolabels["date"] = item["date"]
            if "lastplayed" in item: infolabels["lastplayed"] = item["lastplayed"]
            if "dateadded" in item: infolabels["dateadded"] = item["dateadded"]
            if item["type"] == "episode":
                infolabels["season"] = item["season"]
                infolabels["episode"] = item["episode"]

            liz.setInfo( type="Video", infoLabels=infolabels)

            #streamdetails
            if item.get("streamdetails"):
                liz.addStreamInfo("video", item["streamdetails"].get("video",{}))
                liz.addStreamInfo("audio", item["streamdetails"].get("audio",{}))
                liz.addStreamInfo("subtitle", item["streamdetails"].get("subtitle",{}))

        #music infolabels
        if nodetype == "Music":
            infolabels = {
                "title": item.get("title"),
                "size": item.get("size"),
                "genre": item.get("genre"),
                "year": item.get("year"),
                "tracknumber": item.get("track"),
                "album": item.get("album"),
                "artist": " / ".join(item.get('artist')),
                "rating": str(item.get("rating",0)),
                "lyrics": item.get("lyrics"),
                "playcount": item.get("playcount")
            }
            if "date" in item: infolabels["date"] = item["date"]
            if "duration" in item: infolabels["duration"] = item["duration"]
            if "lastplayed" in item: infolabels["lastplayed"] = item["lastplayed"]
            liz.setInfo( type="Music", infoLabels=infolabels)

        #artwork
        liz.setArt( item.get("art", {}))
        if "icon" in item:
            liz.setIconImage(item['icon'])
        if "thumbnail" in item:
            liz.setThumbnailImage(item['thumbnail'])
            
        #contextmenu
        if item["type"] in ["episode","season"] and "season" in item and "tvshowid" in item:
            #add series and season level to widgets
            if not "contextmenu" in item:
                item["contextmenu"] = []
            item["contextmenu"] += [ 
                (ADDON.getLocalizedString(32051), "ActivateWindow(Video,videodb://tvshows/titles/%s/,return)"
                    %(item["tvshowid"])),
                (ADDON.getLocalizedString(32052), "ActivateWindow(Video,videodb://tvshows/titles/%s/%s/,return)"
                    %(item["tvshowid"],item["season"])) ]
        if "contextmenu" in item:
            liz.addContextMenuItems(item["contextmenu"])
    
        if asTuple:
            return (item["file"], liz, item.get("isFolder",False))
        else:
            return liz
    except Exception as e:
        log_msg(format_exc(sys.exc_info()),xbmc.LOGDEBUG)
        log_msg("ERROR Creating ListItem --> %s" %e, xbmc.LOGERROR)
        return None

def prepare_listitem(item):
    try:
        #fix values returned from json to be used as listitem values
        properties = item.get("extraproperties",{})

        #set type
        for idvar in [ ('episode','DefaultTVShows.png'),('tvshow','DefaultTVShows.png'),('movie','DefaultMovies.png'),('song','DefaultAudio.png'),('musicvideo','DefaultMusicVideos.png'),('recording','DefaultTVShows.png'),('album','DefaultAudio.png') ]:
            if item.get(idvar[0] + "id"):
                properties["DBID"] = str(item.get(idvar[0] + "id"))
                if not item.get("type"): item["type"] = idvar[0]
                if not item.get("icon"): item["icon"] = idvar[1]
                break

        #general properties
        if item.get('genre') and isinstance(item.get('genre'), list): item["genre"] = " / ".join(item.get('genre'))
        if item.get('studio') and isinstance(item.get('studio'), list): item["studio"] = " / ".join(item.get('studio'))
        if item.get('writer') and isinstance(item.get('writer'), list): item["writer"] = " / ".join(item.get('writer'))
        if item.get('director') and isinstance(item.get('director'), list): item["director"] = " / ".join(item.get('director'))
        if not isinstance(item.get('artist'), list) and item.get('artist'): item["artist"] = [item.get('artist')]
        if not item.get('artist'): item["artist"] = []
        if item.get('type') == "album" and not item.get('album'): item['album'] = item.get('label')
        if not item.get("duration") and item.get("runtime"): item["duration"] = item.get("runtime")
        if not item.get("plot") and item.get("comment"): item["plot"] = item.get("comment")
        if not item.get("tvshowtitle") and item.get("showtitle"): item["tvshowtitle"] = item.get("showtitle")
        if not item.get("premiered") and item.get("firstaired"): item["premiered"] = item.get("firstaired")
        if not properties.get("imdbnumber") and item.get("imdbnumber"): properties["imdbnumber"] = item.get("imdbnumber")
        properties["dbtype"] = item.get("type")
        properties["type"] = item.get("type")
        properties["path"] = item.get("file")

        #cast
        listCast = []
        listCastAndRole = []
        if item.get("cast") and isinstance(item["cast"],list):
            for castmember in item["cast"]:
                if isinstance(castmember,dict):
                    listCast.append( castmember.get("name","") )
                    listCastAndRole.append( (castmember["name"], castmember["role"]) )
                else:
                    listCast.append( castmember )
                    listCastAndRole.append( (castmember, "") )

        item["cast"] = listCast
        item["castandrole"] = listCastAndRole

        if item.get("season") and item.get("episode"):
            properties["episodeno"] = "s%se%s" %(item.get("season"),item.get("episode"))
        if item.get("resume"):
            properties["resumetime"] = str(item['resume']['position'])
            properties["totaltime"] = str(item['resume']['total'])
            properties['StartOffset'] = str(item['resume']['position'])

        #streamdetails
        if item.get("streamdetails"):
            streamdetails = item["streamdetails"]
            audiostreams = streamdetails.get('audio',[])
            videostreams = streamdetails.get('video',[])
            subtitles = streamdetails.get('subtitle',[])
            if len(videostreams) > 0:
                stream = videostreams[0]
                height = stream.get("height","")
                width = stream.get("width","")
                if height and width:
                    resolution = ""
                    if width <= 720 and height <= 480: resolution = "480"
                    elif width <= 768 and height <= 576: resolution = "576"
                    elif width <= 960 and height <= 544: resolution = "540"
                    elif width <= 1280 and height <= 720: resolution = "720"
                    elif width <= 1920 and height <= 1080: resolution = "1080"
                    elif width * height >= 6000000: resolution = "4K"
                    properties["VideoResolution"] = resolution
                if stream.get("codec",""):
                    properties["VideoCodec"] = str(stream["codec"])
                if stream.get("aspect",""):
                    properties["VideoAspect"] = str(round(stream["aspect"], 2))
                item["streamdetails"]["video"] = stream

            #grab details of first audio stream
            if len(audiostreams) > 0:
                stream = audiostreams[0]
                properties["AudioCodec"] = stream.get('codec','')
                properties["AudioChannels"] = str(stream.get('channels',''))
                properties["AudioLanguage"] = stream.get('language','')
                item["streamdetails"]["audio"] = stream

            #grab details of first subtitle
            if len(subtitles) > 0:
                properties["SubtitleLanguage"] = subtitles[0].get('language','')
                item["streamdetails"]["subtitle"] = subtitles[0]
        else:
            item["streamdetails"] = {}
            item["streamdetails"]["video"] =  {'duration': item.get('duration',0)}

        #additional music properties
        if item.get('album_description'):
            properties["Album_Description"] = item.get('album_description')

        #pvr properties
        if item.get("starttime"):
            starttime = get_localdate_from_utc(item['starttime'])
            endtime = get_localdate_from_utc(item['endtime'])
            properties["StartTime"] = starttime[1]
            properties["StartDate"] = starttime[0]
            properties["EndTime"] = endtime[1]
            properties["EndDate"] = endtime[0]
            fulldate = starttime[0] + " " + starttime[1] + "-" + endtime[1]
            properties["Date"] = fulldate
            properties["StartDateTime"] = starttime[0] + " " + starttime[1]
            item["date"] = starttime[0]
            item["premiered"] = starttime[0]
        if item.get("channellogo"):
            properties["channellogo"] = item["channellogo"]
            properties["channelicon"] = item["channellogo"]
        if item.get("episodename"): properties["episodename"] = item.get("episodename","")
        if item.get("channel"): properties["channel"] = item.get("channel","")
        if item.get("channel"): properties["channelname"] = item.get("channel","")
        if item.get("channel"): item["label2"] = item.get("channel","")

        #artwork
        art = item.get("art",{})
        if item["type"] in ["episode","season"]:
            if not art.get("fanart") and art.get("season.fanart"):
                art["fanart"] = art["season.fanart"]
            if not art.get("poster") and art.get("season.poster"):
                art["poster"] = art["season.poster"]
            if not art.get("landscape") and art.get("season.landscape"):
                art["poster"] = art["season.landscape"]
            if not art.get("fanart") and art.get("tvshow.fanart"):
                art["fanart"] = art.get("tvshow.fanart")
            if not art.get("poster") and art.get("tvshow.poster"):
                art["poster"] = art.get("tvshow.poster")
            if not art.get("clearlogo") and art.get("tvshow.clearlogo"):
                art["clearlogo"] = art.get("tvshow.clearlogo")
            if not art.get("landscape") and art.get("tvshow.landscape"):
                art["landscape"] = art.get("tvshow.landscape")
        if not art.get("fanart") and item.get('fanart'): art["fanart"] = item.get('fanart')
        if not art.get("thumb") and item.get('thumbnail'): art["thumb"] = get_clean_image(item.get('thumbnail'))
        if not art.get("thumb") and art.get('poster'): art["thumb"] = get_clean_image(item.get('poster'))
        if not art.get("thumb") and item.get('icon'): art["thumb"] = get_clean_image(item.get('icon'))
        if not item.get("thumbnail") and art.get('thumb'): item["thumbnail"] = art["thumb"]

        item["extraproperties"] = properties
        
        if not "file" in item:
            log_msg("Item is missing file path ! --> %s" %item["label"], xbmc.LOGWARNING)
            item["file"] = ""
        
        #return the result
        return item

    except Exception as e:
        log_msg(format_exc(sys.exc_info()),xbmc.LOGDEBUG)
        log_msg("ERROR Preparing ListItem --> %s" %e, xbmc.LOGERROR)
        return None

def create_main_entry(item):
    return {
            "label": item[0], 
            "file": "plugin://script.skin.helper.widgets/?action=%s" %item[1],
            "icon": item[2],
            "art": {"fanart": "special://home/addons/script.skin.helper.widgets/fanart.jpg"},
            "isFolder": True,
            "type": "file",
            "IsPlayable": "false"
            }
        
def get_localdate_from_utc(timestring):
    try:
        systemtime = xbmc.getInfoLabel("System.Time")
        utc = datetime.fromtimestamp(time.mktime(time.strptime(timestring, '%Y-%m-%d %H:%M:%S')))
        epoch = time.mktime(utc.timetuple())
        offset = datetime.fromtimestamp (epoch) - datetime.utcfromtimestamp(epoch)
        correcttime = utc + offset
        if "AM" in systemtime or "PM" in systemtime:
            return (correcttime.strftime("%Y-%m-%d"),correcttime.strftime("%I:%M %p"))
        else:
            return (correcttime.strftime("%d-%m-%Y"),correcttime.strftime("%H:%M"))
    except Exception as e:
        log_msg(format_exc(sys.exc_info()),xbmc.LOGDEBUG)
        log_msg("ERROR in Utils.get_localdate_from_utc ! --> %s" %e, xbmc.LOGERROR)
        return (timestring,timestring)

def get_clean_image(image):
    if image and "image://" in image:
        image = image.replace("image://","").replace("music@","")
        image=urllib.unquote(image.encode("utf-8"))
        if image.endswith("/"):
            image = image[:-1]
    return try_decode(image)        

def process_method_on_list(method_to_run,items):
    '''helper method that processes a method on each listitem with pooling if the system supports it'''
    all_items = []
    if supportsPool:
        pool = Pool()
        try:
            all_items = pool.map(method_to_run, items)
        except Exception:
            #catch exception to prevent threadpool running forever
            log_msg(format_exc(sys.exc_info()))
            log_msg("Error in %s" %method_to_run)
        pool.close()
        pool.join()
    else:
        all_items = [method_to_run(item) for item in items]
    all_items = filter(None, all_items)
    return all_items