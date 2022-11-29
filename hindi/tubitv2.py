# -*- coding: utf-8 -*-

import datetime
import os
import json
import re
from sys import argv
import string
import random
import traceback


# stream_failed = "Unable to get stream. Please try again later."
stream_plug = "https://m7lib.dev/api/v1/channels/"
# stream_plug = "aHR0cHM6Ly9tN2xpYi5kZXYvYXBpL3YxL2NoYW5uZWxzLw=="
# stream_plug = base64.b64decode(stream_plug).decode('UTF-8')
explore_org_base = "https://omega.explore.org/api/get_cam_group_info.json?id=79"
# explore_org_base = "aHR0cHM6Ly9vbWVnYS5leHBsb3JlLm9yZy9hcGkvZ2V0X2NhbV9ncm91cF9pbmZvLmpzb24/aWQ9Nzk="
# explore_org_base = base64.b64decode(explore_org_base).decode('UTF-8')
tubi_tv_base = "https://tubitv.com/oz"
# tubi_tv_base = "aHR0cHM6Ly90dWJpdHYuY29tL296"
# tubi_tv_base = base64.b64decode(tubi_tv_base).decode('UTF-8')
import xbmcgui, xbmcplugin
from indexers.hindi.live_client import scrapePage, wrigtht_json, agent
from modules.player import infinitePlayer
from modules.kodi_utils import logger, make_listitem, notification, dialog, set_info, set_resolvedurl, addon_fanart, add_items, set_content, end_directory, set_view_mode, get_infolabel
from caches.h_cache import main_cache
aicon = 'https://i.imgur.com/iOllLYX.png' # "hindi_tubi.png")

ch_slugs = ['bloomberg', 'cbs-sports-hq', 'pbs-kids', 'stirr-news-247', 'stirr-bloomberg-tv', 'stirr-law-crime', 'stirr-nasatv', 'stirr-comet', 'stirr-contv', 'stirr-comedy-dynamics', 'stirr-failarmy', 'stirr-afv', 'stirr-johnny-carson-tv', 'stirr-unsolved-mysteries', 'stirr-forensics-files', 'stirr-greatest-american-hero', 'stirr-wiseguy', 'stirr-the-commish', 'stirr-hunter', 'stirr-crime-story', 'stirr-filmrise-free-movies', 'stirr-stirr-movies', 'stirr-cinehouse', 'stirr-docurama', 'stirr-stirr-sports', 'stirr-edgesport', 'stirr-wpt', 'stirr-filmrise-classic-tv', 'stirr-american-classics', 'stirr-britcom', 'stirr-the-lucy-show', 'stirr-the-lone-ranger', 'stirr-stirr-westerns', 'stirr-movie-mix', 'stirr-stirr-comedy', 'stirr-stirr-documentaries', 'stirr-stirr-travel', 'vuit-investigate-tv', 'vuit-wgcl-atlanta-ga', 'vuit-wtvm-columbus-ga', 'vuit-wagt-augusta-ga', 'vuit-wrdw-augusta-ga', 'vuit-politics-uncut', 'vuit-walb-albany-ga', 'vuit-wtoc-savannah-ga', 'xumo-nbc-news-now', 'xumo-abc-news-live', 'xumo-cbs-news', 'xumo-comedy-dynamics', 'xumo-cinelife', 'xumo-docurama', 'pluto-tv-kids', 'pluto-tv-news', 'pluto-cnn', 'pluto-bloomberg-tv', 'pluto-classic-movies-channel', 'pluto-tv-action', 'pluto-tv-science', 'pluto-tv-animals', 'pluto-funny-af', 'pluto-tv-true-crime', 'pluto-buzzr', 'pluto-xive-tv', 'pluto-tv-travel', 'pluto-tv-history', 'pluto-tv-comedy', 'pluto-tv-romance', 'pluto-fox-sports', 'pluto-the-new-detectives', 'pluto-tv-thrillers', 'pluto-tv-drama', 'pluto-cmt-westerns', 'pluto-unsolved-mysteries', 'pluto-tv-sci-fi', 'pluto-tv-fantastic', 'pluto-british-tv', 'pluto-tv-documentaries', 'pluto-tv-spotlight', 'pluto-forensic-files', 'pluto-tv-military', 'pluto-weather-nation', 'pluto-tv-land-sitcoms', 'pluto-cold-case-files', 'pluto-tv-cult-films', 'pluto-tv-terror', 'pluto-bet-tv', 'pluto-comedy-central-tv', 'pluto-nick-jr-tv', 'pluto-tv-backcountry', 'pluto-paramount-movie-channel', 'pluto-doctor-who-classic', 'pluto-nfl-channel', 'pluto-tv-land-drama', 'pluto-american-gladiators', 'pluto-baywatch', 'pluto-tv-lives', 'pluto-cmt-tv', 'pluto-pga-tour', 'pluto-bein-sports-xtra', 'pluto-nbc-news-now', 'pluto-cops', 'pluto-blaze-live', 'pluto-johnny-carson-tv', 'pluto-stories-by-amc', 'pluto-the-walking-dead-esp', 'pluto-western-tv', 'pluto-cbs-sports-hq', 'pluto-csi', 'pluto-star-trek-1', 'pluto-tv-suspense', 'pluto-classic-tv-comedy', 'pluto-classic-tv-drama-ptv1', 'pluto-the-amazing-race', 'pluto-tv-drama-life', 'pluto-tv-crime-drama', 'pluto-90210', 'pluto-tv-crime-movies', 'pluto-tv-staff-picks', 'pluto-narcos', 'pluto-showtime-selects', 'pluto-dr-oz', 'pluto-bbc-home']


