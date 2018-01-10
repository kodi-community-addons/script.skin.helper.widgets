#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    script.skin.helper.widgets
    media.py
    all media (mixed) widgets provided by the script
'''

from utils import create_main_entry
from operator import itemgetter
from movies import Movies
from tvshows import Tvshows
from songs import Songs
from pvr import Pvr
from albums import Albums
from episodes import Episodes
import random


class Media(object):
    '''all media (mixed) widgets provided by the script'''

    def __init__(self, addon, metadatautils, options):
        '''Initializations pass our common classes and the widget options as arguments'''
        self.metadatautils = metadatautils
        self.addon = addon
        self.options = options
        self.movies = Movies(self.addon, self.metadatautils, self.options)
        self.tvshows = Tvshows(self.addon, self.metadatautils, self.options)
        self.songs = Songs(self.addon, self.metadatautils, self.options)
        self.albums = Albums(self.addon, self.metadatautils, self.options)
        self.pvr = Pvr(self.addon, self.metadatautils, self.options)
        self.episodes = Episodes(self.addon, self.metadatautils, self.options)

    def listing(self):
        '''main listing with all our movie nodes'''
        all_items = [
            (self.addon.getLocalizedString(32011), "inprogress&mediatype=media", "DefaultMovies.png"),
            (self.addon.getLocalizedString(32070), "inprogressshowsandmovies&mediatype=media", "DefaultMovies.png"),
            (self.addon.getLocalizedString(32005), "recent&mediatype=media", "DefaultMovies.png"),
            (self.addon.getLocalizedString(32004), "recommended&mediatype=media", "DefaultMovies.png"),
            (self.addon.getLocalizedString(32007), "inprogressandrecommended&mediatype=media", "DefaultMovies.png"),
            (self.addon.getLocalizedString(32060), "inprogressandrandom&mediatype=media", "DefaultMovies.png"),
            (self.addon.getLocalizedString(32022), "similar&mediatype=media", "DefaultMovies.png"),
            (self.addon.getLocalizedString(32059), "random&mediatype=media", "DefaultMovies.png"),
            (self.addon.getLocalizedString(32058), "top250&mediatype=media", "DefaultMovies.png"),
            (self.addon.getLocalizedString(32001), "favourites&mediatype=media", "DefaultMovies.png"),
            (self.addon.getLocalizedString(32075), "playlistslisting&mediatype=media&movie_label=",
                "DefaultMovies.png")
        ]
        return self.metadatautils.process_method_on_list(create_main_entry, all_items)

    def playlistslisting(self):
        '''get tv playlists listing'''
        movie_label = self.options.get("movie_label")
        all_items = []
        for item in self.metadatautils.kodidb.files("special://videoplaylists/"):
            # replace '&' with [and] -- will get fixed when processed in playlist action
            label = item["label"].replace('&', '[and]')
            if movie_label:
                details = (item["label"], "playlist&mediatype=media&movie_label=%s&tv_label=%s" %
                    (movie_label, label), "DefaultTvShows.png")
            else:
                details = (item["label"], "playlistslisting&mediatype=media&movie_label=%s" % label,
                    "DefaultMovies.png")
            all_items.append(create_main_entry(details))
        return all_items

    def playlist(self):
        '''get items in both playlists, sorted by recommended score'''
        movie_label = self.options.get("movie_label").replace('[and]','&')
        tv_label = self.options.get("tv_label").replace('[and]','&')
        # get recommended items from movie playlist
        movies = self.metadatautils.kodidb.movies(filters=
            [{"operator": "is", "field": "playlist", "value": movie_label}])
        movies = self.movies.sort_by_recommended(movies)
        # get recommended items from tvshows playlist
        tvshows = self.metadatautils.kodidb.tvshows(filters=
            [{"operator": "is", "field": "playlist", "value": tv_label}])
        tvshows = self.tvshows.sort_by_recommended(tvshows)
        tvshows = self.metadatautils.process_method_on_list(self.tvshows.process_tvshow, tvshows)
        # concatenate and sort by rating
        all_items = movies+tvshows
        return sorted(all_items, key=itemgetter("recommendedscore"), reverse=True)[:self.options["limit"]]

    def recommended(self):
        ''' get recommended media '''
        all_items = self.movies.recommended()
        all_items += self.tvshows.recommended()
        all_items += self.albums.recommended()
        all_items += self.songs.recommended()
        all_items += self.episodes.recommended()
        return sorted(all_items, key=lambda k: random.random())[:self.options["limit"]]

    def recent(self):
        ''' get recently added media '''
        all_items = self.movies.recent()
        all_items += self.albums.recent()
        all_items += self.songs.recent()
        all_items += self.episodes.recent()
        all_items += self.pvr.recordings()
        return sorted(all_items, key=itemgetter("dateadded"), reverse=True)[:self.options["limit"]]

    def random(self):
        ''' get random media '''
        all_items = self.movies.random()
        all_items += self.tvshows.random()
        all_items += self.albums.random()
        all_items += self.songs.random()
        all_items += self.episodes.random()
        all_items += self.pvr.recordings()
        return sorted(all_items, key=lambda k: random.random())[:self.options["limit"]]

    def inprogress(self):
        ''' get in progress media '''
        all_items = self.movies.inprogress()
        all_items += self.episodes.inprogress()
        all_items += self.pvr.recordings()
        return sorted(all_items, key=itemgetter("lastplayed"), reverse=True)[:self.options["limit"]]

    def inprogressshowsandmovies(self):
        ''' get in progress media '''
        all_items = self.movies.inprogress()
        all_items += self.episodes.inprogress()
        return sorted(all_items, key=itemgetter("lastplayed"), reverse=True)[:self.options["limit"]]

    def similar(self):
        ''' get similar movies and similar tvshows for given imdbid'''
        all_items = self.movies.similar()
        all_items += self.tvshows.similar()
        all_items += self.albums.similar()
        all_items += self.songs.similar()
        return sorted(all_items, key=lambda k: random.random())[:self.options["limit"]]

    def inprogressandrecommended(self):
        ''' get recommended AND in progress media '''
        all_items = self.inprogress()
        all_titles = [item["title"] for item in all_items]
        for item in self.recommended():
            if item["title"] not in all_titles:
                all_items.append(item)
        return all_items[:self.options["limit"]]

    def inprogressandrandom(self):
        ''' get in progress AND random movies '''
        all_items = self.inprogress()
        all_ids = [item["movieid"] for item in all_items]
        for item in self.random():
            if item["movieid"] not in all_ids:
                all_items.append(item)
        return all_items[:self.options["limit"]]

    def top250(self):
        ''' get imdb top250 movies in library '''
        all_items = self.movies.top250()
        all_items += self.tvshows.top250()
        return sorted(all_items, key=itemgetter("top250_rank"))[:self.options["limit"]]

    def favourites(self):
        '''get favourite media'''
        from favourites import Favourites
        self.options["mediafilter"] = "media"
        return Favourites(self.addon, self.metadatautils, self.options).favourites()

    def favourite(self):
        '''synonym to favourites'''
        return self.favourites()
