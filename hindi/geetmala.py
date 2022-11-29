# -*- coding: utf-8 -*-

import datetime
import re
import traceback
import requests
from urllib.parse import urlencode, quote_plus

import json

try:
    from indexers.hindi.live_client import scrapePage, wrigtht_json
    from modules.kodi_utils import logger, build_url, notification, set_info, execute_builtin, addon_fanart, item_next, add_items, set_content, end_directory, set_view_mode, get_infolabel, make_listitem
    from caches.h_cache import main_cache
except:
    import os, sys

    file = os.path.realpath(__file__)
    sys.path.append(os.path.join(os.path.dirname(file), "modules"))
    from modules.live_client import scrapePage, wrigtht_json
    from modules.utils import logger
    from modules.h_cache import main_cache

from modules.dom_parser import parseDOM
from modules.source_utils import normalize
from modules.utils import replace_html_codes

base_link = 'https://www.hindigeetmala.net'


# yt-dlp -f bestaudio -x --audio-format mp3 --audio-quality 0 --add-metadata --embed-thumbnail -o "%(artist)s - %(title)s.%(ext)s" urlhere

def groot(param):
    if param['rescrape'] == 'true':
        # logger('<<< %s' % param)
        get_data_fromxml(param)

    new_params = param.copy()
    new_params.update({'rescrape': 'true'})
    # logger('+++ %s' % new_params)
    if param['action'] == "gdrive_movies": menu_file = "gdrive_M.json"
    else: menu_file = "gdrive_TV.json"
    # gdrive_list = os.path.join(list_data_dir, menu_file)
    with open(menu_file, 'r') as f:
        GD_data = json.load(f)
    glist = []

    for item in GD_data:
        cm = []
        cm_append = cm.append
        listitem = make_listitem()
        thumb = item['thumb']
        listitem.setLabel(item['title'])

        cm_append(("[B]Rescrape Root[/B]", 'RunPlugin(%s)' % build_url(new_params)))
        cm_append(("[B]Add to a Shortcut Folder[/B]", 'RunPlugin(%s)' % build_url({'mode': 'menu_editor.shortcut_folder_add_item', 'name': item['title'], 'iconImage': thumb})))
        listitem.setArt({'icon': thumb, 'poster': thumb, 'thumb': thumb, 'fanart': addon_fanart, 'banner': thumb})
        listitem.addContextMenuItems(cm)
        glist.append((item['url'], listitem, False))
    from sys import argv  # some functions like ActivateWindow() throw invalid handle less this is imported here.
    handle = int(argv[1])
    add_items(handle, glist)
    set_content(handle, 'tvshows')
    end_directory(handle)
    set_view_mode('view.tvshows', 'tvshows')


def get_data_fromxml(param):
    list_data_dir = ''
    if param['action'] == "gdrive_movies":
        menu_file = "G_movies.xml"
        json_file = os.path.join(list_data_dir, "gdrive_M.json")
    else:
        menu_file = "G_tv.xml"
        json_file = os.path.join(list_data_dir, "gdrive_TV.json")
    gdrive_list = os.path.join(list_data_dir, menu_file)
    with open(gdrive_list, 'r') as f:
        drive_data = f.read()

    # glist = []
    mjason = []
    faves = re.compile('<favourite(.+?)</favourite>').findall(drive_data)
    for fave in faves:
        fave = replace_html_codes(fave)
        fave = fave.replace('name=""', '')
        try: name = re.compile('name="(.+?)"').findall(fave)[0]
        except: name = ''
        try: thumb = re.compile('thumb="(.+?)"').findall(fave)[0]
        except: thumb = ''
        try:
            cmd = fave.split('>', 1)[-1]
            cmd = cmd.replace('"', '').replace('10025', 'videos')
            cmd = cmd.replace('listfolder', '_list_folder').replace('contenttype', 'content_type').replace('itemid', 'item_id').replace('itemdriveid', 'item_driveid')
        except: cmd = ''

        url_params = {'mode': 'vod_tv_gdriveply', 'param': param, 'cmd': cmd}
        url = build_url(url_params)
        mjason.append({'url': url, 'title': name, 'thumb': thumb})
    # logger(json.dumps(mjason))
    wrigtht_json(json_file, json.dumps(mjason))


