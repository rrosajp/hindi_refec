# -*- coding: utf-8 -*-

import json
from datetime import timedelta
import re
import traceback

from urllib.parse import urlencode, urljoin

try:
    from indexers.hindi.live_client import scrapePage, get_int_epi, keepclean_title, get_episode_date, find_season_in_title, string_date_to_num
    from indexers.hindi.hindi_meta import fetch_meta, get_plot_tvshow, gettmdb_id
    from modules.kodi_utils import logger, build_url, local_string as ls, get_setting, item_next, set_info, make_listitem, add_items, set_content, end_directory, set_view_mode, get_infolabel, notification, external_browse
    from caches.h_cache import main_cache
    from modules.watched_status import get_watched_info_movie, get_watched_status_movie, get_progress_percent, get_bookmarks, get_watched_info_tv, get_watched_status_episode

    thumb = 'https://i.imgur.com/p18A3dF.png'
    fanart = 'https://i.imgur.com/p18A3dF.png'  # 'https://i.imgur.com/aYEzi5o.jpg'
    selct_scrape, rescrape_select, clearprog_str = ls(50009), ls(32014), ls(32651)
    options_str, watched_str = ls(32646), ls(32642)
    watched_str, unwatched_str = ls(32642), ls(32643)
    opensettings_params = build_url({'mode': 'open_settings', 'query': '0.0'})
    old_hindi_shows = get_setting('old.hindi_shows', 'false') == 'true'
except:
    # logger(f'Error: {traceback.print_exc()}')
    from modules.live_client import scrapePage, get_int_epi, keepclean_title, get_episode_date, find_season_in_title, read_write_file, string_date_to_num
    from modules.utils import logger
    from modules.h_cache import main_cache
    from hindi_meta import fetch_meta, get_plot_tvshow, gettmdb_id

    old_hindi_shows = 'true'

from modules.dom_parser import parseDOM


desirule_url = "https://www.desirulez.cc:443"
run_plugin = 'RunPlugin(%s)'


def movies(params):
    # logger(f'from : movies params: {params}')
    pg_no = int(params['pg_no'])
    ch_name = params['list_name']
    url = params['url']
    rescrape = params['rescrape']
    iconImage = params['iconImage']

    def _process():
        for item in movies_data:
            # logger(f'desirulez _process item: {item}')
            try:
                listitem = make_listitem()
                set_properties = listitem.setProperties
                cm = []
                cm_append = cm.append
                title = item['title']
                year = item['year']
                meta = item['meta']
                poster = meta.get('poster')
                tmdb_id = meta.get('tmdb_id', item['tmdb_id'])
                imdb_id = meta.get('imdb_id', tmdb_id)
                playcount, overlay = get_watched_status_movie(watched_info, str(tmdb_id))
                # logger(f'from : _process tmdb_id: {tmdb_id} playcount: {playcount} overlay: {overlay}')
                meta.update({'mediatype': 'movie', 'premiered': str(year), 'original_title': title, 'playcount': playcount, 'overlay': overlay, 'url': item['url'], 'fanart': poster})
                meta_json = json.dumps(meta)
                setUniqueIDs = {'imdb': str(imdb_id), 'tmdb': str(tmdb_id)}
                listitem.setLabel(title.title())
                if 'Next Page:' in title:
                    next_url_params = {'mode': 'vod_movies_list', 'list_name': ch_name, 'url': item['url'], 'pg_no': item['pg_no'], 'rescrape': 'false', 'iconImage': iconImage}
                    url = build_url(next_url_params)
                    listitem.setArt({'icon': item_next, 'fanart': fanart})
                    set_properties({'SpecialSort': 'bottom', 'infinite_listitem_meta': meta_json})
                    listitem = set_info(listitem, meta, setUniqueIDs)
                    isfolder = True
                else:
                    url_params = {'mode': 'vod_prov_scape', 'media_type': 'movie', 'tmdb_id': tmdb_id, 'hindi_scrape': 'hindi','meta': meta_json}
                    url = build_url(url_params)
                    progress = get_progress_percent(bookmarks, tmdb_id)
                    recrape_params = build_url({'mode': 'scrape_select', 'content': 'movie', 'meta': meta_json, 'c_type': 'hindi'})
                    cm_append((selct_scrape, run_plugin % recrape_params))
                    recrape_params = build_url({'mode': 'rescrape_select', 'content': 'movie', 'meta': meta_json, 'c_type': 'hindi'})
                    cm_append((rescrape_select, run_plugin % recrape_params))
                    cm_append(("[B]Open Settings[/B]", run_plugin % opensettings_params))
                    if progress:
                        clearprog_params = build_url({'mode': 'watched_unwatched_erase_bookmark', 'media_type': 'movie', 'tmdb_id': tmdb_id, 'refresh': 'true'})
                        cm_append((clearprog_str, run_plugin % clearprog_params))
                        set_properties({'WatchedProgress': progress, 'resumetime': progress, 'infinite_in_progress': 'true'})
                    if playcount:
                        unwatched_params = build_url({'mode': 'mark_as_watched_unwatched_movie', 'action': 'mark_as_unwatched', 'tmdb_id': tmdb_id, 'title': title, 'year': year})
                        cm_append((unwatched_str % 'Infinite', run_plugin % unwatched_params))
                    else:
                        watched_params = build_url({'mode': 'mark_as_watched_unwatched_movie', 'action': 'mark_as_watched', 'tmdb_id': tmdb_id, 'title': title, 'year': year})
                        cm_append((watched_str % 'Infinite', run_plugin % watched_params))
                    listitem.addContextMenuItems(cm)
                    listitem.setArt({'poster': poster, 'icon': poster, 'thumb': poster, 'clearart': poster, 'banner': '', 'fanart': fanart, 'clearlogo': '', 'landscape': ''})
                    listitem = set_info(listitem, meta, setUniqueIDs, progress)
                    extras_params = {'mode': 'extras_menu_choice', 'tmdb_id': tmdb_id, 'media_type': 'movie', 'is_widget': is_widget, 'meta': meta_json}
                    set_properties({'infinite_extras_menu_params': json.dumps(extras_params), 'infinite_listitem_meta': meta_json})
                    isfolder = False
                # list_items.append({'listitem': (url, listitem, isfolder), 'display': title})
                yield url, listitem, isfolder
            except: logger(f"desirulez movies {traceback.print_exc()}")

    string = f"{'movies_list'}_{ch_name}_{pg_no}"
    params = {'url': url, 'ch_name': ch_name, 'pg_no': pg_no, 'iconImage': iconImage}
    cache_name = string + urlencode(params)
    if rescrape == 'true':
        main_cache.delete(cache_name)
        movies_data = None
    else:
        movies_data = main_cache.get(cache_name)
    if not movies_data:
        # params.update({'rescrape': rescrape,})
        if 'desirulez' in url: movies_data = get_movies(params)
        else: movies_data = get_movies_desicinemas(params)
        if movies_data:
            # wrigtht_json(json_file, json.dumps(movies_data))
            main_cache.set(cache_name, movies_data, expiration=timedelta(hours=336))  # 14 days cache
    from sys import argv  # some functions like ActivateWindow() throw invalid handle less this is imported here.
    handle = int(argv[1])
    if movies_data:
        bookmarks = get_bookmarks(0, 'movie')
        watched_info = get_watched_info_movie(0)
        # logger(f"from movies len(bookmarks): {len(bookmarks)} bookmarks: {bookmarks}")
        # logger(f"from movies len(watched_info): {len(watched_info)} watched_info: {watched_info}")
        is_widget = external_browse()
        add_items(handle, list(_process()))
        set_content(handle, 'movies')
        end_directory(handle)
        set_view_mode('view.movies', 'movies')
    else:
        notification(f'No movies Found for: :{ch_name} Retry', 900)
        end_directory(handle)
        return


