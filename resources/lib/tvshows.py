#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    script.skin.helper.widgets
    tvshows.py
    all tvshows widgets provided by the script
'''

from operator import itemgetter
import random
import xbmc
from metadatautils import kodi_constants
from resources.lib.utils import create_main_entry, KODI_VERSION, log_msg

class Tvshows(object):
    '''all tvshow widgets provided by the script'''

    def __init__(self, addon, metadatautils, options):
        '''Initializations pass our common classes and the widget options as arguments'''
        self.metadatautils = metadatautils
        self.addon = addon
        self.options = options

    def listing(self):
        '''main listing with all our tvshow nodes'''
        tag = self.options.get("tag", "")
        if tag:
            label_prefix = u"%s - " % tag
        else:
            label_prefix = u""
        icon = "DefaultTvShows.png"
        all_items = [
            (label_prefix + self.addon.getLocalizedString(32044), "inprogress&mediatype=tvshows&tag=%s" % tag, icon),
            (label_prefix + self.addon.getLocalizedString(32045), "recent&mediatype=tvshows&tag=%s" % tag, icon),
            (label_prefix + self.addon.getLocalizedString(32037), "recommended&mediatype=tvshows&tag=%s" % tag, icon),
            (label_prefix + self.addon.getLocalizedString(32041), "random&mediatype=tvshows&tag=%s" % tag, icon),
            (label_prefix + self.addon.getLocalizedString(32047), "top250&mediatype=tvshows&tag=%s" % tag, icon),
            (label_prefix + xbmc.getLocalizedString(135), "browsegenres&mediatype=tvshows&tag=%s" % tag, icon),
        ]
        if not tag:
            all_items += [
                (self.addon.getLocalizedString(32014), "similar&mediatype=tvshows", icon),
                (xbmc.getLocalizedString(10134), "favourites&mediatype=tvshows", icon),
                (self.addon.getLocalizedString(32078), "playlistslisting&mediatype=tvshows", icon),
                (self.addon.getLocalizedString(32076), "playlistslisting&mediatype=tvshows&tag=ref", icon),
                (xbmc.getLocalizedString(20459), "tagslisting&mediatype=tvshows", icon)
            ]
        if tag:
            # add episode nodes with tag filter
            all_items += [
                (label_prefix + self.addon.getLocalizedString(32027), "inprogress&mediatype=episodes&tag=%s" %
                 tag, icon),
                (label_prefix + self.addon.getLocalizedString(32039), "recent&mediatype=episodes&tag=%s" %
                 tag, icon),
                (label_prefix + self.addon.getLocalizedString(32002), "next&mediatype=episodes&tag=%s" %
                 tag, icon),
                (label_prefix + self.addon.getLocalizedString(32008), "random&mediatype=episodes&tag=%s" %
                 tag, icon)]
        return self.metadatautils.process_method_on_list(create_main_entry, all_items)

    def tagslisting(self):
        '''get tags listing'''
        all_items = []
        for item in self.metadatautils.kodidb.files("videodb://tvshows/tags"):
            details = (item["label"], "listing&mediatype=tvshows&tag=%s" % item["label"], "DefaultTags.png")
            all_items.append(create_main_entry(details))
        return all_items

    def playlistslisting(self):
        '''get playlists listing'''
        all_items = []
        for item in self.metadatautils.kodidb.files("special://videoplaylists/"):
            # replace '&' with [and] -- will get fixed when processed in playlist action
            tag_label = item["label"].replace('&', '[and]')
            if self.options.get("tag") == 'ref':
                details = (item["label"], "refplaylist&mediatype=tvshows&tag=%s" % tag_label, "DefaultTvShows.png")
            else:
                details = (item["label"], "playlist&mediatype=tvshows&tag=%s" % tag_label, "DefaultTvShows.png")
            all_items.append(create_main_entry(details))
        return all_items

    def playlist(self):
        '''get items in playlist, sorted by recommended score'''
        # fix ampersand in tag_label
        tag_label = self.options.get("tag").replace('[and]', '&')
        # get all items in playlist
        filters = [{"operator": "is", "field": "playlist", "value": tag_label}]
        all_items = self.metadatautils.kodidb.tvshows(filters=filters)
        # return list sorted by recommended score
        all_items = self.sort_by_recommended(all_items)
        return self.metadatautils.process_method_on_list(self.process_tvshow, all_items)

    def refplaylist(self):
        '''get items similar to items in ref playlist'''
        # fix ampersand in tag_label
        tag_label = self.options.get("tag").replace('[and]', '&')
        # get all items in playlist
        playlist_filter = [{"operator": "is", "field": "playlist", "value": tag_label}]
        ref_items = self.metadatautils.kodidb.tvshows(filters=playlist_filter)
        # get all items not in playlist
        not_playlist_filter = [{"operator": "isnot", "field": "playlist", "value": tag_label}]
        all_items = self.metadatautils.kodidb.tvshows(filters=not_playlist_filter)
        # return list sorted by recommended score
        all_items = self.sort_by_recommended(all_items, ref_items)
        return self.metadatautils.process_method_on_list(self.process_tvshow, all_items)

    def recommended(self):
        ''' get recommended tvshows - library tvshows with score higher than 7
        or if using experimental settings - similar with all recently watched '''
        if self.options["exp_recommended"]:
            # get list of all unwatched movies (optionally filtered by tag)
            filters = [kodi_constants.FILTER_UNWATCHED]
            if self.options.get("tag"):
                filters.append({"operator": "contains", "field": "tag", "value": self.options["tag"]})
            all_items = self.metadatautils.kodidb.tvshows(filters=filters, filtertype='and')
            all_items = self.sort_by_recommended(all_items)
            # return processed show
            return self.metadatautils.process_method_on_list(self.process_tvshow, all_items)
        else:
            filters = [kodi_constants.FILTER_RATING]
            if self.options["hide_watched"]:
                filters.append(kodi_constants.FILTER_UNWATCHED)
            if self.options.get("tag"):
                filters.append({"operator": "contains", "field": "tag", "value": self.options["tag"]})
            tvshows = self.metadatautils.kodidb.tvshows(
                sort=kodi_constants.SORT_RATING, filters=filters, limits=(
                    0, self.options["limit"]))
            return self.metadatautils.process_method_on_list(self.process_tvshow, tvshows)

    def recent(self):
        ''' get recently added tvshows '''
        filters = []
        if self.options["hide_watched"]:
            filters.append(kodi_constants.FILTER_UNWATCHED)
        if self.options.get("tag"):
            filters.append({"operator": "contains", "field": "tag", "value": self.options["tag"]})
        tvshows = self.metadatautils.kodidb.tvshows(
            sort=kodi_constants.SORT_DATEADDED, filters=filters, limits=(
                0, self.options["limit"]))
        return self.metadatautils.process_method_on_list(self.process_tvshow, tvshows)

    def random(self):
        ''' get random tvshows '''
        filters = []
        if self.options.get("tag"):
            filters.append({"operator": "contains", "field": "tag", "value": self.options["tag"]})
        tvshows = self.metadatautils.kodidb.tvshows(
            sort=kodi_constants.SORT_RANDOM, filters=filters, limits=(
                0, self.options["limit"]))
        return self.metadatautils.process_method_on_list(self.process_tvshow, tvshows)

    def inprogress(self):
        ''' get in progress tvshows '''
        filters = [kodi_constants.FILTER_INPROGRESS]
        if self.options.get("tag"):
            filters.append({"operator": "contains", "field": "tag", "value": self.options["tag"]})
        tvshows = self.metadatautils.kodidb.tvshows(
            sort=kodi_constants.SORT_LASTPLAYED, filters=filters, limits=(
                0, self.options["limit"]))
        return self.metadatautils.process_method_on_list(self.process_tvshow, tvshows)

    def similar(self):
        ''' get similar shows for given imdbid, or from a recently watched title if no imdbid'''
        imdb_id = self.options.get("imdbid", "")
        ref_show = None
        if imdb_id:
            # get movie from imdb_id if found
            ref_show = self.metadatautils.kodidb.tvshow_by_imdbid(imdb_id)
        if not ref_show:
            # pick a random recently watched tvshow (for homescreen widget)
            ref_show = self.get_recently_watched_tvshow()
            # use hide_watched setting for homescreen widget only
            hide_watched = self.options["hide_watched_similar"]
        else:
            # don't hide watched otherwise
            hide_watched = False
        if not ref_show:
            return None
        # define ref_show sets for speed
        set_genres = set(ref_show["genre"])
        set_cast = set([x["name"] for x in ref_show["cast"][:10]])
        sets = (set_genres, set_cast)
        # create list of all items
        if hide_watched:
            filters = [kodi_constants.FILTER_UNWATCHED]
            all_items = self.metadatautils.kodidb.tvshows(filters=filters)
        else:
            all_items = self.metadatautils.kodidb.tvshows()
        # get similarity score for all shows
        for item in all_items:
            if item["title"] == ref_show["title"] and item["year"] == ref_show["year"]:
                # don't rank the reference show
                similarscore = 0
            else:
                similarscore = self.get_similarity_score(ref_show, item, sets=sets)
            item["similarscore"] = similarscore
            item["extraproperties"] = {"similartitle": ref_show["title"], "originalpath": item["file"]}
        # sort list by score and cap by limit
        tvshows = sorted(all_items, key=itemgetter("similarscore"), reverse=True)[:self.options["limit"]]
        # return processed show
        return self.metadatautils.process_method_on_list(self.process_tvshow, tvshows)

    def forgenre(self):
        ''' get top rated tvshows for given genre'''
        genre = self.options.get("genre", "")
        all_items = []
        if not genre:
            # get a random genre if no genre provided
            json_result = self.metadatautils.kodidb.genres("tvshow")
            if json_result:
                genre = json_result[0]["label"]
        if genre:
            # get all tvshows from the same genre
            for item in self.get_genre_tvshows(genre, self.options["hide_watched"], self.options["limit"]):
                # append original genre as listitem property for later reference by skinner
                item["extraproperties"] = {"genretitle": genre, "originalpath": item["file"]}
                all_items.append(item)
        # return the list sorted by rating
        tvshows = sorted(all_items, key=itemgetter("rating"), reverse=True)
        return self.metadatautils.process_method_on_list(self.process_tvshow, tvshows)

    def top250(self):
        ''' get imdb top250 tvshows in library '''
        all_items = []
        filters = []
        if self.options.get("tag"):
            filters.append({"operator": "contains", "field": "tag", "value": self.options["tag"]})
        fields = ["imdbnumber"]
        if KODI_VERSION > 16:
            fields.append("uniqueid")
        all_tvshows = self.metadatautils.kodidb.get_json(
            'VideoLibrary.GetTvShows', fields=fields, returntype="tvshows", filters=filters)
        top_250 = self.metadatautils.imdb.get_top250_db()
        for tvshow in all_tvshows:
            # grab imdbid
            imdbnumber = tvshow["imdbnumber"]
            if not imdbnumber and "uniqueid" in tvshow:
                for value in tvshow["uniqueid"]:
                    if value.startswith("tt"):
                        imdbnumber = value
            if imdbnumber and not imdbnumber.startswith("tt"):
                # we have a tvdb id
                tvdb_info = self.metadatautils.thetvdb.get_series(imdbnumber)
                if tvdb_info:
                    imdbnumber = tvdb_info["imdbnumber"]
                else:
                    imdbnumber = None
            if imdbnumber and imdbnumber in top_250:
                tvshow_full = self.metadatautils.kodidb.tvshow(tvshow["tvshowid"])
                tvshow_full["top250_rank"] = int(top_250[imdbnumber])
                all_items.append(tvshow_full)
        tvshows = sorted(all_items, key=itemgetter("top250_rank"))[:self.options["limit"]]
        return self.metadatautils.process_method_on_list(self.process_tvshow, tvshows)

    def browsegenres(self):
        '''
            special entry which can be used to create custom genre listings
            returns each genre with poster/fanart artwork properties from 5
            random tvshows in the genre.
            TODO: get auto generated collage pictures from skinhelper's metadatautils ?
        '''
        all_genres = self.metadatautils.kodidb.genres("tvshow")
        return self.metadatautils.process_method_on_list(self.get_genre_artwork, all_genres)

    def get_genre_artwork(self, genre_json):
        '''helper method for browsegenres'''
        # for each genre we get 5 random items from the library and attach the artwork to the genre listitem
        genre_json["art"] = {}
        genre_json["file"] = "videodb://tvshows/genres/%s/" % genre_json["genreid"]
        if self.options.get("tag"):
            genre_json["file"] = "plugin://script.skin.helper.widgets?"\
                "mediatype=tvshows&action=forgenre&tag=%s&genre=%s" % (self.options["tag"], genre_json["label"])
        genre_json["isFolder"] = True
        genre_json["IsPlayable"] = "false"
        genre_json["thumbnail"] = genre_json.get("thumbnail",
                                                 "DefaultGenre.png")  # TODO: get icon from resource addon ?
        genre_json["type"] = "genre"
        sort = kodi_constants.SORT_RANDOM if self.options.get("random") else kodi_constants.SORT_TITLE
        genre_tvshows = self.get_genre_tvshows(genre_json["label"], False, 5, sort)
        if not genre_tvshows:
            return None
        for count, genre_tvshow in enumerate(genre_tvshows):
            genre_json["art"]["poster.%s" % count] = genre_tvshow["art"].get("poster", "")
            genre_json["art"]["fanart.%s" % count] = genre_tvshow["art"].get("fanart", "")
            if "fanart" not in genre_json["art"]:
                # set genre's primary fanart image to first movie fanart
                genre_json["art"]["fanart"] = genre_tvshow["art"].get("fanart", "")
        return genre_json

    def nextaired(self):
        '''legacy method: get nextaired episodes instead'''
        from episodes import Episodes
        eps = Episodes(self.addon, self.metadatautils.kodidb, self.options)
        result = eps.nextaired()
        del eps
        return result

    def get_random_watched_tvshow(self):
        '''gets a random watched or inprogress tvshow from kodi_constants.'''
        filters = [kodi_constants.FILTER_WATCHED, kodi_constants.FILTER_INPROGRESS]
        tvshows = self.metadatautils.kodidb.tvshows(
            sort=kodi_constants.SORT_RANDOM,
            filters=filters,
            filtertype="or",
            limits=(0, 1))
        if tvshows:
            return tvshows[0]
        return None

    def get_recently_watched_tvshow(self):
        ''' returns the tvshow of a recently watched episode '''
        num_recent_similar = self.options["num_recent_similar"]
        episodes = self.metadatautils.kodidb.episodes(sort=kodi_constants.SORT_LASTPLAYED,
                                                      filters=[kodi_constants.FILTER_WATCHED],
                                                      limits=(0, num_recent_similar))
        if episodes:
            show_title = random.choice(episodes)['showtitle']
            title_filter = [{"field": "title", "operator": "is", "value": "%s" % show_title}]
            tvshow = self.metadatautils.kodidb.tvshows(filters=title_filter, limits=(0, 1))
            return tvshow[0]
        return None

    def get_genre_tvshows(self, genre, hide_watched=False, limit=100, sort=kodi_constants.SORT_RANDOM):
        '''helper method to get all tvshows in a specific genre'''
        filters = [{"operator": "is", "field": "genre", "value": genre}]
        if hide_watched:
            filters.append(kodi_constants.FILTER_UNWATCHED)
        if self.options.get("tag"):
            filters.append({"operator": "contains", "field": "tag", "value": self.options["tag"]})
        return self.metadatautils.kodidb.tvshows(sort=sort, filters=filters, limits=(0, limit))

    @staticmethod
    def process_tvshow(item):
        '''set optional details to tvshow item'''
        item["file"] = "videodb://tvshows/titles/%s" % item["tvshowid"]
        item["isFolder"] = True
        return item

    def favourites(self):
        '''get favourites'''
        from favourites import Favourites
        self.options["mediafilter"] = "tvshows"
        return Favourites(self.addon, self.metadatautils, self.options).favourites()

    def favourite(self):
        '''synonym to favourites'''
        return self.favourites()

    def get_tvshows_from_episodes(self, episodes):
        ''' gets associated tvshows from episodes (includes duplicates) '''
        tvshows = []
        for episode in episodes:
            show_title = episode['showtitle']
            title_filter = [{"field": "title", "operator": "is", "value": show_title}]
            tvshow = self.metadatautils.kodidb.tvshows(filters=title_filter, limits=(0, 1))[0]
            tvshows.append(tvshow)
        return tvshows

    def sort_by_recommended(self, all_items, ref_shows=None):
        ''' sort list of tvshows by recommended score'''
        # use recent items if ref_items not given
        if not ref_shows:
            # get recently watched episodes
            num_recent_similar = self.options["num_recent_similar"]
            episodes = self.metadatautils.kodidb.episodes(sort=kodi_constants.SORT_LASTPLAYED,
                                                          filters=[kodi_constants.FILTER_WATCHED],
                                                          limits=(0, 2*num_recent_similar))
            # get tvshows from episodes
            tvshows = self.get_tvshows_from_episodes(episodes)
            # combine lists and sort by last played recent
            items = sorted(tvshows, key=itemgetter('lastplayed'), reverse=True)
            # find duplicates and set weights
            titles = set()
            ref_shows = list()
            weights = dict()
            weight_sum = 0
            for item in items:
                title = item['title']
                if title in titles:
                    weights[title] += 0.5
                    weight_sum += 0.5
                else:
                    ref_shows.append(item)
                    titles.add(title)
                    weights[title] = 1
                    weight_sum += 1
                if weight_sum >= num_recent_similar:
                    break
            del titles, items, weight_sum
        else:
            # set equal weights for pre-defined ref_shows
            weights = dict()
            for item in ref_shows:
                weights[item['title']] = 1
        # predefine feature sets
        ref_sets = dict()
        for ref_show in ref_shows:
            title = ref_show['title']
            set_genres = set(ref_show["genre"])
            set_cast = set([x["name"] for x in ref_show["cast"][:10]])
            ref_sets[title] = (set_genres, set_cast)
        # average scores together for every item
        for item in all_items:
            similarscore = 0
            for ref_show in ref_shows:
                title = ref_show['title']
                similarscore += weights[title] * self.get_similarity_score(
                    ref_show, item, sets=ref_sets[title])
            item["recommendedscore"] = similarscore / (1+item["playcount"]) / len(ref_shows)
        # return sorted list capped by limit
        return sorted(all_items, key=itemgetter("recommendedscore"), reverse=True)[:self.options["limit"]]

    @staticmethod
    def get_similarity_score(ref_show, other_show, sets=None):
        '''
            get a similarity score (0-1) between two shows
            optional parameters should be calculated beforehand if called inside loop
            TODO: make a database of ratings
        '''
        # assign arguments not given
        if sets:
            set_genres, set_cast = sets
        else:
            set_genres = set(ref_show["genre"])
            set_cast = set([x["name"] for x in ref_show["cast"][:10]])
        # calculate individual scores for contributing factors
        # genre_score = (numer of matching genres) / (number of unique genres between both)
        genre_score = 0 if not set_genres else \
            float(len(set_genres.intersection(other_show["genre"]))) / \
            len(set_genres.union(other_show["genre"]))
        # cast_score is normalized by fixed amount of 10, and scaled up nonlinearly
        cast_score = (float(len(set_cast.intersection([x["name"] for x in other_show["cast"][:10]])))/10)**(1./2)
        # rating_score is "closeness" in rating, scaled to 1
        if ref_show["rating"] and other_show["rating"] and abs(ref_show["rating"]-other_show["rating"]) < 3:
            rating_score = 1-abs(ref_show["rating"]-other_show["rating"])/3
        else:
            rating_score = 0
        # year_score is "closeness" in release year, scaled to 1 (0 if not from same decade)
        if ref_show["year"] and other_show["year"] and abs(ref_show["year"]-other_show["year"]) < 10:
            year_score = 1-abs(ref_show["year"]-other_show["year"])/10
        else:
            year_score = 0
        # studio gets 1 if same studio, otherwise 0
        studio_score = 1 if ref_show["studio"] and ref_show["studio"] == other_show["studio"] else 0
        # mpaa_score gets 1 if same mpaa rating, otherwise 0
        mpaa_score = 1 if ref_show["mpaa"] and ref_show["mpaa"] == other_show["mpaa"] else 0
        # calculate overall score using weighted average
        similarscore = .5*genre_score + .05*studio_score + .35*cast_score + \
            .025*rating_score + .05*year_score + .025*mpaa_score
        return similarscore
