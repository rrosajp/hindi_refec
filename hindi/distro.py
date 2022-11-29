# -*- coding: utf-8 -*-
import datetime
import json
import os
import re

import requests

# from urllib.parse import quote_plus, urlencode
try:
    from indexers.hindi.live_client import agent, read_write_file
    from modules.kodi_utils import logger, build_url, make_listitem, set_info, addon_fanart, add_items, set_content, end_directory, set_view_mode, get_infolabel, addon_fanart, item_next
    from caches.h_cache import main_cache
except:
    from modules.live_client import agent, read_write_file
    from modules.utils import logger
    from modules.h_cache import main_cache
    from modules.utils import to_utf8, normalize

headers = {'authority': 'tv.jsrdn.com',
           'accept': 'application/json, text/javascript, */*; q=0.01',
           'sec-fetch-dest': 'empty',
           'user-agent': agent(),
           'origin': 'https://www.distro.tv',
           'sec-fetch-site': 'cross-site',
           'sec-fetch-mode': 'cors',
           'referer': 'https://www.distro.tv/live',
           'accept-language': 'en-US,en;q=0.9'}
base_url = "https://tv.jsrdn.com/tv_v5/getfeed.php"
payload = {}


def _process(list_data):
    for i in list_data:
        cm = []
        cm_append = cm.append
        title = i['title']
        try:
            thumb = icon = i['meta']['poster']
            if thumb == '': thumb = icon = addon_fanart
        except: thumb = icon = addon_fanart
        url_params = {'mode': i['mode'], 'title': title, 'url': i['url'], 'list_name': i['list_name']}
        # logger(f"distro _process url_params: {url_params}")
        url = build_url(url_params)
        options_params = {'mode': 'options_menu_choice', 'suggestion': title, 'play_params': url}
        cm_append(("[B]Options...[/B]", f'RunPlugin({build_url(options_params)})'))
        try: 
            year = i['meta']['year']
            year = re.search(r'\d{4}', year).group()
        except: year = 0000
        try: rating = i['meta']['rating']
        except: rating = ''
        try: duration = i['meta']['duration']
        except: duration = 0
        try: genre = i['meta']['genre']
        except: genre = ''
        try: plot = i['meta']['plot']
        except: plot = ''
        is_folder = i['isFolder']
        if 'Next Page:' in title:
            icon = thumb = item_next
            info = {'plot': f'Go To {title}...:'}
        else:
            info = {"title": title, "plot": plot, "rating": rating, "year": year, "duration": duration, "genre": genre}
        # logger(f"distro _process info: {info}")
        listitem = make_listitem()
        listitem.setLabel(title)
        listitem.addContextMenuItems(cm)
        listitem.setArt({'icon': icon, 'poster': thumb, 'thumb': thumb, 'clearart': thumb, 'clearlogo': thumb})
        info.update({'imdb_id': title, 'mediatype': 'episode', 'episode': 1, 'season': 0})
        setUniqueIDs = {'imdb': str(title)}
        listitem = set_info(listitem, info, setUniqueIDs)
        yield url, listitem, is_folder
    return


def get_distro_data():
    # cache_name = "content_list_distro_data"
    # distro_data = main_cache.get(cache_name)
    # if not distro_data:
        # distro_data = get_data_from_web()
        # main_cache.set(cache_name, distro_data, expiration=datetime.timedelta(hours=168))  # 1 days cache
        # return distro_data
    distro_data = get_data_from_web()
    return distro_data


def _distro_live_vod(list_name):
    data = get_distro_data()
    topics = data['topics']
    distro_items = []
    title_list = []
    for t in topics:
        title = t['title']
        Type = t['type']
        if Type == list_name:
            # logger(title)
            title_list.append(title)
            distro_items.append({'list_name': list_name, 'url': title, 'isFolder': True, 'mode': 'distro_get_items', 'title': title, 'meta': {'year': '', 'poster': '', 'plot': '', 'genre': ''}})
        elif Type == list_name:
            # logger(t)
            title_list.append(title)
            distro_items.append({'list_name': list_name, 'url': title, 'isFolder': True, 'mode': 'distro_get_items', 'title': title, 'meta': {'year': '', 'poster': '', 'plot': '', 'genre': ''}})  # addDir(title, title, 3, addon_icon, addon_fanart, title)
    return distro_items


