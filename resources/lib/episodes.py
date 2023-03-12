#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    script.skin.helper.widgets
    episodes.py
    all episodes widgets provided by the script
'''
import os, sys
from operator import itemgetter
import xbmc
from metadatautils import kodi_constants
from resources.lib.utils import create_main_entry,log_msg

class Episodes(object):
    '''all episode widgets provided by the script'''
    options = {}
    kodidb = None
    addon = None

    def __init__(self, addon, metadatautils, options):
        '''Initialization'''
        self.addon = addon
        self.metadatautils = metadatautils
        options["next_inprogress_only"] = self.addon.getSetting("nextup_inprogressonly") == "true"
        options["episodes_enable_specials"] = self.addon.getSetting("episodes_enable_specials") == "true"
        options["group_episodes"] = self.addon.getSetting("episodes_grouping") == "true"
        self.options = options

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
            (self.addon.getLocalizedString(32068), "airingtoday&mediatype=episodes", "DefaultTvShows.png"),
            (xbmc.getLocalizedString(10134), "favourites&mediatype=episodes", "DefaultMovies.png")
        ]
        return self.metadatautils.process_method_on_list(create_main_entry, all_items)

    def favourites(self):
        '''get favourites'''
        from favourites import Favourites
        self.options["mediafilter"] = "episodes"
        return Favourites(self.addon, self.metadatautils, self.options).favourites()

    def favourite(self):
        '''synonym to favourites'''
        return self.favourites()

    def recommended(self):
        ''' get recommended episodes - library episodes with score higher than 7 '''
        filters = [kodi_constants.FILTER_RATING]
        if self.options["hide_watched"]:
            filters.append(kodi_constants.FILTER_UNWATCHED)
        return self.metadatautils.kodidb.episodes(sort=kodi_constants.SORT_RATING, filters=filters,
                                                  limits=(0, self.options["limit"]))

    def recent(self):
        ''' get recently added episodes '''
        log_msg("recent widget", xbmc.LOGINFO)
        tvshow_episodes = {}
        total_count = 0
        unique_count = 0
        filters = []
        if self.options["hide_watched"]:
            filters.append(kodi_constants.FILTER_UNWATCHED)
        if self.options.get("tag"):
            filters.append({"operator": "contains", "field": "tag", "value": self.options["tag"]})
        if self.options.get("path"):
            filters.append({"operator": "startswith", "field": "path", "value": self.options["path"]})
        while unique_count < self.options["limit"]:
            recent_episodes = self.metadatautils.kodidb.episodes(
                sort=kodi_constants.SORT_DATEADDED, filters=filters, limits=(
                    total_count, self.options["limit"] + total_count))
            log_msg("Check grouping setting", xbmc.LOGINFO)
            if not self.options["group_episodes"]:
                # grouping is not enabled, just return the result
                log_msg("Grouping not enabled, return normal result", xbmc.LOGINFO)
                return recent_episodes

            if len(recent_episodes) < self.options["limit"]:
                # break the loop if there are no more episodes
                unique_count = self.options["limit"]

            # if multiple episodes for the same show with same addition date, we combine them into one
            # to do that we build a dict with recent episodes for all episodes of the same season added on the same date
            for episode in recent_episodes:
                total_count += 1
                unique_key = "%s-%s-%s" % (episode["tvshowid"], episode["dateadded"].split(" ")[0], episode["season"])
                log_msg("Unique %s" % unique_key, xbmc.LOGINFO)
                if unique_key not in tvshow_episodes:
                    tvshow_episodes[unique_key] = []
                    unique_count += 1
                tvshow_episodes[unique_key].append(episode)

        log_msg("Return entries sorted by dateadded", xbmc.LOGINFO)
        # create our entries and return the result sorted by dateadded
        all_items = self.metadatautils.process_method_on_list(self.create_grouped_entry, tvshow_episodes.values())
        return sorted(all_items, key=itemgetter("dateadded"), reverse=True)[:self.options["limit"]]

    def random(self):
        ''' get random episodes '''
        filters = []
        if self.options["hide_watched"]:
            filters.append(kodi_constants.FILTER_UNWATCHED)
        if self.options.get("tag"):
            filters.append({"operator": "contains", "field": "tag", "value": self.options["tag"]})
        if self.options.get("path"):
            filters.append({"operator": "startswith", "field": "path", "value": self.options["path"]})
        return self.metadatautils.kodidb.episodes(sort=kodi_constants.SORT_RANDOM, filters=filters,
                                                  limits=(0, self.options["limit"]))

    def inprogress(self):
        ''' get in progress episodes '''
        filters = [kodi_constants.FILTER_INPROGRESS]
        if self.options.get("tag"):
            filters.append({"operator": "contains", "field": "tag", "value": self.options["tag"]})
        if self.options.get("path"):
            filters.append({"operator": "startswith", "field": "path", "value": self.options["path"]})
        return self.metadatautils.kodidb.episodes(sort=kodi_constants.SORT_LASTPLAYED, filters=filters,
                                                  limits=(0, self.options["limit"]))

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
        filters = [kodi_constants.FILTER_UNWATCHED]
        if self.options["next_inprogress_only"]:
            filters = [kodi_constants.FILTER_INPROGRESS]
        if self.options.get("tag"):
            filters.append({"operator": "contains", "field": "tag", "value": self.options["tag"]})
        if self.options.get("path"):
            filters.append({"operator": "startswith", "field": "path", "value": self.options["path"]})
        # First we get a list of all the inprogress/unwatched TV shows ordered by lastplayed
        all_shows = self.metadatautils.kodidb.tvshows(sort=kodi_constants.SORT_LASTPLAYED, filters=filters,
                                                      limits=(0, self.options["limit"]))
        return self.metadatautils.process_method_on_list(self.get_next_episode_for_show,
                                                         [d['tvshowid'] for d in all_shows])

    def get_next_episode_for_show(self, show_id):
        '''
        get last played watched episode for show,
        return next unwatched episode after that,
        unless nothing after that, then return first episode
        '''
        filters = []
        fields = ["playcount", "season"]
        next_episode = None
        if not self.options["episodes_enable_specials"]:
            filters.append({"field": "season", "operator": "greaterthan", "value": "0"})

        # get the next unwatched episode after the last played episode
        last_played_episode = self.metadatautils.kodidb.episodes(sort=kodi_constants.SORT_LASTPLAYED,
                    filters=filters + [kodi_constants.FILTER_WATCHED], limits=(0, 1), tvshowid=show_id, fields=fields)
        if last_played_episode:
            last_played_episode = last_played_episode[0]
            filter_season = last_played_episode["season"] - 1
            filter_season = [{"field": "season", "operator": "greaterthan", "value": "%s" % filter_season}]
            all_episodes = self.metadatautils.kodidb.episodes(sort=kodi_constants.SORT_EPISODE,
                    filters=filters + filter_season, tvshowid=show_id, fields=fields)
            # find index of last_played_episode in the list all_episodes
            try:
                for index, episode in enumerate(all_episodes):
                    if episode['episodeid'] == last_played_episode['episodeid']:
                        i = 1
                        while True:
                            if int(all_episodes[index + i]['playcount']) < 1:
                                next_episode = all_episodes[index + i]
                                break
                            i += 1
            except IndexError:
                # no unplayed episodes left
                next_episode = None
        # just get the first unwatched episode (e.g. when we simply do not yet have any fully played episodes)
        if not next_episode:
            next_episode = self.metadatautils.kodidb.episodes(
                sort=kodi_constants.SORT_EPISODE, filters=filters + [kodi_constants.FILTER_UNWATCHED],
                limits=(0, 1), tvshowid=show_id, fields=fields)
            next_episode = next_episode[0] if next_episode else None
        # return full details for our episode
        return self.metadatautils.kodidb.episode(next_episode["episodeid"]) if next_episode else None


    def unaired(self):
        ''' get all unaired episodes for shows in the library - provided by tvdb module'''
        self.metadatautils.thetvdb.days_ahead = 120

        filters = [kodi_constants.FILTER_UNWATCHED]
        if self.options["next_inprogress_only"]:
            filters = [kodi_constants.FILTER_INPROGRESS]
        if self.options.get("tag"):
            filters.append({"operator": "contains", "field": "tag", "value": self.options["tag"]})
        if self.options.get("path"):
            filters.append({"operator": "startswith", "field": "path", "value": self.options["path"]})

        # First we get a list of all the inprogress/unwatched TV shows ordered by lastplayed
        all_shows = self.metadatautils.kodidb.tvshows(sort=kodi_constants.SORT_LASTPLAYED, filters=filters,
                                                      limits=(0, self.options["limit"]))
        tvshows_ids = [d['tvshowid'] for d in all_shows]
        episodes = self.metadatautils.thetvdb.get_kodi_unaired_episodes(False, False, tvshows_ids)
        episodes = episodes[:self.options["limit"]]
        return [self.map_episode_props(episode) for episode in episodes]

    def nextaired(self, days_ahead=60):
        ''' get all next airing episodes for shows in the library - provided by tvdb module'''
        self.metadatautils.thetvdb.days_ahead = days_ahead

        filters = [kodi_constants.FILTER_UNWATCHED]
        if self.options["next_inprogress_only"]:
            filters = [kodi_constants.FILTER_INPROGRESS]
        if self.options.get("tag"):
            filters.append({"operator": "contains", "field": "tag", "value": self.options["tag"]})
        if self.options.get("path"):
            filters.append({"operator": "startswith", "field": "path", "value": self.options["path"]})

        # First we get a list of all the inprogress/unwatched TV shows ordered by lastplayed
        all_shows = self.metadatautils.kodidb.tvshows(sort=kodi_constants.SORT_LASTPLAYED, filters=filters,
                                                      limits=(0, self.options["limit"]))
        tvshows_ids = [d['tvshowid'] for d in all_shows]
        episodes = self.metadatautils.thetvdb.get_kodi_unaired_episodes(True, False, tvshows_ids)
        return [self.map_episode_props(episode) for episode in episodes]

    def airingtoday(self):
        ''' get today airing episodes - provided by tvdb module'''
        return self.nextaired(0)

    @staticmethod
    def create_grouped_entry(tvshow_episodes):
        '''helper for grouped episodes'''
        firstepisode = tvshow_episodes[0]
        if len(tvshow_episodes) > 2:
            # add as season entry if there were multiple episodes for the same show
            # use first episode as reference to keep the correct sorting order
            item = firstepisode
            item["type"] = "season"
            item["label"] = "%s %s" % (xbmc.getLocalizedString(20373), firstepisode["season"])
            item["plot"] = u"[B]%s[/B] • %s %s[CR]%s: %s"\
                % (item["label"], len(tvshow_episodes), xbmc.getLocalizedString(20387),
                   xbmc.getLocalizedString(570), firstepisode["dateadded"].split(" ")[0])
            item["extraproperties"] = {"UnWatchedEpisodes": "%s" % len(tvshow_episodes)}
            return item
        # just add the single item
        return firstepisode

    @staticmethod
    def map_episode_props(episode_details):
        ''''adds some of the optional fields as extra properties for the listitem'''
        extraprops = {}
        for item in ["network", "airdate", "airdate.label", "airtime", "airdatetime", "airdatetime.label", "airday"]:
            extraprops[item] = episode_details[item]
        extraprops["DBTYPE"] = "episode"
        episode_details["extraproperties"] = extraprops
        return episode_details
