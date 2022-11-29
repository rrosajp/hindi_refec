# -*- coding: utf-8 -*-

import datetime
import json
import re
import traceback

try:
	from indexers.hindi.live_client import scrapePage, agent
	from modules.kodi_utils import notification, logger, make_listitem, item_next, addon_fanart, build_url, set_info, add_items, set_content, end_directory, set_view_mode, get_infolabel, addon_icon, addon_fanart
	from caches.h_cache import main_cache
	from modules.utils import remove_accents
	aicon = 'https://i.imgur.com/iOllLYX.png' # "hindi_tubi.png")
except:
	from modules.live_client import scrapePage, agent
	from modules.utils import logger
	from modules.h_cache import main_cache
	from modules.utils import remove_accents
	aicon, addon_icon, addon_fanart = "hindi_tubi.png", '', ''


tubitv = True#False
ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
headers = {
        'authority': 'tubitv.com',
        'user-agent': agent(),
        'sec-fetch-dest': 'empty',
        'accept': '*/*',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'accept-language': 'en-US,en;q=0.9', }
# 'cookie': 'deviceId=acb2e6c0-0df9-421d-a57e-8883884121cd; _ga=GA1.2.1067293052.1588638053; _gid=GA1.2.637864145.1588638053; ab.storage.deviceId.5cd8f5e0-9c05-44d2-b407-9cf055e5733c=%7B%22g%22%3A%225ce196d7-6c09-1adf-6602-02ad9e11a928%22%2C%22c%22%3A1588638053150%2C%22l%22%3A1588638053150%7D; '
#           'GED_PLAYLIST_ACTIVITY=W3sidSI6IitWazAiLCJ0c2wiOjE1ODg2MzgxMTUsIm52IjowLCJ1cHQiOjE1ODg2MzgwNTIsImx0IjoxNTg4NjM4MTA3fV0.; _gat=1; ab.storage.sessionId.5cd8f5e0-9c05-44d2-b407-9cf055e5733c=%7B%22g%22%3A%221e309c17-adca-19ae-120d-d7435f11f4b4%22%2C%22e%22%3A1588639915731%2C%22c%22%3A1588638053146%2C%22l%22%3A1588638115731%7D'}
# 'referer': 'https://tubitv.com/movies/522070/open_season_2',
# 'cookie': 'deviceId=acb2e6c0-0df9-421d-a57e-8883884121cd; _ga=GA1.2.1067293052.1588638053; _gid=GA1.2.637864145.1588638053; ab.storage.deviceId.5cd8f5e0-9c05-44d2-b407-9cf055e5733c=%7B%22g%22%3A%225ce196d7-6c09-1adf-6602-02ad9e11a928%22%2C%22c%22%3A1588638053150%2C%22l%22%3A1588638053150%7D; '
#           'ab.storage.sessionId.5cd8f5e0-9c05-44d2-b407-9cf055e5733c=%7B%22g%22%3A%221813a4c9-485e-9f8c-fc66-4d5861175baa%22%2C%22e%22%3A1588651125555%2C%22c%22%3A1588649325553%2C%22l%22%3A1588649325555%7D; GED_PLAYLIST_ACTIVITY=W3sidSI6IjBmSm0iLCJ0c2wiOjE1ODg2NTI3MTMsIm52IjoxLCJ1cHQiOjE1ODg2MzgxNTQsImx0IjoxNTg4NjUyNzExfV0.; _gat=1',
# 'if-none-match': 'W/"9fc-s+qOH8lZhrKqiowHa18So4WAGOE"'}


