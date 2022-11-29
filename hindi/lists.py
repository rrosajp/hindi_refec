# -*- coding: utf-8 -*-

import datetime
import base64
import json
import re
import traceback
from urllib.parse import urlencode

from modules import dom_parser

try:
    from modules.kodi_utils import logger, build_url, addon_icon, make_listitem, set_info,  notification, add_items, set_content, end_directory, set_view_mode, get_infolabel
    from modules.utils import normalize
    from indexers.hindi.live_client import scrapePage, agent, read_write_file, string_escape
    from caches.h_cache import main_cache
except:
    # logger(f'import Exception: {traceback.print_exc()}')
    from modules.utils import logger, normalize
    from modules.live_client import scrapePage, agent, read_write_file, string_escape
    from modules.h_cache import main_cache
    import os
selective = [{"title": "Fox 5 Atlanta (WAGA)", "url": "https://lnc-waga-fox-aws.tubi.video/index.m3u8", "poster": "https://i.imgur.com/qdYfhpZ.jpg", "action": "ltp_pluto"},
    {"title": "Fox 5 Atlanta GA (WAGA-TV)", "url": "https://csm-e-eb.csm.tubi.video/csm/extlive/tubiprd01,p-WAGA-Monetizer.m3u8", "action": "ltp_pluto"},
    {"title": "Fox Atlanta-GA (WAGA-DT1)", "url": "https://trn10.tulix.tv/WAGA-FOX/index.m3u8", "action": "ltp_pluto"},
    {"title": "Fox Weather", "url": "https://csm-e-eb.csm.tubi.video/csm/extlive/tubiprd01,Fox-Weather.m3u8", "action": "ltp_pluto"},
    {"title": "Fox Weather", "url": "https://live-news-manifest.tubi.video/live-news-manifest/csm/extlive/tubiprd01,Fox-Weather.m3u8", "action": "ltp_pluto"},
    {"title": "Fox Weather", "url": "https://247wlive.foxweather.com/stream/index.m3u8", "poster": "https://i.imgur.com/ojLdgOg.png", "action": "ltp_pluto"}
]

def youtube_m3u(params):
    ch_name = params['list_name']
    rescrape = params['rescrape']
    iconImage = params['iconImage']
    params = {'ch_name': ch_name, 'rescrape': rescrape, 'iconImage': iconImage}
    cache_name = f"content_list_youtube_m3u_{ch_name}{urlencode(params)}"
    list_data = None
    if rescrape == 'true': main_cache.delete(cache_name)
    else: list_data = main_cache.get(cache_name)
    # logger(f"from cache list_data: {list_data}")
    if not list_data:
        # uri = "https://raw.githubusercontent.com/benmoose39/YouTube_to_m3u/main/youtube.m3u"
        # page = scrapePage(uri).text
        # list_data = m3u2list(normalize(page))
        uri = "https://raw.githubusercontent.com/djp11r/repo_n/mayb/etc/allxml/youtub_live.json"
        data = scrapePage(uri).text
        list_data = json.loads(data)
        # logger(f"new list_data: {list_data}")
        if list_data: main_cache.set(cache_name, list_data, expiration=datetime.timedelta(hours=12))
    from sys import argv # some functions like ActivateWindow() throw invalid handle less this is imported here.
    handle = int(argv[1])
    if list_data:
        item_list = list(_process(list_data, 'youtube_m3u'))
        add_items(handle, item_list)
        set_content(handle, 'episodes')
        end_directory(handle)
        set_view_mode('view.episodes', 'episodes')
    else:
        notification(f'No links Found for: :{ch_name} Retry', 900)
        end_directory(handle)
        return


def m3u2list(result):
    nondesiralbe = ('Marathi', 'Malayalam', 'Tamil', 'Urdu', 'Albania', 'Exyu', 'Telugu', 'Kannada', 'Odisha', 'Malayalam', 'Radio', 'Türk', 'East Africa', 'France', 'Pakistan', 'Taiwan News', 'Music')
    matches = re.compile('^#EXTINF:-?[0-9]*(.*?),([^\"]*?)\n(.*?)$', re.M).findall(result)
    li = []
    for params, display_name, url in matches:
        item_data = {"params": params, "display_name": display_name.strip(), "url": url.strip()}
        li.append(item_data)
    chList = []
    for channel in li:
        item_data = {"title": channel["display_name"], "url": channel["url"], "poster":  "icon.png", "action": "ltp_pluto"}
        matches = re.compile(' (.*?)="(.*?)"').findall(channel["params"])
        desirable = True
        for field, value in matches:
            field = field.strip().lower().replace('-', '_')
            if field == 'tvg_logo':
                field = 'poster'
                if value == "": value = "icon.png"
            if field == 'group_title' and value.strip() in nondesiralbe:
                desirable = False
            # logger(f"field: {field} value: {value}")
            item_data[field] = value.strip()
        if desirable: chList.append(item_data)
    return chList


