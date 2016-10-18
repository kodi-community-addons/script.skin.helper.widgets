#!/usr/bin/python
# -*- coding: utf-8 -*-
from utils import ADDON, process_method_on_list
from operator import itemgetter
from artutils import kodidb
import xbmc


class Episodes(object):
    '''all episode widgets provided by the script'''
    arguments = {}
    
    def __init__(self):
        self.kodi_db = kodidb.KodiDb()
    
    def listing(self):
        '''main listing with all our episode nodes'''
        all_items = [ 
            (ADDON.getLocalizedString(32027), "inprogress&mediatype=episodes", "DefaultTvShows.png"), 
            (ADDON.getLocalizedString(32002), "next&mediatype=episodes", "DefaultTvShows.png"), 
            (ADDON.getLocalizedString(32039), "recent&mediatype=episodes", "DefaultRecentlyAddedEpisodes.png"),
            (ADDON.getLocalizedString(32009), "recommended&mediatype=episodes", "DefaultTvShows.png"),
            (ADDON.getLocalizedString(32010), "inprogressandrecommended&mediatype=episodes", "DefaultTvShows.png"),
            (ADDON.getLocalizedString(32049), "inprogressandrandom&mediatype=episodes", "DefaultTvShows.png"),
            (ADDON.getLocalizedString(32008), "random&mediatype=episodes", "DefaultTvShows.png"),
            (ADDON.getLocalizedString(32042), "unaired&mediatype=episodes", "DefaultTvShows.png"),
            (ADDON.getLocalizedString(32043), "nextaired&mediatype=episodes", "DefaultTvShows.png"),
            ]
        return process_method_on_list(self.kodi_db.create_main_entry,all_items)

    def recommended(self):
        ''' get recommended episodes - library episodes with score higher than 7 '''
        filters = [kodidb.FILTER_RATING]
        if self.arguments["hide_watched"]:
            filters += kodidb.FILTER_UNWATCHED
        return self.kodi_db.episodes(sort=kodidb.SORT_RATING, filters=filters, limits=(0,self.arguments["limit"]))
                
    def recent(self):
        ''' get recently added episodes '''
        tvshow_episodes = {}
        total_count = 0
        unique_count = 0
        filters = []
        if self.arguments["hide_watched"]:
            filters += kodidb.FILTER_UNWATCHED
        while unique_count < self.arguments["limit"]:
            recent_episodes = self.kodi_db.episodes(sort=kodidb.SORT_DATEADDED,filters=filters,limits=(total_count,self.arguments["limit"]+total_count))
            if not self.arguments["group_episodes"]:
                #grouping is not enabled, just return the result
                return recent_episodes
                
            if len(recent_episodes) < self.arguments["limit"]:
                #break the loop if there are no more episodes
                unique_count = self.arguments["limit"]

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
        return sorted(all_items,key=itemgetter("dateadded"),reverse=True)[:self.arguments["limit"]]
                
    def random(self):
        ''' get random episodes '''
        filters = []
        if self.arguments["hide_watched"]:
            filters += kodidb.FILTER_UNWATCHED
        return self.kodi_db.episodes(sort=kodidb.SORT_DATEADDED, filters=filters, limits=(0,self.arguments["limit"]))
                
    def inprogress(self):
        ''' get in progress episodes '''
        return self.kodi_db.episodes(sort=kodidb.SORT_LASTPLAYED, filters=[kodidb.FILTER_INPROGRESS], limits=(0,self.arguments["limit"]))

    def inprogressandrecommended(self):
        ''' get recommended AND in progress episodes '''
        all_items = self.inprogress()
        all_titles = [item["title"] for item in all_items]
        for item in self.recommended():
            if item["title"] not in all_titles:
                all_items.append(item)
        return all_items[:self.arguments["limit"]]
        
    def inprogressandrandom(self):
        ''' get recommended AND random episodes '''
        all_items = self.inprogress()
        all_ids = [item["episodeid"] for item in all_items]
        for item in self.random():
            if item["episodeid"] not in all_ids:
                all_items.append(item)
        return all_items[:self.arguments["limit"]]
    
    def next(self):
        ''' get next episodes '''
        filters = [ kodidb.FILTER_UNWATCHED ]
        if self.arguments["next_inprogress_only"]:
            filters = [ kodidb.FILTER_INPROGRESS ]
        fields = [ "title", "lastplayed", "playcount" ]
        # First we get a list of all the inprogress/unwatched TV shows ordered by lastplayed
        all_shows = self.kodi_db.tvshows(sort=kodidb.SORT_LASTPLAYED, filters=filters, limits=(0,self.arguments["limit"]))
        return process_method_on_list(self.get_next_episode_for_show, [d['tvshowid'] for d in all_shows])
        
    def get_next_episode_for_show(self,show_id):
        '''get next unwatched episode for tvshow'''
        filters = [ kodidb.FILTER_UNWATCHED ]
        if not self.arguments["enable_specials"]:
            filters.append( {"field": "season", "operator": "greaterthan", "value": "0"} )
        json_episodes = self.kodi_db.episodes(sort=kodidb.SORT_EPISODE, filters=filters, limits=(0,1), tvshowid=show_id)
        if json_episodes:
            return json_episodes[0]
        else:
            return None
            
    def unaired(self):
        ''' get all unaired episodes for shows in the library - provided by tvdb module'''
        import thetvdb
        thetvdb.DAYS_AHEAD = 120
        episodes = thetvdb.getKodiSeriesUnairedEpisodesList(False)[:self.arguments["limit"]]
        return process_method_on_list(self.set_unaired_episodes_props, episodes)
        
    def nextaired(self):
        ''' get all next airing episodes for shows in the library - provided by tvdb module'''
        import thetvdb
        thetvdb.DAYS_AHEAD = 45
        episodes = thetvdb.getKodiSeriesUnairedEpisodesList(True)
        return process_method_on_list(self.set_unaired_episodes_props, episodes)
     
    @staticmethod
    def set_unaired_episodes_props(episode_json):
        '''helper to set some additional properties on unaired episode widget'''
        extraprops = {}
        extraprops["airday"] = episode_json["seriesinfo"]["airsDayOfWeek"]
        extraprops["airtime"] = episode_json["seriesinfo"]["airsTime"]
        extraprops["DBTYPE"] = "episode"
        episode_json["extraproperties"] = extraprops
        return episode_json
        
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
        
        