def gdrive_play(param):
    cmd = param['cmd']
    # logger(cmd)
    # if "PlayMedia" in cmd:
        # paramstring = re.compile(r'PlayMedia\((.+?)\)').findall(cmd)[0]
        # paramstring = paramstring.replace('action=play', 'action=_list_folder')
        # cmd = 'ActivateWindow(videos,%s,,return)' % paramstring

    # cmd = cmd.replace('"', '').replace('10025', 'videos')
    # cmd = cmd.replace('listfolder', '_list_folder').replace('contenttype', 'content_type').replace('itemid', 'item_id').replace('itemdriveid', 'item_driveid')
    # elif "ActivateWindow" in cmd:
        # cmd = cmd.replace('itemdriveid', 'item_driveid') # .replace('driveid', 'drive_id')
    # paramstring = paramstring.replace('&amp;', '&').replace('&quot;', '').replace('10025,', '')
    # logger(cmd)
    execute_builtin(cmd)
    # sim_recom_params = {'mode': 'vod_tv_gdrive', 'action': 'gdrive_movies', 'foldername': 'G Drive', 'list_name': 'GD Movies'}
    # execute_builtin('RunPlugin(%s)' % build_url(sim_recom_params))
    # execute_builtin('ActivateWindow(videos,plugin://plugin.googledrive/?%s,return)' % groot(param['param']))


def geetm_root(params):
    cache_name = "content_list_geetmala_chennel"
    if params['rescrape'] == 'true':
        main_cache.delete(cache_name)
        list_data = None
    else:
        list_data = main_cache.get(cache_name)
        # logger(f"from cache list_data: {list_data}")
    if not list_data:
        uri = "https://raw.githubusercontent.com/djp11r/repo_n/mayb/etc/allxml/geetmala.json"
        data = scrapePage(uri).text
        list_data = json.loads(data)
        # logger(f"new list_data: {list_data}")
        if list_data: main_cache.set(cache_name, list_data, expiration=datetime.timedelta(hours=168))

    # logger(geetmala_data)
    def _process(list_data):
        for item in list_data:
            listitem = make_listitem()
            cm = []
            cm_append = cm.append
            title = item['name']
            url_params = {'mode': 'geetm_list', 'list_name': title, 'ch_name': title, 'url': item['url'], 'pg_no': '1'}
            thumb = item['image']
            url = build_url(url_params)
            listitem.setLabel(title)
            cm_append(("[B]Add to a Shortcut Folder[/B]", 'RunPlugin(%s)' % build_url({'mode': 'menu_editor.shortcut_folder_add_item', 'name': title, 'iconImage': thumb})))
            listitem.addContextMenuItems(cm)
            listitem.setArt({'icon': thumb, 'poster': thumb, 'thumb': thumb, 'fanart': addon_fanart, 'banner': thumb})
            yield url, listitem, True
        # xbmcplugin.addDirectoryItem(int(argv[1]), url, listitem, isFolder=True)

    # item_list = list(_process())
    from sys import argv  # some functions like ActivateWindow() throw invalid handle less this is imported here.
    handle = int(argv[1])
    add_items(handle, list(_process(list_data)))
    set_content(handle, 'tvshows')
    end_directory(handle)
    set_view_mode('view.tvshows', 'tvshows')


