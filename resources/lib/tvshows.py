#!/usr/bin/python
# -*- coding: utf-8 -*-
from utils import process_method_on_list
from operator import itemgetter
from artutils import kodi_constants, Imdb, TheTvDb
import xbmc

class Tvshows(object):
    '''all tvshow widgets provided by the script'''

    def __init__(self, addon, kodidb, options):
        '''Initializations pass our common classes and the widget options as arguments'''
        self.kodidb = kodidb
        self.addon = addon
        self.options = options
        self.imdb = Imdb()
        self.thetvdb = TheTvDb()

    def __del__(self):
        '''Cleanup'''
        del self.imdb

    def listing(self):
        '''main listing with all our tvshow nodes'''
        all_items = [
            (self.addon.getLocalizedString(32044), "inprogress&mediatype=tvshows", "DefaultTvShows.png"),
            (self.addon.getLocalizedString(32045), "recent&mediatype=tvshows", "DefaultTvShows.png"),
            (self.addon.getLocalizedString(32037), "recommended&mediatype=tvshows", "DefaultTvShows.png"),
            (self.addon.getLocalizedString(32014), "similar&mediatype=tvshows", "DefaultTvShows.png"),
            (self.addon.getLocalizedString(32041), "random&mediatype=tvshows", "DefaultTvShows.png"),
            (self.addon.getLocalizedString(32047), "top250&mediatype=tvshows", "DefaultTvShows.png"),
            (xbmc.getLocalizedString(135), "browsegenres&mediatype=tvshows", "DefaultGenres.png")
            ]
        return process_method_on_list(self.kodidb.create_main_entry,all_items)

    def recommended(self):
        ''' get recommended tvshows - library tvshows with score higher than 7 '''
        filters = [kodi_constants.FILTER_RATING]
        if self.options["hide_watched"]:
            filters += kodi_constants.FILTER_UNWATCHED
        return self.kodidb.tvshows(sort=kodi_constants.SORT_RATING, filters=filters, limits=(0,self.options["limit"]))

    def recent(self):
        ''' get recently added tvshows '''
        filters = []
        if self.options["hide_watched"]:
            filters += kodi_constants.FILTER_UNWATCHED
        return self.kodidb.tvshows(sort=kodi_constants.SORT_DATEADDED, filters=filters, limits=(0,self.options["limit"]))

    def random(self):
        ''' get random tvshows '''
        filters = []
        if self.options["hide_watched"]:
            filters += kodi_constants.FILTER_UNWATCHED
        return self.kodidb.tvshows(sort=kodi_constants.SORT_RANDOM, filters=filters, limits=(0,self.options["limit"]))

    def inprogress(self):
        ''' get in progress tvshows '''
        return self.kodidb.tvshows(sort=kodi_constants.SORT_LASTPLAYED, filters=[kodi_constants.FILTER_INPROGRESS], limits=(0,self.options["limit"]))

    def similar(self):
        ''' get similar tvshows for given imdbid or just from random watched title if no imdbid'''
        imdb_id = self.options.get("imdbid","")
        all_items = []
        all_titles = list()
        json_result = []
        #lookup tvshow by imdbid or just pick a random watched tvshow
        ref_tvshow = None
        if imdb_id:
            #get tvshow by imdbid
            ref_tvshow = self.kodidb.tvshow_by_imdbid(imdb_id)
        if not ref_tvshow:
            #just get a random watched tvshow
            ref_tvshow = self.get_random_watched_tvshow()
        if ref_tvshow:
            #get all tvshows for the genres in the tvshow
            genres = ref_tvshow["genre"]
            similar_title = ref_tvshow["title"]
            for genre in genres:
                self.options["genre"] = genre
                genre_tvshows = self.forgenre()
                for item in genre_tvshows:
                    #prevent duplicates so skip reference tvshow and titles already in the list
                    if not item["title"] in all_titles and not item["title"] == similar_title:
                        item["extraproperties"] = {"similartitle": similar_title, "originalpath": item["file"]}
                        all_items.append(item)
                        all_titles.append(item["title"])
        #return the list capped by limit and sorted by rating
        return sorted(all_items,key=itemgetter("rating"),reverse=True)[:self.options["limit"]]

    def forgenre(self):
        ''' get top rated tvshows for given genre'''
        genre = self.options.get("genre","")
        all_items = []
        if not genre:
            #get a random genre if no genre provided
            json_result = self.kodidb.genres("tvshow")
            if json_result:
                genre = json_result[0]["label"]
        if genre:
            #get all tvshows from the same genre
            for item in self.get_genre_tvshows(genre,self.options["hide_watched"],self.options["limit"]):
                #append original genre as listitem property for later reference by skinner
                item["extraproperties"] = {"genretitle": genre, "originalpath": item["file"]}
                all_items.append(item)

        #return the list sorted by rating
        return sorted(all_items,key=itemgetter("rating"),reverse=True)

    def top250(self):
        ''' get imdb top250 tvshows in library '''
        all_items = []
        all_tvshows = self.kodidb.get_json('VideoLibrary.GetTvShows',fields=["imdbnumber"],returntype="tvshows")
        top_250 = self.imdb.get_top250_db()
        for tvshow in all_tvshows:
            if tvshow["imdbnumber"] and not tvshow["imdbnumber"].startswith("tt"):
                #we have a tvdb id
                tvdb_info = self.thetvdb.get_series(tvshow["imdbnumber"])
                if tvdb_info:
                    tvshow["imdbnumber"] = tvdb_info["imdbnumber"]
            if tvshow["imdbnumber"] in top_250:
                tvshow_full = self.kodidb.tvshow(tvshow["tvshowid"])
                tvshow_full["top250_rank"] = int(top_250[tvshow["imdbnumber"]])
                all_items.append(tvshow_full)
        return sorted(all_items,key=itemgetter("top250_rank"))[:self.options["limit"]]

    def browsegenres(self):
        '''
            special entry which can be used to create custom genre listings
            returns each genre with poster/fanart artwork properties from 5
            random tvshows in the genre.
            TODO: get auto generated collage pictures from skinhelper's artutils ?
        '''
        all_genres = self.kodidb.genres("tvshow")
        return process_method_on_list(self.get_genre_artwork,all_genres)

    def get_genre_artwork(self, genre_json):
        '''helper method for browsegenres'''
        #for each genre we get 5 random items from the library and attach the artwork to the genre listitem
        genre_json["art"] = {}
        genre_json["file"] = "videodb://tvshows/genres/%s/"%genre_json["genreid"]
        genre_json["isFolder"] = True
        genre_json["IsPlayable"] = "false"
        genre_json["thumbnail"] = genre_json.get("thumbnail", "DefaultGenre.png") #TODO: get icon from resource addon ?
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
        from episodes import Episodes
        eps = Episodes( self.addon, self.kodidb, self.options )
        result = eps.nextaired()
        del eps
        return result

    def get_random_watched_tvshow(self):
        '''gets a random watched or inprogress tvshow from kodi_constants.'''
        filters = [kodi_constants.FILTER_WATCHED,kodi_constants.FILTER_INPROGRESS]
        tvshows = self.kodidb.tvshows(sort=kodi_constants.SORT_RANDOM,filters=filters,filtertype="or",limits=(0,1))
        if tvshows:
            return tvshows[0]
        else:
            return None

    def get_genre_tvshows(self,genre,hide_watched=False,limit=100):
        '''helper method to get all tvshows in a specific genre'''
        filters = [{"operator":"is", "field":"genre","value":genre}]
        if hide_watched:
            filters += kodi_constants.FILTER_UNWATCHED
        return self.kodidb.tvshows(sort=kodi_constants.SORT_RANDOM,filters=filters,limits=(0,limit))