def get_movies(params):
    # logger(f'from : get_movies params: {params}')
    non_str_list = ['+', 'season', 'episode']
    url = params['url']
    ch_name = params['ch_name']
    # iconImage = params['iconImage']
    pg_no = params['pg_no']
    movies = results = next_p = []
    movies_page = scrapePage(url)
    if movies_page:
        results = parseDOM(movies_page.text, "h3", attrs={"class": "threadtitle"})
        next_p = parseDOM(movies_page.text, "span", attrs={"class": "prev_next"})
    for item in results:
        # logger(f'item: {item}')
        try:
            try: title = parseDOM(item, "a", attrs={"class": "title threadtitle_unread"})[0]
            except:
                title = parseDOM(item, "a", attrs={"class": "title"})
                title = title[0] if title else parseDOM(item, "a")[0]
            # title = title#.encode('ascii', 'ignore')
            # logger(f'title: {title} type(title): {type(title)}')
            try: parsed = re.compile(r'(.+) [{(](\d+|\w+ \d+|\w+)[})]').findall(str(title))[0]
            except: parsed = '', ''
            # logger(f'type title: {type(parsed[0])} parsed[0]: {parsed[0]} parsed[1] {parsed[1]}')
            title = parsed[0]
            year = parsed[1]
            if not re.search(r'\d{4}', year):
                try: year = re.search(r'\d{4}', title).group()
                except: year = 2022
            url = parseDOM(item, "a", ret="href")
            if not url: url = parseDOM(item, "a", attrs={"class": "title"}, ret="href")
            if type(url) is list and len(url) > 0: url = str(url[0])
            url = urljoin(desirule_url, url) if not url.startswith(desirule_url) else url
            if title and not any([x in title for x in non_str_list]):
                title = keepclean_title(title)
                tmdb_id = gettmdb_id('movie', title, year, None)
                meta = fetch_meta(mediatype='movie', title=title, tmdb_id=tmdb_id, homepage=url, year=year)
                movies.append({'year': year, 'ch_name': ch_name, 'url': url, 'tmdb_id': tmdb_id, 'meta': meta, 'pg_no': pg_no, 'title': title})
        except: logger(f"desirulez get_movies {traceback.print_exc()}")

    if next_p:
        next_p_url = parseDOM(next_p, "a", attrs={"rel": "next"}, ret="href")[0]
        if "?" in next_p_url: url = next_p_url.split("?")[0]
        else: url = next_p_url
        try:
            pg_no = re.compile(r'page\d{1,2}').findall(url)[0]
            pg_no = pg_no.replace('page', '')
            # logger(f"pg_no: {pg_no}")
        except:
            pg_no = '1'
        title = f"Next Page: {pg_no}"
        if url.startswith('forumdisplay'): url = f"https://www.desirulez.cc:443/{url}"
        movies.append({'year': '', 'ch_name': ch_name, 'url': url, 'tmdb_id': '', 'meta': {'poster': item_next, 'plot': f"For More: {ch_name} Movies Go To: {title}", 'genre': []}, 'pg_no': pg_no, 'title': title})
    # movies = json.dumps(movies, default = hindi_sources.dumper, indent = 2)
    # logger(f'len(movies): {len(movies)} movies :  {movies}')
    return movies


