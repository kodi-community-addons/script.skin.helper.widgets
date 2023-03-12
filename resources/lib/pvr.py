#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    script.skin.helper.widgets
    pvr.py
    all PVR widgets provided by the script
'''

import os, sys
from resources.lib.utils import create_main_entry, log_msg
from operator import itemgetter
import xbmc
from urllib.parse import quote_plus


class Pvr(object):
    '''all channel widgets provided by the script'''

    def __init__(self, addon, metadatautils, options):
        '''Initializations pass our common classes and the widget options as arguments'''
        self.metadatautils = metadatautils
        self.addon = addon
        self.options = options
        self.enable_artwork = self.addon.getSetting("pvr_enable_artwork") == "true"

    def listing(self):
        '''main listing with all our channel nodes'''

        # add generic pvr entries
        all_items = [
            (self.addon.getLocalizedString(32069),
             "lastchannels&mediatype=pvr&reload=$INFO[Window(Home).Property(widgetreload2)]",
             "DefaultAddonPVRClient.png"),
            (self.addon.getLocalizedString(32018),
             "recordings&mediatype=pvr&reload=$INFO[Window(Home).Property(widgetreload2)]",
             "DefaultAddonPVRClient.png"),
            (self.addon.getLocalizedString(32019),
             "nextrecordings&mediatype=pvr&reload=$INFO[Window(Home).Property(widgetreload2)]",
             "DefaultAddonPVRClient.png"),
            (self.addon.getLocalizedString(32031),
             "nextrecordings&mediatype=pvr&reversed=true&reload=$INFO[Window(Home).Property(widgetreload2)]",
             "DefaultAddonPVRClient.png"),
            (self.addon.getLocalizedString(32021),
             "timers&mediatype=pvr&reload=$INFO[Window(Home).Property(widgetreload2)]",
             "DefaultAddonPVRClient.png")]

        # get all channel groups and create a tv channels entry for each groups
        for item in self.metadatautils.kodidb.channelgroups():
            label = "%s: %s" % (self.addon.getLocalizedString(32020), item["label"])
            widgetpath = "channels&mediatype=pvr&reload=$INFO[Window(Home).Property(widgetreload2)]"
            widgetpath += "&channelgroup=%s" % (item["channelgroupid"])
            all_items.append((label, widgetpath, "DefaultAddonPVRClient.png"))

        return self.metadatautils.process_method_on_list(create_main_entry, all_items)

    def channels(self):
        ''' get all channels '''
        all_items = []
        channelgroupid = self.options.get("channelgroup")
        if channelgroupid:
            channelgroupid = int(channelgroupid)
        if xbmc.getCondVisibility("Pvr.HasTVChannels"):
            all_items = self.metadatautils.kodidb.channels(
                limits=(0, self.options["limit"]),
                channelgroupid=channelgroupid)
            all_items = self.metadatautils.process_method_on_list(self.process_channel, all_items)
        return all_items

    def lastchannels(self):
        ''' get last played channels '''
        all_items = []
        if xbmc.getCondVisibility("Pvr.HasTVChannels"):
            # get full channels listing (as there is no way to apply filtering)
            for channel in self.metadatautils.kodidb.channels():
                # only add channels to the final list that are actually played once
                if not channel["lastplayed"].startswith("1970"):
                    all_items.append(channel)
            # sort by last played field and apply limit
            all_items = sorted(all_items, key=itemgetter('lastplayed'), reverse=True)[:self.options["limit"]]
            all_items = self.metadatautils.process_method_on_list(self.process_channel, all_items)
        return all_items

    def recordings(self, next_only=False):
        '''get all recordings'''
        all_items = []
        all_titles = []
        if xbmc.getCondVisibility("Pvr.HasTVChannels"):
            # Get a list of all the unwatched tv recordings
            recordings = self.metadatautils.kodidb.recordings()
            pvr_backend = xbmc.getInfoLabel("Pvr.BackendName")
            for item in recordings:
                # exclude live tv items from recordings list (mythtv workaround)
                if not ("mythtv" in pvr_backend.lower() and "/livetv/" in item.get("file", "").lower()):
                    if not (self.options["hide_watched"] and item["playcount"] != 0):
                        # only include next unwatched if nextonly param given
                        if not next_only:
                            all_items.append(item)
                        elif (not item.get("directory", "") in all_titles) and item["playcount"] == 0:
                            all_items.append(item)
                            if item.get("directory"):
                                all_titles.append(item["directory"])

            # sort the list so we return the list with the oldest unwatched first
            # if reversed we return the newest first
            if self.options.get("reversed", "") == "true":
                all_items = sorted(all_items, key=itemgetter('endtime'), reverse=False)
            else:
                all_items = sorted(all_items, key=itemgetter('endtime'), reverse=True)

            # return result including artwork...
            return self.metadatautils.process_method_on_list(self.process_recording, all_items)
        return all_items

    def nextrecordings(self):
        ''' get all recordings '''
        return self.recordings(True)

    def timers(self):
        '''get pvr timers'''
        all_items = []
        if xbmc.getCondVisibility("Pvr.HasTVChannels"):
            # only add timers which have a broadcast date
            for timer in self.metadatautils.kodidb.timers():
                if timer["starttime"] and not timer["starttime"].startswith("1970"):
                    # filter out recurring timer entries
                    if timer["starttime"] != timer["endtime"]:
                        all_items.append(timer)
            all_items = self.metadatautils.process_method_on_list(self.process_timer, all_items)
        return all_items

    def process_channel(self, channeldata):
        '''transform the json received from kodi into something we can use'''
        item = {}
        channelname = channeldata["label"]
        channellogo = self.metadatautils.get_clean_image(channeldata['thumbnail'])
        if channeldata.get('broadcastnow'):
            # channel with epg data
            item = channeldata['broadcastnow']
            item["runtime"] = item["runtime"] * 60
            item["genre"] = " / ".join(item["genre"])
            # del firstaired as it's value doesn't make any sense at all
            del item["firstaired"]
            # append artwork
            if self.enable_artwork:
                self.metadatautils.extend_dict(
                    item, self.metadatautils.get_pvr_artwork(
                        item["title"], channelname, item["genre"]))
        else:
            # channel without epg
            item = channeldata
            item["title"] = xbmc.getLocalizedString(161)
        item["file"] = "plugin://script.skin.helper.service?action=playchannel&channelid=%s"\
            % (channeldata["channelid"])
        item["channel"] = channelname
        item["channelid"] = ""
        item["dbid"] = ""	
        if item.get("media_type"):
            item["type"] = item.get("media_type")
        else:
            item["type"] = "musicvideo"
        item["label"] = channelname
        #item["channelid"] = channeldata["channelid"]
        if not channellogo:
            channellogo = self.metadatautils.get_channellogo(channelname)
        if channellogo:
            if not item.get("art"):
                item["art"] = {}
            if not item["art"].get("thumb"):
                item["art"]["thumb"] = channellogo
        item["channellogo"] = channellogo
        item["isFolder"] = False
        return item

    def process_recording(self, item):
        '''transform the json received from kodi into something we can use'''
        if self.enable_artwork:
            self.metadatautils.extend_dict(item, self.metadatautils.get_pvr_artwork(item["title"], item["channel"]))
        item["type"] = "recording"
        item["channellogo"] = self.metadatautils.get_channellogo(item["channel"])
        item["file"] = "plugin://script.skin.helper.service?action=playrecording&recordingid=%s"\
            % (item["recordingid"])
        item["dateadded"] = item["endtime"].split(" ")[0]
        if item["resume"].get("position"):
            item["lastplayed"] = item["endtime"].split(" ")[0]
        else:
            item["lastplayed"] = ""
        if not item["art"].get("thumb"):
            item["art"]["thumb"] = item["channellogo"]
        return item

    def process_timer(self, item):
        '''transform the json received from kodi into something we can use'''
        item["file"] = "plugin://script.skin.helper.service?action=playchannel&channelid=%s"\
            % (item["channelid"])
        if not item["channelid"] == -1:
            channel_details = self.metadatautils.kodidb.channel(item["channelid"])
            channelname = channel_details["label"]
        else:
            channelname = ""
        log_msg("get_pvr_all - process_timer from json ==%s=" %  (item))
        item["channelid"] = ""
        item["dbid"] = ""	
        item["channel"] = channelname
        summary = item.get("summary", "")
        item["type"] = "musicvideo"
        item["isFolder"] = False
        if self.enable_artwork:
            self.metadatautils.extend_dict(item, self.metadatautils.get_pvr_artwork(item["title"], item["channel"]))
        channellogo = self.metadatautils.get_channellogo(channelname)	
        if item.get("media_type"):
            item["type"] = item.get("media_type")
        else:
            item["type"] = "musicvideo"
        item["plot"] = "%s[CR]%s"  % (summary, item.get("plot", ""))
        if channellogo:
            if not item.get("art"):
                item["art"] = {}
            if not item["art"].get("thumb"):
                item["art"]["thumb"] = channellogo
        item["channellogo"] = channellogo
        return item