class LiveChannels:

    @staticmethod
    def channel_list():
        try:
            channels_list = main_cache.get("content_list_tubitv2_livech_root")
            if not channels_list:
                channels_list = Common.get_channels()
                if channels_list: main_cache.set("content_list_tubitv2_livech_root", channels_list, expiration = datetime.timedelta(hours = 336)) # 336 == 14 days cache

            # Generate Channel List
            # logger("LiveChannels channels_list {}".format(channels_list))
            Common.add_section("tubitv_livesearch", aicon, addon_fanart, "Search Channel")
            for channel in channels_list:
                try:
                    if channel["slug"] in ch_slugs: Common.add_channel(f"{channel['slug']}tubitv_liveget_channel", channel["poster"], addon_fanart, channel["name"], {}, True)
                except: logger(f"LiveChannels channel_list channel Error: {traceback.print_exc()}")
            handle = int(argv[1])
            set_content(handle, 'episodes')
            end_directory(handle)
        except:
            logger(f"LiveChannels channel_list Error {traceback.print_exc()}")
            notification("Oops something went wrong.", 1000)

    @staticmethod
    def search_list():
        try:
            # Generate Channel List from search query
            retval = dialog.input("Search...", type=xbmcgui.INPUT_ALPHANUM)
            if retval and len(retval) > 0:
                search_list = main_cache.get(f"content_list_tubitv2_livech_search_{retval}")
                if not search_list:
                    search_list = Common.search_channels(retval)
                    if search_list: main_cache.set(f"content_list_tubitv2_livech_search_{retval}", search_list, expiration = datetime.timedelta(hours = 336)) # 336 == 14 days cache
                if len(search_list) > 0:
                    for channel in search_list:
                        Common.add_channel(f"{channel['slug']}tubitv_liveget_channel", channel["poster"], addon_fanart, channel["name"], {}, True)
                    handle = int(argv[1])
                    set_content(handle, 'episodes')
                    end_directory(handle)
                    set_view_mode('view.episodes', 'episodes')
                else:
                    notification("No results.", 1000)
                    exit()
            else:
                notification("Please enter something to search for.", 1000)
                exit()
        except:
            logger(f"LiveChannels search_list Error {traceback.print_exc()}")
            notification("Oops something went wrong.", 1000)
            exit()

    @staticmethod
    def get_channel(params):
        try:
            title = params['title']
            mode = params['mode']
            mode = mode.split('tubitv_liveget_channel')[0]
            Common.get_stream_and_play(mode)
        except: logger(f"LiveChannels get_channel Error {traceback.print_exc()}")