def get_live_vod(params):
    list_name = params['list_name']
    cache_name = f"content_list_distro_live_vod_{list_name}"
    distro_items = main_cache.get(cache_name)
    if not distro_items:
        distro_items = _distro_live_vod(list_name)
        main_cache.set(cache_name, distro_items, expiration=datetime.timedelta(hours=24))  # 1 days cache
    from sys import argv
    handle = int(argv[1])
    add_items(handle, list(_process(distro_items)))
    set_content(handle, 'movies')
    end_directory(handle)
    set_view_mode('view.movies', 'movies')


def _distro_live_cats(url, list_name):
    data = get_distro_data()
    topics = data['topics']
    distro_items = []
    for t in topics:
        title = t['title']
        Type = t['type']
        if Type == "live":
            if url == title:
                # logger(t)
                shows = t['shows']
                for s in shows:
                    s = str(s)
                    # logger(s)
                    Show = data['shows'][s]['title']  #.encode('utf-8')
                    rating = data['shows'][s]['rating']
                    summary = data['shows'][s]['description']  #.encode('utf-8')
                    image = data['shows'][s]['img_thumbv']
                    # fanart = data['shows'][s]['img_poster']
                    genre = data['shows'][s]['genre']
                    year = data['shows'][s]['pubdate']
                    # res = s + "**" + fanart
                    # logger(res)
                    link = data['shows'][s]['seasons'][0]['episodes'][0]['content']['url']
                    # logger(title)
                    distro_items.append({'list_name': list_name, 'url': link, 'isFolder': False, 'mode': 'distro_pls', 'title': Show, 'meta': {'year': year, 'poster': image, 'plot': summary, 'genre': genre, 'rating': rating}, })  # addDirVid(Show, link, 101, image, fanart, summary)
    return distro_items


def live_cats(params):
    url = params['url']
    list_name = params['list_name']
    cache_name = f"content_list_distro_live_cats_{url}_{list_name}"
    distro_items = main_cache.get(cache_name)
    if not distro_items:
        distro_items = _distro_live_cats(url, list_name)
        main_cache.set(cache_name, distro_items, expiration=datetime.timedelta(hours=24))  # 1 days cache
    # logger(distro_items)
    # logger(title_list)
    from sys import argv
    handle = int(argv[1])
    add_items(handle, list(_process(distro_items)))
    set_content(handle, 'movies')
    end_directory(handle)
    set_view_mode('view.movies', 'movies')


def _distro_vod_cats(url, list_name):
    data = get_distro_data()
    topics = data['topics']
    distro_items = []
    for t in topics:
        title = t['title']
        Type = t['type']
        if Type == "vod":
            # logger(t)
            if url == title:
                shows = t['shows']
                # logger(shows)
                for s in shows:
                    s = str(s)
                    Show = data['shows'][s]['title']  #.encode('utf-8')
                    rating = data['shows'][s]['rating']
                    summary = data['shows'][s]['description']  #.encode('utf-8')
                    image = data['shows'][s]['img_thumbv']
                    # fanart = data['shows'][s]['img_poster']
                    # genre = data['shows'][s]['genre']
                    year = data['shows'][s]['pubdate']
                    episodes = data['shows'][s]['seasons'][0]['episodes']
                    res = "%s**%s" % (s, image)
                    if len(episodes) > 1:
                        # addDir(Show, res, 5, image, fanart, summary)
                        distro_items.append({'list_name': list_name, 'url': res, 'isFolder': True, 'mode': 'distro_get_items', 'title': Show, 'meta': {'year': year, 'poster': image, 'plot': summary, 'genre': '', 'rating': rating}})

                    else:
                        link = data['shows'][s]['seasons'][0]['episodes'][0]['content']['url']
                        duration = data['shows'][s]['seasons'][0]['episodes'][0]['content']['duration']
                        # addDirVid(Show, link, 101, image, fanart, summary)
                        distro_items.append({'list_name': list_name, 'url': link, 'isFolder': False, 'mode': 'distro_pls', 'title': Show, 'meta': {'duration': duration, 'year': year, 'poster': image, 'plot': summary, 'genre': '', 'rating': rating}})
    return distro_items


def vod_cats(params):
    url = params['url']
    list_name = params['list_name']
    cache_name = f"content_list_distro_vod_cats_{url}_{list_name}"
    distro_items = main_cache.get(cache_name)
    if not distro_items:
        distro_items = _distro_vod_cats(url, list_name)
        main_cache.set(cache_name, distro_items, expiration=datetime.timedelta(hours=24))  # 1 days cache
    # logger(distro_items)
    from sys import argv
    handle = int(argv[1])
    add_items(handle, list(_process(distro_items)))
    set_content(handle, 'tvshows')
    end_directory(handle)
    set_view_mode('view.tvshows', 'tvshows')


