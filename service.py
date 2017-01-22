#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    script.skin.helper.widgets
    Main service entry point
'''

from resources.lib.utils import log_msg
from resources.lib.kodi_monitor import KodiMonitor
import xbmc
import xbmcgui
import time

widget_task_interval = 520
win = xbmcgui.Window(10000)
kodimonitor = KodiMonitor(win=win)
log_msg('Backgroundservice started', xbmc.LOGNOTICE)

# keep the kodi monitor alive which processes database updates to refresh widgets
while not kodimonitor.abortRequested():
    
    # set generic widget reload
    if widget_task_interval >= 300:
        win.setProperty("widgetreload2", time.strftime("%Y%m%d%H%M%S", time.gmtime()))
        widget_task_interval = 0
    else:
        widget_task_interval += 10
    
    # sleep for 10 seconds
    kodimonitor.waitForAbort(10)
    
log_msg('Backgroundservice stopped', xbmc.LOGNOTICE)