class Channels:

    @staticmethod
    def section_list(rescrape):
        try:
            Common.add_section("tubitv-search", aicon, addon_fanart, "Search Tubi")
            # logger(f"section_list rescrape: {rescrape}")
            if rescrape == 'true': main_cache.delete_one("content_list_tubitv2_root")
            section_list = main_cache.get("content_list_tubitv2_root")
            if not section_list:
                # logger(" Updating section_list: %s" % section_list)
                section_list = Stream.get_tubi_tv_categories()
                if section_list: main_cache.set("content_list_tubitv2_root", section_list, expiration=datetime.timedelta(hours=336)) # 14 days cache

            for category in section_list:
                try:
                    if re.search(r"espanol|Español|lgbt|LGBT|ganadores_y_nominados|telenovelas_y_series|para_los_nios_y_familias", str(category), flags=re.I): continue
                    Common.add_section(f"{category['id']}tubitv-content", category["icon"], addon_fanart, category["title"], {})
                except Exception as e: logger(f"Channels section_list category Error: {traceback.print_exc()}")
            handle = int(argv[1])
            set_content(handle, 'tvshows')
            end_directory(handle)
            set_view_mode('view.tvshows', 'tvshows')
        except Exception as e:
            logger(f"Channels section_list Error {traceback.print_exc()}")
            notification("Oops something went wrong.", 1000)

    @staticmethod
    def content_list(mode):
        try:
            category = mode.split('tubitv-content')[0]
            cache_name = f"content_list_tubitv2_content_{category}"
            content_list = main_cache.get(cache_name)
            if not content_list:
                content_list = Stream.get_tubi_tv_content(category)
                if content_list: main_cache.set(cache_name, content_list, expiration=datetime.timedelta(hours=48))  # 48 hrs cache

            for entry in content_list:
                try:
                    if entry["type"] == "v": Common.add_channel(f"{entry['id']}play-tubitv", entry["icon"], addon_fanart, entry["title"], entry["meta"], live=False)
                    elif entry["type"] == "s": Common.add_section(f"{entry['id']}tubitv-episodes", entry["icon"], addon_fanart, entry["title"], entry["meta"])
                except Exception as e: logger(f"Channels content_list entry Error {traceback.print_exc()}")
            handle = int(argv[1])
            set_content(handle, 'tvshows')
            end_directory(handle)
            set_view_mode('view.tvshows', 'tvshows')
        except Exception as e:
            logger(f"Channels content_list mode: {mode} Error {traceback.print_exc()}")
            notification("content_list Oops something went wrong.", 1000)

    @staticmethod
    def episode_list(mode):
        try:
            show = mode.split('tubitv-episodes')[0]
            cache_name = f"content_list_tubitv2_episodes_{show}"
            episode_list = main_cache.get(cache_name)
            if not episode_list:
                episode_list = Stream.get_tubi_tv_episodes(show)
                if episode_list: main_cache.set(cache_name, episode_list, expiration=datetime.timedelta(hours=48))  # 48 hrs cache

            for entry in episode_list:
                try: Common.add_channel(f"{entry['id']}play-tubitv", entry["icon"], addon_fanart, entry["title"], entry["meta"], live=False)
                except Exception as e: logger(f"Channels episode_list entry Error {traceback.print_exc()}")
            handle = int(argv[1])
            set_content(handle, 'episodes')
            end_directory(handle)
            set_view_mode('view.episodes', 'episodes')
        except Exception as e:
            logger(f"Channels episode_list Error {traceback.print_exc()}")
            notification("episode_list Oops something went wrong.", 1000)

    @staticmethod
    def search_tubi():
        try:
            retval = dialog.input("Search Tubi", type=xbmcgui.INPUT_ALPHANUM)
            if retval and len(retval) > 0:
                search_list = main_cache.get(f"content_list_tubitv2_search_tubi_{retval}")
                if not search_list:
                    search_list = Stream.get_tubi_tv_search(retval)
                    if search_list: main_cache.set(f"content_list_tubitv2_search_tubi_{retval}", search_list, expiration=datetime.timedelta(hours=336)) # 336 == 14 days cache

                if len(search_list) > 1:
                    for entry in search_list:
                        try:
                            if re.search(r"espanol|lgbt|LGBT", str(entry), flags=re.I): continue
                            if entry["type"] == "v": Common.add_channel(f"{entry['id']}play-tubitv", entry["icon"], addon_fanart, entry["title"], entry["meta"], live=False)
                            elif entry["type"] == "s": Common.add_section(f"{entry['id']}tubitv-episodes", entry["icon"], addon_fanart, entry["title"], entry["meta"])
                        except Exception as e: logger(f"Channels search_tubi entry Error {traceback.print_exc()}")
                    handle = int(argv[1])
                    set_content(handle, 'tvshows')
                    end_directory(handle)
                    set_view_mode('view.tvshows', 'tvshows')
                else:
                    notification("No results.", 1000)
                    exit()
            else:
                notification("Please enter something to search for.", 1000)
                exit()
        except Exception as e:
            logger(f"Channels search_tubi Error {traceback.print_exc()}")
            notification("search_tubi Oops something went wrong.", 1000)

    @staticmethod
    def play_tubi(params):
        try:
            title = params['title']
            mode = params['mode']
            # logger(f"play_tubi:: mode: {mode}")
            stream_id = mode.split('play-tubitv')[0]
            Common.get_tubi_tv_stream(stream_id)
        except Exception as e:
            logger(f"Channels play_tubi Error {traceback.print_exc()}")
            notification("play_tubi Oops something went wrong.", 1000)


