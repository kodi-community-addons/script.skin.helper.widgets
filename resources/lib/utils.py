#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    script.skin.helper.widgets
    utils.py
    helper methods
'''

import sys
import urllib
from traceback import format_exc
import xbmc
import xbmcaddon

ADDON_ID = "script.skin.helper.widgets"
KODI_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split(".")[0])


def log_msg(msg, loglevel=xbmc.LOGDEBUG):
    ''' log message with addon name and version to kodi log '''
    if isinstance(msg, unicode):
        msg = msg.encode('utf-8')
    addon = xbmcaddon.Addon(id=ADDON_ID)
    addon_name = addon.getAddonInfo('name')
    addon_ver = addon.getAddonInfo('version')
    xbmc.log("{0} v{1} --> {2}".format(addon_name, addon_ver, msg), level=loglevel)


def log_exception(modulename, exceptiondetails):
    '''helper to properly log an exception'''
    log_msg(format_exc(sys.exc_info()), xbmc.LOGWARNING)
    log_msg("Exception in %s ! --> %s" % (modulename, exceptiondetails), xbmc.LOGERROR)


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


def urlencode(text):
    '''helper to urlencode a (unicode) string'''
    if isinstance(text, unicode):
        text = text.encode("utf-8")
    blah = urllib.urlencode({'blahblahblah': text})
    blah = blah[13:]
    return blah