def _process(list_data):
	    # info = {}
	for i in list_data:
		if not re.search(r"espanol|lgbt|nominados|telenovelas", str(i), flags=re.I):
			cm = []
			cm_append = cm.append
			title = i['title']
			thumb = icon = i['icon'] if i.get('icon', None) else addon_fanart
			url_params = {'mode': i['action'], 'title': title, 'id': i['id'], 'page': i['page']}
			# logger(f"tubutv _process url_params: {url_params}")
			url = build_url(url_params)
			options_params = {'mode': 'options_menu_choice', 'suggestion': title, 'play_params': url}
			cm_append(("[B]Options...[/B]", f'RunPlugin({build_url(options_params)})'))
			cm_append(("[B]Add to a Shortcut Folder[/B]", 'RunPlugin(%s)' % build_url({'mode': 'menu_editor.shortcut_folder_add_item', 'name': title, 'iconImage': icon})))
			try: year = i['year']
			except: year = 2022
			try: rating = i['rating']
			except: rating = ''
			try: duration = i['duration']
			except: duration = 1500
			try: genre = i['genre']
			except: genre = []
			if 'Next Page:' in remove_accents(title):
			    icon = thumb = item_next
			    info = {'plot': f'Go To Next Page....: {i["page"]}', "year": year, "genre": genre}
			else:
			    info = {
			        "title": title,
			        "plot": str(i.get('summary', '')),
			        "rating": rating,
			        "year": year,
			        "duration": duration, # "Cast":actors,
			        "genre": genre}
			# logger(f"tubutv _process info: {info}")
			listitem = make_listitem()
			is_folder = i['is_folder']
			listitem.setLabel(title)
			listitem.addContextMenuItems(cm)
			info |= {'imdb_id': title, 'mediatype': 'episode', 'episode': 1, 'season': 0}
			setUniqueIDs = {'imdb': str(title)}
			listitem = set_info(listitem, info, setUniqueIDs)
			listitem.setArt({'icon': icon, 'poster': thumb, 'thumb': thumb, 'banner': thumb})
			yield url, listitem, is_folder
	return


def tubitv_root():
    if tubitv:
        cache_name = "content_list_tubitv_root"
        ch_data = main_cache.get(cache_name)
        if not ch_data:
            ch_data = get_ch_data()
            # logger(f"##### - NEW ch_data: {ch_data}")
            if ch_data:
                # wrigtht_json(ustv_chennel, json.dumps(ch_data))
                main_cache.set(cache_name, ch_data, expiration=datetime.timedelta(hours=48))  # 2 days cache
    else: ch_data = get_ch_data()
    # ch_data = get_ch_data()
    from sys import argv # some functions like ActivateWindow() throw invalid handle less this is imported here.
    handle = int(argv[1])
    add_items(handle, list(_process(ch_data)))
    set_content(handle, 'tvshows')
    end_directory(handle)
    set_view_mode('view.tvshows', 'tvshows')


def play(params):
    try:
        url2 = f"https://tubitv.com/oz/videos/{params['id']}/content"
        # logger(f"u_a: {agent()}")
        # headers.update({'user-agent': agent(),})
        response = scrapePage(url2, headers=headers).text
        data = json.loads(response)
        # logger(f"play data: {data}")
        # res = json.dumps(data, indent=2)
        url = data.get("url", None)
        if not url:
            video_resources = data["video_resources"]
            # logger(f"play video_resources: {video_resources}")
            url_list = [d['manifest'].get('url') for d in video_resources if d['manifest'].get('url') and d['type'] == 'hlsv3']
            # logger(f"play url_list: {url_list}")
            url = f"{url_list[0]}"

        # logger(f"play url: {url}")
        if url:
            # logger(f"play url: {url}")
            link = f"{url}|{agent()}"
            from modules.player import infinitePlayer
            infinitePlayer().run(link, 'video', {'title': str(params['title'])})
        else: notification('Tubi TV - url Not found:', 900)
    except:
        logger(f'---Tubi TV - Exception: \n{traceback.print_exc()}\n')
        notification('Tubi TV - Exception:', 900)
        return