def pluto(params):
    cache_name = "content_list_pluto_"
    list_data = None
    if params['rescrape'] == 'true': main_cache.delete(cache_name)
    else: list_data = main_cache.get(cache_name)

    if not list_data:
        # uri = 'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL1RlbXBlc3QwNTgwL3htbC9tYXN0ZXIvcGx1dG8ubTN1'
        # try: uri = base64.b64decode(uri.encode('ascii')).decode('ascii')
        # except: uri = base64.b64decode(uri.encode('ascii'))
        uri = "https://raw.githubusercontent.com/djp11r/repo_n/mayb/etc/allxml/pluto.json"
        data = scrapePage(uri).text
        list_data = json.loads(data)
        # uri = "https://raw.githubusercontent.com/Tempest0580/xml/master/webos.m3u8"
        # uri = "https://raw.githubusercontent.com/Tempest0580/xml/master/pluto.m3u"
        # page = scrapePage(uri).text
        # list_data = m3u2list(page)
        if list_data: main_cache.set(cache_name, list_data, expiration=datetime.timedelta(hours=36))
    # else:
        # with open(pluto_chennel, 'r') as f:
            # page = json.load(f)

    from sys import argv # some functions like ActivateWindow() throw invalid handle less this is imported here.
    handle = int(argv[1])
    add_items(handle, list(_process(list_data, 'pluto')))
    set_content(handle, 'episodes')
    end_directory(handle)
    set_view_mode('view.episodes', 'episodes')


def indian_live(params):
    cache_name = "content_list_indian_live"
    list_data = None
    if params['rescrape'] == 'true': main_cache.delete(cache_name)
    else: list_data = main_cache.get(cache_name)

    if not list_data:
        # uri = 'https://raw.githubusercontent.com/Vikassm73/AjaykRepo/main/Zips/India.m3u'
        # page = scrapePage(uri).text
        # # page = read_write_file(file_n='raw.githubusercontent.com.html')
        # # with open(pluto_chennel1, 'r', encoding='utf-8') as f:
            # # page = f.read()
        # list_data = m3u2list(page)
        uri = "https://raw.githubusercontent.com/djp11r/repo_n/mayb/etc/allxml/indian_live.json"
        data = scrapePage(uri).text
        list_data = json.loads(data)
        if list_data: main_cache.set(cache_name, list_data, expiration=datetime.timedelta(hours=36))
        # logger(f'page: {page}')
    # else:
        # with open(pluto_chennel, 'r') as f:
            # page = json.load(f)
    # logger(f'total: {len(page)} page: {page}')
    from sys import argv # some functions like ActivateWindow() throw invalid handle less this is imported here.
    handle = int(argv[1])
    add_items(handle, list(_process(list_data, 'indian_live')))
    set_content(handle, 'episodes')
    end_directory(handle)
    set_view_mode('view.episodes', 'episodes')


def _process(list_data, provider):
    if provider == 'indian_live': list_data = selective + list_data
    for i in list_data:
        # logger(f"lists _process item: {item}")
        listitem = make_listitem()
        name = i['title']
        poster = i.get('poster', '')
        thumb = i['poster'] if poster.startswith('http') else addon_icon
        url_params = {'mode': i['action'], 'title': name, 'url': i['url'], 'provider': provider}
        url = build_url(url_params)
        options_params = {'mode': 'options_menu_choice', 'suggestion': name, 'play_params': json.dumps(url_params)}
        cm = [("[B]Options...[/B]", f'RunPlugin({build_url(options_params)})')]
        listitem.setLabel(name)
        listitem.addContextMenuItems(cm)
        listitem.setArt({'thumb': thumb})
        i.update({'imdb_id': name, 'mediatype': 'episode', 'episode': 1, 'season': 0})
        setUniqueIDs = {'imdb': str(name)}
        listitem = set_info(listitem, i, setUniqueIDs)
        yield url, listitem, False
    return


def play(params):
    # logger(f'play params "{params}"')
    url = params['url']
    try:
        if params['provider'] == 'pluto':
            if 'm3u8' in url:
                url = f'{url}|User-Agent={agent()}&Referer={url}'
        elif params['provider'] == 'youtube_m3u':
            # logger(f'--- Playing title: {params["title"]} url: {params["url"]}')
            cache_name = f"content_list_play_{params['url']}"
            url = main_cache.get(cache_name)
            if not url or 'benmoose39' in url:
                url = get_m3u8_url(params['url'])
                if url: main_cache.set(cache_name, url, expiration=datetime.timedelta(hours=3))
        else: url = f'{url}|User-Agent={agent()}' #url = f'{url}|User-Agent={agent()}&Upgrade-Insecure-Requests=1'
        logger(f'--- Playing "{params["title"]}". {url}')
        from modules.player import infinitePlayer
        # infoLabels = {'title': params['title']}
        infinitePlayer().run(url, 'video', {'title': params['title']})
    except:
        logger(f'play provider: {params["provider"]} - Exception: {traceback.print_exc()}')
        return


