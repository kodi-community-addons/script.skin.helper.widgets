#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    script.skin.helper.widgets
    utils.py
    helper methods
'''

import xbmc

ADDON_ID = "script.skin.helper.widgets"
KODI_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split(".")[0])

def log_msg(msg, loglevel=xbmc.LOGDEBUG):
    '''log message to kodi log'''
    if isinstance(msg, unicode):
        msg = msg.encode('utf-8')
    xbmc.log("Skin Helper Widgets --> %s" % msg, level=loglevel)


def create_main_entry(item):
    '''helper to create a simple (directory) listitem'''
    if "//" in item[1]:
        filepath = item[1]
    else:
        filepath = "plugin://script.skin.helper.widgets/?action=%s" % item[1]
    return {
        "label": item[0],
        "file": filepath,
        "icon": item[2],
        "art": {"fanart": "special://home/addons/script.skin.helper.widgets/fanart.jpg"},
        "isFolder": True,
        "type": "file",
        "IsPlayable": "false"
    }