def get_movies_desicinemas(params):
    # logger(f'from : get_movies_desicinemas params: {params}')
    m_url = params['url']
    ch_name = params['ch_name']
    pg_no = params['pg_no']
    movies = results = next_p = []
    # m_url = 'https://desicinemas.tv/movies/'
    movies_page = scrapePage(m_url)
    # movies_page = to_utf8(remove_accents(movies_page))
    # movies_page = movies_page.replace('\n', ' ')
    # read_write_file(read=False, result=movies_page)
    # movies_page = read_write_file()
    # logger(f'movies_page: {movies_page}')
    # result = parseDOM(result, "div", attrs={"class": "Main Container"})
    if movies_page:
        results = parseDOM(movies_page.text, "li", attrs={"class": "TPostMv post-.+?"})
        next_p = parseDOM(movies_page.text, "div", attrs={"class": "nav-links"})
    # logger(f"total episodes: {len(result)} result: {result}")
    # r = [(parseDOM(i, 'a', ret='href'), parseDOM(i, 'a', ret='title'), parseDOM(i, 'a')[0]) for i in results]
    # logger(f'r: {r}\n >>>.')
    for i in results:
        try:
            url = parseDOM(i, 'a', ret='href')[0]
            title = parseDOM(i, "h2", attrs={"class": "Title"})[0]
            try:
                year = parseDOM(i, "span", attrs={"class": "Qlty Yr"})[0]
                if not year: year = parseDOM(i, "span", attrs={"class": "Date"})[0]
            except: year = 2023
            # logger(f'genre: {genre}\n >>>.')
            # logger(f'url: {Descri}\n >>>.')
            # if url:
            if '(Punjabi)' in title: continue
            if '(Marathi)' in title: continue
            title = keepclean_title(title)
            tmdb_id = gettmdb_id('movie', title, year, None)
            imgurl = parseDOM(i, 'img', ret='data-src')[0]
            Descri = parseDOM(i, "div", attrs={"class": "Description"})[0]
            plot = parseDOM(Descri, "p")[0]
            genre = parseDOM(Descri, "p", attrs={"class": "Genre"})
            genre = parseDOM(genre, "a")
            # if type(genre) is list: genre = ', '.join(x.strip() for x in genre if x != '')
            cast = parseDOM(Descri, "p", attrs={"class": "Cast"})
            cast = parseDOM(cast, "a")
            # logger(f'imdbdata: {imdbdata}')
            meta = fetch_meta(mediatype='movie', title=title, tmdb_id=tmdb_id, homepage=url, poster=imgurl, year=year, plot=plot, genre=genre, cast=cast)
            movies.append({'year': year, 'ch_name': ch_name, 'url': url, 'tmdb_id': tmdb_id, 'meta': meta, 'pg_no': pg_no, 'title': title})
        except:
            logger(f"get_movies_desicinemas {traceback.print_exc()}")

    # logger(f'total movies: {len(movies)} movies: {movies}')
    # ## Next page
    # logger(f"next_p: {next_p}")
    if not movies: return
    if next_p:
        try:
            # next_p_u = parseDOM(next_p, "a", attrs={"class": "page-link"}, ret="href")[1]
            next_p_u = parseDOM(next_p, "a", ret="href")[-1]
            # logger(f"next_p_u: {next_p_u}")
            pg_no = re.compile('/([0-9]+)/').findall(next_p_u)[0]
            # logger(f"pg_no: {pg_no}")
            title = f"Next Page: {pg_no}"
            movies.append({'year': '', 'ch_name': ch_name, 'url': next_p_u, 'tmdb_id': '', 'meta': {'poster': item_next, 'plot': f"For More: {ch_name} Movies Go To: {title}", 'genre': ['-']}, 'pg_no': pg_no, 'title': title})
        except: logger(f"get_movies_desicinemas {traceback.print_exc()}")
    # logger(f'total movies: {len(movies)} movies: {movies}')
    return movies