def get_song_list(params):
    pg_no = int(params['pg_no'])
    ch_name = params['ch_name']
    url = params['url']
    rescrape = params.get('rescrape', 'false')
    if url.endswith('value='):
        search_text = get_SearchQuery('Hindi Geetmala')
        search_text = quote_plus(search_text)
        url += search_text

    string = f"content_list_geetm_song_list_{ch_name}"
    params = {'url': url, 'ch_name': ch_name, 'pg_no': pg_no}
    cache_name = string + urlencode(params)
    song_list = None
    if rescrape == 'true': main_cache.delete(cache_name)
    else: song_list = main_cache.get(cache_name)
    if not song_list:
        song_list = make_song_list(params)
        if song_list:
            main_cache.set(cache_name, song_list, expiration=datetime.timedelta(hours=24))  # 1 days cache

    def _process():
        info = {}
        for item in song_list:
            cm = []
            cm_append = cm.append
            title = item['name']
            thumb = item['image']
            url_params = {
                'mode': item['mode'],
                'rescrap': 'false',
                'Album': item['Album'],
                'list_name': title,
                'ch_name': item['ch_name'],
                'url': item['url'],
                'thumb': thumb,
                'pg_no': item['pg_no']}
            rescrape_params = {
                'mode': item['mode'],
                'rescrap': 'true',
                'url': item['url'],
                'list_name': title,
                'thumb': thumb,
                'Album': item['Album']}
            cm_append(("[B]Rescrape and Select[/B]", f'RunPlugin({build_url(rescrape_params)})'))
            is_folder = True
            if 'Next Page:' in title: info.update({'plot': 'Go To Next Page....'})
            else: info.update({'plot': f"Album: {item['Album']}\nArtist: {item['Artist']}"})
            listitem = make_listitem()
            listitem.setLabel(title)
            info.update({'imdb_id': title, 'mediatype': 'episode', 'episode': 1, 'season': 0})
            setUniqueIDs = {'imdb': str(title)}
            listitem = set_info(listitem, info, setUniqueIDs)

            url = build_url(url_params)
            listitem.addContextMenuItems(cm)
            # listitem.setProperty('IsPlayable', 'true')
            listitem.setArt({'icon': thumb, 'poster': thumb, 'thumb': thumb, 'fanart': addon_fanart, 'banner': thumb})
            yield url, listitem, is_folder

    # logger(f'get_song_list item_list: {list(_process())}')
    from sys import argv  # some functions like ActivateWindow() throw invalid handle less this is imported here.
    handle = int(argv[1])
    add_items(handle, list(_process()))
    set_content(handle, 'episodes')
    end_directory(handle)
    set_view_mode('view.episodes', 'episodes')


def get_SearchQuery(sitename):
    import xbmc
    keyboard = xbmc.Keyboard()
    keyboard.setHeading('Search ' + sitename)
    keyboard.doModal()
    search_text = ''
    if keyboard.isConfirmed(): search_text = keyboard.getText()
    return search_text


def make_song_list(params):
    find_data = re.compile('itemprop="name">(.+?)</span>')
    pg_no = int(params['pg_no'])
    ch_name = params['ch_name']
    song_perpage = 25
    url = params['url']
    songs = []
    nextpg = True
    while len(songs) < song_perpage and nextpg:
        song_page = scrapePage(url).text
        result = parseDOM(song_page, "tr", attrs={"itemprop": "track"})
        for item in result:
            try:
                title = parseDOM(item, "span", attrs={"itemprop": "name"})[0]
                vid_url = parseDOM(item, "a", ret="href")[0]
                img = parseDOM(item, "img", ret="src")[0]
                Album = parseDOM(item, "span", attrs={"itemprop": "inAlbum"})[0]
                # Album = find_data.findall(Album)[0]
                m_name = find_data.findall(Album)[0]
                m_year = re.findall(r"\(.+?\)", Album, re.MULTILINE)
                if m_year: m_year = m_year[0].replace("(", "").replace(")", "")
                else: m_year = ""
                Album = f"{m_name} - {m_year}"

                Artist = parseDOM(item, "span", attrs={"itemprop": "byArtist"})[0]
                Artist = find_data.findall(Artist)[0]
                songs.append({
                    'name': title,
                    'ch_name': ch_name,
                    'pg_no': pg_no,
                    'mode': 'geetm_vid_list',
                    'Album': Album,
                    'Artist': Artist,
                    'url': base_link + vid_url,
                    'image': base_link + img})
            except: pass
        if nextpg:
            pg_no += 1
            if "?page=" not in url: url += f"?page={pg_no}"
            else:
                url = url.split("=")[0]
                url += f"={pg_no}"
        else: nextpg = False

    if nextpg:
        name = f"Next Page: {pg_no}"
        next_pg_dict = {
            'name': name,
            'ch_name': ch_name,
            'pg_no': pg_no,
            'mode': 'geetm_list',
            'Album': '',
            'Artist': '',
            'url': url,
            'image': item_next}
        songs.append(next_pg_dict)
    # logger('totle from url: %s pg_no: %s song: %s \n %s' % (params['url'], pg_no, len(songs), songs))
    return songs


