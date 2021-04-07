'''
    Cumination
    Copyright (C) 2017 Whitecream, hdgdl, Team Cumination
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
import sqlite3
import json
import re
import xbmc, xbmcgui
import requests
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite('stripchat', '[COLOR hotpink]stripchat.com[/COLOR]', 'http://stripchat.com', 'stripchat.jpg', 'stripchat', True)


@site.register(default_mode=True)
def Main():
    female = True if utils.addon.getSetting("chatfemale") == "true" else False
    male = True if utils.addon.getSetting("chatmale") == "true" else False
    couple = True if utils.addon.getSetting("chatcouple") == "true" else False
    trans = True if utils.addon.getSetting("chattrans") == "true" else False
    site.add_dir('[COLOR red]Refresh Stripchat images[/COLOR]', '', 'clean_database', '', Folder=False)

    bu = "https://stripchat.com/api/external/v4/widget/?limit=1000&modelsCountry=&modelsLanguage=&modelsList=&tag="
    site.add_dir('[COLOR hotpink]HD[/COLOR]', '{0}hd'.format(bu), 'List', '', '')
    if female:
        site.add_dir('[COLOR hotpink]Female[/COLOR]', '{0}female'.format(bu), 'List', '', '')
    if couple:
        site.add_dir('[COLOR hotpink]Couples[/COLOR]', '{0}couples'.format(bu), 'List', '', '')
    if male:
        site.add_dir('[COLOR hotpink]Male[/COLOR]', '{0}men'.format(bu), 'List', '', '')
    if trans:
        site.add_dir('[COLOR hotpink]Transsexual[/COLOR]', '{0}trans'.format(bu), 'List', '', '')
    utils.eod()


@site.register()
def List(url):
    if utils.addon.getSetting("chaturbate") == "true":
        clean_database(False)

    try:
        response = utils.getHtml(url)
    except:
        return None
    data = json.loads(response)
    model_list = data["models"]

    for model in model_list:
        name = utils.cleanhtml(model['username']).encode("ascii", errors="ignore")
        videourl = model['stream']['url']
        img = model['previewUrl'] if utils.addon.getSetting(
            "model_pic") == "0" else model['snapshotUrl']

        site.add_download_link(name, videourl, 'Playvid', img, '', noDownload=True)
    utils.eod()


@site.register(clean_mode=True)
def clean_database(showdialog=True):
    conn = sqlite3.connect(utils.TRANSLATEPATH("special://database/Textures13.db"))
    try:
        with conn:
            list = conn.execute("SELECT id, cachedurl FROM texture WHERE url LIKE '%%%s%%';" % ".stripst.com")
            for row in list:
                conn.execute("DELETE FROM sizes WHERE idtexture LIKE '%s';" % row[0])
                try:
                    os.remove(utils.TRANSLATEPATH("special://thumbnails/" + row[1]))
                except:
                    pass
            conn.execute("DELETE FROM texture WHERE url LIKE '%%%s%%';" % ".stripst.com")
            if showdialog:
                utils.notify('Finished', 'Stripchat images cleared')
    except:
        pass


@site.register()
def Playvid(url, name):
    vp = utils.VideoPlayer(name)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    altUrl = 'https://stripchat.com/api/external/v4/widget/?limit=1&modelsList='
    if requests.get(url).status_code != 200:
        data = json.loads(utils.getHtml(altUrl + name))["models"][0]
        if data["username"] == name:
            url = data['stream']['url']
        else:
            xbmc.executebuiltin("Notification(" + name + ",Couldn\'t find a playable webcam link, ," + xbmc.getInfoImage("ListItem.Thumb") + ")")
            return

    vp.progress.update(75, "[CR]Found Stream[CR]")
    vp = utils.VideoPlayer(name)
    vp.play_from_direct_link(url)


@site.register()
def Refresh():
    xbmc.executebuiltin('Container.Refresh')


@site.register()
def List2(url):
    site.add_download_link('[COLOR red][B]Refresh[/B][/COLOR]', url, 'Refresh', '', '', noDownload=True)
    if utils.addon.getSetting("online_only") == "true":
        url = url + '/?online_only=1'
        site.add_download_link('[COLOR red][B]Show all models[/B][/COLOR]', url, 'online', '', '', noDownload=True)
    else:
        site.add_download_link('[COLOR red][B]Show only models online[/B][/COLOR]', url, 'online', '', '', noDownload=True)

    if utils.addon.getSetting("chaturbate") == "true":
        clean_database(False)
    sess = requests.session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0',
        'Accept': '*/*',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Referer': url,
        'X-Requested-With': 'XMLHttpRequest',
        'DNT': '1',
        'Connection': 'keep-alive',
    }
    data = sess.get(url, headers=headers, verify=False).content
    match = re.compile('class="top_ranks(.+?)class="title_h3', re.I | re.M | re.S).findall(data)
    if not match:
        match = re.compile('class="top_others(.+?)class="title_h3', re.I | re.M | re.S).findall(data)
    match = re.compile('class="top_thumb".+?href="([^"]+)".+?src="([^"]+)".+?class="mn_lc">(.+?)</span>', re.I | re.M | re.S).findall(match[0])
    for url, img, name in match:
        if 'profile' in url:
            name = '[COLOR hotpink][Offline][/COLOR] ' + name
            url = "  "
        site.add_download_link(name, url[1:], 'Playvid', 'https:' + img, '')
    utils.eod()

@site.register()
def List3(url):
    site.add_download_link('[COLOR red][B]Refresh[/B][/COLOR]', url, 'Refresh', '', '', noDownload=True)
    if utils.addon.getSetting("online_only") == "true":
        url = url + '/?online_only=1'
        site.add_download_link('[COLOR red][B]Show all models[/B][/COLOR]', url, 'online', '', '', noDownload=True)
    else:
        site.add_download_link('[COLOR red][B]Show only models online[/B][/COLOR]', url, 'online', '', '', noDownload=True)

    if utils.addon.getSetting("chaturbate") == "true":
        clean_database(False)
    sess = requests.session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0',
        'Accept': '*/*',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Referer': url,
        'X-Requested-With': 'XMLHttpRequest',
        'DNT': '1',
        'Connection': 'keep-alive',
    }
    data = sess.get(url, headers=headers, verify=False).content
    match = re.compile('class="top_ranks(.+?)trs_actions', re.I | re.M | re.S).findall(data)
    match = re.compile('class="top_thumb".+?href="([^"]+)".+?src="([^"]+)".+?class="mn_lc">(.+?)</span>', re.I | re.M | re.S).findall(match[0])
    for url, img, name in match:
        if 'profile' in url:
            name = '[COLOR hotpink][Offline][/COLOR] ' + name
            url = "  "
        site.add_download_link(name, url[1:], 'Playvid', 'https:' + img, '')
    utils.eod()

@site.register()
def online(url):
    if utils.addon.getSetting("online_only") == "true":
        utils.addon.setSetting("online_only", "false")
    else:
        utils.addon.setSetting("online_only", "true")
    xbmc.executebuiltin('Container.Refresh')