def tv_shows(params):
    # logger(f'from : tv_shows params: {params}')
    ch_name = params['list_name']
    url = params['url']
    iconImage = params['iconImage']
    rescrape = params['rescrape']
    string = f"{'shows_list'}_{ch_name}"
    params = {'url': url, 'ch_name': ch_name, 'iconImage': iconImage}
    cache_name = string + urlencode(params)
    if rescrape == 'true':
        main_cache.delete(cache_name)
        shows = None
    else:
        shows = main_cache.get(cache_name)
    # logger(f"For shows: {shows} params: {params}")
    if not shows:
        # params.update({'rescrape': rescrape,})
        if 'desirulez' in url: shows = get_tv_shows(params)
        elif 'yodesi' in url: shows = get_tv_shows_yo(params)
        elif 'playdesi' in url or 'serials' in url: shows = get_tv_shows_desitelly(params)

        if shows: main_cache.set(cache_name, shows, expiration=timedelta(hours=336))  # 14 days cache

    def _process():
        for item in shows:
            try:
                if old_hindi_shows == 'false' and '-archive' in item['url']:
                    # logger(f"meta For show old_hindi_shows: {old_hindi_shows} item['url']: {item['url']}")
                    continue
                cm = []
                # info = {}
                cm_append = cm.append
                title = item['title']
                meta = item['meta']
                # logger(f"meta For show title: {title} meta: {repr(meta)}")
                poster = meta.get('poster', iconImage)
                tmdb_id = meta.get('tmdb_id')
                playcount = item['playcount'] if item.get('playcount', None) else 0
                total_seasons = meta.get('seasons', 1)
                if ',' in str(total_seasons):
                    total_seasons = total_seasons.split(',')[-1]
                    total_seasons = total_seasons.strip()
                # info.update({'tvshowtitle': title, 'mediatype': 'tvshow', 'genre': meta.get('genre'), 'year': meta.get('year'), 'plot': meta.get('plot'), 'duration': meta.get('duration'),})
                meta.update({'mediatype': 'tvshow', 'playcount': playcount, 'original_title': title, 'season': meta.get('season', 1), 'total_seasons': total_seasons, 'url': item['url'], 'fanart': poster, 'premiered': str(meta.get('year'))})
                # logger(f"meta For show title: {title} info: {info}")
                meta_json = json.dumps(meta)
                # logger(f"meta_json: {meta_json}")
                url_params = {'mode': 'vod_tvepis_dr', 'list_name': title, 'ch_name': ch_name, 'url': item['url'], 'thumb': poster, 'meta': meta_json, 'pg_no': '1', 'rescrape': 'false'}
                url = build_url(url_params)
                listitem = make_listitem()
                set_properties = listitem.setProperties
                listitem.setLabel(title.title())
                listitem.setArt({'icon': poster, 'poster': poster, 'thumb': poster, 'fanart': fanart, 'banner': poster})
                recrape_params = {'mode': 'vod_tvepis_dr', 'list_name': title, 'ch_name': ch_name, 'url': item['url'], 'thumb': poster, 'meta': meta_json, 'pg_no': '1', 'rescrape': 'true'}
                cm_append(("[B]Reload list[/B]", run_plugin % build_url(recrape_params)))
                cm_append(("[B]Open Settings[/B]", run_plugin % opensettings_params))
                # cm_append(("[B]Add to a Menu[/B]", run_plugin % build_url({'mode': 'menu_editor.add_external', 'name': title, 'iconImage': poster})))
                cm_append(("[B]Add to a Shortcut Folder[/B]", run_plugin % build_url({'mode': 'menu_editor.shortcut_folder_add_item', 'name': title, 'iconImage': poster})))
                extras_params = {'mode': 'extras_menu_choice', 'tmdb_id': tmdb_id, 'media_type': 'tvshow', 'is_widget': is_widget, 'meta': meta_json}
                listitem.addContextMenuItems(cm, replaceItems=False)
                imdb_id = meta.get('imdb_id', tmdb_id)
                setUniqueIDs = {'imdb': str(imdb_id), 'tmdb': str(tmdb_id), 'tvdb': ''}
                listitem = set_info(listitem, meta, setUniqueIDs)
                set_properties({'infinite_extras_menu_params': json.dumps(extras_params), 'totalepisodes': str(meta.get('episodes', '1')), 'totalseasons': str(total_seasons), 'infinite_listitem_meta': meta_json})
                yield url, listitem, True
            except: logger(f"desirulez tv_shows item: {item} Error: {traceback.print_exc()}")

    from sys import argv  # some functions like ActivateWindow() throw invalid handle less this is imported here.
    handle = int(argv[1])
    if shows:
        is_widget = external_browse()
        add_items(handle, list(_process()))
        set_content(handle, 'tvshows')
        end_directory(handle)
        set_view_mode('view.main', 'tvshows')
    else:
        notification(f'No Shows Found for: {ch_name} Retry or change the Hindi provider in setting.')
        end_directory(handle)
        return


