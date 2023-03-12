#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    script.skin.helper.widgets
    media.py
    all media (mixed) widgets provided by the script
'''

from operator import itemgetter
import random
from metadatautils import kodi_constants
from resources.lib.utils import create_main_entry
from resources.lib.movies import Movies
from resources.lib.tvshows import Tvshows
from resources.lib.songs import Songs
from resources.lib.pvr import Pvr
from resources.lib.albums import Albums
from resources.lib.episodes import Episodes

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
            (self.addon.getLocalizedString(32079), "inprogressepisodesandmovies&mediatype=media", "DefaultMovies.png"),
            (self.addon.getLocalizedString(32005), "recent&mediatype=media", "DefaultMovies.png"),
            (self.addon.getLocalizedString(32004), "recommended&mediatype=media", "DefaultMovies.png"),
            (self.addon.getLocalizedString(32007), "inprogressandrecommended&mediatype=media", "DefaultMovies.png"),
            (self.addon.getLocalizedString(32060), "inprogressandrandom&mediatype=media", "DefaultMovies.png"),
            (self.addon.getLocalizedString(32022), "similar&mediatype=media", "DefaultMovies.png"),
            (self.addon.getLocalizedString(32080), "similarmoviestvshows&mediatype=media", "DefaultMovies.png"),
            (self.addon.getLocalizedString(32059), "random&mediatype=media", "DefaultMovies.png"),
            (self.addon.getLocalizedString(32058), "top250&mediatype=media", "DefaultMovies.png"),
            (self.addon.getLocalizedString(32001), "favourites&mediatype=media", "DefaultMovies.png"),
            (self.addon.getLocalizedString(32075), "playlistslisting&mediatype=media",
             "DefaultMovies.png"),
            (self.addon.getLocalizedString(32077), "playlistslisting&mediatype=media&tag=ref",
             "DefaultMovies.png")
        ]
        return self.metadatautils.process_method_on_list(create_main_entry, all_items)

    def playlistslisting(self):
        '''get tv playlists listing'''
        #TODO: append (Movie playlist) and (TV Show Playlist)
        #TODO: only show playlists with appropriate type (Movie or TV Show)
        movie_label = self.options.get("movie_label")
        tag_label = self.options.get("tag")
        all_items = []
        for item in self.metadatautils.kodidb.files("special://videoplaylists/"):
            # replace '&' with [and] -- will get fixed when processed in playlist action
            label = item["label"].replace('&', '[and]')
            if tag_label == 'ref':
                if movie_label:
                    details = (item["label"], "refplaylist&mediatype=media&movie_label=%s&tv_label=%s" %
                               (movie_label, label), "DefaultTvShows.png")
                else:
                    details = (item["label"], "playlistslisting&mediatype=media&tag=ref&movie_label=%s" % label,
                               "DefaultMovies.png")
            else:
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
        movie_label = self.options.get("movie_label").replace('[and]', '&')
        tv_label = self.options.get("tv_label").replace('[and]', '&')
        movies = self.metadatautils.kodidb.movies(
            filters=[{"operator": "is", "field": "playlist", "value": movie_label}])
        tvshows = self.metadatautils.kodidb.tvshows(
            filters=[{"operator": "is", "field": "playlist", "value": tv_label}])
        tvshows = self.metadatautils.process_method_on_list(self.tvshows.process_tvshow, tvshows)
        all_items = self.sort_by_recommended(movies+tvshows)
        return sorted(all_items, key=itemgetter("recommendedscore"), reverse=True)[:self.options["limit"]]

    def refplaylist(self):
        '''get items similar to items in playlists '''
        movie_label = self.options.get("movie_label").replace('[and]', '&')
        tv_label = self.options.get("tv_label").replace('[and]', '&')
        ref_movies = self.metadatautils.kodidb.movies(
            filters=[{"operator": "is", "field": "playlist", "value": movie_label}])
        ref_tvshows = self.metadatautils.kodidb.tvshows(
            filters=[{"operator": "is", "field": "playlist", "value": tv_label}])
        movies = self.metadatautils.kodidb.movies(
            filters=[{"operator": "isnot", "field": "playlist", "value": movie_label}])
        tvshows = self.metadatautils.kodidb.tvshows(
            filters=[{"operator": "isnot", "field": "playlist", "value": tv_label}])
        tvshows = self.metadatautils.process_method_on_list(self.tvshows.process_tvshow, tvshows)
        all_items = self.sort_by_recommended(movies+tvshows, ref_movies+ref_tvshows)
        return sorted(all_items, key=itemgetter("recommendedscore"), reverse=True)[:self.options["limit"]]

    def recommended(self):
        ''' get recommended media '''
        if self.options["exp_recommended"]:
            # get all unwatched, not in-progess movies & tvshows
            movies = self.metadatautils.kodidb.movies(filters=[kodi_constants.FILTER_UNWATCHED])
            tvshows = self.metadatautils.kodidb.tvshows(filters=[kodi_constants.FILTER_UNWATCHED])
            tvshows = self.metadatautils.process_method_on_list(self.tvshows.process_tvshow, tvshows)
            # return list sorted by recommended score, and capped by limit
            return self.sort_by_recommended(movies+tvshows)
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

    def inprogressepisodesandmovies(self):
        ''' get in progress media '''
        all_items = self.movies.inprogress()
        all_items += self.episodes.inprogress()
        return sorted(all_items, key=itemgetter("lastplayed"), reverse=True)[:self.options["limit"]]


    def inprogressshowsandmovies(self):
        ''' get in progress media '''
        all_items = self.tvshows.inprogress()
        all_items += self.movies.inprogress()
        return sorted(all_items, key=itemgetter("lastplayed"), reverse=True)[:self.options["limit"]]

    def similar(self):
        ''' get similar movies and similar tvshows for given imdbid'''
        all_items = self.movies.similar()
        all_items += self.tvshows.similar()
        all_items += self.albums.similar()
        all_items += self.songs.similar()
        return sorted(all_items, key=lambda k: random.random())[:self.options["limit"]]

    def similarmoviestvshows(self):
        ''' get similar movies and similar tvshows for given imdbid'''
        all_items = self.movies.similar()
        all_items += self.tvshows.similar()
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
        all_ids = [item["title"] for item in all_items]
        for item in self.random():
            if item["title"] not in all_ids:
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
        num_recent_similar = self.options["num_recent_similar"]
        # get recently played movies
        recent_items = self.metadatautils.kodidb.movies(sort=kodi_constants.SORT_LASTPLAYED,
                                                        filters=[kodi_constants.FILTER_WATCHED],
                                                        limits=(0, num_recent_similar))
        # get recently played episodes
        recent_items += self.metadatautils.kodidb.episodes(sort=kodi_constants.SORT_LASTPLAYED,
                                                           filters=[kodi_constants.FILTER_WATCHED],
                                                           limits=(0, num_recent_similar))
        # sort all by last played, then randomly pick
        recent_items = sorted(recent_items, key=itemgetter("lastplayed"), reverse=True)[:num_recent_similar]
        item = random.choice(recent_items)
        # if item is an episode, get its tvshow
        if not ("genre"):
            show_title = item['showtitle']
            title_filter = [{"field": "title", "operator": "is", "value": "%s" % show_title}]
            tvshow = self.metadatautils.kodidb.tvshows(filters=title_filter, limits=(0, 1))
            return tvshow[0]
        return item

    def sort_by_recommended(self, all_items, ref_items=None):
        ''' sort list of mixed movies/tvshows by recommended score'''
        # use recent items if ref_items not given
        if not ref_items:
            num_recent_similar = self.options["num_recent_similar"]
            # get recently watched movies
            movies = self.metadatautils.kodidb.movies(sort=kodi_constants.SORT_LASTPLAYED,
                                                      filters=[kodi_constants.FILTER_WATCHED],
                                                      limits=(0, 2*num_recent_similar))
            # get recently watched episodes
            episodes = self.metadatautils.kodidb.episodes(sort=kodi_constants.SORT_LASTPLAYED,
                                                          filters=[kodi_constants.FILTER_WATCHED],
                                                          limits=(0, 2*num_recent_similar))
            # get tvshows from episodes
            tvshows = self.tvshows.get_tvshows_from_episodes(episodes)
            # combine lists and sort by last played recent
            items = sorted(movies + tvshows, key=itemgetter('lastplayed'), reverse=True)
            # find duplicates and set weights
            titles = set()
            ref_items = list()
            weights = dict()
            weight_sum = 0
            for item in items:
                title = item['title']
                if title in titles:
                    weights[title] += 0.5
                    weight_sum += 0.5
                else:
                    ref_items.append(item)
                    titles.add(title)
                    weights[title] = 1
                    weight_sum += 1
                if weight_sum >= num_recent_similar:
                    break
            del titles, items, weight_sum
        else:
            # set equal weights for pre-defined ref_items
            weights = dict()
            for item in ref_items:
                weights[item['title']] = 1
        # average scores together for every item
        for item in all_items:
            similarscore = 0
            for ref_item in ref_items:
                title = ref_item['title']
                # add all similarscores for item
                if ("uniqueid")in ref_item and ("uniqueid") in item:
                    # use movies method if both items are movies
                    similarscore += weights[title] * self.movies.get_similarity_score(ref_item, item)
                elif ("uniqueid")in  ref_item or ("uniqueid") in item:
                    # use media method if only one item is a movie
                    similarscore += weights[title] * self.get_similarity_score(ref_item, item)
                else:
                    # use tvshows method if neither items are movies
                    similarscore += weights[title] * self.tvshows.get_similarity_score(ref_item, item)
            # average score and scale down based on playcount
            item["recommendedscore"] = similarscore / (1+item["playcount"]) / len(ref_items)
        # return sorted list capped by limit
        return sorted(all_items, key=itemgetter("recommendedscore"), reverse=True)[:self.options["limit"]]

    def get_similarity_score(self, ref_item, other_item):
        '''
            get a similarity score (0-.625) between movie and tvshow
        '''
        # get set of genres
        if ("uniqueid") in ref_item:
            set_genres = set(ref_item["genre"])
        else:
            # change genres to movie equivalents if tvshow
            set_genres = self.convert_tvshow_genres(ref_item["genre"])
        set_cast = set([x["name"] for x in ref_item["cast"][:5]])
        # calculate individual scores for contributing factors
        # genre_score = (numer of matching genres) / (number of unique genres between both)
        genre_score = 0 if not set_genres else \
            float(len(set_genres.intersection(other_item["genre"]))) / \
            len(set_genres.union(other_item["genre"]))
        # cast_score is normalized by fixed amount of 5, and scaled up nonlinearly
        cast_score = (float(len(set_cast.intersection([x["name"] for x in other_item["cast"][:5]])))/5)**(1./2)
        # rating_score is "closeness" in rating, scaled to 1
        if ref_item["rating"] and other_item["rating"] and abs(ref_item["rating"]-other_item["rating"]) < 3:
            rating_score = 1 - abs(ref_item["rating"]-other_item["rating"])/3
        else:
            rating_score = 0
        # year_score is "closeness" in release year, scaled to 1 (0 if not from same decade)
        if ref_item["year"] and other_item["year"] and abs(ref_item["year"]-other_item["year"]) < 10:
            year_score = 1 - abs(ref_item["year"]-other_item["year"])/10
        else:
            year_score = 0
        # calculate overall score using weighted average
        similarscore = .5*genre_score + .05*cast_score + .025*rating_score + .05*year_score
        return similarscore

    @staticmethod
    def convert_tvshow_genres(genres):
        ''' converts tvshow genres into movie genre equivalent '''
        mapped_genres = {'TV Documentaries': 'Documentary',
                         'TV Sci-Fi & Fantasy': 'Sci-Fi & Fantasy',
                         'TV Action & Adventure': 'Action & Adventure',
                         'TV Comedies': 'Comedy',
                         'TV Mysteries': 'Mystery',
                         'TV Westerns': 'Westerns',
                         'TV Dramas': 'Drama',
                         'TV Crime Dramas': 'Crime Dramas',
                        }
        for genre in genres:
            if (genre) in mapped_genres:
                genre = mapped_genres[genre]
        return set(genres)
