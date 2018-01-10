#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    script.skin.helper.widgets
    media.py
    all media (mixed) widgets provided by the script
'''

from utils import create_main_entry
from metadatautils import kodi_constants
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
        movies = self.metadatautils.kodidb.movies(filters=
            [{"operator": "is", "field": "playlist", "value": movie_label}])
        tvshows = self.metadatautils.kodidb.tvshows(filters=
            [{"operator": "is", "field": "playlist", "value": tv_label}])
        tvshows = self.metadatautils.process_method_on_list(self.tvshows.process_tvshow, tvshows)
        all_items = self.sort_by_recommended(movies+tvshows)
        return sorted(all_items, key=itemgetter("recommendedscore"), reverse=True)[:self.options["limit"]]

    def recommended(self):
        ''' get recommended media '''
        if self.options["exp_recommended"]:
            # get all unwatched, not in-progess movies & tvshows
            movies = self.metadatautils.kodidb.movies(filters=[kodi_constants.FILTER_UNWATCHED])
            tvshows = self.metadatautils.kodidb.tvshows(filters=[kodi_constants.FILTER_UNWATCHED,
                       {"operator":"false", "field":"inprogress", "value":""}])
            tvshows = self.metadatautils.process_method_on_list(self.tvshows.process_tvshow, tvshows)
            # return list sorted by recommended score, and capped by limit
            return self.sort_by_recommended(movies+tvshows)
        else:
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
        if self.options["exp_recommended"]:
            # get ref item, and check if movie
            ref_item = self.get_recently_watched_item()
            is_ref_movie = ref_item.has_key("uniqueid")
            # create list of all items
            if self.options["hide_watched_similar"]:
                all_items = self.metadatautils.kodidb.movies(filters=[kodi_constants.FILTER_UNWATCHED])
                all_items += self.metadatautils.process_method_on_list(
                    self.tvshows.process_tvshow, self.metadatautils.kodidb.tvshows(
                        filters=[kodi_constants.FILTER_UNWATCHED,
                            {"operator":"false", "field":"inprogress", "value":""}]))
            else:
                all_items = self.metadatautils.kodidb.movies()
                all_items += self.metadatautils.process_method_on_list(
                    self.tvshows.process_tvshow, self.metadatautils.kodidb.tvshows())
            if ref_item:
                if is_ref_movie:
                    # define sets for speed
                    set_genres = set(ref_item["genre"])
                    set_directors = set(ref_item["director"])
                    set_writers = set(ref_item["writer"])
                    set_cast = set([x["name"] for x in ref_item["cast"][:5]])
                    # get similarity score for all items
                    for item in all_items:
                        if item.has_key("uniqueid"):
                            # if item is also movie, check if it's the ref_item
                            if item["title"]==ref_item["title"] and item["year"]==ref_item["year"]:
                                # don't rank the reference movie
                                similarscore = 0
                            else:
                                # otherwise, use movie method for score
                                similarscore = self.movies.get_similarity_score(ref_item, item,
                                    set_genres=set_genres, set_directors=set_directors,
                                    set_writers=set_writers, set_cast=set_cast)
                        else:
                            # if item isn't movie, use mixed method
                            similarscore = self.get_similarity_score(ref_item, item)
                        # set extraproperties
                        item["similarscore"] = similarscore
                        item["extraproperties"] = {"similartitle": ref_item["title"], "originalpath": item["file"]}
                else:
                    # define sets for speed
                    set_genres = set(ref_item["genre"])
                    set_cast = set([x["name"] for x in ref_item["cast"][:10]])
                    # get similarity score for all items
                    for item in all_items:
                        if not item.has_key("uniqueid"):
                            # if item is also tvshow, check if it's the ref_item
                            if item["title"]==ref_item["title"] and item["year"]==ref_item["year"]:
                                # don't rank the reference movie
                                similarscore = 0
                            else:
                                # otherwise, use tvshow method for score
                                similarscore = self.tvshows.get_similarity_score(ref_item, item,
                                    set_genres=set_genres, set_cast=set_cast)
                        else:
                            # if item isn't tvshow, use mixed method
                            similarscore = self.get_similarity_score(ref_item, item)
                        # set extraproperties
                        item["similarscore"] = similarscore
                        item["extraproperties"] = {"similartitle": ref_item["title"], "originalpath": item["file"]}
                # return list sorted by score and capped by limit
                return sorted(all_items, key=itemgetter("similarscore"), reverse=True)[:self.options["limit"]]
        else:
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

    def get_recently_watched_item(self):
        ''' get a random recently watched movie or tvshow '''
        num_recent_similar = (self.options["num_recent_similar"]+1)/2
        recent_items = self.metadatautils.kodidb.movies(sort=kodi_constants.SORT_LASTPLAYED,
                                             filters=[kodi_constants.FILTER_WATCHED],
                                             limits=(0, num_recent_similar))
        recent_items += self.metadatautils.kodidb.tvshows(sort=kodi_constants.SORT_LASTPLAYED,
                                                filters=[kodi_constants.FILTER_WATCHED,
                                                    kodi_constants.FILTER_INPROGRESS],
                                                filtertype="or",
                                                limits=(0, num_recent_similar))
        if recent_items:
            return recent_items[random.randint(0,len(recent_items)-1)]

    def sort_by_recommended(self, all_items):
        ''' sort list of mixed movies/tvshows by recommended score'''
        # get recently watched items
        num_recent_similar = self.options["num_recent_similar"]
        all_refs = self.metadatautils.kodidb.tvshows(sort=kodi_constants.SORT_LASTPLAYED,
                                                        filters=[kodi_constants.FILTER_WATCHED],
                                                        limits=(0, num_recent_similar))
        all_refs += self.metadatautils.kodidb.movies(sort=kodi_constants.SORT_LASTPLAYED,
                                                        filters=[kodi_constants.FILTER_WATCHED],
                                                        limits=(0, num_recent_similar))
        # average scores together for every item
        for item in all_items:
            similarscore = 0
            for ref_item in all_refs:
                # add all similarscores for item
                if ref_item.has_key("uniqueid") and item.has_key("uniqueid"):
                    # use movies method if both items are movies
                    similarscore += self.movies.get_similarity_score(ref_item, item)
                elif ref_item.has_key("uniqueid") or item.has_key("uniqueid"):
                    # use media method if only one item is a movie
                    similarscore += self.get_similarity_score(ref_item, item)
                else:
                    # use tvshows method if neither items are movies
                    similarscore += self.tvshows.get_similarity_score(ref_item, item)
            item["recommendedscore"] = similarscore / (1+item["playcount"]) / len(all_refs)
        # return sorted list capped by limit
        return sorted(all_items, key=itemgetter("recommendedscore"), reverse=True)[:self.options["limit"]]

    @staticmethod
    def get_similarity_score(ref_item, other_item):
        '''
            get a similarity score (0-.75) between movie and tvshow
        '''
        set_genres = set(ref_item["genre"])
        set_cast = set([x["name"] for x in ref_item["cast"][:5]])
        # calculate individual scores for contributing factors
        # genre_score = (numer of matching genres) / (number of unique genres between both)
        genre_score = float(len(set_genres.intersection(other_item["genre"]))) / \
            len(set_genres.union(other_item["genre"]))
        # cast_score is normalized by fixed amount of 5, and scaled up nonlinearly
        cast_score = (float(len(set_cast.intersection( [x["name"] for x in other_item["cast"][:5]] )))/5)**(1./2)
        # rating_score is "closeness" in rating, scaled to 1
        if ref_item["rating"] and other_item["rating"] and abs(ref_item["rating"]-other_item["rating"])<3:
            rating_score = 1-abs(ref_item["rating"]-other_item["rating"])/3
        else:
            rating_score = 0
        # year_score is "closeness" in release year, scaled to 1 (0 if not from same decade)
        if ref_item["year"] and other_item["year"] and abs(ref_item["year"]-other_item["year"])<10:
            year_score = 1-abs(ref_item["year"]-other_item["year"])/10
        else:
            year_score = 0
        # calculate overall score using weighted average
        similarscore = .5*genre_score + .1*cast_score + .025*rating_score + .025*year_score
        return similarscore
