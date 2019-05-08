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
from datetime import datetime

ADDON = xbmcaddon.Addon(id="service.takealugepgdownloader")
addon_name = ADDON.getAddonInfo('name')
addon_version = ADDON.getAddonInfo('version')
lang_string = ADDON.getLocalizedString

speicherort = ADDON.getSetting("path").decode('utf-8')
server1 = 'https://takealug.de/wordpress'
username = ADDON.getSetting('username')
uc = username.capitalize()
password = ADDON.getSetting('password')
choose_epg = lang_string(int(ADDON.getSetting('choose_epg')) + 32010)
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
    ADDON.setSetting('next_download', str(int(time.time())))

logged_in = weblogin.doLogin(datapath, username, password)
logged_inpremium = weblogin.doLoginPremium(datapath, username, password)

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

    with open(os.path.join(temp, 'guide.xml'), 'w') as f_xml:
        with gzip.open(gz_file, 'r') as f_in:
            f_xml.write(f_in.read())

    tin = os.path.join(temp, 'guide.xml')
    fout = os.path.join(speicherort, 'guide.xml')

    if not xbmcvfs.copy(tin, fout):
        log('Could not copy to %s' % speicherort, xbmc.LOGERROR)
        return False
    if not xbmcvfs.delete(tin):
        log('Could not delete % s' % tin, xbmc.LOGERROR)
        return False
    notify(lang_string(32040), fout)
    return True


def takealug_download():
    if choose_epg == lang_string(32011):
        de_at_ch_premium()
    elif choose_epg == lang_string(32012):
        easy_epg_premium()
    elif choose_epg == lang_string(32013):
        zattoo_de_premium()
    elif choose_epg == lang_string(32014):
        zattoo_ch_premium()
    elif choose_epg == lang_string(32015):
        de_at_ch_free()
    elif choose_epg == lang_string(32016):
        easy_epg_free()
    elif choose_epg == lang_string(32017):
        zattoo_de_free()
    elif choose_epg == lang_string(32018):
        zattoo_ch_free()
    else:
        pass


def de_at_ch_premium():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1 + '/download/879/'
        if logged_inpremium == False:
            notify(lang_string(32041) % uc, lang_string(32042), icon=xbmcgui.NOTIFICATION_WARNING)
        elif logged_inpremium == True:
            download_and_move(s, url)


def easy_epg_premium():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1 + '/download/1122/'
        if logged_inpremium == False:
            notify(lang_string(32041) % uc, lang_string(32042), icon=xbmcgui.NOTIFICATION_WARNING)
        elif logged_inpremium == True:
            download_and_move(s, url)


def zattoo_de_premium():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1 + '/download/1123/'
        if logged_inpremium == False:
            notify(lang_string(32041) % uc, lang_string(32042), icon=xbmcgui.NOTIFICATION_WARNING)
        elif logged_inpremium == True:
            download_and_move(s, url)


def zattoo_ch_premium():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1 + '/download/1124/'
        if logged_inpremium == False:
            notify(lang_string(32041) % uc, lang_string(32042), icon=xbmcgui.NOTIFICATION_WARNING)
        elif logged_inpremium == True:
            download_and_move(s, url)


def de_at_ch_free():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1 + '/download/1271/'
        download_and_move(s, url)


def easy_epg_free():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1 + '/download/1125/'
        download_and_move(s, url)


def zattoo_de_free():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1 + '/download/1126/'
        download_and_move(s, url)


def zattoo_ch_free():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1 + '/download/1127/'
        download_and_move(s, url)


def worker(next_download):
    while not Monitor.waitForAbort(60):
        log('Worker walk through...')
        initiate_download = False

        # check if guide.gz already exists and check timestamp of this file.
        # if timestamp is not older than 24 hours, there's nothing to do,
        # otherwise download it.

        last_file = os.path.join(temp, 'guide.gz')

        if os.path.exists(last_file):
            last_timestamp = os.path.getmtime(last_file)
            log('Timestamp of last downloaded archive is %s' % datetime.fromtimestamp(last_timestamp).strftime(
                '%d.%m.%Y %H:%M'))
            if (int(time.time()) - 86400) < last_timestamp < int(time.time()):
                log('Waiting for next download at %s' % datetime.fromtimestamp(next_download).strftime(
                    '%d.%m.%Y %H:%M'))
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

            calc_next_download = datetime.now()
            calc_next_download = calc_next_download.replace(day=calc_next_download.day + 1, hour=timeswitch, minute=0,
                                                            second=0, microsecond=0)

            # Deal with a windows strftime bug (Win don't know '%s' formatting)
            try:
                next_download = int(calc_next_download.strftime("%s"))
            except ValueError:
                next_download = int(time.mktime(calc_next_download.timetuple()))
                
            ADDON.setSetting('next_download', str(next_download))


def startup():
    # deal with bug that happens if the datapath and/or temp doesn't exist
    if not os.path.exists(temp):
        os.makedirs(temp)

    # get username and password and do login with them
    # also get whether to hide successful login notification

    logged_inpremium = weblogin.doLoginPremium(datapath, username, password)
    if logged_inpremium:
        notify(lang_string(32043) % uc, lang_string(32044), hide=hidesuccess)
    else:
        logged_in = weblogin.doLogin(datapath, username, password)
        if logged_in:
            notify(lang_string(32043) % uc, lang_string(32045), hide=hidesuccess)
        else:
            notify(lang_string(32046), lang_string(32047) % uc, icon=xbmcgui.NOTIFICATION_ERROR)
            return False
    return True


# Addon starts at this point

def manual_download():
    manual_download = False
    try:
        if sys.argv[1:][0] == 'manual_download':
            manual_download = True
    except:
        pass
    return manual_download

if manual_download() == True:
    if logged_in == True:
        if speicherort == 'choose': 
            notify(lang_string(32041) % uc, lang_string(32048), icon=xbmcgui.NOTIFICATION_WARNING)                    
        else:
            if choose_epg == 'None':
                notify(lang_string(32041) % uc, lang_string(32049), icon=xbmcgui.NOTIFICATION_WARNING)
            else:
                dialog = xbmcgui.Dialog()
                ret = dialog.yesno(lang_string(32000), lang_string(32050) % choose_epg)
                if ret:
                    manual = True
                    notify('Manual Download', choose_epg)
                    takealug_download()          

if startup():
    if auto_download:
        if speicherort == 'choose':
            notify(lang_string(32041) % uc, lang_string(32048), icon=xbmcgui.NOTIFICATION_WARNING)
        elif choose_epg == 'None':
            notify(lang_string(32041) % uc, lang_string(32049), icon=xbmcgui.NOTIFICATION_WARNING)
        else:
            worker(int(ADDON.getSetting('next_download')))


xbmcvfs.delete(cookie)
