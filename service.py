import xbmcgui
import sys
import os
import xbmc
import xbmcaddon
import xbmcvfs
import requests
import gzip
from resources.lib import weblogin
from cookielib import LWPCookieJar
import time
import datetime

ADDON = xbmcaddon.Addon(id="service.takealugepgdownloader")
addon_name = ADDON.getAddonInfo('name')
addon_version = ADDON.getAddonInfo('version')
speicherort = ADDON.getSetting("path").decode('utf-8')
server1 = 'https://takealug.de/wordpress'
username = ADDON.getSetting('username')
uc = username.capitalize()
password = ADDON.getSetting('password')
choose_epg = ADDON.getSetting('choose_epg')
auto_download = True if ADDON.getSetting('auto_download').lower() == 'true' else False
timeswitch = int(ADDON.getSetting('timeswitch'))
datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
cookie = os.path.join(datapath, "cookies.lwp")
temp = os.path.join(datapath, "temp")
hidesuccess = True if ADDON.getSetting('hide-successful-login-messages').lower() == 'true' else False

# deal with setting 'next_download' which not exists at first time
try:
    next_download = int(ADDON.getSetting('next_download'))
except ValueError:
    ADDON.setSetting('next_download', '0')

logged_in = False
logged_inpremium = False

OSD = xbmcgui.Dialog()
Monitor = xbmc.Monitor()

def notify(title, message, icon=xbmcgui.NOTIFICATION_INFO, hide=False):
    if not hide:
        OSD.notification(title, message, icon)

# make a debug logger

def log(message, loglevel=xbmc.LOGDEBUG):
    xbmc.log('[%s %s] %s' % (addon_name, addon_version, str(message)), loglevel)

# make a function for download, temporal storage and moving guide.xml to destination,
# as this is the same for all download types

def download_and_move(session, url):
    r = session.get(url)
    gz_file = os.path.join(temp, "guide.gz")

    with open(gz_file, 'wb') as f:
        f.write(r.content)
    
    with open(os.path.join(speicherort, 'guide.xml'), 'wb') as f_xml:
        with gzip.open(gz_file, 'rb') as f_in:
            f_xml.write(f_in.read())

    tin= os.path.join(temp, 'guide.xml')
    fout = os.path.join(speicherort,'guide.xml')
    xbmcvfs.copy(tin, fout)
    xbmcvfs.delete(tin)
    notify('Guide Stored', speicherort)


def takealug_download():
    if choose_epg == 'Premium DE AT CH 12-14Day':
        de_at_ch_premium()
    else:
        pass
    if choose_epg == 'Premium easyEPG 12-14Day':
        easy_epg_premium()
    else:
        pass
    if choose_epg == 'Premium Zattoo DE 12-14Day':
        zattoo_de_premium()
    else:
        pass
    if choose_epg == 'Premium Zattoo CH 12-14Day':
        zattoo_ch_premium()
    else:
        pass
    if choose_epg == 'Free DE AT CH 3-5Day':
        de_at_ch_free()
    else:
        pass
    if choose_epg == 'Free easyEPG 3-5Day':
        easy_epg_free()
    else:
        pass
    if choose_epg == 'Free Zattoo DE 3-5Day':
        zattoo_de_free()
    else:
        pass
    if choose_epg == 'Free Zattoo CH 3-5Day':
        zattoo_ch_free()
    else:
        pass          


def de_at_ch_premium():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1+'/download/879/'
        if logged_inpremium == False:
            notify('Sorry %s' % uc, 'You need Premium Membership for this File', icon=xbmcgui.NOTIFICATION_WARNING)
        elif logged_inpremium == True:
            download_and_move(s, url)


def easy_epg_premium():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1+'/download/1122/'
        if logged_inpremium == False:
            notify('Sorry %s' % uc, 'You need Premium Membership for this File', icon=xbmcgui.NOTIFICATION_WARNING)
        elif logged_inpremium == True: 
            download_and_move(s, url)


def zattoo_de_premium():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1+'/download/1123/'
        if logged_inpremium == False:
            notify('Sorry %s' % uc, 'You need Premium Membership for this File', icon=xbmcgui.NOTIFICATION_WARNING)
        elif logged_inpremium == True: 
            download_and_move(s, url)


