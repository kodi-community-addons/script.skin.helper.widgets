#!/usr/bin/python
# -*- coding: utf-8 -*-
from utils import process_method_on_list
from operator import itemgetter
from artutils import kodi_constants
import xbmc


class Pvr(object):
    '''all pvr widgets provided by the script'''

    def __init__(self, addon, kodidb, options):
        '''Initializations pass our common classes and the widget options as arguments'''
        self.kodidb = kodidb
        self.addon = addon
        self.options = options

    def listing(self):
        '''main listing with all our pvr nodes'''
        all_items = [
            (self.addon.getLocalizedString(32027), "inprogress&mediatype=episodes", "DefaultTvShows.png"),
            (self.addon.getLocalizedString(32002), "next&mediatype=episodes", "DefaultTvShows.png"),
            (self.addon.getLocalizedString(32039), "recent&mediatype=episodes", "DefaultRecentlyAddedEpisodes.png"),
            (self.addon.getLocalizedString(32009), "recommended&mediatype=episodes", "DefaultTvShows.png"),
            (self.addon.getLocalizedString(32010), "inprogressandrecommended&mediatype=episodes","DefaultTvShows.png"),
            (self.addon.getLocalizedString(32049), "inprogressandrandom&mediatype=episodes", "DefaultTvShows.png"),
            (self.addon.getLocalizedString(32008), "random&mediatype=episodes", "DefaultTvShows.png"),
            (self.addon.getLocalizedString(32042), "unaired&mediatype=episodes", "DefaultTvShows.png"),
            (self.addon.getLocalizedString(32043), "nextaired&mediatype=episodes", "DefaultTvShows.png"),
            ]
        return process_method_on_list(self.kodidbcreate_main_entry,all_items)