def resolve_url(url, ltype):
    try:
        import resolveurl
        hmf = resolveurl.HostedMediaFile(url=url)
        if hmf.valid_url() is True: return hmf.resolve()
        else: return ''
    except Exception as e:
        msg = f"for: {e} Error: {ltype}"
        notification(f'Infinite not resolved\n{msg}', 5000)
        logger(f'from GeetMala resolve_url Error: {msg}')
        return ''


def get_yt_vid_links(url, title, Album):
    vid_page = scrapePage(url).text
    # logger(f'search vid_page {vid_page} ')
    result = parseDOM(vid_page, "table", attrs={"class": "b1 w760 alcen"})
    result += parseDOM(vid_page, "table", attrs={"class": "b1 allef w100p"})
    choices = []
    try:
        link = parseDOM(result, 'iframe', ret='src')[0]
        if 'youtube.com/embed' in link:
            v_id = link.replace('https://www.youtube.com/embed/', '').strip()
            # v_link = resolve_url(link, "Song")
            # logger('resolver return for Song: %s v_link: %s' % (url, v_link))
            if v_id:  # and "http" in v_link:
                v_link = f"plugin://plugin.video.youtube/play/?video_id={v_id}"
                choices.append({"title": "Song : %s" % title, "url": v_link})
    except:
        result = parseDOM(vid_page, "div", attrs={"class": "yt_nt"})
        # print(f"result: {result}")
        results = parseDOM(result, "a", attrs={"class": "yt_nt"})
        # print(f"results: {results}")
        for item in results:
            v_id = item.replace('https://www.youtube.com/watch?v=', '').strip()
            if v_id:
                v_link = f"plugin://plugin.video.youtube/play/?video_id={v_id}"
                choices.append({"title": f"Song : {title}", "url": v_link})
        if len(choices) > 1: return choices
    # else:
    #     v_link = parseDOM(result, 'a', ret = 'href')[0]

    links = parseDOM(result, 'tr')
    find_data = re.compile('<td>(.+?)</td>')
    for link in links:
        # logger(f'from Movie link: \n{link}\n>>>>>\n')
        td_data = find_data.findall(link)
        try:
            if 'Watch Full Movie:' in td_data[0]:
                movie_link = parseDOM(td_data[1], "a", ret="href")
                # logger('from youtube movie links: %s' % movie_link)
                for link in movie_link:
                    v_id = link.replace('https://www.youtube.com/watch?v=', '').strip()
                    # v_link = resolve_url(link, "Movie")
                    v_link = f"plugin://plugin.video.youtube/play/?video_id={v_id}"
                    if v_link: choices.append({"title": f"Movie: {Album}", "url": v_link})
        except: pass
    if not len(choices) > 1: choices = Movie_search().search(Album, choices)
    return choices


def get_yt_links(params):
    url = params['url']
    title = params['list_name']
    Album = params['Album']
    rescrap = params['rescrap']
    thumb = params['thumb']
    string = f"content_list_geetm_yt_links_{title}_{Album}"
    choices = main_cache.get(string)
    if not choices or rescrap == 'true':
        # logger(f'---geetmala link: {url}\ntitle: {title}\nAlbum: {Album}')
        choices = get_yt_vid_links(url, title, Album)
        if choices: main_cache.set(string, choices, expiration=datetime.timedelta(hours=24))

    # logger(f"rescrap: {rescrap} choices {choices}")
    def _process():
        for choice in choices:
            try:
                # logger("get_yt_links choice: {}".format(choice))
                listitem = make_listitem()
                url_params = {'mode': 'geetm_plvid', 'url': choice['url'], 'title': choice['title']}
                url = build_url(url_params)
                listitem.setLabel(label=choice['title'])
                # listitem.setInfo(type='video', infoLabels={'title': choice['title']})
                choice.update({'imdb_id': choice['title'], 'mediatype': 'episode', 'episode': 1, 'season': 0})
                setUniqueIDs = {'imdb': str(choice['title'])}
                listitem = set_info(listitem, choice, setUniqueIDs)
                listitem.setArt({'thumb': thumb})
                # listitem.setProperty('IsPlayable', 'true')
                yield url, listitem, False
            except: logger(f'Error: {traceback.print_exc()}')

    # logger(f"get_yt_links item_list: {list(_process())}")
    from sys import argv  # some functions like ActivateWindow() throw invalid handle less this is imported here.
    handle = int(argv[1])
    add_items(handle, list(_process()))
    set_content(handle, 'videos')
    end_directory(handle)
    set_view_mode('view.videos', 'videos')