class Common:
    UA = agent()
    # logger("Common get_stream_and_play UA: %s" % (UA))

    # Begin Tubi TV #

    @staticmethod
    def dlg_failed(mode):
        notification(mode, 1000)
        exit()

    @staticmethod
    def random_generator(size=6, chars=string.ascii_uppercase + string.digits):
        # Added '# nosec' to suppress bandit warning since this is not used for security/cryptographic purposes.
        return ''.join(random.choice(chars) for x in range(size))  # nosec

    @staticmethod
    # Parse string and extracts first match as a string
    # The default is to find the first match. Pass a 'number' if you want to match a specific match. So 1 would match
    # the second and so forth
    def find_single_match(text, pattern, number=0):
        try:
            matches = re.findall(pattern, text, flags=re.DOTALL)
            result = matches[number]
        except AttributeError: result = ""
        return result

    @staticmethod
    # Parse string and extracts multiple matches using regular expressions
    def find_multiple_matches(text, pattern):
        matches = re.findall(pattern, text, re.DOTALL)
        return matches

    @staticmethod
    # Open URL
    def open_url(url, user_agent=True):
        if not user_agent: header = {'User-Agent': Common.UA}
        else: header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11' 'KODI'}
        # logger(f"Common get_stream_and_play header: {header}")
        httpHeaders = {'Accept': "application/json, text/javascript, text/html,*/*",
                       'Accept-Encoding': 'gzip,deflate,sdch',
                       'Accept-Language': 'en-US,en;q=0.8'
                       }
        response = scrapePage(url, headers=header).text
        # logger(f"Common open_url response: {response}")
        return response

    @staticmethod
    # Available channels
    def get_channels():
        url = f"{stream_plug}index.json"
        # logger(f"get_channels url: {url}")
        data = Common.open_url(url)
        channel_list = json.loads(data)
        return channel_list

    @staticmethod
    def search_channels(query):
        url = f"{stream_plug}?search={query}"
        # logger(f"search_channels url: {url}")
        data = Common.open_url(url)
        channel_list = json.loads(data)
        return channel_list

    @staticmethod
    def add_streams(streams):
        coll = []
        for stream in streams:
            icon = stream['icon']
            mode = stream['mode']
            u = f"{argv[0]}?mode={str(mode)}&pvr=.pvr"  # argv[0] + '?mode=' + str(stream['id']) + '&pvr=.pvr'
            item = stream['title'] if stream['title'] is not None else stream['id']
            listitem = make_listitem()
            listitem.setLabel(str(item))
            listitem.setProperty('skipPlayCount', 'true')
            listitem.setProperty('IsPlayable', 'true')
            listitem.setContentLookup(False)
            listitem.setIsFolder(False)
            listitem.setArt({'thumb': icon, 'poster': icon, 'banner': icon})
            stream.update({'imdb_id': str(item), 'mediatype': 'episode', 'episode': 1, 'season': 0})
            setUniqueIDs = {'imdb': str(item)}
            listitem = set_info(listitem, stream, setUniqueIDs)
            coll.append((u, listitem, False))
        return xbmcplugin.addDirectoryItems(int(argv[1]), coll)

    @staticmethod
    def add_channel(mode, icon, fanart, title=None, meta={}, live=True):
        if title is not None: item = str(title)
        else: item = str(mode)
        if live is True: u = f"{argv[0]}?mode={str(mode)}&pvr=.pvr&title={item}"  # argv[0] + "?mode=" + str(mode) + "&pvr=.pvr"
        else: u = f"{argv[0]}?mode={str(mode)}&title={item}"  # argv[0] + "?mode=" + str(mode)
        # logger(f"get_channels meta: {meta}")
        # logger(f"get_channels url: {item}  u: {u}")
        if icon == '': icon = aicon
        listitem = make_listitem()
        listitem.setLabel(item)
        listitem.setArt({'thumb': icon, 'poster': icon, 'banner': icon, 'fanart': fanart})
        try: meta.update({'title': item})
        except: meta = {'title': item}
        meta.update({'imdb_id': str(item), 'episode': 1, 'season': 0})
        setUniqueIDs = {'imdb': str(item)}
        listitem = set_info(listitem, meta, setUniqueIDs)
        ok = xbmcplugin.addDirectoryItem(handle=int(argv[1]), url=u, listitem=listitem, isFolder=False)
        # logger(f"get_channels ok: {ok}")
        return ok

    @staticmethod
    def add_section(mode, icon, fanart, title=None, meta={}):
        # logger(f"Common add_section argv[0]: {argv[0]}")
        u = f"{argv[0]}?mode={str(mode)}&rand={Common.random_generator()}"
        # logger(f"Common add_section mode: {mode} title: {title}")
        cm = []
        cm_append = cm.append
        if title is not None: item = title#.decode('UTF-8')
        else: item = mode
        if icon == '': icon = aicon
        listitem = make_listitem()
        listitem.setLabel(str(item))
        listitem.setArt({'thumb': icon, 'poster': icon, 'banner': icon, 'fanart': fanart})
        try: meta.update({'title': item})
        except: meta = {'title': item}
        cm_append(("[B]Add to a Shortcut Folder[/B]", f"RunPlugin({argv[0]}?mode=menu_editor.shortcut_folder_add_item&name={title}&iconImage={icon})"))
        listitem.addContextMenuItems(cm)
        meta.update({'imdb_id': str(item), 'episode': 1, 'season': 0})
        setUniqueIDs = {'imdb': str(item)}
        listitem = set_info(listitem, meta, setUniqueIDs)
        ok = xbmcplugin.addDirectoryItem(handle=int(argv[1]), url=u, listitem=listitem, isFolder=True)
        return ok

    @staticmethod
    # Return the Channel ID from YouTube URL
    def get_youtube_channel_id(url):
        return url.split("?v=")[-1].split("/")[-1].split("?")[0].split("&")[0]

    @staticmethod
    # Return the full YouTube plugin url
    def get_playable_youtube_url(channel_id):
        return f'plugin://plugin.video.youtube/play/?video_id={channel_id}'

    @staticmethod
    # Play stream
    # Optional: set xbmc_player to True to use xbmc.Player() instead of xbmcplugin.setResolvedUrl()
    def play(stream, channel='NO LABLE', xbmc_player=False):
        # logger(f"Common play:: channel: {channel} type(stream): {type(stream)} stream: {stream}")
        try: infinitePlayer().run(stream, 'video', {'title': channel})
        except: logger(f"Common play:: {channel} Error {traceback.print_exc()}")

    @staticmethod
    # Get and Play stream
    def get_stream_and_play(mode):
        stream = None
        name, stream = 'Not Found', ''
        url = f"{stream_plug}?slug={mode}"
        try:
            data = json.loads(Common.open_url(url))
            name = data['name']
            # logger(f"Common get_stream_and_play data: {data}")
            stream = data['stream']
        except: logger(f"get_stream_and_play Error {traceback.print_exc()}")

        if "m3u8" in stream: Common.play(stream, name)
        else: Common.dlg_failed(f"Can not found url for: {name}")

    @staticmethod
    def get_tubi_tv_stream(stream_id):
        url = f"{tubi_tv_base}/videos/{stream_id}/content"
        name, stream = 'Not Found', ''
        try:
            data = json.loads(Common.open_url(url))
            name = data['title']
            # logger(f"Common get_tubi_tv_stream data: {data}")
            stream = data.get("url", None)
            if not stream:
                video_resources = data["video_resources"]
                # logger(f"Common get_tubi_tv_stream video_resources: {video_resources}")
                url_list = [d['manifest'].get('url') for d in video_resources if d['manifest'].get('url') and d['type'] == 'hlsv3']
                # logger(f"Common get_tubi_tv_stream url_list: {url_list}")
                stream = f"{url_list[0]}" #f"{random.choice(url_list)}"
        except: logger(f"get_tubi_tv_stream Error {traceback.print_exc()}")

        if "m3u8" in stream: Common.play(stream, name)
        else: Common.dlg_failed(f"Can not found url for: {name}")