def zattoo_ch_premium():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1+'/download/1124/'
        if logged_inpremium == False:
            notify('Sorry %s' % uc, 'You need Premium Membership for this File', icon=xbmcgui.NOTIFICATION_WARNING)
        elif logged_inpremium == True: 
            download_and_move(s, url)


def de_at_ch_free():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1+'/download/1271/'
        download_and_move(s, url)


def easy_epg_free():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1+'/download/1125/'
        download_and_move(s, url)


def zattoo_de_free():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1+'/download/1126/'
        download_and_move(s, url)


def zattoo_ch_free():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1+'/download/1127/'
        download_and_move(s, url)


def worker(next_download):
    while not Monitor.waitForAbort(60):
        log('Worker walk through...')
        initiate_download = False

        # check if guide.gz already exists and check timestamp of this file.
        # if timestamp is not older than 24 hours, there's nothing to do,
        # otherwise download it.

        last_file = os.path.join(temp, 'guide.gz')
        last_timestamp = os.path.getmtime(last_file)

        if os.path.exists(last_file):
            log('Timestamp of last downloaded archive is %s' % datetime.datetime.fromtimestamp(last_timestamp).strftime('%d.%m.%Y %H:%M'))
            if (int(time.time()) - 86400) < last_timestamp < int(time.time()):
                log('Waiting for next download at %s' % datetime.datetime.fromtimestamp(next_download).strftime('%d.%m.%Y %H:%M'))
            else:
                log('Archive is older than 24 hours, initiate download')
                initiate_download = True

            if next_download < int(time.time()):

                # suggested download time has passed (e.g. system was offline) or time is now, download epg
                # and set a new timestamp for the next download
                log('Download time has reached, initiate download')
                initiate_download = True
        else:
            initiate_download = True

        if initiate_download:
            takealug_download()

            calc_next_download = datetime.datetime.now()
            calc_next_download = calc_next_download.replace(day=calc_next_download.day + 1, hour=timeswitch, minute=0, second=0, microsecond=0)

            next_download = int(calc_next_download.strftime("%s"))
            ADDON.setSetting('next_download', str(next_download))

def startup():
    # deal with bug that happens if the datapath and/or temp doesn't exist
    if not os.path.exists(temp):
        os.makedirs(temp)

    # get username and password and do login with them
    # also get whether to hide successful login notification

    logged_inpremium = weblogin.doLoginPremium(datapath, username, password)
    if logged_inpremium:
        notify('Welcome back, %s' % uc, 'Thank you for donating!', hide=hidesuccess)
    else:
        logged_in = weblogin.doLogin(datapath, username, password)
        if logged_in:
            notify('Welcome back, %s' % uc, 'Takealug say hello', hide=hidesuccess)
        else:
            notify('Login Failure', '%s could not login' % uc, icon=xbmcgui.NOTIFICATION_ERROR)
            return False
    return True

# Addon starts at this point

if startup():
    if auto_download:
        if speicherort == 'choose':
            notify('Sorry %s' % uc, 'You need to choose your Downloadlocation first', icon=xbmcgui.NOTIFICATION_WARNING)
        elif choose_epg == 'None':
            notify('Sorry %s' % uc, 'You need to choose your EPG first', icon=xbmcgui.NOTIFICATION_WARNING)
        else:
            worker(int(ADDON.getSetting('next_download')))
    else:
        try:
            if sys.argv[1] == 'manual_download':
                if speicherort == 'choose':
                    notify('Sorry %s' % uc, 'You need to choose your Downloadlocation first', icon=xbmcgui.NOTIFICATION_WARNING)
                elif choose_epg == 'None':
                        notify('Sorry %s' % uc, 'You need to choose your EPG first', icon=xbmcgui.NOTIFICATION_WARNING)
                else:
                    dialog = xbmcgui.Dialog()
                    ret = dialog.yesno('Takealug EPG Downloader', 'Start Manual Download')
                    if ret:
                        manual = True
                        notify('Manual Download', choose_epg)
                        takealug_download()
        except IndexError:
            pass

xbmcvfs.delete(cookie)