def get_videoId(from_func, response):
    vars_ = re.compile(r'var ytInitialData =.*?[\'|"|{](.+)[\'|"|}][,;]</script>').findall(response)
    # logger(f"vars_>>> : {vars_}")
    ytInitialData = string_escape(vars_[0])
    # logger(f"ytInitialData: {ytInitialData}")
    videoId = re.findall(r'(compactvideoRenderer|videoRenderer)\":\{\"videoId\":\"(.+?)\",', ytInitialData, re.IGNORECASE)
    logger(f"from_func: {from_func} videoId: {videoId}")
    return videoId


def get_playlist_video_url(url):
    # logger(f"get_m3u8_url url: {url}")
    url = f'{url}/videos'
    response = scrapePage(url).text
    # response = read_write_file('www.youtube.com.html')
    # response = to_utf8(response)
    # logger(response)
    videoId = get_videoId('get_playlist_video_url', response)
    return f'https://www.youtube.com/watch?v={videoId[0][1]}'


def get_m3u8_url(url):
    # logger(f"get_m3u8_url url: {url}")
    response = scrapePage(url).text
    if videoId := get_videoId('get_m3u8_url', response):
        live_yturl = f'https://www.youtube.com/watch?v={videoId[0][1]}'
    else:
        live_yturl = get_playlist_video_url(url)
    # logger(f"live_yturl: {live_yturl}")
    response = scrapePage(live_yturl).text
    # logger(f'<<<--->>> \n{response}\n<<<--->>>')
    if '.m3u8' not in response:
        live_yturl = get_playlist_video_url(url)
        response = scrapePage(live_yturl).text
        # logger(f'wget <<<--->>> \n{response}\n<<<--->>>')
    if '.m3u8' not in response:
        return 'https://raw.githubusercontent.com/benmoose39/YouTube_to_m3u/main/assets/moose_na.m3u'

    end = response.find('.m3u8') + 5
    tuner = 100
    while True:
        if 'https://' in response[end - tuner: end]:
            link = response[end - tuner: end]
            start = link.find('https://')
            end = link.find('.m3u8') + 5
            break
        else: tuner += 5
    return link[start: end]


def m3u2list(response, chList):
    matches = re.compile('^#EXTINF:-?[0-9]*(.*?),([^\"]*?)\n(.*?)$', re.M).findall(response)
    li = []
    for params, display_name, url in matches:
        display_name = display_name.strip()
        # logger(f'display_name: {display_name}')
        display_name = display_name.replace('$ ', '')
        if url != '':
            item_data = {"params": params, "title": display_name.strip(), "url": url.strip()}
            li.append(item_data)
    for channel in li:
        item_data = {"action": "ltp_pluto", "title": (channel["title"]), "url": channel["url"]}
        matches = re.compile(' (.*?)="(.*?)"').findall(channel["params"])
        for field, value in matches:
            if field == 'tvg-logo':
                value = value.strip()
                if value is None or value == 'logo N/A' or value == '.': value = ''
                elif value.endswith('.png') or not value.endswith('.jpg'): value = value
            item_data[field.strip().lower().replace('-', '_')] = value.strip()
        if 'tvg_logo' not in item_data:
            item_data['tvg_logo'] = ''
        chList.append(item_data)
    #logger(f'chList: {chList}')
    return chList


def get_redjoyiptv_list(params):
    # url = 'https://embed.castamp.com/ArchieIPL'
    url = 'https://redjoyiptv.co/ipl-crickethindi.m3u8'
    response = scrapePage(url).text
    # response = read_write_file('crickethindi.m3u8')
    logger(f'response: {response}')
    matches = re.compile('^https([^\'"]+.m3u8)$', re.M).findall(response)
    from sys import argv # some functions like ActivateWindow() throw invalid handle less this is imported here.
    handle = int(argv[1])
    try:
        url = f'https{matches[0]}'
        # logger(f'matches: https{matches[0]}')
        # response = scrapePage(url).text
        # ch_list = m3u2list(response, [])
        ch_list = [{"action": "ltp_pluto", "title": "IPL Cricket", "url": url}]
        add_items(handle, list(_process(ch_list, 'redjoyiptv_list')))
        set_content(handle, 'episodes')
        end_directory(handle)
        set_view_mode('view.episodes', 'episodes')
    except:
        notification(f'No links Found matches :{matches} Retry', 900)
        end_directory(handle)
        return

# if __name__ == "__main__":
    # response = read_write_file('neff.m3u8')
    # m3u2list(response, [])
    #get_redjoyiptv_list()
#     # import random
#     # indian_live()
#     # get_vardata()
#     # with open('list_data/youtub_live.json', 'r', encoding='utf-8') as f:
#     #     page = json.load(f)
#     # item = random.choice(page)
#     # logger(item)
#     # logger(f"final url: {item['url']}")
#     item = {'url': "https://www.youtube.com/channel/UCBAvMHZO3BIfMMhOK9LMOYQ"}
#     url = get_m3u8_url(item['url'])
#     logger(f"final url: {url}")