class Stream:

    # Begin Explore.org #
    @staticmethod
    def get_explore_org_streams():
        stream_list = []
        url = explore_org_base # base64.b64decode(explore_org_base).decode('UTF-8')
        data = Common.open_url(url)
        json_results = json.loads(data)['data']['feeds']
        for stream in sorted(json_results, key=lambda k: k['title']):
            if stream["is_inactive"] is False and stream["is_offline"] is False and stream["video_id"] is not None:
                if stream["thumb"] == "": icon = f"https://i.ytimg.com/vi/{stream['video_id']}/hqdefault.jpg"
                else: icon = stream["thumb"]
                if stream["thumbnail_large_url"] == "": fanart = f"https://i.ytimg.com/vi/{stream['video_id']}/hqdefault.jpg"
                else: fanart = stream["thumbnail_large_url"]
                meta = {"duration": 10}
                stream_list.append({"id": stream["video_id"], "icon": icon, "fanart": fanart, "title": stream["title"], "meta": meta})
        return stream_list
    # End Explore.org #

    # Begin Tubi TV #
    @staticmethod
    def get_meta(year, genre, plot, duration, itemtype):
        mediatype = 'movie'
        if itemtype == 'v':
            if duration <= 60: mediatype = 'episode'
        elif itemtype == 'tvshow':  mediatype = 'tvshow'
        meta = {"year": int(year), "genre": genre, "plot": plot, "duration": duration, "mediatype": mediatype}
        return meta


    @staticmethod
    def get_tubi_tv_categories():
        cat_list = []
        url = f'{tubi_tv_base}/containers/'
        # logger("url {}".format(url))
        data = Common.open_url(url)
        json_results = json.loads(data)
        for category in range(0, len(json_results['list'])):
            try: icon = json_results['hash'][json_results['list'][category]]['thumbnail']
            except: icon = aicon
            try:
                cat_list.append({"id": json_results['list'][category],
                                 "icon": icon,
                                 "title": json_results['hash'][json_results['list'][category]]['title']})
            except: logger(f"Stream get_tubi_tv_categories Error: {traceback.print_exc()}")
        return cat_list

    @staticmethod
    def get_tubi_tv_content(category):
        content_list = []
        url = f'{tubi_tv_base}/containers/{category}/content?cursor=1&limit=200'
        data = Common.open_url(url)
        json_results = json.loads(data)

        for movie in json_results['contents'].keys():
            try:
                if re.search(r"espanol|Español|lgbt|LGBT", str(json_results['contents'][movie]), flags=re.I): continue
                try: duration = json_results['contents'][movie]['duration']
                except: duration = 0
                try: year = json_results['contents'][movie]['year']
                except: year = 0000
                try: genre = json_results['contents'][movie]['tags']
                except: genre = []
                try: plot = json_results['contents'][movie]['description']
                except: plot = ''
                itemtype = json_results['contents'][movie]['type']
                meta = Stream.get_meta(year, genre, plot, duration, itemtype)
                content_list.append({"id": json_results['contents'][movie]['id'],
                                     "icon": json_results['contents'][movie]['posterarts'][0],
                                     "title": json_results['contents'][movie]['title'],
                                     "type": json_results['contents'][movie]['type'],
                                     "meta": meta})
            except: logger(f"Stream get_tubi_tv_content category: {category} Error {traceback.print_exc()}")
        return content_list

    @staticmethod
    def get_tubi_tv_episodes(show):
        episode_list = []
        url = f'{tubi_tv_base}/videos/0{show}/content'
        data = Common.open_url(url)
        json_results = json.loads(data)

        for season in range(0, len(json_results['children'])):
            try:
                for episode in range(0, len(json_results['children'][season]['children'])):
                    if re.search(r"espanol|Español|lgbt|LGBT", str(json_results['children'][season]['children'][episode]), flags=re.I): continue
                    try: duration = json_results['children'][season]['children'][episode]['duration']
                    except: duration = 0
                    try: year = json_results['children'][season]['children'][episode]['year']
                    except: year = 0000
                    try: genre = json_results['children'][season]['children'][episode]['tags']
                    except: genre = []
                    try: plot = json_results['children'][season]['children'][episode]['description']
                    except: plot = ''
                    itemtype = 'tvshow'
                    meta = Stream.get_meta(year, genre, plot, duration, itemtype)
                    episode_list.append({"id": json_results['children'][season]['children'][episode]['id'],
                                         "icon": json_results['children'][season]['children'][episode]['thumbnails'][0],
                                         "title": json_results['children'][season]['children'][episode]['title'],
                                         "meta": meta})
            except: logger(f"Stream get_tubi_tv_episodes category: {show} Error {traceback.print_exc()}")
        return episode_list

    @staticmethod
    def get_tubi_tv_search(query):
        search_list = []
        url = f'{tubi_tv_base}/search/{query}'
        data = Common.open_url(url)
        json_results = json.loads(data)

        for result in json_results:
            try:
                if not re.search(r"espanol|Español|lgbt|LGBT", str(result), flags=re.I): continue
                try: duration = result['duration']
                except: duration = 0
                try: year = result['year']
                except: year = 0000
                try: genre = result['tags']
                except: genre = []
                try: plot = result['description']
                except: plot = ''
                # logger(f"Stream search result {result}")
                itemtype = result['type']
                meta = Stream.get_meta(year, genre, plot, duration, itemtype)
                search_list.append({"id": result['id'],
                                    "icon": result['posterarts'][0],
                                    "title": result['title'],
                                    "type": itemtype,
                                    "meta": meta})
            except: logger(f"Stream get_tubi_tv_search result: {result} Error {traceback.print_exc()}")
        return search_list

    # End Tubi TV #
