#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    script.skin.helper.widgets
    movies.py
    all movies widgets provided by the script
'''

from operator import itemgetter
import random
import xbmc
from metadatautils import kodi_constants
from resources.lib.utils import create_main_entry, KODI_VERSION


class Movies(object):
    '''all movie widgets provided by the script'''

    def __init__(self, addon, metadatautils, options):
        '''Initializations pass our common classes and the widget options as arguments'''
        self.metadatautils = metadatautils
        self.addon = addon
        self.options = options

    def listing(self):
        '''main listing with all our movie nodes'''
        tag = self.options.get("tag", "")
        if tag:
            label_prefix = "%s - " % tag
        else:
            label_prefix = ""
        icon = "DefaultMovies.png"
        all_items = [
            (label_prefix + self.addon.getLocalizedString(32028), "inprogress&mediatype=movies&tag=%s" % tag, icon),
            (label_prefix + self.addon.getLocalizedString(32038), "recent&mediatype=movies&tag=%s" % tag, icon),
            (label_prefix + self.addon.getLocalizedString(32003), "recommended&mediatype=movies&tag=%s" % tag, icon),
            (label_prefix + self.addon.getLocalizedString(32029),
             "inprogressandrecommended&mediatype=movies&tag=%s" % tag, icon),
            (label_prefix + self.addon.getLocalizedString(32048), "random&mediatype=movies&tag=%s" % tag, icon),
            (label_prefix + self.addon.getLocalizedString(32066), "unwatched&mediatype=movies&tag=%s" % tag, icon),
            (label_prefix + self.addon.getLocalizedString(32046), "top250&mediatype=movies&tag=%s" % tag, icon),
            (label_prefix + xbmc.getLocalizedString(135),
             "browsegenres&mediatype=movies&tag=%s" % tag, "DefaultGenres.png")
        ]
        if not tag:
            all_items += [
                (self.addon.getLocalizedString(32006), "similar&mediatype=movies&tag=%s" % tag, icon),
                (xbmc.getLocalizedString(10134), "favourites&mediatype=movies&tag=%s" % tag, icon),
                (self.addon.getLocalizedString(32078), "playlistslisting&mediatype=movies", icon),
                (self.addon.getLocalizedString(32076), "playlistslisting&mediatype=movies&tag=ref", icon),
                (xbmc.getLocalizedString(20459), "tagslisting&mediatype=movies", icon)
            ]
        return self.metadatautils.process_method_on_list(create_main_entry, all_items)

    def tagslisting(self):
        '''get tags listing'''
        all_items = []
        for item in self.metadatautils.kodidb.files("videodb://movies/tags"):
            details = (item["label"], "listing&mediatype=movies&tag=%s" % item["label"], "DefaultTags.png")
            all_items.append(create_main_entry(details))
        return all_items

    def playlistslisting(self):
        '''get playlists listing'''
        all_items = []
        for item in self.metadatautils.kodidb.files("special://videoplaylists/"):
            # replace '&' with [and] -- will get fixed when processed in playlist action
            tag_label = item["label"].replace('&', '[and]')
            if self.options.get("tag") == 'ref':
                details = (item["label"], "refplaylist&mediatype=movies&tag=%s" % tag_label, "DefaultMovies.png")
            else:
                details = (item["label"], "playlist&mediatype=movies&tag=%s" % tag_label, "DefaultMovies.png")
            all_items.append(create_main_entry(details))
        return all_items

    def playlist(self):
        '''get items in playlist, sorted by recommended score'''
        # fix amperstand in tag_label
        tag_label = self.options.get("tag").replace('[and]', '&')
        # get all items in playlist
        filters = [{"operator": "is", "field": "playlist", "value": tag_label}]
        all_items = self.metadatautils.kodidb.movies(filters=filters)
        # return list sorted by recommended score
        return self.sort_by_recommended(all_items)

    def refplaylist(self):
        '''get items similar to items in ref playlist'''
        # fix amperstand in tag_label
        tag_label = self.options.get("tag").replace('[and]', '&')
        # get all items in playlist
        playlist_filter = [{"operator": "is", "field": "playlist", "value": tag_label}]
        ref_items = self.metadatautils.kodidb.movies(filters=playlist_filter)
        # get all items not in playlist
        not_playlist_filter = [{"operator": "isnot", "field": "playlist", "value": tag_label}]
        all_items = self.metadatautils.kodidb.movies(filters=not_playlist_filter)
        # return list sorted by recommended score
        return self.sort_by_recommended(all_items, ref_items)

    def recommended(self):
        ''' get recommended movies - library movies with score higher than 7 '''
        filters = [kodi_constants.FILTER_RATING]
        if self.options["hide_watched"]:
            filters.append(kodi_constants.FILTER_UNWATCHED)
        if self.options.get("tag"):
            filters.append({"operator": "contains", "field": "tag", "value": self.options["tag"]})
        return self.metadatautils.kodidb.movies(sort=kodi_constants.SORT_RATING, filters=filters,
                                           limits=(0, self.options["limit"]))

    def recent(self):
        ''' get recently added movies '''
        filters = []
        if self.options["hide_watched"]:
            filters.append(kodi_constants.FILTER_UNWATCHED)
        if self.options.get("tag"):
            filters.append({"operator": "contains", "field": "tag", "value": self.options["tag"]})
        return self.metadatautils.kodidb.movies(sort=kodi_constants.SORT_DATEADDED, filters=filters,
                                                limits=(0, self.options["limit"]))

    def random(self):
        ''' get random movies '''
        filters = []
        if self.options["hide_watched"]:
            filters.append(kodi_constants.FILTER_UNWATCHED)
        if self.options.get("tag"):
            filters.append({"operator": "contains", "field": "tag", "value": self.options["tag"]})
        return self.metadatautils.kodidb.movies(sort=kodi_constants.SORT_RANDOM, filters=filters,
                                                limits=(0, self.options["limit"]))

    def inprogress(self):
        ''' get in progress movies '''
        filters = [kodi_constants.FILTER_INPROGRESS]
        if self.options.get("tag"):
            filters.append({"operator": "contains", "field": "tag", "value": self.options["tag"]})
        return self.metadatautils.kodidb.movies(sort=kodi_constants.SORT_LASTPLAYED,
                                                filters=filters,
                                                limits=(0, self.options["limit"]))

    def unwatched(self):
        ''' get unwatched movies '''
        filters = [kodi_constants.FILTER_UNWATCHED]
        if self.options.get("tag"):
            filters.append({"operator": "contains", "field": "tag", "value": self.options["tag"]})
        return self.metadatautils.kodidb.movies(sort=kodi_constants.SORT_TITLE, filters=filters,
                                                limits=(0, self.options["limit"]))

    def similar(self):
        ''' get similar movies for given imdbid or just from random watched title if no imdbid'''
        imdb_id = self.options.get("imdbid", "")
        all_items = []
        all_titles = list()
        # lookup movie by imdbid or just pick a random watched movie
        ref_movie = None
        hide_watched = self.options["hide_watched"]
        if imdb_id:
            # get movie by imdbid
            ref_movie = self.metadatautils.kodidb.movie_by_imdbid(imdb_id)
        if not ref_movie:
            # just get a random watched movie
            ref_movie = self.get_random_watched_movie()
            # when getting a random movie, it's for a homescreen widget, and
            # and that means it should hide watched movies
            self.options["hide_watched"] = True
        if ref_movie:
            # get all movies for the genres in the movie
            genres = ref_movie["genre"]
            similar_title = ref_movie["title"]
            for genre in genres:
                self.options["genre"] = genre
                genre_movies = self.forgenre()
                for item in genre_movies:
                    # prevent duplicates so skip reference movie and titles already in the list
                    if not item["title"] in all_titles and not item["title"] == similar_title:
                        item["extraproperties"] = {"similartitle": similar_title}
                        item["num_match"] = len(set(genres).intersection(item["genre"]))
                        all_items.append(item)
                        all_titles.append(item["title"])
        # restore hide_watched settings
        self.options["hide_watched"] = hide_watched
        # return the list capped by limit and sorted by number of matching genres then rating
        items_by_rating = sorted(all_items, key=itemgetter("rating"), reverse=True)
        return sorted(items_by_rating, key=itemgetter("num_match"), reverse=True)[:self.options["limit"]]

    def forgenre(self):
        ''' get top rated movies for given genre'''
        hide_watched = self.options["hide_watched"]
        limit = self.options["limit"]
        genre = self.options.get("genre", "")
        # get a random genre if no genre found
        if not genre:
            genre = self.metadatautils.kodidb.genres("movie")[0]["label"]
        all_items = []
        if genre:
            # get all movies from the same genre
            for item in self.get_genre_movies(genre, hide_watched=hide_watched, limit=limit):
                # append original genre as listitem property for later reference by skinner
                item["extraproperties"] = {"genretitle": genre, "originalpath": item["file"]}
                all_items.append(item)
        # return the list sorted by rating
        return sorted(all_items, key=itemgetter("rating"), reverse=True)

    def inprogressandrecommended(self):
        ''' get recommended AND in progress movies '''
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
        all_items = []
        filters = []
        if self.options.get("tag"):
            filters.append({"operator": "contains", "field": "tag", "value": self.options["tag"]})
        fields = ["imdbnumber"]
        if KODI_VERSION > 16:
            fields.append("uniqueid")
        all_movies = self.metadatautils.kodidb.get_json(
            'VideoLibrary.GetMovies', fields=fields, returntype="movies", filters=filters)
        top_250 = self.metadatautils.imdb.get_top250_db()
        for movie in all_movies:
            imdbnumber = movie["imdbnumber"]
            if not imdbnumber and "uniqueid" in movie:
                for value in movie["uniqueid"]:
                    if value.startswith("tt"):
                        imdbnumber = value
            if imdbnumber and imdbnumber in top_250:
                movie = self.metadatautils.kodidb.movie(movie["movieid"])
                movie["top250_rank"] = int(top_250[imdbnumber])
                all_items.append(movie)
        return sorted(all_items, key=itemgetter("top250_rank"))[:self.options["limit"]]

    def browsegenres(self):
        '''
            special entry which can be used to create custom genre listings
            returns each genre with poster/fanart artwork properties from 5
            random movies in the genre.
            TODO: get auto generated collage pictures from skinhelper's metadatautils ?
        '''
        all_genres = self.metadatautils.kodidb.genres("movie")
        return self.metadatautils.process_method_on_list(self.get_genre_artwork, all_genres)

    def get_genre_artwork(self, genre_json):
        '''helper method for browsegenres'''
        # for each genre we get 5 random items from the library and attach the artwork to the genre listitem
        genre_json["art"] = {}
        genre_json["file"] = "videodb://movies/genres/%s/" % genre_json["genreid"]
        if self.options.get("tag"):
            genre_json["file"] = "plugin://script.skin.helper.widgets?mediatype=movies&action=forgenre&tag=%s&genre=%s"\
                % (self.options["tag"], genre_json["label"])
        genre_json["isFolder"] = True
        genre_json["IsPlayable"] = "false"
        genre_json["thumbnail"] = genre_json.get("thumbnail",
                                                 "DefaultGenre.png")  # TODO: get icon from resource addon ?
        genre_json["type"] = "genre"
        sort = kodi_constants.SORT_RANDOM if self.options.get("random") else kodi_constants.SORT_TITLE
        genre_movies = self.get_genre_movies(genre_json["label"], False, 5, sort)
        if not genre_movies:
            return None
        for count, genre_movie in enumerate(genre_movies):
            genre_json["art"]["poster.%s" % count] = genre_movie["art"].get("poster", "")
            genre_json["art"]["fanart.%s" % count] = genre_movie["art"].get("fanart", "")
            if "fanart" not in genre_json["art"]:
                # set genre's primary fanart image to first movie fanart
                genre_json["art"]["fanart"] = genre_movie["art"].get("fanart", "")
        return genre_json

    def get_random_watched_movie(self):
        '''gets a random watched movie from kodi_constants.'''
        movies = self.metadatautils.kodidb.movies(sort=kodi_constants.SORT_RANDOM,
                                                  filters=[kodi_constants.FILTER_WATCHED],
                                                  limits=(0, 1))
        if movies:
            return movies[0]
        return None

    def get_recently_watched_movie(self):
        '''gets a random recently watched movie from kodi_constants.'''
        num_recent_similar = self.options["num_recent_similar"]
        movies = self.metadatautils.kodidb.movies(sort=kodi_constants.SORT_LASTPLAYED,
                                                  filters=[kodi_constants.FILTER_WATCHED],
                                                  limits=(0, num_recent_similar))
        if movies:
            return random.choice(movies)
        return None

    def get_genre_movies(self, genre, hide_watched=False, limit=100, sort=kodi_constants.SORT_RANDOM):
        '''helper method to get all movies in a specific genre'''
        filters = [{"operator": "is", "field": "genre", "value": genre}]
        if self.options.get("tag"):
            filters.append({"operator": "contains", "field": "tag", "value": self.options["tag"]})
        if hide_watched:
            filters.append(kodi_constants.FILTER_UNWATCHED)
        return self.metadatautils.kodidb.movies(sort=sort, filters=filters, limits=(0, limit))

    def favourites(self):
        '''get favourites'''
        from favourites import Favourites
        self.options["mediafilter"] = "movies"
        return Favourites(self.addon, self.metadatautils, self.options).favourites()

    def favourite(self):
        '''synonym to favourites'''
        return self.favourites()

    def sort_by_recommended(self, all_items, ref_movies=None):
        ''' sort list of movies by recommended score'''
        if not ref_movies:
            # get recently watched movies
            ref_movies = self.metadatautils.kodidb.movies(sort=kodi_constants.SORT_LASTPLAYED,
                                                          filters=[kodi_constants.FILTER_WATCHED],
                                                          limits=(0, self.options["num_recent_similar"]))
        # predefine feature sets
        ref_sets = dict()
        for ref_movie in ref_movies:
            title = ref_movie['title']
            set_genres = set(ref_movie["genre"])
            set_directors = set(ref_movie["director"])
            set_writers = set(ref_movie["writer"])
            set_cast = set([x["name"] for x in ref_movie["cast"][:5]])
            ref_sets[title] = (set_genres, set_directors, set_writers, set_cast)
        # average scores together for every item
        for item in all_items:
            similarscore = 0
            for ref_movie in ref_movies:
                title = ref_movie['title']
                similarscore += self.get_similarity_score(ref_movie, item, sets=ref_sets[title])
            item["recommendedscore"] = similarscore // (1+item["playcount"]) // len(ref_movies)
        # return list sorted by score and capped by limit
        return sorted(all_items, key=itemgetter("recommendedscore"), reverse=True)[:self.options["limit"]]

    @staticmethod
    def get_similarity_score(ref_movie, other_movie, sets=None):
        '''
            get a similarity score (0-1) between two movies
            optional parameters should be calculated beforehand if called inside loop
            TODO: make a database of ratings
        '''
        if sets:
            # unpack sets if given
            set_genres, set_directors, set_writers, set_cast = sets
        else:
            # define sets
            set_genres = set(ref_movie["genre"])
            set_directors = set(ref_movie["director"])
            set_writers = set(ref_movie["writer"])
            set_cast = set([x["name"] for x in ref_movie["cast"][:5]])
        # calculate individual scores for contributing factors
        # [feature]_score = (numer of matching [features]) / (number of unique [features] between both)
        genre_score = 0 if not set_genres else \
            float(len(set_genres.intersection(other_movie["genre"]))) // \
            len(set_genres.union(other_movie["genre"]))
        director_score = 0 if not set_directors else \
            float(len(set_directors.intersection(other_movie["director"]))) // \
            len(set_directors.union(other_movie["director"]))
        writer_score = 0 if not set_writers else \
            float(len(set_writers.intersection(other_movie["writer"]))) // \
            len(set_writers.union(other_movie["writer"]))
        # cast_score is normalized by fixed amount of 5, and scaled up nonlinearly
        cast_score = (float(len(set_cast.intersection([x["name"] for x in other_movie["cast"][:5]])))//5)**(1.//2)
        # rating_score is "closeness" in rating, scaled to 1 (0 if greater than 3)
        if ref_movie["rating"] and other_movie["rating"] and abs(ref_movie["rating"]-other_movie["rating"]) < 3:
            rating_score = 1 - abs(ref_movie["rating"]-other_movie["rating"])//3
        else:
            rating_score = 0
        # year_score is "closeness" in release year, scaled to 1 (0 if not from same decade)
        if ref_movie["year"] and other_movie["year"] and abs(ref_movie["year"]-other_movie["year"]) < 10:
            year_score = 1 - abs(ref_movie["year"]-other_movie["year"])//10
        else:
            year_score = 0
        # mpaa_score gets 1 if same mpaa rating, otherwise 0
        mpaa_score = 1 if ref_movie["mpaa"] and ref_movie["mpaa"] == other_movie["mpaa"] else 0
        # calculate overall score using weighted average
        similarscore = .5*genre_score + .15*director_score + .1*writer_score + .1*cast_score + \
            .05*rating_score + .075*year_score + .025*mpaa_score
        # exponentially scale score for movies in same set
        if ref_movie["setid"] and ref_movie["setid"] == other_movie["setid"]:
            similarscore **= (1.//2)
        return similarscore