def get_tv_shows(params):
    # logger(f'from : get_tv_shows params: {params}')
    url = params['url']
    ch_name = params['ch_name']
    iconImage = params['iconImage']
    shows = results = []
    show_page = scrapePage(url)
    if show_page:
        result = parseDOM(show_page.text, "h2", attrs={"class": "forumtitle"})
    # logger(f"items shows: {result}")
    for item in results:
        try: title = parseDOM(item, "a", attrs={"class": "title threadtitle_unread"})[0]
        except:
            title = parseDOM(item, "a", attrs={"class": "title"})
            title = title[0] if title else parseDOM(item, "a")[0]
        title = keepclean_title(title)
        url = parseDOM(item, "a", ret="href")
        if not url: url = parseDOM(item, "a", attrs={"class": "title"}, ret="href")
        if type(url) is list and len(url) > 0: url = str(url[0])
        if 'Past Shows' not in title:
            tmdb_id = gettmdb_id('tvshow', title, None, ch_name)
            url = urljoin(desirule_url, url) if not url.startswith(desirule_url) else url
            meta = fetch_meta(mediatype='tvshow', title=title, tmdb_id=tmdb_id, homepage=url, studio=ch_name, poster=iconImage)
            shows.append({"url": url, "title": title, "ch_name": ch_name, "tmdb_id": tmdb_id, "meta": meta})
    # logger(f'len(shows): {len(shows)} shows :  {shows}')
    return shows


def get_tv_shows_yo(params):
    # logger(f'from : get_tv_shows_yo params: {params}')
    url = params['url']
    ch_name = params['ch_name']
    iconImage = params['iconImage']
    shows = results = []
    show_page = scrapePage(url)
    # show_page = read_write_file('www.yodesi.net.html')
    if show_page:
        rawResult = parseDOM(show_page.text, "div", attrs={"id": "content_box"})[0]
        # result = parseDOM(rawResult, "div", attrs={"class": re.compile('^one_')})
        results = parseDOM(rawResult, "div", attrs={"class": "one_fourth  "})
        results += parseDOM(rawResult, "div", attrs={"class": "one_fourth  column-last "})
    # logger(f"result total: {len(result)} result: {result}")
    for item in results:
        # try:
        title = parseDOM(item, "p", attrs={"class": "small-title"})[0]
        url = parseDOM(item, "a", ret="href")[0]
        title = parseDOM(title, "a")[0]
        title = keepclean_title(title)
        if 'concert' in title.lower(): continue
        if type(url) is list and len(url) > 0: url = str(url[0])
        tmdb_id = gettmdb_id('tvshow', title, None, ch_name)
        show = {"url": url, "title": title, "ch_name": ch_name, "tmdb_id": f'{ch_name}|{title.lower()}'}
        if old_hindi_shows == 'true':
            meta = fetch_meta(mediatype='tvshow', title=title, tmdb_id=tmdb_id, homepage=url, studio=ch_name, poster=iconImage)
            show.update({"meta": meta})
            shows.append(show)
        elif '-archive' not in url:
            meta = fetch_meta(mediatype='tvshow', title=title, tmdb_id=tmdb_id, homepage=url, studio=ch_name, poster=iconImage)
            show.update({"meta": meta})
            shows.append(show)
        # except: pass
    # logger(f'len(shows): {len(shows)} shows :  {shows}')
    return shows


def get_tv_shows_desitelly(params):
    # logger(f'from : get_tv_shows_desitelly params: {params}')
    base_url = params['url']
    ch_name = params['ch_name']
    iconImage = params['iconImage']
    shows = results = []
    show_page = scrapePage(base_url)
    if show_page:
        results = parseDOM(show_page.text, "div", attrs={"class": "vc_column_container col-md-3"})
        results += parseDOM(show_page.text, "div", attrs={"class": "vc_column_container col-md-4"})
    # logger(f"result shows: {result}")

    for i in results:
        if i:
            url = parseDOM(i, 'a', ret='href')[0]
            lch_name = url.split('/')
            chan_name = lch_name[4]
            # ch_name = str(chan_name.replace('-', ' ').title())
            if chan_name:
                imgurl = parseDOM(i, 'img', ret='src')
                try: imgurl = imgurl[0]
                except: imgurl = iconImage
                if "www.desi-serials.cc" in base_url:
                    if imgurl.startswith('/images'): imgurl = f"https://www.desi-serials.cc{imgurl}"
                    try:
                        title = parseDOM(i, "a", attrs={"class": "porto-sicon-title-link"})[0]
                        title_overview = parseDOM(i, "div", attrs={"class": "porto-sicon-header"})[0]
                        genre = re.findall(r'<\/h5>\s+(.+?)$', title_overview)  # logger("1 desi-serials title: {} ,genre: {} ".format(title, genre))
                    except:
                        title_overview = parseDOM(i, "div", attrs={"class": "porto-sicon-header"})[0]
                        title_overview = re.findall(r'porto-sicon-title-link.+>(.+?)<\/a><\/h5>(.+?)$', title_overview)[0]
                        title = title_overview[0]
                        genre = title_overview[1]
                        logger(f"2 desi-serials title: {title} ,genre: {genre} ")
                else:
                    if imgurl.startswith('/images'): imgurl = f"https://playdesi.tv{imgurl}"
                    genre = parseDOM(i, 'p')  #[0]
                    title = parseDOM(i, 'h4', attrs={"class": "porto-sicon-title"})[0]
                title = keepclean_title(title)
                tmdb_id = gettmdb_id('tvshow', title, None, ch_name)
                # logger(f"for playdesi: title: {title} ,genre: {genre} ")
                # if imgurl is None: imgurl = iconImage
                meta = fetch_meta(mediatype='tvshow', title=title, tmdb_id=tmdb_id, homepage=url, studio=ch_name, poster=imgurl)
                shows.append({"url": url, "title": title, "ch_name": ch_name, "tmdb_id": tmdb_id, "meta": meta})
    # logger(f'len(shows): {len(shows)} shows :  {shows}')
    return shows


