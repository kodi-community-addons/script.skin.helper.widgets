#!/usr/bin/python
# -*- coding: utf-8 -*-
from utils import ADDON_ID, process_method_on_list
from operator import itemgetter
from artutils import kodi_constants
from thetvdb import TheTvDb
import xbmc


class Episodes(object):
    '''all episode widgets provided by the script'''
    options = {}
    kodidb = None
    addon = None
    
    def __init__(self, addon, kodidb, options):
        '''Initialization'''
        self.tvdb = TheTvDb()
        self.addon = addon
        self.kodidb = kodidb
        self.options = options
        
    def __del__(self):
        '''Cleanup'''
        del self.tvdb
    
    def listing(self):
        '''main listing with all our episode nodes'''
        all_items = [ 
            (self.addon.getLocalizedString(32027), "inprogress&mediatype=episodes", "DefaultTvShows.png"), 
            (self.addon.getLocalizedString(32002), "next&mediatype=episodes", "DefaultTvShows.png"), 
            (self.addon.getLocalizedString(32039), "recent&mediatype=episodes", "DefaultRecentlyAddedEpisodes.png"),
            (self.addon.getLocalizedString(32009), "recommended&mediatype=episodes", "DefaultTvShows.png"),
            (self.addon.getLocalizedString(32010), "inprogressandrecommended&mediatype=episodes", "DefaultTvShows.png"),
            (self.addon.getLocalizedString(32049), "inprogressandrandom&mediatype=episodes", "DefaultTvShows.png"),
            (self.addon.getLocalizedString(32008), "random&mediatype=episodes", "DefaultTvShows.png"),
            (self.addon.getLocalizedString(32042), "unaired&mediatype=episodes", "DefaultTvShows.png"),
            (self.addon.getLocalizedString(32043), "nextaired&mediatype=episodes", "DefaultTvShows.png"),
            ]
        return process_method_on_list(self.kodidb.create_main_entry,all_items)

    def recommended(self):
        ''' get recommended episodes - library episodes with score higher than 7 '''
        filters = [kodi_constants.FILTER_RATING]
        if self.options["hide_watched"]:
            filters += kodi_constants.FILTER_UNWATCHED
        return self.kodidb.episodes(sort=kodi_constants.SORT_RATING, filters=filters, 
            limits=(0,self.options["limit"]))
                
    def recent(self):
        ''' get recently added episodes '''
        tvshow_episodes = {}
        total_count = 0
        unique_count = 0
        filters = []
        if self.options["hide_watched"]:
            filters += kodi_constants.FILTER_UNWATCHED
        while unique_count < self.options["limit"]:
            recent_episodes = self.kodidb.episodes(sort=kodi_constants.SORT_DATEADDED,
                filters=filters,limits=(total_count,self.options["limit"]+total_count))
            if not self.options["group_episodes"]:
                #grouping is not enabled, just return the result
                return recent_episodes
                
            if len(recent_episodes) < self.options["limit"]:
                #break the loop if there are no more episodes
                unique_count = self.options["limit"]

            #if multiple episodes for the same show with same addition date, we combine them into one
            #to do that we build a dict with recent episodes for all episodes of the same season added on the same date
            for episode in recent_episodes:
                total_count += 1
                unique_key = "%s-%s-%s" %(episode["tvshowid"],episode["dateadded"].split(" ")[0],episode["season"])
                if not tvshow_episodes.has_key(unique_key):
                    tvshow_episodes[unique_key] = []
                    unique_count += 1
                tvshow_episodes[unique_key].append(episode)
        
        #create our entries and return the result sorted by dateadded
        all_items = process_method_on_list(self.create_grouped_entry,tvshow_episodes.itervalues())
        return sorted(all_items,key=itemgetter("dateadded"),reverse=True)[:self.options["limit"]]
                
    def random(self):
        ''' get random episodes '''
        filters = []
        if self.options["hide_watched"]:
            filters += kodi_constants.FILTER_UNWATCHED
        return self.kodidb.episodes(sort=kodi_constants.SORT_DATEADDED, filters=filters, 
            limits=(0,self.options["limit"]))
                
    def inprogress(self):
        ''' get in progress episodes '''
        return self.kodidb.episodes(sort=kodi_constants.SORT_LASTPLAYED, filters=[kodi_constants.FILTER_INPROGRESS], 
            limits=(0,self.options["limit"]))

    def inprogressandrecommended(self):
        ''' get recommended AND in progress episodes '''
        all_items = self.inprogress()
        all_titles = [item["title"] for item in all_items]
        for item in self.recommended():
            if item["title"] not in all_titles:
                all_items.append(item)
        return all_items[:self.options["limit"]]
        
    def inprogressandrandom(self):
        ''' get recommended AND random episodes '''
        all_items = self.inprogress()
        all_ids = [item["episodeid"] for item in all_items]
        for item in self.random():
            if item["episodeid"] not in all_ids:
                all_items.append(item)
        return all_items[:self.options["limit"]]
    
    def next(self):
        ''' get next episodes '''
        filters = [ kodi_constants.FILTER_UNWATCHED ]
        if self.options["next_inprogress_only"]:
            filters = [ kodi_constants.FILTER_INPROGRESS ]
        fields = [ "title", "lastplayed", "playcount" ]
        # First we get a list of all the inprogress/unwatched TV shows ordered by lastplayed
        all_shows = self.kodidb.tvshows(sort=kodi_constants.SORT_LASTPLAYED, filters=filters, 
            limits=(0,self.options["limit"]))
        return process_method_on_list(self.get_next_episode_for_show, [d['tvshowid'] for d in all_shows])
        
    def get_next_episode_for_show(self,show_id):
        '''get next unwatched episode for tvshow'''
        filters = [ kodi_constants.FILTER_UNWATCHED ]
        if not self.options["enable_specials"]:
            filters.append( {"field": "season", "operator": "greaterthan", "value": "0"} )
        json_episodes = self.kodidb.episodes(sort=kodi_constants.SORT_EPISODE, filters=filters, 
            limits=(0,1), tvshowid=show_id)
        if json_episodes:
            return json_episodes[0]
        else:
            return None
            
    def unaired(self):
        ''' get all unaired episodes for shows in the library - provided by tvdb module'''
        self.tvdb.days_ahead = 120
        return self.tvdb.get_kodi_series_unaired_episodes_list(False)[:self.options["limit"]]
        
    def nextaired(self):
        ''' get all next airing episodes for shows in the library - provided by tvdb module'''
        self.tvdb.days_ahead = 45
        result = self.tvdb.get_kodi_series_unaired_episodes_list(True)
     
    @staticmethod
    def create_grouped_entry(tvshow_episodes):
        '''helper for grouped episodes'''
        firstepisode = tvshow_episodes[0]
        if len(tvshow_episodes) > 2:
            #add as season entry if there were multiple episodes for the same show
            #use first episode as reference to keep the correct sorting order
            item = firstepisode
            item["type"] = "season"
            item["label"] = "%s %s" %(xbmc.getLocalizedString(20373), firstepisode["season"])
            item["plot"] = u"[B]%s[/B] • %s %s[CR]%s: %s"\
                %(item["label"],len(tvshow_episodes),xbmc.getLocalizedString(20387),
                xbmc.getLocalizedString(570),firstepisode["dateadded"].split(" ")[0])
            item["extraproperties"] = {"UnWatchedEpisodes": "%s"%len(tvshow_episodes)}
            return item
        else:
            #just add the single item
            return firstepisode
        
        