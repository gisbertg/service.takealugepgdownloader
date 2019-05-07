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

usrsettings = xbmcaddon.Addon(id="service.takealugepgdownloader")
speicherort = usrsettings.getSetting("path").decode('utf-8')
server1 = 'https://takealug.de/wordpress'
username = usrsettings.getSetting('username')
uc = username.capitalize()
password = usrsettings.getSetting('password')
choose_epg = usrsettings.getSetting('choose_epg')
auto_download = usrsettings.getSetting('auto_download')
timeswitch = usrsettings.getSetting('timeswitch')
datapath = xbmc.translatePath(usrsettings.getAddonInfo('profile'))
cookie = os.path.join(datapath, "cookies.lwp")
temp = os.path.join(datapath, "temp")
hidesuccess = usrsettings.getSetting('hide-successful-login-messages')

# deal with setting 'next_download' which not exists at first time
try:
    next_download = int(usrsettings.getSetting('next_download'))
except ValueError:
    usrsettings.setSetting('next_download', '0')

OSD = xbmcgui.Dialog()
Monitor = xbmc.Monitor()

def notify(title, message, icon=xbmcgui.NOTIFICATION_INFO):
    OSD.notification(title, message, icon)


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
    xbmcvfs.delete(cookie)
    notify('Guide Stored', speicherort)

def LOGIN(username,password,hidesuccess):
        uc = username[0].upper() + username[1:]
        lc = username.lower()
        
        logged_inpremium = weblogin.doLoginPremium(datapath, username, password)
        
        if logged_inpremium == True:
            if hidesuccess == 'false':
                notify('Welcome back %s' % uc, 'Thank you for donating!')
                
        elif logged_inpremium == False:
            logged_in = weblogin.doLogin(datapath, username, password)
        
            if logged_in == True:
                if hidesuccess == 'false':
                    notify('Welcome back %s' % uc, 'Takealug say hello')
                
            elif logged_in == False:
                notify('Login Failure', '%s could not login' % uc)
    
logged_inpremium = weblogin.doLoginPremium(datapath, username, password)
    
                
def STARTUP_ROUTINES():
        # deal with bug that happens if the datapath and/or temp doesn't exist
        if not os.path.exists(temp):
            os.makedirs(temp)

        # get username and password and do login with them
        # also get whether to hid successful login notification
        LOGIN(username,password,hidesuccess)


STARTUP_ROUTINES()


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
            if hidesuccess == 'false':
                notify('Sorry %s' % uc, 'You need Premium Membership for this File', icon=xbmcgui.NOTIFICATION_WARNING)
        elif logged_inpremium == True:
            download_and_move(s, url)


def easy_epg_premium():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1+'/download/1122/'
        if logged_inpremium == False:
            if hidesuccess == 'false':
                notify('Sorry %s' % uc, 'You need Premium Membership for this File', icon=xbmcgui.NOTIFICATION_WARNING)
        elif logged_inpremium == True: 
            download_and_move(s, url)


def zattoo_de_premium():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1+'/download/1123/'
        if logged_inpremium == False:
            if hidesuccess == 'false':
                notify('Sorry %s' % uc, 'You need Premium Membership for this File', icon=xbmcgui.NOTIFICATION_WARNING)
        elif logged_inpremium == True: 
            download_and_move(s, url)


def zattoo_ch_premium():
    with requests.Session() as s:
        s.cookies = LWPCookieJar(cookie)
        s.cookies.load(ignore_discard=True)
        url = server1+'/download/1124/'
        if logged_inpremium == False:
            if hidesuccess == 'false':
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


#Download Files
def AUTO():
    logged_in = weblogin.doLogin(datapath, username, password)
    if logged_in == True:
        if speicherort == 'choose': 
            notify('Sorry %s' % uc, 'You need to choose your Downloadlocation first', icon=xbmcgui.NOTIFICATION_WARNING)
        else:
            if choose_epg == 'None':
                notify('Sorry %s' % uc, 'You need to choose your EPG first', icon=xbmcgui.NOTIFICATION_WARNING)
            else:
                if auto_download == 'true':
                    notify('Auto-Download', choose_epg)
                    takealug_download()

if auto_download == 'true':
    AUTO()

def manual_download():
    manual_download = False
    try:
        if sys.argv[1:][0] == 'manual_download':
            manual_download = True
    except:
        pass
    return manual_download

if manual_download() == True:
    logged_in = weblogin.doLogin(datapath, username, password)
    if logged_in == True:
        if speicherort == 'choose': 
            notify('Sorry %s' % uc, 'You need to choose your Downloadlocation first', icon=xbmcgui.NOTIFICATION_WARNING)
        else:
            if choose_epg == 'None':
                notify('Sorry %s' % uc, 'You need to choose your EPG first', icon=xbmcgui.NOTIFICATION_WARNING)
            else:
                dialog = xbmcgui.Dialog()
                ret = dialog.yesno('Takealug EPG Downloader', 'Start Manual Download')
                if ret:
                    manual = True
                    notify('Manual Download', choose_epg)
                    takealug_download()          

def worker():
    while not Monitor.waitForAbort(60):
        initiate_download = False

        # check if guide.gz already exists and check timestamp of this file.
        # if timestamp not older than 24 hours, there's nothing to do

        if os.path.exists(os.path.join(temp, 'guide.gz')):
            if (int(time.time()) - 86400) < os.path.getmtime(os.path.join(temp, 'guide.gz')) < int(time.time()):
                pass
            elif next_download < int(time.time()):

                # suggested download time has passed (e.g. system was offline) or time is now, download epg
                # and set a new timestamp for the next download

                initiate_download = True
        else:
            initiate_download = True

        if initiate_download:

            takealug_download()
            next_download = datetime.datetime.now()
            next_download.replace(hour=timeswitch, minute=0, second=0, microsecond=0)
            usrsettings.setSetting('next_download', next_download.strftime("%s"))

if timeswitch == 'true':
    logged_in = weblogin.doLogin(datapath, username, password)
    if logged_in == True:
        if speicherort == 'choose': 
            notify('Sorry %s' % uc, 'You need to choose your Downloadlocation first', icon=xbmcgui.NOTIFICATION_WARNING)
        else:
            if choose_epg == 'None':
                notify('Sorry %s' % uc, 'You need to choose your EPG first', icon=xbmcgui.NOTIFICATION_WARNING)
            else:
                worker()
