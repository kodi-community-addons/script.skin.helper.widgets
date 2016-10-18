#!/usr/bin/python
# -*- coding: utf-8 -*-

import urlparse
from utils import process_method_on_list, WINDOW, log_msg, SETTING
from operator import itemgetter
from simplecache import SimpleCache
import xbmcplugin, xbmcgui, xbmc, xbmcaddon, xbmcvfs
import os,sys
from artutils import KodiDb

ADDON_HANDLE = int(sys.argv[1])
IGNORE_CACHE = True

class Main(object):
    arguments = {}
    
    def __init__(self):
        ''' our main subroutine which will load the correct endpoint based on the given parameters '''
        
        #skip if shutdown requested
        if WINDOW.getProperty("SkinHelperShutdownRequested"):
            log_msg("Not forfilling request: Kodi is exiting!" ,xbmc.LOGWARNING)
            xbmcplugin.endOfDirectory(handle=ADDON_HANDLE)
            return

        self.kodi_db = KodiDb()
        self.cache = SimpleCache()
        
        #get the arguments provided to the plugin path
        self.get_arguments()
        
        if not "mediatype" in self.arguments or not "action" in self.arguments:
            #we need both mediatype and action, so show the main listing
            self.mainlisting()
        else:
            #we have a mediatype and action so display the widget listing
            self.show_widget_listing()

    def get_arguments(self):
        '''get the arguments provided to the plugin path'''
        arguments = dict(urlparse.parse_qsl(sys.argv[2].replace('?','').lower().decode("utf-8")))
        if not "mediatype" in arguments and "action" in arguments:
            #get the mediatype and action from the path (for backwards compatability with old style paths)
            for item in [("movies","movies"), ("shows","tvshows"), ("episode","episodes"), ("tv","pvr")]:
                if item[0] in arguments["action"]:
                    arguments["mediatype"] = item[1]
                    arguments["action"] = arguments["action"].replace(arguments["mediatype"],"")
                    break
        #prefer refresh param for the mediatype
        if "mediatype" in arguments:
            alt_refresh = WINDOW.getProperty("widgetreload-%s" %arguments["mediatype"])
            if alt_refresh:
                arguments["refresh"] = alt_refresh
                
        #set the optional settings as arguments
        arguments["hide_watched"] = SETTING("hideWatchedItemsInWidgets") == "true"
        arguments["next_inprogress_only"] = SETTING("nextupInprogressShowsOnly") == "true"
        arguments["enable_specials"] = SETTING("enableSpecialsInWidgets") == "true"
        arguments["group_episodes"] = SETTING("groupRecentEpisodes") == "true"
        if "limit" in arguments:
            arguments["limit"] = int(arguments["limit"])
        else:
            arguments["limit"] = int(SETTING("default_limit"))
        
        #set the self.arguments dict
        self.arguments = arguments
            
    def show_widget_listing(self):
        '''display the listing for the provided action and mediatype'''
        media_type = self.arguments["mediatype"]
        action = self.arguments["action"]
        refresh = self.arguments.get("refresh","")
        #set widget content type
        xbmcplugin.setContent(ADDON_HANDLE, media_type)

        #try to get from cache first...
        #we use a checksum based on the arguments to make sure the cache is ignored when needed
        all_items = []
        cache_str = "SkinHelper.Widgets.%s.%s" %(media_type,action)
        cache_checksum = ".".join([repr(value) for value in self.arguments.itervalues()])
        if not refresh:
            cache_checksum = None
        cache = self.cache.get(cache_str,checksum=cache_checksum)
        if cache and not IGNORE_CACHE:
            log_msg("MEDIATYPE: %s - ACTION: %s -- got items from cache - CHECKSUM: %s" %(media_type,action,cache_checksum))
            all_items = cache

        #Call the correct method to get the content from json when no cache
        if not all_items:
            log_msg("MEDIATYPE: %s - ACTION: %s -- no cache, quering kodi api to get items - CHECKSUM: %s"
                %(media_type,action,cache_checksum))
            
            #dynamically import and load the correct module, class and function
            media_module = __import__(media_type)
            media_class = getattr(media_module, media_type.capitalize())()
            media_class.arguments = self.arguments
            all_items = getattr(media_class, action)()
            #randomize output if requested by skinner or user
            if self.arguments.get("randomize","") == "true":
                all_items = sorted(all_items, key=lambda k: random.random())
            
            #prepare listitems and store in cache
            all_items = process_method_on_list(self.kodi_db.prepare_listitem,all_items)
            self.cache.set(cache_str,all_items,checksum=cache_checksum)

        #fill that listing...
        all_items = process_method_on_list(self.kodi_db.create_listitem,all_items)
        xbmcplugin.addDirectoryItems(ADDON_HANDLE, all_items, len(all_items))

        #end directory listing
        xbmcplugin.endOfDirectory(handle=ADDON_HANDLE)
    
    def mainlisting(self):
        '''main listing'''
        all_items = []
        #movie nodes
        if xbmc.getCondVisibility("Library.HasContent(movies)"):
            all_items.append( (xbmc.getLocalizedString(342), "movieslisting", "DefaultMovies.png") )
        #tvshows and episodes nodes
        if xbmc.getCondVisibility("Library.HasContent(tvshows)"):
            all_items.append( (xbmc.getLocalizedString(20343), "tvshowslisting", "DefaultTvShows.png") )
            all_items.append( (xbmc.getLocalizedString(20360), "episodeslisting", "DefaultTvShows.png") )
        
        #process the listitems and display listing
        all_items = process_method_on_list(self.kodi_db.create_main_entry,all_items)
        all_items = process_method_on_list(self.kodi_db.prepare_listitem,all_items)
        all_items = process_method_on_list(self.kodi_db.create_listitem,all_items)
        xbmcplugin.addDirectoryItems(ADDON_HANDLE, all_items, len(all_items))
        xbmcplugin.endOfDirectory(handle=ADDON_HANDLE)