def play(stream, channel=None, xbmc_player=False):
    # logger('play stream: {} channel: {}'.format(stream, channel))
    execute_builtin(f'RunPlugin({stream})')


class Movie_search:
    def __init__(self):
        self.key = 'AIzaSyCjf8izIeXa1oFZo7_HeL0WgrOq1WF_I1k'
        # self.key_link = f'&key={self.key}'
        self.search_link = f'https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=15&q=%s&key={self.key}'
        # self.session = requests.Session()

    def search(self, name, choices):
        try:
            query = name + ' full|Full movie|Movie'
            query_url = self.search_link % quote_plus(query)
            # logger(f"query: {query}")

            query_url += "&relevanceLanguage=en"
            headers = {"Accept": "application/json"}
            response = requests.get(query_url, headers=headers).json()
            # logger(f'search json response {response} ')
            error = response.get('error', [])
            if error:
                message = error.get('message', [])
                logger(f"message: {message}")
                return None

            json_items = response.get('items', [])
            # logger(f'search json_items {json_items} ')
            # logger(f'search json_items {to_utf8(json_items)} ')
            for search_result in json_items:
                try:
                    query = query.split('-')[0].lower().replace('.', '')
                    item_title = normalize(search_result["snippet"]["title"].replace('.', ''))
                    # item_title = replace_html_codes(search_result["snippet"]["title"].replace('.', ''))
                    if re.search(r'Full Movie|Movie', item_title, re.I) and re.search(query, item_title, re.I):
                        # logger(f'search item {query} == {item_title}')
                        # if query in item_title.lower() and "movie" in item_title.lower():
                        if search_result["id"]["kind"] == "youtube#video":
                            vid_id = search_result["id"]["videoId"]
                            payload = {'id': vid_id, 'part': 'contentDetails', 'key': self.key}
                            url = 'https://www.googleapis.com/youtube/v3/videos/?&%s' % urlencode(payload)
                            resp_dict = requests.get(url, headers=headers).json()
                            # resp_dict = self.session.get('https://www.googleapis.com/youtube/v3/videos', params=payload).json()
                            dur = resp_dict["items"][0]["contentDetails"]["duration"]
                            duration = convert_youtube_duration_to_minutes(dur)
                            # logger(f'dur: {dur} duration: {duration}')
                            if duration > 70:
                                # item_title = clean_title(item_title)
                                v_link = f"plugin://plugin.video.youtube/play/?video_id={vid_id}"
                                # logger(f'item_title: {item_title} v_link: {v_link}')
                                choices.append({"title": f"Movie: ({duration} minutes) {item_title}", "url": v_link})
                except: logger(f'Error: {traceback.print_exc()}')
        except: logger(f'Error: {traceback.print_exc()}')
        # logger(f'choices: {choices}')
        return choices


def convert_youtube_duration_to_minutes(duration):
    """
    :param duration:
    convert_YouTube_duration_to_minits('P2DT1S')
    172801
    convert_YouTube_duration_to_minits('PT2H12M51S')
    7971
    :return:
    """
    day_time = duration.split('T')
    day_duration = day_time[0].replace('P', '')
    day_list = day_duration.split('D')
    hour = minute = second = day = 0
    if len(day_list) == 2: day = int(day_list[0]) * 60 * 60 * 24  # day_list = day_list[1]
    hour_list = day_time[1].split('H')
    if len(hour_list) == 2:
        hour = int(hour_list[0]) * 60 * 60
        hour_list = hour_list[1]
    else: hour_list = hour_list[0]
    minute_list = hour_list.split('M')
    if len(minute_list) == 2:
        minute = int(minute_list[0]) * 60
        minute_list = minute_list[1]
    else: minute_list = minute_list[0]
    second_list = minute_list.split('S')
    if len(second_list) == 2: second = int(second_list[0])
    minutes = (day + hour + minute + second) / 60
    return int(minutes)