def tv_episo(params):
    # logger(f'from : tv_episo params: {params}')
    def _process():
        for item in episodes_data:
            try:
                # logger("desirulez _process item: {}".format(item))
                listitem = make_listitem()
                set_properties = listitem.setProperties
                cm = []
                cm_append = cm.append
                season = meta.get("season", 1)
                int_epi = item['episode']
                year = item['year']
                ep_name = item['title']
                # logger(f'title: {title} int_epi: {int_epi} ep_name: {ep_name}')
                premiered = item['premiered']
                tmdb_id = f"{ch_name}|{title.lower()}"
                poster = meta.get("poster", None)
                imdb_id = meta.get('imdb_id', tmdb_id)
                meta.update({'mediatype': 'episode', 'trailer': '', 'premiered': premiered, 'episode': int_epi, 'year': year, 'ep_name': ep_name, 'url': item['url']})
                setUniqueIDs = {'imdb': str(imdb_id), 'tmdb': str(tmdb_id), 'tvdb': ''}
                listitem.setLabel(ep_name.title())
                if 'Next Page:' in ep_name:
                    next_url_params = {'mode': 'vod_tvepis_dr', 'list_name': title, 'ch_name': ch_name, 'url': item['url'], 'thumb': poster, 'meta': json.dumps(meta), 'pg_no': item['pg_no'], 'rescrape': 'false'}
                    url = build_url(next_url_params)
                    item.update({'plot': f"For More:[CR]{title} [CR]Go To: {ep_name}"})
                    listitem.setArt({'icon': item_next, 'fanart': fanart})
                    set_properties({'SpecialSort': 'bottom'})
                    listitem = set_info(listitem, item, setUniqueIDs)
                    isfolder = True
                else:
                    # logger(f"tmdb_id: {repr(tmdb_id)} season: {repr(season)} , int_epi: {repr(int_epi)}")
                    playcount, overlay = get_watched_status_episode(watched_info, tmdb_id, int(season), int(int_epi))
                    # logger(f"tmdb_id: {tmdb_id} playcount: {playcount} , overlay: {overlay}")
                    meta.update({'playcount': playcount, 'overlay': overlay})
                    meta_json = json.dumps(meta)
                    # logger(f"desirulez tv_episo _process meta_json: {meta_json}")
                    url_params = {'mode': 'vod_prov_scape', 'media_type': 'episode', 'tmdb_id': tmdb_id, 'tvshowtitle': title, 'season': season, 'episode': int_epi, 'hindi_scrape': 'hindi', 'meta': meta_json}
                    url = build_url(url_params)
                    progress = get_progress_percent(bookmarks, tmdb_id, int(season), int(int_epi))
                    recrape_params = build_url({'mode': 'scrape_select', 'content': 'episode', 'meta': meta_json, 'season': season, 'episode': int_epi, 'c_type': 'hindi'})
                    cm_append((selct_scrape, run_plugin % recrape_params))
                    recrape_params = build_url({'mode': 'rescrape_select', 'content': 'episode', 'meta': meta_json, 'season': season, 'episode': int_epi, 'c_type': 'hindi'})
                    cm_append((rescrape_select, run_plugin % recrape_params))
                    cm_append(("[B]Open Settings[/B]", run_plugin % opensettings_params))
                    # logger(f'desirulez _process progress: {repr(progress)} playcount: {repr(playcount)} ep_name: {ep_name}')
                    if progress:
                        clearprog_params = build_url({'mode': 'watched_unwatched_erase_bookmark', 'media_type': 'episode', 'tmdb_id': tmdb_id, 'season': season, 'episode': int_epi, 'refresh': 'true'})
                        cm_append((clearprog_str, run_plugin % clearprog_params))
                        set_properties({'WatchedProgress': progress, 'resumetime': progress, 'infinite_in_progress': 'true'})
                    if playcount:
                        unwatched_params = build_url({'mode': 'mark_as_watched_unwatched_episode', 'action': 'mark_as_unwatched', 'tmdb_id': tmdb_id, 'tvdb_id': '', 'season': season, 'episode': int_epi, 'title': title, 'year': year})
                        cm_append((unwatched_str % 'Infinite', run_plugin % unwatched_params))
                    else:
                        watched_params = build_url({'mode': 'mark_as_watched_unwatched_episode', 'action': 'mark_as_watched', 'tmdb_id': tmdb_id, 'tvdb_id': '', 'season': season, 'episode': int_epi, 'title': title, 'year': year})
                        cm_append((watched_str % 'Infinite', run_plugin % watched_params))
                    listitem.addContextMenuItems(cm)
                    listitem.setArt({'poster': poster, 'fanart': fanart, 'icon': poster, 'thumb': poster, 'clearart': poster, 'banner': '', 'clearlogo': '', 'landscape': ''})
                    listitem = set_info(listitem, meta, setUniqueIDs, progress)
                    isfolder = False
                list_items_append({'listitem': (url, listitem, isfolder), 'display': ep_name})
                # yield url, listitem, isfolder
            except: logger(f"desirulez tv_episo item: {item} Error: {traceback.print_exc()}")

    from sys import argv  # some functions like ActivateWindow() throw invalid handle less this is imported here.
    handle = int(argv[1])
    list_items = []
    list_items_append = list_items.append
    url = params['url']
    title = params['list_name']
    ch_name = params['ch_name']
    page = params['pg_no']
    meta = params['meta']
    rescrape = params['rescrape']
    meta = json.loads(meta)
    string = f"{'episodes_list'}_{title}_{page}"
    params = {'url': url, 'title': title, 'ch_name': ch_name, 'pg_no': page}
    cache_name = string + urlencode(params)
    if rescrape == 'true':
        main_cache.delete(cache_name)
        episodes_data = None
    else:
        episodes_data = main_cache.get(cache_name)
    # episodes, next_page = cache_object(get_tv_episo, string, params, False, 12)
    if not episodes_data:
        # params.update({'rescrape': rescrape,})
        if 'desirulez' in url: episodes_data = get_tv_episo(params)
        elif 'yodesi' in url: episodes_data = get_tv_episo_yo(params)
        elif 'playdesi' in url or 'serials' in url: episodes_data = get_tv_episo_desitelly(params)
        if episodes_data: main_cache.set(cache_name, episodes_data, expiration=timedelta(hours=18))  # 12 hrs cache
    # logger(f"len(episodes_data): {len(episodes_data)} episodes_data: {episodes_data}")
    if episodes_data:
        bookmarks = get_bookmarks(0, 'episode')
        watched_info = get_watched_info_tv(0)
        # logger(f"from tv_episo len(bookmarks): {len(bookmarks)} bookmarks: {bookmarks}")
        # logger(f"from tv_episo len(watched_info): {len(watched_info)} watched_info: {watched_info}")
        _process()
        # logger(f"len(list_items): {len(list_items)} list_items: {list_items}")
        if 'Episode' in list_items[0]['display']: list_items.sort(key=lambda x: x['display'])
        # logger(f"len(list_items): {len(list_items)} list_items: {list_items}")
        item_list = [i['listitem'] for i in list_items]
        add_items(handle, item_list)
        set_content(handle, 'episodes')
        end_directory(handle)
        set_view_mode('view.episode_lists', 'episodes')
    else:
        notification(f'No Episode Found for: {title} Retry or change the Hindi provider in setting.')
        end_directory(handle)
        return


