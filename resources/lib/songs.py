#!/usr/bin/python
# -*- coding: utf-8 -*-
from utils import process_method_on_list, create_main_entry
from operator import itemgetter
from artutils import kodi_constants
import xbmc

class Songs(object):
    '''all song widgets provided by the script'''

    def __init__(self, addon, artutils, options):
        '''Initializations pass our common classes and the widget options as arguments'''
        self.artutils = artutils
        self.addon = addon
        self.options = options


    def listing(self):
        '''main listing with all our song nodes'''
        all_items = [
            (self.addon.getLocalizedString(32013), "recentplayed&mediatype=songs", "DefaultSongs.png"),
            (self.addon.getLocalizedString(32012), "recent&mediatype=songs", "DefaultSongs.png"),
            (self.addon.getLocalizedString(32016), "recommended&mediatype=songs", "DefaultSongs.png"),
            (self.addon.getLocalizedString(32055), "similar&mediatype=songs", "DefaultSongs.png"),
            (self.addon.getLocalizedString(32034), "random&mediatype=songs", "DefaultSongs.png"),
            (xbmc.getLocalizedString(10134), "favourites&mediatype=songs", "DefaultAlbums.png")
            ]
        return process_method_on_list(create_main_entry,all_items)
        
    def favourites(self):
        '''get favourites'''
        from favourites import Favourites
        self.options["mediafilter"] = "songs"
        return Favourites(self.addon, self.artutils, self.options).listing()

    def recommended(self):
        ''' get recommended songs - library songs with score higher than 7 '''
        filters = [kodi_constants.FILTER_RATING_MUSIC]
        return self.artutils.kodidb.songs(sort=kodi_constants.SORT_RATING, filters=filters,
            limits=(0,self.options["limit"]))

    def recent(self):
        ''' get recently added songs '''
        return self.artutils.kodidb.get_json("AudioLibrary.GetRecentlyAddedSongs", filters=[],
            fields=kodi_constants.FIELDS_SONGS, limits=(0,self.options["limit"]), returntype="songs")

    def random(self):
        ''' get random songs '''
        return self.artutils.kodidb.songs(sort=kodi_constants.SORT_RANDOM, filters=[],
            limits=(0,self.options["limit"]))

    def recentplayed(self):
        ''' get in progress songs '''
        return self.artutils.kodidb.songs(sort=kodi_constants.SORT_LASTPLAYED, filters=[],
            limits=(0,self.options["limit"]))

    def similar(self):
        ''' get similar songs for recent played song'''
        all_items = []
        all_titles = list()
        json_result = []
        ref_song = self.get_random_played_song()
        if ref_song:
            #get all songs for the genres in the song
            genres = ref_song["genre"]
            similar_title = ref_song["title"]
            for genre in genres:
                genre = genre.split(";")[0]
                self.options["genre"] = genre
                genre_songs = self.get_genre_songs(genre)
                for item in genre_songs:
                    #prevent duplicates so skip reference song and titles already in the list
                    if not item["title"] in all_titles and not item["title"] == similar_title:
                        item["extraproperties"] = {"similartitle": similar_title}
                        all_items.append(item)
                        all_titles.append(item["title"])
        #return the list capped by limit and sorted by rating
        return sorted(all_items,key=itemgetter("rating"),reverse=True)[:self.options["limit"]]

        
    def get_random_played_song(self):
        '''gets a random played song from kodi_constants.'''
        songs = self.artutils.kodidb.songs(sort=kodi_constants.SORT_RANDOM,
            filters=[kodi_constants.FILTER_WATCHED], limits=(0,1))
        if songs:
            return songs[0]
        else:
            return None

    def get_genre_songs(self,genre,limit=100):
        '''helper method to get all songs in a specific genre'''
        filters = [{"operator":"contains", "field":"genre","value":genre}]
        return self.artutils.kodidb.songs(sort=kodi_constants.SORT_RANDOM, filters=filters, limits=(0,limit))