def get_ch_data():
    url = "https://tubitv.com/oz/containers?isKidsModeEnabled=false&groupStart=1&groupSize=200"
    headers.update({'referer': 'https://tubitv.com/home',})
    response = scrapePage(url, headers=headers).text
    data = json.loads(response)
    cats = data['list']
    ch_lists = []
    for c in cats:
        try:
            title = str(data['hash'][c]['title'])#.encode('utf-8')
            if not re.search(r"espanol|lgbt|nominados|telenovelas", str(c), flags=re.I):
                try: summary = str(data['hash'][c]['description'])#.encode('utf-8')
                except: summary = ""
                sid = data['hash'][c]['id']
                image = data['hash'][c]['thumbnail']
                if image == '': image = aicon
                try: fanart = data['hash'][c]['backgrounds'][0]
                except: fanart = image
                data2 = sid  # + "**1"
                # print(title, data2, 2, image, fanart, summary)
                ch_lists.append({
                    'action': 'tubio_list',
                    'icon': image,
                    'fanart': fanart,
                    'title': title,
                    'id': data2,
                    'page': '1',
                    'is_folder': True,
                    'plot': summary})
        except:
            logger(f'---Tubi TV - Exception: \n{traceback.print_exc()}\n')
    # print(ch_lists)
    return ch_lists


def tubitv_categs(params):
    item = params['id']
    page = params['page']
    if tubitv:
        cache_name = f"content_list_tubitv_categs_{item}_{page}"
        ch_lists = main_cache.get(cache_name)
        if not ch_lists:
            ch_lists = get_categs(item, page)
            # logger("##### - NEW ch_lists: ")
            if ch_lists:
                # wrigtht_json(ustv_chennel, json.dumps(ch_lists))
                main_cache.set(cache_name, ch_lists, expiration=datetime.timedelta(hours=48))
    else: ch_lists = get_categs(item, page)
    # logger(f"tubitv_categs ch_lists: {ch_lists}")
    # item_list = list(_process(ch_lists))
    # logger(f"##### tubutv _process item_list: {item_list}")
    from sys import argv # some functions like ActivateWindow() throw invalid handle less this is imported here.
    handle = int(argv[1])
    add_items(handle, list(_process(ch_lists)))
    set_content(handle, 'tvshows')
    end_directory(handle)
    set_view_mode('view.tvshows', 'tvshows')


def get_categs(item, page):
	url2 = f"https://tubitv.com/oz/containers/{item}/content?parentId&cursor=10&limit=450&isKidsModeEnabled=false&expand=0"
	# logger(f"##### tubutv _process item_list: {url2} : {page}")
	headers.update({'referer': 'https://tubitv.com/home',})
	response = scrapePage(url2, headers=headers).text
	# logger(f"##### tubutv _process item_list: {response} : {page}")
	data = json.loads(response)
	# logger(f"get_categs data: {data}")
	children = data['containersHash'][item]['children']
	if page == "1":
		x = children[:75]
	elif page == "2":
		x = children[75:150]
	elif page == "3":
		x = children[150:225]
	elif page == "4":
		x = children[225:300]
	elif page == "5":
		x = children[300:375]
	elif page == "6":
		x = children[375:450]
	elif page == "7":
		x = children[450:525]

	ch_lists = []

	for c in x:
		try:
			title = str(data['contents'][c]['title'])#.encode('utf-8')
			# check = data['contents'][c]['availability_duration']
			type_media = data['contents'][c]['type']
			summary = str(data['contents'][c]['description'])#.encode('utf-8')
			image = data['contents'][c]['posterarts'][0]
			try: year = int(data['contents'][c]['year'])
			except: year = 2022
			try: fanart = data['contents'][c]['backgrounds'][0]
			except: fanart = addon_fanart
			try: duration = data['contents'][c]['duration']
			except: duration = 1500
			try: rating = data['contents'][c]['ratings'][0]['code']
			except: rating = ""
			try: actors = data['contents'][c]['actors']
			except: actors = []
			try: genre = data['contents'][c]['tags']#[0]
			except: genre = []
			            # logger(f"get_categs title: {title} check: {check}")
			if type_media == 's':
				# print(title,c,3,image,fanart,summary)
				folder_data = {
				    'action': 'tubio_tv',
				    'icon': image,
				    'fanart': fanart,
				    'title': title,
				    'id': c,
				    'page': f'{page}',
				    'plot': summary,
				    'year': year,
				    'actors': actors,
				    'rating': rating,
				    'duration': duration,
				    'is_folder': True,
				    'genre': genre}
				# logger(f"##### tubutv _process item_list: {folder_data}")
				ch_lists.append(folder_data)
				# tools.addDir(title,c,3,image,fanart,summary)
			else:
				sid = data['contents'][c]['id']
				                # print(title,sid,4,image,fanart,summary,year,actors,rating,duration,genre)
				ch_lists.append(
					{
						'action': 'ltp_tubitv',
						'icon': image,
						'fanart': fanart,
						'title': title,
						'id': sid,
						'page': f'{page}',
						'plot': summary,
						'year': year,
						'actors': actors,
						'rating': rating,
						'duration': duration,
						'is_folder': False,
						'genre': genre,
					}
				)

		            # tools.addDirMeta(title,sid,4,image,fanart,summary,year,actors,rating,duration,genre)
		except: pass
	# data2 = url+"**"+str(page)
	page = int(page) + 1
	ch_lists.append({
	    'action': 'tubio_list',
	    'icon': '',
	    'fanart': addon_fanart,
	    'title': f"Next Page: {page}",
	    'id': item,
	    'page': f'{page}',
	    'plot': '',
	    'year': '',
	    'actors': '',
	    'rating': '',
	    'duration': '',
	    'is_folder': True,
	    'genre': []})
	# print(ch_lists)
	return ch_lists