def get_tv_episo(params):
    # logger(f'from : get_tv_episo params: {params}')
    try:
        url = params['url']
        title = params['title']
        ch_name = params['ch_name']
        pg_no = params['pg_no']
        # logger(f'title: {title} url: {url}')
        episo_page = scrapePage(url).text
        results = parseDOM(episo_page, "h3", attrs={"class": "title threadtitle_unread"})
        results += parseDOM(episo_page, "h3", attrs={"class": "threadtitle"})
        episodes = []
        for item in results:
            ep_name = parseDOM(item, "a", attrs={"class": "title"})
            ep_name += parseDOM(item, "a", attrs={"class": "title threadtitle_unread"})
            if type(ep_name) is list: ep_name = ep_name[0]
            url = parseDOM(item, "a", ret="href")
            if type(url) is list: url = url[0]
            if "Online" not in ep_name: continue
            # logger(f"title: {title} ep_name: {ep_name}")
            if not title == 'Awards': ep_name = get_episode_date(ep_name, title)
            if "?" in url: url = url.split("?")[0]
            url = urljoin(desirule_url, url) if not url.startswith(desirule_url) else url
            # urls.append(url)
            int_epi, year = get_int_epi(ep_name)
            premiered = string_date_to_num(ep_name)
            episodes.append({"url": url, "title": ep_name, "ch_name": ch_name, "episode": int_epi, "premiered": premiered, "year": int(year), "pg_no": pg_no})

        next_p = parseDOM(episo_page, "span", attrs={"class": "prev_next"})
        if next_p:
            next_p_u = parseDOM(next_p, "a", attrs={"rel": "next"}, ret="href")
            if next_p_u:
                next_p_u = next_p_u[0]
                if "?" in next_p_u: url = next_p_u.split("?")[0]
                else: url = next_p_u
                try:
                    pg_no = re.compile(r'page\d{1,2}').findall(url)[0]
                    pg_no = pg_no.replace('page', '')
                    # logger(f"pg_no: {pg_no}")
                except:
                    pg_no = '1'
                name = f"Next Page: {pg_no}"
                url = urljoin(desirule_url, url) if not url.startswith(desirule_url) else url
                episodes.append({"url": url, "title": name, "ch_name": ch_name, "plot": f"For More {title} Go To {name} ....", "episode": pg_no, "premiered": '', "season": 0, "year": 0, "pg_no": pg_no})
        # logger(f'len(shows): {len(episodes)} episodes :  {episodes}')
        return episodes
    except: logger(f'get_tv_episo episodes {traceback.print_exc()}')


