#!/usr/bin/python
# -*- coding: utf-8 -*-
from utils import *
from operator import itemgetter

class Tvshows(object):
    '''all tvshow widgets provided by the script'''
    hide_watched = SETTING("hideWatchedItemsInWidgets") == "true"
    arguments = {}
    
    def listing(self):
        '''main listing with all our tvshow nodes'''
        all_items = [ 
            (ADDON.getLocalizedString(32044), "inprogress&mediatype=tvshows", "DefaultTvShows.png"), 
            (ADDON.getLocalizedString(32045), "recent&mediatype=tvshows", "DefaultTvShows.png"),
            (ADDON.getLocalizedString(32037), "recommended&mediatype=tvshows", "DefaultTvShows.png"),
            (ADDON.getLocalizedString(32014), "similar&mediatype=tvshows", "DefaultTvShows.png"),
            (ADDON.getLocalizedString(32041), "random&mediatype=tvshows", "DefaultTvShows.png"),
            (ADDON.getLocalizedString(32047), "top250&mediatype=tvshows", "DefaultTvShows.png"),
            (xbmc.getLocalizedString(135), "browsegenres&mediatype=tvshows", "DefaultGenres.png")
            ]
        return process_method_on_list(create_main_entry,all_items)

    def recommended(self):
        ''' get recommended tvshows - library tvshows with score higher than 7 '''
        filters = [FILTER_RATING]
        if self.arguments["hide_watched"]:
            filters += FILTER_UNWATCHED
        return get_kodi_json('VideoLibrary.GetTvShows','rating',filters,FIELDS_TVSHOWS,(0,self.arguments["limit"]),"tvshows")
                
    def recent(self):
        ''' get recently added tvshows '''
        filters = []
        if self.arguments["hide_watched"]:
            filters += FILTER_UNWATCHED
        return get_kodi_json('VideoLibrary.GetTvShows','dateadded',filters,FIELDS_TVSHOWS,(0,self.arguments["limit"]),"tvshows")
                
    def random(self):
        ''' get random tvshows '''
        filters = []
        if self.arguments["hide_watched"]:
            filters += FILTER_UNWATCHED
        return get_kodi_json('VideoLibrary.GetTvShows','random',filters,FIELDS_TVSHOWS,(0,self.arguments["limit"]),"tvshows")
                
    def inprogress(self):
        ''' get in progress tvshows '''
        return get_kodi_json('VideoLibrary.GetTvShows','lastplayed',[FILTER_INPROGRESS],FIELDS_TVSHOWS,(0,self.arguments["limit"]),"tvshows")

    def similar(self):
        ''' get similar tvshows for given imdbid or just from random watched title if no imdbid'''
        imdb_id = self.arguments.get("imdbid","")
        all_items = []
        all_titles = list()
        json_result = []
        #lookup tvshow by imdbid or just pick a random watched tvshow
        ref_tvshow = None
        if imdb_id:
            #get tvshow by imdbid
            ref_tvshow = self.get_tvshow_by_imdbid(imdb_id)
        if not ref_tvshow:
            #just get a random watched tvshow
            ref_tvshow = self.get_random_watched_tvshow()
        if ref_tvshow:
            #get all tvshows for the genres in the tvshow
            genres = ref_tvshow["genre"]
            similar_title = ref_tvshow["title"]
            for genre in genres:
                self.arguments["genre"] = genre
                genre_tvshows = self.forgenre()
                for item in genre_tvshows:
                    #prevent duplicates so skip reference tvshow and titles already in the list
                    if not item["title"] in all_titles and not item["title"] == similar_title:
                        item["extraproperties"] = {"similartitle": similar_title, "originalpath": item["file"]}
                        all_items.append(item)
                        all_titles.append(item["title"])
        #return the list capped by limit and sorted by rating
        return sorted(all_items,key=itemgetter("rating"),reverse=True)[:self.arguments["limit"]]
    
    def forgenre(self):
        ''' get top rated tvshows for given genre'''
        genre = self.arguments.get("genre","")
        all_items = []
        if not genre:
            #get a random genre if no genre provided
            json_result = get_kodi_json('VideoLibrary.GetGenres','random',[],[],(0,1),"genres",{"type": "tvshow"})
            if json_result: 
                genre = json_result[0]["label"]
        if genre:
            #get all tvshows from the same genre
            for item in self.get_genre_tvshows(genre,self.arguments["hide_watched"],self.arguments["limit"]):
                #append original genre as listitem property for later reference by skinner
                item["extraproperties"] = {"genretitle": genre, "originalpath": item["file"]}
                all_items.append(item)

        #return the list sorted by rating
        return sorted(all_items,key=itemgetter("rating"),reverse=True)
        
    def top250(self):
        ''' get imdb top250 tvshows in library '''
        all_items = []
        all_tvshows = get_kodi_json('VideoLibrary.GetTvShows','',[],["imdbnumber"],(),"tvshows")
        #top_250 = artutils.getImdbTop250() #TODO
        top_250 = {}
        for tvshow in all_tvshows:
            if tvshow["imdbnumber"] in top_250:
                get_kodi_json('VideoLibrary.GetTvShowDetails','',[],[FIELDS_TVSHOWS],(),
                    "tvshows", {"tvshowid":tvshow["tvshowid"]})
                tvshow["top250_rank"] = int(top_250[tvshow["imdbnumber"]])
                all_items.append(tvshow)
        return sorted(all_items,key=itemgetter("top250_rank"))[:self.arguments["limit"]]
    
    def browsegenres(self):
        '''
            special entry which can be used to create custom genre listings
            returns each genre with poster/fanart artwork properties from 5
            random tvshows in the genre.
            TODO: get auto generated collage pictures from skinhelper's artutils ?
        '''
        all_genres = get_kodi_json('VideoLibrary.GetGenres','title',[],[],None,"genres",{"type": "tvshow"})
        return process_method_on_list(self.get_genre_artwork,all_genres)
        
    def get_genre_artwork(self, genre_json):
        '''helper method for browsegenres'''
        #for each genre we get 5 random items from the library and attach the artwork to the genre listitem
        genre_json["art"] = {}
        genre_json["file"] = "videodb://tvshows/genres/%s/"%genre_json["genreid"]
        genre_json["isFolder"] = True
        genre_json["IsPlayable"] = "false"
        genre_json["thumbnail"] = "DefaultGenre.png"
        genre_json["type"] = "genre"
        genre_tvshows = self.get_genre_tvshows(genre_json["label"],False,5)
        for count, genre_tvshow in enumerate(genre_tvshows):
            genre_json["art"]["poster.%s" %count] = genre_tvshow["art"].get("poster","")
            genre_json["art"]["fanart.%s" %count] = genre_tvshow["art"].get("fanart","")
            if not "fanart" in genre_json["art"]:
                #set genre's primary fanart image to first movie fanart
                genre_json["art"]["fanart"] = genre_tvshow["art"].get("fanart","")
        return genre_json
    
    def nextaired(self):
        '''legacy method: get nextaired episodes instead'''
        import episodes
        eps_class = episodes.Episodes()
        eps_class.limit = self.arguments["limit"]
        eps_class.arguments = self.arguments
        return eps_class.nextaired()
        
    @staticmethod
    def get_tvshow_by_imdbid(imdb_id):
        '''gets a tvshow from kodidb by imdbid.'''
        filters = [{ "operator":"is", "field":"imdbnumber", "value":imdb_id}]
        tvshows = get_kodi_json('VideoLibrary.GetTvShows',None,filters,FIELDS_TVSHOWS,None,"tvshows")
        if tvshows:
            return tvshows[0]
        else:
            return None
            
    @staticmethod
    def get_random_watched_tvshow():
        '''gets a random watched or inprogress tvshow from kodidb.'''
        filter = [ {"or": [FILTER_WATCHED,FILTER_INPROGRESS] } ]
        tvshows = get_kodi_json('VideoLibrary.GetTvShows','random',filter,FIELDS_TVSHOWS,(0,1),"tvshows")
        if tvshows:
            return tvshows[0]
        else:
            return None
            
    @staticmethod
    def get_genre_tvshows(genre,hide_watched=False,limit=100):
        '''helper method to get all tvshows in a specific genre'''
        filters = [{"operator":"is", "field":"genre","value":genre}]
        if hide_watched:
            filters += FILTER_UNWATCHED
        return get_kodi_json('VideoLibrary.GetTvShows','random',filters,FIELDS_TVSHOWS,(0,limit),"tvshows")


