# -*- coding: utf-8 -*-
import traceback
from modules.kodi_utils import logger, get_setting, sleep
# from modules.kodi_utils import update_hindi_metadb
from windows.skip import Skip
from windows import open_window, create_window
import sys, time, datetime
# from caches import clean_databases


def testting():
    # update_hindi_metadb()
    test_window()


def test_window(win='confirm_progress_media'):
    meta = {'tmdb_id': 21572, 'tvdb_id': 170491, 'imdb_id': 'tt1190931', 'rating': 8.4, 'plot': 'Case 1: The Imposter: Dr. Barnes For twenty years he was an imposter doctor! Dr. Gerald Barnes has a thriving practice specializing in "executive" medical exams. His salary is six-figures and life is good. But there\'s a problem: he\'s not the real Dr. Gerald Barnes. Case 2: Interstate Bank Mart Bandit He leaves no clues behind, only a trail of broken dreams and empty bank accounts. Forty-three robberies in 20 months. The M.O. is always the same. Police say it\'s the work of one man: "The Interstate Bank Mart Bandit!".', 'tagline': '', 'votes': 8, 'premiered': '2007-06-28', 'year': '2007', 'poster': 'https://image.tmdb.org/t/p/w185/bilmBb9Q4sLesr1gdMknSGfQQ7H.jpg', 'fanart': 'https://image.tmdb.org/t/p/w300/z7OINGcfImMIU4bg0EUrrycZWR6.jpg', 'genre': ['Documentary', 'Crime'], 'title': 'American Greed', 'original_title': 'American Greed', 'english_title': '', 'season_data': [{'air_date': '2009-09-09', 'episode_count': 3, 'id': 31339, 'name': 'Specials', 'overview': '', 'poster_path': None, 'season_number': 0}, {'air_date': '2007-06-21', 'episode_count': 6, 'id': 31335, 'name': 'Season 1', 'overview': '', 'poster_path': None, 'season_number': 1}, {'air_date': '2008-01-30', 'episode_count': 10, 'id': 31336, 'name': 'Season 2', 'overview': '', 'poster_path': None, 'season_number': 2}, {'air_date': '2009-01-07', 'episode_count': 8, 'id': 31337, 'name': 'Season 3', 'overview': '', 'poster_path': None, 'season_number': 3}, {'air_date': '2010-02-03', 'episode_count': 12, 'id': 31338, 'name': 'Season 4', 'overview': '', 'poster_path': None, 'season_number': 4}, {'air_date': '2011-01-19', 'episode_count': 14, 'id': 31340, 'name': 'Season 5', 'overview': '', 'poster_path': None, 'season_number': 5}, {'air_date': '2012-01-25', 'episode_count': 17, 'id': 31341, 'name': 'Season 6', 'overview': '', 'poster_path': None, 'season_number': 6}, {'air_date': '2013-02-22', 'episode_count': 13, 'id': 31342, 'name': 'Season 7', 'overview': '', 'poster_path': None, 'season_number': 7}, {'air_date': None, 'episode_count': 1, 'id': 83919, 'name': 'Season 8', 'overview': '', 'poster_path': None, 'season_number': 8}, {'air_date': '2015-01-15', 'episode_count': 6, 'id': 83918, 'name': 'Season 9', 'overview': '', 'poster_path': None, 'season_number': 9}, {'air_date': '2016-03-31', 'episode_count': 12, 'id': 79035, 'name': 'Season 10', 'overview': '', 'poster_path': None, 'season_number': 10}, {'air_date': '2017-01-23', 'episode_count': 5, 'id': 85896, 'name': 'Season 11', 'overview': '', 'poster_path': None, 'season_number': 11}, {'air_date': '2018-02-26', 'episode_count': 20, 'id': 100110, 'name': 'Season 12', 'overview': '', 'poster_path': None, 'season_number': 12}, {'air_date': '2019-08-12', 'episode_count': 16, 'id': 130186, 'name': 'Season 13', 'overview': '', 'poster_path': None, 'season_number': 13}, {'air_date': '2021-01-18', 'episode_count': 7, 'id': 166369, 'name': 'Season 14', 'overview': '', 'poster_path': '/lp4BWrPsfQUY0yTBBbkbdUJkfPm.jpg', 'season_number': 14}, {'air_date': '2021-06-27', 'episode_count': 6, 'id': 200545, 'name': 'Season 15', 'overview': '', 'poster_path': None, 'season_number': 15}], 'alternative_titles': [], 'duration': 2580, 'rootname': 'American Greed - 1x02', 'imdbnumber': 'tt1190931', 'country': [], 'mpaa': '', 'trailer': '', 'country_codes': [], 'writer': [], 'director': [], 'all_trailers': [], 'cast': [], 'studio': ['CNBC'], 'extra_info': {'status': 'Returning Series', 'type': 'Documentary', 'homepage': 'https://www.cnbc.com/american-greed/', 'created_by': 'N/A', 'next_episode_to_air': None, 'last_episode_to_air': {'air_date': '2021-07-12', 'episode_number': 6, 'id': 3071490, 'name': "A Father's Fraud", 'overview': 'Karl Karlsen is a hardworking man with what seems to be a terrible streak of bad luck, as his wife and son both die in accidents nearly 20 years apart; Karl has a secret: their suspicious deaths have been keeping his bank account full.', 'production_code': '', 'runtime': 43, 'season_number': 15, 'show_id': 21572, 'still_path': None, 'vote_average': 0.0, 'vote_count': 0}}, 'total_aired_eps': 153, 'mediatype': 'tvshow', 'total_seasons': 15, 'tvshowtitle': 'American Greed', 'status': 'Returning Series', 'clearlogo': '', 'images': {'backdrops': [{'file_path': '/hLA3vuKSOXmyu7DH804huzlgj9j.jpg'}, {'file_path': '/jqWjO8VDnX56zzBTQSZO0E3Aa7Z.jpg'}], 'logos': [], 'posters': [{'file_path': '/bilmBb9Q4sLesr1gdMknSGfQQ7H.jpg'}]}, 'changed_artwork': {}, 'poster2': '', 'fanart2': '', 'clearlogo2': '', 'banner': '', 'clearart': '', 'landscape': '', 'discart': '', 'keyart': '', 'fanart_added': True, 'media_type': 'episode', 'season': 1, 'episode': 2, 'ep_name': 'The Imposter: Dr. Barnes / Interstate Bank Mart Bandit', 'background': False, 'skip_option': {'title': 'American Greed', 'service': 'True', 'skip': '50', 'start': '10', 'eskip': '60'}, 'skip_style': 'netflix', 'url': 'stack://https://hls10x.vidfiles.net/videos/hls/Xfr7iZq8WhU_8biyCi66dw/1663270600/336669/c57c343c19862f3f143cb7c67efe60be/ep.1.v1.1655284255.m3u8|User-Agent=Mozilla%2F5.0+%28Windows+NT+10.0%3B+Win64%3B+x64%3B+rv%3A68.0%29+Gecko%2F20100101+Firefox%2F68.0&Referer=https%3A%2F%2Fmembed.net%2Floadserver.php%3Fid%3DMzM2NjY5', 'bookmark': 0}
    # meta = {'mediatype': 'episode', 'year': 2022, 'plot': 'The Kapil Sharma Show, also known as TKSS, is an Indian Hindi-language stand-up comedy and talk show broadcast by Sony Entertainment Television. Hosted by Kapil Sharma The series revolved around Sharma and his neighbours in the Shantivan Non Co-operative Housing Society.', 'title': 'The Kapil Sharma Show Season 4', 'studio': ['Sony'], 'poster': 'https://www.desi-serials.cc/wp-content/uploads/2022/08/The-Kapil-Sharma-Show-300x169.jpg', 'homepage': 'https://www.desi-serials.cc/watch-online/sony-tv/the-kapil-sharma-show-season-4/', 'genre': ['Saturday  Sunday.', 'Comedy', 'Talk-Show'], 'cast': [], 'tmdb_id': 'Sony|The Kapil Sharma Show Season 4', 'imdb_id': 'tt5747326', 'rating': 7.3, 'clearlogo': '', 'trailer': '', 'votes': 50, 'tagline': '', 'director': [], 'writer': [], 'episodes': 390, 'seasons': '1, 2, 3, 4', 'extra_info': {'status': '', 'collection_id': ''}, 'tvdb_id': 'Sony|the kapil sharma show', 'duration': 3600, 'mpaa': 'TV-MA', 'season': 4, 'episode': 910, 'tvshowtitle': 'The Kapil Sharma Show Season 4', 'playcount': 0, 'original_title': 'The Kapil Sharma Show Season 4', 'total_seasons': '4', 'url': 'https://www.desi-serials.cc/the-kapil-sharma-show-season-4-episode-10th-september-2022-watch-online/441968/', 'fanart': 'https://www.desi-serials.cc/wp-content/uploads/2022/08/The-Kapil-Sharma-Show-300x169.jpg', 'premiered': '2022-09-10', 'ep_name': '10th September 2022', 'overlay': 4, 'media_type': 'episode', 'background': False, 'skip_option': {'title': 'The Kapil Sharma Show', 'service': 'True', 'skip': '50', 'start': '10', 'eskip': '300'}, 'skip_style': 'netflix'}
    if win == 'nextep_win': # windows.next_episode <<<<<<<<<
        # action = open_window(('windows.next_episode', 'NextEpisode'), 'next_episode.xml', meta=meta, function='confirm')
        # action = open_window(('windows.next_episode', 'NextEpisode'), 'next_episode.xml', meta=meta, test=True, function='next_ep')
        action = open_window(('windows.next_episode', 'NextEpisode'), 'next_episode.xml', meta=meta, test=True, default_action='cancel', play_type='autoplay_nextep', focus_button=11)
        action = open_window(('windows.next_episode', 'NextEpisode'), 'next_episode.xml', meta=meta, test=True, default_action='cancel', play_type='autoscrape_nextep', focus_button=11)
    elif win == 'infopop': # windows.infopop <<<<<<<<<
        action = open_window(('windows.extras', 'Extras'), 'extras.xml', meta=meta, is_widget='false')
    elif win == 'skip_win': # windows.skip <<<<<<<<<<
        skip_option = {'title': 'The Blacklist', 'service': 'True', 'skip': '50', 'start': '10', 'eskip': '300'}
        # if get_setting('skip.dialog') == "Regular":
            # buttonskip = open_window(('windows.skip', 'Skip'), 'skip_dialog.xml', skip_option=skip_option)
            # # buttonskip = Skip("skip_dialog.xml", location, "default", "1080i", skip_option=self.skip_option)
        # else:
            # buttonskip = open_window(('windows.skip', 'Skip'), 'skip.xml', skip_option=skip_option)
        windowstyle = get_setting('skip.dialog')
        logger(f'windowstyle: {windowstyle.lower()}')
        buttonskip = open_window(('windows.skip', 'Skip'), 'skipmulti.xml', skip_option=skip_option, focus_button=201, window_style=windowstyle.lower())
        logger(f'buttonskip: {buttonskip}')
    elif win == 'confirm_progress_media': # confirm_progress_media && resolver_dialog<<<<<<<
        from threading import Thread
        from modules import kodi_utils, settings
        # kwargs = {'meta': meta, 'text': 'ok i see', 'enable_buttons': True, 'true_button': "Yes", 'false_button': "No", 'focus_button': 11}
        kwargs = {'meta': meta, 'text': 'ok i see', 'enable_fullscreen': True}
        _threads = []
        start_time = time.time()
        timeout = 20
        sleep_time = settings.display_sleep_time()
        end_time = start_time + timeout
        line1 = '[COLOR %s][B]%s[/B][/COLOR]'
        main_line = '%s[CR]%s[CR]%s'
        dialog_format, remaining_format = '[COLOR %s][B]%s[/B][/COLOR] 4K: %s | 1080p: %s | 720p: %s | SD: %s | Total: %s', kodi_utils.local_string(32676)
        progress_dialog = kodi_utils.confirm_progress_media(meta=meta, enable_fullscreen=True)
        # progress_dialog = kodi_utils.confirm_progress_media(meta=meta, enable_fullscreen=False)
        # progress_dialog = kodi_utils.confirm_progress_media(meta=meta, text="Resume Point: [B]15%%[/B]", enable_buttons=True, true_button="Resume", false_button="Start Over", focus_button=10, percent=15)
        ### &&&& for resolver_dialog uncomment next line
        progress_dialog.enable_resolver()
        remaining_providers = ['freeworldnews.tv', 'playersb.com', 'vedshare.com', 'voeunblock8.com', 'youtu.be']
        while not progress_dialog.iscanceled():
            try:
                if kodi_utils.monitor.abortRequested(): break
                if progress_dialog.iscanceled():
                    progress_dialog.close()
                    break
                # self._process_internal_results()
                s4k_label, s1080_label = 5, 10
                s720_label, ssd_label, stotal_label = 7, 10, 25
                try:
                    current_time = time.time()
                    current_progress = current_time - start_time
                    line2 = dialog_format % ('dodgerblue', 'Int:', s4k_label, s1080_label, s720_label, ssd_label, stotal_label)
                    line3 = remaining_format % ', '.join(remaining_providers).upper()
                    percent = int((current_progress/float(timeout))*100)
                    progress_dialog.update(main_line % (line1, line2, line3), percent)
                    kodi_utils.sleep(10)
                    # if len(remaining_providers) == 0: break
                    # if percent >= 100:
                        # progress_dialog.close()
                        # break
                except:
                    logger(f'error: {traceback.format_exc()}')
                    progress_dialog.close()
            except:
                logger(f'error: {traceback.format_exc()}')
                progress_dialog.close()
        if progress_dialog.iscanceled():
            progress_dialog.close()
    elif win == 'select_ok_win': # windows.select_ok <<<<<<<<<<<<
        from modules.kodi_utils import local_string, confirm_dialog, ok_dialog
        confirm_dialog(heading='Infinite', text=local_string(32855), ok_label=local_string(32824), cancel_label=local_string(32828), top_space=True)
        ok_dialog(heading='Infinite', text=local_string(32855))

def cache_test():
    ctime = datetime.datetime.now()
    current_time = int(time.mktime(ctime.timetuple()))
    clean_databases(current_time, database_check=False, silent=True)
    from modules.source_utils import sources
    providers = sources('true', 'episode')
    from indexers.hindi.lists import youtube_m3u
    youtube_m3u()
    from caches.h_cache import MainCache
    MainCache().clean_hindi_lists()
    logger(providers)
    from caches import clrCache_version_update
    clrCache_version_update(clr_cache=True, clr_navigator=False)
    from apis.trakt_api import trakt_sync_activities
    status = trakt_sync_activities()
    logger(f'status: {status}')