def get_tv_episo_yo(params):
    # logger(f'from : get_tv_episo_yo params: {params}')
    try:
        url = params['url']
        title = params['title']
        ch_name = params['ch_name']
        pg_no = params['pg_no']
        # logger(f'title: {title} url: {url}')
        episo_page = scrapePage(url).text

        results = parseDOM(episo_page, "article")
        # logger(f"total episodes: {len(result)} result: {result}")
        episodes = []
        for item in results:
            if "promo" in item or '(Day' in item: continue
            item = parseDOM(item, "h2")[0]
            ep_name = parseDOM(item, "a", ret="title")
            if type(ep_name) is list: ep_name = ep_name[0]
            url = parseDOM(item, "a", ret="href")
            if type(url) is list: url = url[0]
            if "Online" not in ep_name: continue
            ep_name = get_episode_date(ep_name, title)
            int_epi, year = get_int_epi(ep_name)
            premiered = string_date_to_num(ep_name)
            episodes.append({"url": url, "title": ep_name, "ch_name": ch_name, "episode": int_epi, "premiered": premiered, "year": int(year), "pg_no": pg_no})
        # logger(f"episodes: {episodes}")
        next_p = parseDOM(episo_page, "div", attrs={"class": "nav-links"})
        if next_p:
            next_p_u = next_pagination_dict(next_p, title, ch_name)
            if next_p_u: episodes.append(next_p_u)
        # logger(f'len(shows): {len(episodes)} episodes :  {episodes}')
        return episodes
    except: logger(f'get_tv_episo_yo episodes {traceback.print_exc()}')


def get_tv_episo_desitelly(params):
    # logger(f'from : get_tv_episo_desitelly params: {params}')
    try:
        url = params['url']
        title = params['title']
        ch_name = params['ch_name']
        pg_no = params['pg_no']
        episo_page = scrapePage(url).text
        #episo_page = read_write_file('JSTesting/www.desi-serials.cc.html')
        # logger(f"episo_page: {episo_page}")
        results = parseDOM(episo_page, "div", attrs={"class": "main-content col-lg-9"})
        # logger(f"results: {results}")
        if not results:
            results = parseDOM(episo_page, "div", attrs={"class": "blog-posts posts-large posts-container"})
            # logger(f"results: {results}")
        # ## for Episodes <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        results = parseDOM(results, "h2", attrs={"class": "entry-title"})
        # logger(f"total episodes: {len(results)} results: {results}")
        episodes = []
        for i in results:
            url = parseDOM(i, 'a', ret='href')[0]
            # logger(f"url: {url}")
            ep_name = parseDOM(i, 'a')[0]
            # logger(f"ep_name: {ep_name}")
            # ep_name = unescape(ep_name)
            if "watch online" in ep_name.lower() and "episode" in ep_name.lower():
                if 'Awards' in title:
                    ep_name = ep_name.lower().replace("watch online", "").replace("hd", "").replace("telecast", "")
                    ep_name = ep_name.title()
                else:
                    if "Episode" in ep_name: ep_name = get_episode_date(ep_name, title)
                if ep_name:
                    int_epi, year = get_int_epi(ep_name)
                    premiered = string_date_to_num(ep_name)
                    # logger(f"ep_name: {ep_name}")
                    episodes.append({"url": url, "title": ep_name, "ch_name": ch_name, "episode": int_epi, "premiered": premiered, "year": int(year), "pg_no": pg_no})
        # ## for Next page <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        next_p = parseDOM(episo_page, "div", attrs={"class": "pagination-wrap"})
        # logger(f"next_p: {next_p}")
        if next_p:
            next_p_u = next_pagination_dict(next_p, title, ch_name)
            if next_p_u: episodes.append(next_p_u)
        # logger(f'len(shows): {len(episodes)} episodes :  {episodes}')
        return episodes
    except: logger(f'get_tv_episo_desitelly episodes {traceback.print_exc()}')


def next_pagination_dict(next_p, title, ch_name):
    next_p_u = parseDOM(next_p, "a", attrs={"class": "next page-numbers"}, ret="href")
    if next_p_u:
        next_p_url = next_p_u[0]
        # logger(f'{repr(next_p_url)}')
        pg_no = re.compile('/([0-9]+)/').findall(next_p_url)[0]
        name = f"Next Page: {pg_no}"
        next_dict = {"url": next_p_url, "title": name, "ch_name": ch_name, "premiered": '', "plot": f"For More {title} Go To {name} ....", "episode": pg_no, "season": 0, "year": 0, "pg_no": pg_no}
        return next_dict
    else: return
