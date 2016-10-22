#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc, xbmcaddon
import sys
from traceback import format_exc
from datetime import datetime
import time

try:
    from multiprocessing.pool import ThreadPool as Pool
    supportsPool = True
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
  
def get_localdate_from_utc(timestring):
    try:
        systemtime = xbmc.getInfoLabel("System.Time")
        utc = datetime.fromtimestamp(time.mktime(time.strptime(timestring, '%Y-%m-%d %H:%M:%S')))
        epoch = time.mktime(utc.timetuple())
        offset = datetime.fromtimestamp (epoch) - datetime.utcfromtimestamp(epoch)
        correcttime = utc + offset
        if "AM" in systemtime or "PM" in systemtime:
            return (correcttime.strftime("%Y-%m-%d"),correcttime.strftime("%I:%M %p"))
        else:
            return (correcttime.strftime("%d-%m-%Y"),correcttime.strftime("%H:%M"))
    except Exception as e:
        log_msg(format_exc(sys.exc_info()),xbmc.LOGDEBUG)
        log_msg("ERROR in Utils.get_localdate_from_utc ! --> %s" %e, xbmc.LOGERROR)
        return (timestring,timestring)

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