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
from io import BytesIO

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

# deal with setting 'last_download/next_download' which not exists at first time

try:
    next_download = int(ADDON.getSetting('next_download'))
except ValueError:
    ADDON.setSetting('next_download', str(int(time.time())))
try:
    last_download = int(ADDON.getSetting('last_download'))
except ValueError:
    ADDON.setSetting('last_download', str(int(time.time())))

logged_in = weblogin.doLogin(datapath, username, password)
logged_inpremium = weblogin.doLoginPremium(datapath, username, password)

OSD = xbmcgui.Dialog()
Monitor = xbmc.Monitor()


# list of i18n language strings (see EPG types in language files here), server folder and premium service (bool)
# as classifier, simplify source code
#
# structure: {str EPG language string: {'folder': str server folder, 'premium': bool premium service}}

classifier = {lang_string(32011): {'folder': '879', 'premium': True},
              lang_string(32012): {'folder': '1122', 'premium': True},
              lang_string(32013): {'folder': '1123', 'premium': True},
              lang_string(32014): {'folder': '1124', 'premium': True},
              lang_string(32016): {'folder': '1271', 'premium': False},
              lang_string(32017): {'folder': '1125', 'premium': False},
              lang_string(32018): {'folder': '1126', 'premium': False},
              lang_string(32019): {'folder': '1127', 'premium': False},
              }


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
    ct = r.headers['Content-Type']

    if ct in ('application/octet-stream', 'application/x-gzip', 'application/binary'):

        # ct is a binary file, write it out directly to memory
        # because combined read/write-IO on storage is a Android nightmare

        gz_file = gzip.GzipFile(fileobj=BytesIO(r.content))

        tin = os.path.join(temp, 'guide.xml')
        fout = os.path.join(speicherort, 'guide.xml')

        with open(tin, 'w') as f_xml:
            f_xml.write(gz_file.read())

        # copy to destination
        
        if not xbmcvfs.copy(tin, fout):
            log('Could not copy to %s' % speicherort, xbmc.LOGERROR)
            return False
        if not xbmcvfs.delete(tin):
            log('Could not delete % s' % tin, xbmc.LOGERROR)
            return False
        notify(lang_string(32040), fout)
        ADDON.setSetting('last_download', str(int(time.time())))
        return True
    else:
        log('Wrong content-type: %s' % ct, xbmc.LOGERROR)
        notify(lang_string(32051), lang_string(32053))
        return False


def takealug_download():
    if choose_epg == lang_string(32011):
        return de_at_ch_premium()
    elif choose_epg == lang_string(32012):
        return easy_epg_premium()
    elif choose_epg == lang_string(32013):
        return zattoo_premium()
    elif choose_epg == lang_string(32014):
        wilmaa_premium()
    elif choose_epg == lang_string(32016):
        return de_at_ch_free()
    elif choose_epg == lang_string(32017):
        return easy_epg_free()
    elif choose_epg == lang_string(32018):
        return zattoo_free()
    elif choose_epg == lang_string(32019):
        return wilmaa_free()
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
            return download_and_move(s, url)


def easy_epg_premium():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1 + '/download/1122/'
        if logged_inpremium == False:
            notify(lang_string(32041) % uc, lang_string(32042), icon=xbmcgui.NOTIFICATION_WARNING)
        elif logged_inpremium == True:
            return download_and_move(s, url)


def zattoo_premium():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1 + '/download/1123/'
        if logged_inpremium == False:
            notify(lang_string(32041) % uc, lang_string(32042), icon=xbmcgui.NOTIFICATION_WARNING)
        elif logged_inpremium == True:
            return download_and_move(s, url)


def wilmaa_premium():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1 + '/download/1124/'
        if logged_inpremium == False:
            notify(lang_string(32041) % uc, lang_string(32042), icon=xbmcgui.NOTIFICATION_WARNING)
        elif logged_inpremium == True:
            return download_and_move(s, url)


def de_at_ch_free():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1 + '/download/1271/'
        return download_and_move(s, url)


def easy_epg_free():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1 + '/download/1125/'
        return download_and_move(s, url)


def zattoo_free():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1 + '/download/1126/'
        return download_and_move(s, url)


def wilmaa_free():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1 + '/download/1127/'
        return download_and_move(s, url)


def worker(next_download):
    dl_attempts = 0
    while not Monitor.waitForAbort(60):
        log('Worker walk through...')
        initiate_download = False

        # check if property 'last_download' in settings already exists and check timestamp of this file.
        # if timestamp is not older than 24 hours, there's nothing to do, otherwise download GZIP.

        try:
            last_timestamp = int(ADDON.getSetting('last_download'))
        except ValueError:
            last_timestamp = 0

        if last_timestamp > 0:
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
            if dl_attempts < 3:
                notify(lang_string(32000), lang_string(32054))
                weblogin.doLogin(datapath, username, password)
                if takealug_download():
                    dl_attempts = 0
                    xbmcvfs.delete(cookie)
                else:
                    dl_attempts += 1
            else:
                # has tried 3x to download files in a row, giving up
                ADDON.setSetting('last_download', str(int(time.time())))
                log("Tried downlad 3x without success", xbmc.LOGERROR)

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

if startup():
    try:
        if sys.argv[1] == 'manual_download':
            if speicherort == 'choose':
                OSD.ok(lang_string(32000), lang_string(32048) % uc)
            elif choose_epg == 'None':
                OSD.ok(lang_string(32000), lang_string(32049) % uc)
            else:
                dialog = xbmcgui.Dialog()
                ret = dialog.yesno(lang_string(32000), lang_string(32050) % choose_epg)
                if ret:
                    manual = True
                    notify('Manual Download', choose_epg)
                    takealug_download()

    except IndexError:
        if auto_download:
            if speicherort == 'choose':
                notify(lang_string(32041) % uc, lang_string(32055), icon=xbmcgui.NOTIFICATION_WARNING)
            elif choose_epg == 'None':
                notify(lang_string(32041) % uc, lang_string(32056), icon=xbmcgui.NOTIFICATION_WARNING)
            else:
                worker(int(ADDON.getSetting('next_download')))

xbmcvfs.delete(cookie)
