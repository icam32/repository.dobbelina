'''
    Cumination
    Copyright (C) 2021 Team Cumination

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

import re
from resources.lib import utils
from resources.lib.decrypters.kvsplayer import kvs_decode
from resources.lib.adultsite import AdultSite
import xbmc
from six.moves import urllib_parse
from kodi_six import xbmcgui, xbmcplugin

site = AdultSite('kissjav', '[COLOR hotpink]Kiss JAV[/COLOR]', 'https://kissjav.com/', 'kissjav.png', 'kissjav')


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', site.url + 'categories/', 'Categories', site.img_cat)
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + 'search/', 'Search', site.img_search)
    List(site.url + 'latest-updates/')
    utils.eod()


@site.register()
def List(url):
    html = utils.getHtml(url, site.url)

    delimiter = '<div class="item'
    re_videopage = 'href="([^"]+)"'
    re_name = 'title="([^"]+)"'
    re_img = 'src="([^"]+)"'
    re_duration = 'duration">([^<]+)<'
    re_quality = 'class="is-hd">(HD)<'
    utils.videos_list(site, 'kissjav.Playvid', html, delimiter, re_videopage, re_name, re_img, re_quality, re_duration)

    match = re.search(r'class="page-current"><span>(\d+)<.+?class="next">.+?data-block-id="([^"]+)"\s+data-parameters="([^"]+)">Next', html, re.DOTALL | re.IGNORECASE)
    if match:
        npage = int(match.group(1)) + 1
        block_id = match.group(2)
        params = match.group(3).replace(';', '&').replace(':', '=')
        nurl = url.split('?')[0] + '?mode=async&function=get_block&block_id={0}&{1}'.format(block_id, params)
        lpnr, lastp = None, ''
        match = re.search(r':(\d+)">Last', html, re.DOTALL | re.IGNORECASE)
        if match:
            lpnr = match.group(1)
            lastp = '/{}'.format(lpnr)
        nurl = nurl.replace('+from_albums', '')
        nurl = re.sub(r'&from([^=]*)=\d+', r'&from\1={}'.format(npage), nurl)

        cm_page = (utils.addon_sys + "?mode=javbangers.GotoPage" + "&url=" + urllib_parse.quote_plus(nurl) + "&np=" + str(npage) + "&lp=" + str(lpnr))
        cm = [('[COLOR violet]Goto Page #[/COLOR]', 'RunPlugin(' + cm_page + ')')]

        site.add_dir('[COLOR hotpink]Next Page...[/COLOR] (' + str(npage) + lastp + ')', nurl, 'List', site.img_next, contextm=cm)
    utils.eod()


@site.register()
def GotoPage(list_mode, url, np, lp):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, 'Enter Page number')
    if pg:
        if url.endswith('/{}/'.format(np)):
            url = url.replace('/{}/'.format(np), '/{}/'.format(pg))
        if int(lp) > 0 and int(pg) > int(lp):
            utils.notify(msg='Out of range!')
            return
        contexturl = (utils.addon_sys + "?mode=" + str(list_mode) + "&url=" + urllib_parse.quote_plus(url))
        xbmc.executebuiltin('Container.Update(' + contexturl + ')')


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url)
    match = re.compile(r'class="item" href="([^"]+)" title="([^"]+)".+?(?:src="([^"]+)"|>no image<)(.+?)</a>', re.IGNORECASE | re.DOTALL).findall(cathtml)
    for caturl, name, img, data in match:
        img = img.replace(' ', '%20')
        name = utils.cleantext(name)
        if '/categories/' in url:
            name = name.capitalize()
        if 'videos">' in data:
            match = re.compile(r'videos">([^<]+)<', re.IGNORECASE | re.DOTALL).findall(data)
            name = name + ' [COLOR cyan][{}][/COLOR]'.format(match[0])
        site.add_dir(name, caturl, 'List', img)
    re_npurl = r'class="next"><a href="([^"]+)"'
    re_npnr = r'class="next"><a href="[^"]+/(\d+)/"'
    re_lpnr = r'class="last"><a href="[^"]+/(\d+)/"'
    utils.next_page(site, 'heroero.Categories', cathtml, re_npurl, re_npnr, re_lpnr=re_lpnr, contextm='heroero.GotoPage')
    if '/categories/' in url:
        xbmcplugin.addSortMethod(utils.addon_handle, xbmcplugin.SORT_METHOD_TITLE)
    utils.eod()


@site.register()
def Playlists(url):
    cathtml = utils.getHtml(url, site.url)
    match = re.compile(r'<div\s*id="playlist-\d+.+?data-src="([^"]+).+?href="([^"]+)[^>]+>([^<]+).+?video"[^\d]+(\d+)', re.IGNORECASE | re.DOTALL).findall(cathtml)
    for img, caturl, name, count in match:
        name = utils.cleantext(name) + ' [COLOR hotpink]({0} videos)[/COLOR]'.format(count)
        if caturl.startswith('/'):
            caturl = site.url[:-1] + caturl
        site.add_dir(name, caturl, 'List', site.url[:-1] + img)

    nextp = re.compile(r'<a href="([^"]+)"\s*class="pagination-next">', re.DOTALL | re.IGNORECASE).search(cathtml)
    if nextp:
        np = nextp.group(1)
        if np.startswith('/'):
            np = site.url[:-1] + np
        curr_pg = re.findall(r'class="pagination-link\s*is-current[^>]+>([^<]+)', cathtml)[0]
        last_pg = re.findall(r'class="pagination-link[^>]+>([^<]+)', cathtml)[-1]
        site.add_dir('[COLOR hotpink]Next Page[/COLOR] (Currently in Page {0} of {1})'.format(curr_pg, last_pg), np, 'Playlists', site.img_next)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        url = url + keyword.replace(' ', '+') + '/'
        List(url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    html = utils.getHtml(url)
    surl = re.search(r"video_url:\s*'([^']+)'", html)
    if surl:
        surl = surl.group(1)
        if surl.startswith('function/'):
            license = re.findall(r"license_code:\s*'([^']+)", html)[0]
            surl = kvs_decode(surl, license)
    else:
        vp.progress.close()
        return
    vp.progress.update(75, "[CR]Video found[CR]")
    vp.play_from_direct_link(surl)