def tubitv_shows(params):
    item = params['id']
    if tubitv:
        cache_name = f"content_list_tubitv_shows_{item}"
        ch_lists = main_cache.get(cache_name)
        if not ch_lists:
            ch_lists = gettv_shows(params)
            # logger("##### - NEW ch_lists: ")
            if ch_lists:
                # wrigtht_json(ustv_chennel, json.dumps(ch_lists))
                main_cache.set(cache_name, ch_lists, expiration=datetime.timedelta(hours=24))
    else: ch_lists = gettv_shows(params)
    if len(ch_lists) > 0:
        from sys import argv # some functions like ActivateWindow() throw invalid handle less this is imported here.
        handle = int(argv[1])
        add_items(handle, list(_process(ch_lists)))
        set_content(handle, 'episodes')
        end_directory(handle)
        set_view_mode('view.episodes', 'episodes')
    else:
        notification('Tubi TV - Exception:', 900)


def gettv_shows(params):
    # item = params['id']
    url = f"https://tubitv.com/oz/videos/{params['id']}/content"
    # headers.update({'user-agent': agent(),})
    response = scrapePage(url, headers=headers).text
    data = json.loads(response)
    children = data['children']
    ch_lists = []
    for child in children:
        try: Children = child['children']
        except: Children = []
        for c in Children:
            try:
                sid = c['id']
                title = str(c['title'])#.encode('utf-8')
                try: summary = str(c['description'])#.encode('utf-8')
                except: summary = ""
                try: image = c['thumbnails'][0]
                except: image = addon_icon
                try: fanart = c['backgrounds'][0]
                except: fanart = image
                try: year = int(c['year'])
                except: year = 2022
                try: duration = c['duration']
                except: duration = 1500
                try: rating = c['ratings'][0]['code']
                except: rating = ""
                try: actors = c['actors']
                except: actors = []
                try: genre = c['tags']#[0]
                except: genre = []
                ch_lists.append({
                    'action': 'ltp_tubitv',
                    'icon': image,
                    'fanart': fanart,
                    'title': title,
                    'id': sid,
                    'page': f'{params["page"]}',
                    'plot': summary,
                    'year': year,
                    'actors': actors,
                    'rating': rating,
                    'duration': duration,
                    'is_folder': False,
                    'genre': genre})
                # tools.addDirMeta(title,sid,4,image,fanart,summary,year,actors,rating,duration,genre)
            except: pass
    # print(ch_lists)
    return ch_lists


# if __name__ == "__main__":
#     print(get_ch_data())