def _distro_seasons(sid, list_name):
    distro_items = []
    data = get_distro_data()
    try: episodes = data['shows'][sid]['seasons'][0]['episodes']
    except: return distro_items
    # logger("distro_seasons episodes: {}".format(episodes))
    for e in episodes:
        title = e['title'].encode('utf-8')
        image = e['img_thumbh']
        summary = e['description'].encode('utf-8')
        link = e['content']['url']
        duration = e['content']['duration']
        # addDirVid(title, link, 101, image, fanart, summary)
        distro_items.append({'list_name': list_name, 'url': link, 'isFolder': False, 'mode': 'distro_pls', 'title': title, 'meta': {'duration': duration, 'year': '', 'poster': image, 'plot': summary, 'genre': '', 'rating': ''}})
    return distro_items


def distro_seasons(params):
    list_name = params['list_name']
    url = params['url']
    sid = url.split("**")[0]
    # fanart = url.split("**")[-1]
    cache_name = f"content_list_distro_seasons_{sid}_{list_name}"
    distro_items = main_cache.get(cache_name)
    if not distro_items:
        distro_items = _distro_seasons(sid, list_name)
        main_cache.set(cache_name, distro_items, expiration=datetime.timedelta(hours=24))  # 1 days cache
    # logger("distro_seasons distro_items: {}".format(distro_items))
    # item_list = list(_process(distro_items))
    from sys import argv
    handle = int(argv[1])
    add_items(handle, list(_process(distro_items)))
    set_content(handle, 'episodes')
    end_directory(handle)
    set_view_mode('view.episodes', 'episodes')


def play(params):
    url = params['url']
    # title = params['title']
    # logger(f'Play Selected Link - no resolveURL reqd params: {params}')
    url = f'{url}|User-Agent={agent()}&Upgrade-Insecure-Requests=1'
    from modules.player import infinitePlayer
    # info = {'info': params['title']}
    infinitePlayer().run(url, 'video', {'title': params['title']})


def get_data_from_web(data_dict=None):
    # distro_data = read_write_file(file_n='distro.html')
    if not data_dict:
        distro_data = requests.request("GET", base_url, headers=headers, data=payload).text
        distro_data = re.sub(r"\s+", "", distro_data, flags=re.I)
        # distro_data = to_utf8(normalize(distro_data))
        data_dict = distro_data.replace('\\', '/')
    # logger(f'initial list: {data_dict}')
    deletekey = ["adtags", "adtemplates"]
    data_dict = json.loads(str(data_dict))
    # logger(f"type: {type(data_dict)} len: {len(data_dict)}")
    for key in deletekey:
        try: del data_dict[key]
        except KeyError: logger(f'Key {key} not found')
    # data_dict.pop("adtags")
    # data_dict.pop("adtemplates")
    # logger(f"type: {type(data_dict)} len: {len(data_dict)}")
    # logger(f'initial list: {data_dict}')
    return data_dict


# if __name__ == "__main__":
#     import sys, random
#
#
#     # sys.exit()
#     distro_items = _distro_live_vod('vod')
#     logger(f'initial list: {distro_items}')
#     """Live Categaries"""
#     urls = [u'Featured', u'News & Opinion', u'Business', u'Movies', u'Shows & Comedy', u'Fun & Games', u'Live Sports', u'MMA & More', u'Outdoors', u'Reality & Docs', u'Lifestyle', u'Spanish', u'Indian & Southeast Asian', u'Music', u'Moods', u'Radio']
#     url = random.choice(urls)
#     distro_items = _distro_live_cats(url, 'live')
#     logger(f'Live list: {distro_items}')
#     """VOD Categaries"""
#     urls = [u'Featured', u'CineLife', u'HOOKd', u'Reelz', u'Family', u'Sports & Fitness', u'Gusto TV - Food & Recipes', u'Business & Finance', u'Movie Kingdom', u'Drama', u'Action Thriller', u'Comedy', u'Sci-Fi', u'Horror', u'Indian & Southeast Asian', u'Chinese Movies & Shows', u'Documentaries', u'Tech & Science', u'Travel & LifeStyle', u'Things That Go']
#     url = random.choice(urls)
#     distro_items = _distro_vod_cats(url, 'vod')
#     logger(f'VOD list: {distro_items}')
#     """Seasons Categaries"""
#     params = {'url': '10**fanart.png', 'list_name': 'vod'}
#     sid = url.split("**")[0]
#     distro_items = _distro_seasons(sid, 'vod')
#     logger(f'Seasons list: {distro_items}')
