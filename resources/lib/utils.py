#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc, xbmcaddon
import sys
from traceback import format_exc
from datetime import datetime
import urllib

try:
    from multiprocessing.pool import ThreadPool as Pool
    supportsPool = False
except Exception: 
    supportsPool = False

try:
    import simplejson as json
except Exception:
    import json

ADDON_ID = "script.skin.helper.widgets"

def log_msg(msg, loglevel = xbmc.LOGDEBUG):
    if isinstance(msg, unicode):
        msg = msg.encode('utf-8')
    xbmc.log("Skin Helper Widgets --> %s" %msg, level=loglevel)
  
def process_method_on_list(method_to_run,items):
    '''helper method that processes a method on each listitem with pooling if the system supports it'''
    all_items = []
    if supportsPool:
        pool = Pool()
        try:
            all_items = pool.map(method_to_run, items)
        except Exception:
            #catch exception to prevent threadpool running forever
            log_msg(format_exc(sys.exc_info()))
            log_msg("Error in %s" %method_to_run, xbmc.LOGERROR)
        pool.close()
        pool.join()
    else:
        all_items = [method_to_run(item) for item in items]
    all_items = filter(None, all_items)
    return all_items
    
def get_clean_image(image):
    if image and "image://" in image:
        image = image.replace("image://","").replace("music@","")
        image=urllib.unquote(image.encode("utf-8"))
        if image.endswith("/"):
            image = image[:-1]
        if not isinstance(image, unicode):
            image = image.decode("utf8")
    return image
    
def create_main_entry(item):
    '''helper to create a simple (directory) listitem'''
    if "//" in item[1]:
        filepath = item[1]
    else:
        filepath = "plugin://script.skin.helper.widgets/?action=%s" %item[1]
    return {
            "label": item[0],
            "file": filepath,
            "icon": item[2],
            "art": {"fanart": "special://home/addons/script.skin.helper.widgets/fanart.jpg"},
            "isFolder": True,
            "type": "file",
            "IsPlayable": "false"
            }
