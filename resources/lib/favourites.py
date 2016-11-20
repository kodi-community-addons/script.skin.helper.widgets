#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    script.skin.helper.widgets
    favourites.py
    all favourites widgets provided by the script
'''

from artutils import extend_dict
import xbmc
import xbmcvfs
from urllib import quote_plus


class Favourites(object):
    '''all favourites widgets provided by the script'''

    def __init__(self, addon, artutils, options):
        '''Initializations pass our common classes and the widget options as arguments'''
        self.artutils = artutils
        self.addon = addon
        self.options = options
        self.enable_artwork = self.addon.getSetting("music_enable_artwork") == "true"
        self.browse_album = self.addon.getSetting("music_browse_album") == "true"

    def listing(self):
        '''show kodi favourites '''
        all_items = []
        media_filter = self.options.get("mediafilter", "")

        # emby favorites
        if xbmc.getCondVisibility("System.HasAddon(plugin.video.emby) + Skin.HasSetting(SmartShortcuts.emby)"):
            if media_filter in ["media", "movies"]:
                filters = [{"operator": "contains", "field": "tag", "value": "Favorite movies"}]
                all_items += self.artutils.kodidb.movies(filters=filters)

            if media_filter in ["media", "tvshows"]:
                filters = [{"operator": "contains", "field": "tag", "value": "Favorite tvshows"}]
                for item in self.artutils.kodidb.tvshows(filters=filters):
                    item["file"] = "videodb://tvshows/titles/%s" % item["tvshowid"]
                    item["isFolder"] = True
                    all_items.append(item)

        # Kodi favourites
        for fav in self.artutils.kodidb.favourites():
            match_found = False
            if fav.get("windowparameter") and (not media_filter or media_filter == "tvshows"):

                # check for tvshow
                if fav["windowparameter"].startswith("videodb://tvshows/titles"):
                    tvshowid = int(fav["windowparameter"].split("/")[-2])
                    result = self.artutils.kodidb.tvshow(tvshowid)
                    if result:
                        match_found = True
                        item["file"] = "videodb://tvshows/titles/%s" % item["tvshowid"]
                        item["isFolder"] = True
                        all_items.append(result)

            # apparently only the filename can be used for the search
            media_path = fav["path"]
            if "/" in media_path:
                sep = "/"
            else:
                sep = "\\"
            filename = media_path.split(sep)[-1]
            filters = [{"operator": "contains", "field": "filename", "value": filename}]
            # is this a movie?
            if not match_found and (media_filter or media_filter in ["movies", "media"]):
                for item in self.artutils.kodidb.movies(filters=filters):
                    if item['file'] == media_path:
                        match_found = True
                        all_items.append(item)
            # is this an episode ?
            if not match_found and (not media_filter or media_filter in ["episodes", "media"]):
                for item in self.artutils.kodidb.movies(filters=filters):
                    if item['file'] == media_path:
                        match_found = True
                        all_items.append(item)
            # is this a song ?
            if not match_found and (not media_filter or media_filter in ["songs", "media"]):
                for item in self.artutils.kodidb.songs(filters=filters):
                    if item['file'] == media_path:
                        match_found = True
                        if self.enable_artwork:
                            extend_dict(item, self.artutils.get_music_artwork(item["title"], item["artist"][0]))
                        all_items.append(item)
            # is this a musicvideo ?
            if not match_found and (not media_filter or media_filter in ["musicvideos", "media"]):
                for item in self.artutils.kodidb.musicvideos(filters=filters):
                    if item['file'] == media_path:
                        match_found = True
                        all_items.append(item)
            # is this an album ?
            if not match_found and (not media_filter or media_filter in ["albums", "media"]):
                if "musicdb://albums/" in fav.get("windowparameter", ""):
                    item = self.artutils.kodidb.album(fav["windowparameter"].replace("musicdb://albums/", ""))
                    if item:
                        match_found = True
                        if self.enable_artwork:
                            extend_dict(item, self.artutils.get_music_artwork(item["title"], item["artist"][0]))
                        if self.browse_album:
                            item["file"] = "musicdb://albums/%s" % item["albumid"]
                            item["isFolder"] = True
                        else:
                            item["file"] = u"plugin://script.skin.helper.service?action=playalbum&albumid=%s" \
                                % item["albumid"]
                        all_items.append(item)
            # add unknown item in the result...
            if not match_found and not media_filter:
                is_folder = False
                if fav.get("windowparameter"):
                    media_path = fav.get("windowparameter", "")
                    is_folder = True
                elif fav.get("type") == "media":
                    media_path = fav.get("path")
                else:
                    media_path = 'plugin://script.skin.helper.service/?action=launch&path=%s'\
                        % quote_plus(fav.get("path"))
                if not fav.get("label"):
                    fav["label"] = fav.get("title")
                if not fav.get("title"):
                    fav["label"] = fav.get("label")
                item = {
                    "label": fav.get("label"),
                    "title": fav.get("title"),
                    "thumbnail": fav.get("thumbnail"),
                    "file": media_path,
                    "type": "favourite"}
                if ((fav.get("thumbnail").endswith("icon.png") or fav.get("thumbnail").endswith("icon.png")) and
                        xbmcvfs.exists(fav.get("thumbnail").replace("icon.png", "fanart.jpg"))):
                    item["art"] = {
                        "landscape": fav.get("thumbnail"),
                        "poster": fav.get("thumbnail"),
                        "fanart": fav.get("thumbnail").replace("icon.png", "fanart.jpg")}
                    if is_folder:
                        item["isFolder"] = True
                all_items.append(item)
        return all_items
