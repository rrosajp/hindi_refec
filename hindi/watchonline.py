# -*- coding: utf-8 -*-

import re
import traceback
import base64
import requests
from sys import argv


try:
    from indexers.hindi.live_client import scrapePage, agent, keepclean_title, read_write_file
    from modules.kodi_utils import logger, build_url, add_items, end_directory, set_content, set_view_mode, get_infolabel, notification, add_item, make_listitem, addon_fanart
    import resolveurl
    opensettings_params = build_url({'mode': 'open_settings', 'query': '0.0'})
except:
    from modules.live_client import scrapePage, agent, keepclean_title, read_write_file
    from modules.utils import logger
    from modules.h_cache import main_cache, metacache
    from hindi_meta import fetch_meta, get_plot_tvshow
    logger(f'import Exception: \n{traceback.print_exc()}')

from modules.dom_parser import parseDOM
from openscrapers.modules.source_utils import __top_domain
from openscrapers.modules.scrape_sources import prepare_link, process
from openscrapers.modules.py_tools import ensure_str


def hostDict():
    try:
        # logger(f'__init__ Strated: ')
        from scrapers.external import get_host_dict
        hostDict = get_host_dict()
    except:
        logger(f'__init__ Exception: \n{traceback.print_exc()}')
        hostDict = []

season_site = ['watchgreekonline', 'watchweedsonline', 'watchdesperatehousewives', 'watchbatesmotelonline', 'watchbaywatchonline']
sites = [
    {'title': '30 Rock', 'url': 'https://watch30rockonline.com/', 'image': 'https://i.ibb.co/wK9R4KC/30-rock.jpg'},
    {'title': 'According To Jim', 'url': 'https://watchaccordingtojimonline.com/', 'image': 'https://i.ibb.co/TtSg6Zb/jim.png'},
    {'title': 'Archer', 'url': 'https://watcharcheronline.cc/', 'image': 'https://i.ibb.co/D937Lsc/archer.jpg'},
    {'title': 'Bates Motel', 'url': 'https://watchbatesmotelonline.com/', 'image': 'https://i.ibb.co/gR8bQmV/batesmotel.png'},
    {'title': 'Baywatch', 'url': 'https://watchbaywatchonline.com/', 'image': 'https://i.ibb.co/7QRBzQB/baywatch.png'},
    {'title': 'Bojack Horseman', 'url': 'https://watchbojackhorseman.online/', 'image': 'https://i.ibb.co/0yGqSqJ/bojack-horseman.jpg'},
    {'title': 'Bones', 'url': 'https://watchbonesonline.com/', 'image': 'https://i.ibb.co/w7dQKw7/bones.jpg'},
    {'title': 'Californication', 'url': 'https://watchcalifornicationonline.com/', 'image': 'https://i.ibb.co/pPPg4WC/californication.jpg'},
    {'title': 'Castle', 'url': 'https://watchcastleonline.com/', 'image': 'https://i.ibb.co/2P6C7cH/castle.jpg'},
    {'title': 'Charmed', 'url': 'https://watchcharmedonline.com/', 'image': 'https://i.ibb.co/FwX6kVF/charmed.jpg'},
    {'title': 'Cheers', 'url': 'https://watchcheersonline.com/', 'image': 'https://i.ibb.co/kgqJz0s/cheers.jpg'},
    {'title': 'Curb Your Enthusiasm', 'url': 'https://watchcurbyourenthusiasm.com/', 'image': 'https://i.ibb.co/Smvg51B/curb-your-enthusiasm.jpg'},
    {'title': 'Desperate Housewives', 'url': 'https://watchdesperatehousewives.com/', 'image': 'https://i.ibb.co/LZxbJ2V/desperate-housewives.jpg'},
    {'title': 'Doctor Who', 'url': 'https://watchdoctorwhoonline.com/', 'image': 'https://i.ibb.co/Wp0fD9D/doctor-who.jpg'},
    {'title': 'Downton Abbey', 'url': 'https://watchdowntonabbeyonline.com/', 'image': 'https://i.ibb.co/n0DK7Ff/downton-abbey.jpg'},
    {'title': 'Elementary', 'url': 'https://watchelementaryonline.com/', 'image': 'https://i.ibb.co/xDxx87M/elementary.jpg'},
    {'title': 'ER', 'url': 'https://watcheronline.net/', 'image': 'https://i.ibb.co/vxm1YZ7/er.jpg'},
    {'title': 'Everybody Loves Raymond', 'url': 'https://watcheverybodylovesraymond.com/', 'image': 'https://i.ibb.co/JrnbHKG/everybody-loves-raymond.jpg'},
    {'title': 'Fugget About It', 'url': 'https://watchfuggetaboutit.online/', 'image': 'https://i.ibb.co/Sx2CVt6/fugget-about-it.jpg'},
    {'title': 'Gilmore Girls', 'url': 'https://watchgilmoregirlsonline.com/', 'image': 'https://i.ibb.co/wdKMLgX/gilmoregirls.png'},
    {'title': 'Glee', 'url': 'https://watchgleeonline.com/', 'image': 'https://i.ibb.co/sCxsFHn/glee.jpg'},
    {'title': 'Gossip Girl', 'url': 'https://watchgossipgirlonline.net/', 'image': 'https://i.ibb.co/F5Z8RGQ/gossip-girl.jpg'},
    {'title': 'Greek', 'url': 'https://watchgreekonline.com/', 'image': 'https://i.ibb.co/x23gLyG/greek.png'},
    {'title': 'Greys Anatomy', 'url': 'https://watchgreysanatomy.online/', 'image': 'https://i.ibb.co/8rBrScY/greysanatomy.jpg'},
    {'title': 'Hawaii Five0(Down 3-28-22)', 'url': 'https://watchhawaiifive0online.com/', 'image': 'https://i.ibb.co/wSNnyj9/hawaii-five-0.png'},
    {'title': 'Heroes', 'url': 'https://watchheroes.online/', 'image': 'https://i.ibb.co/fNYZfSm/heroes.jpg'},
    {'title': 'Hogans Heroes', 'url': 'https://watchhogansheroes.online/', 'image': 'https://i.ibb.co/F7k1hcC/hogan-s-heroes.jpg'},
    {'title': 'House', 'url': 'https://watchhouseonline.net/', 'image': 'https://i.ibb.co/KsR0LvV/house.jpg'},
    {'title': 'How I Met Your Mother', 'url': 'https://watchhowimetyourmother.online/', 'image': 'https://i.ibb.co/0VR2Vvg/how-i-met-your-mother.jpg'},
    {'title': 'Impractical Jokers', 'url': 'https://watchimpracticaljokers.online/', 'image': 'https://i.ibb.co/tc4dWX8/impractical-jokers.jpg'},
    {'title': 'Lost', 'url': 'https://watchlostonline.net/', 'image': 'https://i.ibb.co/jb8fGxd/lost.jpg'},
    {'title': 'Malcolm In The Middle', 'url': 'https://watchmalcolminthemiddle.com/', 'image': 'https://i.ibb.co/GPBZ2gr/malcolm-in-the-middle.jpg'},
    {'title': 'Mash', 'url': 'https://watchmash.online/', 'image': 'https://i.ibb.co/R9GKrT5/mash.jpg'},
    {'title': 'Monk', 'url': 'https://watchmonkonline.com/', 'image': 'https://i.ibb.co/g6gWxd2/monk.jpg'},
    {'title': 'My Name Is Earl', 'url': 'https://watchmynameisearl.com/', 'image': 'https://i.ibb.co/RH4mTky/my-name-is-earl.jpg'},
    {'title': 'New Girl', 'url': 'https://watchnewgirlonline.net/', 'image': 'https://i.ibb.co/dQTtHy9/new-girl.jpg'},
    {'title': 'Once Upon A Time', 'url': 'https://watchonceuponatimeonline.com/', 'image': 'https://i.ibb.co/WBLdkMh/once-upon-a-time.jpg'},
    {'title': 'One Tree Hill', 'url': 'https://watchonetreehillonline.com/', 'image': 'https://i.ibb.co/z5Df1rQ/one-tree-hill.jpg'},
    {'title': 'Only Fools And Horses', 'url': 'https://watchonlyfoolsandhorses.com/', 'image': 'https://i.ibb.co/XsVkFBP/only-fools-and-horses.jpg'},
    {'title': 'Parks And Recreation', 'url': 'https://watchparksandrecreation.net/', 'image': 'https://i.ibb.co/Qc36dhv/parks-and-recreation.jpg'},
    {'title': 'Pretty Little Liars', 'url': 'https://watchprettylittleliarsonline.com/', 'image': 'https://i.ibb.co/r7p5YtS/pretty-little-liars.jpg'},
    {'title': 'Psych', 'url': 'https://watchpsychonline.net/', 'image': 'https://i.ibb.co/kDRzvTp/psych.jpg'},
    {'title': 'Roseanne(Down 3-28-22)', 'url': 'https://watchroseanneonline.com/', 'image': 'https://i.ibb.co/zJ57DYd/roseanne.png'},
    {'title': 'Rules Of Engagement', 'url': 'https://watchrulesofengagementonline.com/', 'image': 'https://i.ibb.co/PxPRcCh/rules-of-engagement.jpg'},
    {'title': 'Scrubs', 'url': 'https://watchscrubsonline.com/', 'image': 'https://i.ibb.co/0Gg15r6/scrubs.jpg'},
    {'title': 'Seinfeld', 'url': 'https://watchseinfeld.com/', 'image': 'https://i.ibb.co/Dw2PbP9/seinfeld.jpg'},
    {'title': 'Sex And The City', 'url': 'https://watchsexandthecity.com/', 'image': 'https://i.ibb.co/6NQsLPP/sex-and-the-city.jpg'},
    {'title': 'South Park', 'url': 'https://watchsouthpark.tv/', 'image': 'https://i.ibb.co/bRb32GK/south-park.jpg'},
    {'title': 'SpongeBob SquarePants', 'url': 'https://watchspongebobsquarepantsonline.com/', 'image': 'https://i.ibb.co/xzvM2rN/spongebob.png'},
    {'title': 'Suits', 'url': 'https://watchsuitsonline.net/', 'image': 'https://i.ibb.co/pdPh3Wx/suits.jpg'},
    {'title': 'Teen Wolf', 'url': 'https://watchteenwolfonline.net/', 'image': 'https://i.ibb.co/b2rx3p7/teen-wolf.jpg'},
    {'title': 'That 70s Show(Down 3-28-22)', 'url': 'https://watchthat70show.net/', 'image': 'https://i.imgur.com/vCiYiXr.png'},
    {'title': 'The 100', 'url': 'https://watchthe100online.com/', 'image': 'https://i.ibb.co/W0pPnmh/the100.png'},
    {'title': 'The Big Bang Theory', 'url': 'https://watchthebigbangtheory.com/', 'image': 'https://i.ibb.co/GpDpQt8/the-big-bang-theory.jpg'},
    {'title': 'The Flintstones', 'url': 'https://watchtheflintstones.online/', 'image': 'https://i.ibb.co/NCxzsYk/the-flintstones.jpg'},
    {'title': 'The Fresh Prince Of Bel-Air', 'url': 'https://watchthefreshprinceofbel-air.com/', 'image': 'https://i.ibb.co/Z23xp5s/the-fresh-prince-of-bel-air.jpg'},
    {'title': 'The King Of Queens', 'url': 'https://watchthekingofqueens.com/', 'image': 'https://i.ibb.co/2q5FV6t/the-king-of-queens.jpg'},
    {'title': 'The Middle', 'url': 'https://watchthemiddleonline.com/', 'image': 'https://i.ibb.co/wcS0Gmf/the-middle.jpg'},
    {'title': 'The Office', 'url': 'https://watchtheofficetv.com/', 'image': 'https://i.ibb.co/ZJ2cfHX/the-office.jpg'},
    {'title': 'The Ricky Gervais Show', 'url': 'https://watchtherickygervaisshow.online/', 'image': 'https://i.ibb.co/4V5d3Yv/the-ricky-gervais-show.jpg'},
    {'title': 'The Vampire Diaries', 'url': 'https://watchthevampirediaries.com/', 'image': 'https://i.ibb.co/HFBhT5x/the-vampire-diaries.jpg'},
    {'title': 'Two And A Half Men', 'url': 'https://watchtwoandahalfmenonline.com/', 'image': 'https://i.ibb.co/5h2RWPJ/two-and-a-half-men.jpg'},
    {'title': 'Weeds', 'url': 'https://watchweedsonline.com/', 'image': 'https://i.ibb.co/d0fRd1B/weeds.png'}
]
hostDict = hostDict()

def root():
    try:
        for i in sites:
            AD({'title': i['title'], 'url': i['url'], 'image': i['image'], 'mode': 'watchonline_scrape_seasons'}, 'root')
        _end_directory()
    except: logger(f'root Exception: \n{traceback.print_exc()}')


def scrape_seasons(url):
    try:
        if any([x in url for x in season_site]): url = url + 'seasons/'
        else: url = url + 'season-watch/'
        html = scrapePage(url).text
        # logger(f'html: {html}')
        # if '/page/2/' in html:
            # page2 = url + 'page/2/'
            # html += scrapePage(page2).text
        # if '/page/3/' in html:
            # page3 = url + 'page/3/'
            # html += scrapePage(page3).text
        r = parseDOM(html, 'article', attrs={'class': 'item se seasons'})
        # logger(f'scrape_seasons r: {len(r)} r: {r}')
        for i in r:
            # logger(f'scrape_seasons i: {i}')
            link = parseDOM(i, 'a', ret='href')[0]
            title = parseDOM(i, 'img', ret='alt')[0]
            label = keepclean_title(title.title())
            try: art = parseDOM(i, 'img', ret='data-src')[0]
            except: art = parseDOM(i, 'img', ret='src')[0]
            AD({'title': label, 'url': link, 'image': art, 'mode': 'watchonline_scrape_episodes'}, 'scrape_seasons')
        _end_directory()
    except: logger(f'scrape_seasons Exception: {traceback.print_exc()}')


def scrape_episodes(url):
    try:
        html = scrapePage(url).text
        if '/page/2/' in html:
            page2 = re.findall('href="(.+?/page/2/)"', html)[0]
            html += scrapePage(page2).text
        if '/page/3/' in html:
            page3 = re.findall('href="(.+?/page/3/)"', html)[0]
            html += scrapePage(page3).text
        r = parseDOM(html, 'li', attrs={'class': 'mark-.+?'})
        # logger(f'scrape_episodes r: {len(r)} r: {r}')
        for i in r:
            try:
                # logger(f'scrape_episodes i: {i}')
                link = parseDOM(i, 'a', ret='href')[0]
                label = parseDOM(i, 'a')[0]
                label = re.sub(r'\<[^>]*\>|\([^>]*\)', '', label)
                # logger(f'scrape_episodes label: {label}')
                try: info = re.findall('/(?:episodes|stream|stream-free|episode-lists|episode-watch)/(?:watch-|)([A-Za-z0-9-]+)', link)[0]
                except: info = ''
                # logger(f'scrape_episodes info: {info}')
                if not info == '' and label != '': label = '%s - %s' % (info, label)
                elif not info == '': label = info
                # elif not label == '': label = label
                # if not info2 == '': label = '%s - %s' % (info2, label)
                # label = unescape(label)
                # logger(f'final scrape_episodes label: {label}')
                try:
                    try: art = parseDOM(i, 'img', ret='data-src')[0]
                    except: art = parseDOM(i, 'img', ret='src')[0]
                except: art = 'DefaultFolder.png'
                AD({'title': label, 'url': link, 'image': art, 'mode': 'watchonline_scrape_source'}, 'scrape_episodes')
            except: logger(f'scrape_episodes Exception: \n{traceback.print_exc()}')
        _end_directory()
    except: logger(f'scrape_episodes Exception: {traceback.print_exc()}')


def scrape_source(params):
    try:
        domain = __top_domain(params['url'])
        # logger(f"domain {domain}  match: {params['url']}")
        session = requests.Session()
        customheaders = {
            'Host': domain,
            'Accept': '*/*',
            'Origin': 'https://%s' % domain,
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': agent(),
            'Referer': params['url'],
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        html = scrapePage(params['url']).text
        # logger(f'html: {html}')
        # html = read_write_file(file_n='JSTesting/watchgreysanatomy.online.html')
        try: # about 5 sites that i know of use this for fsapi.xyz sources.
            link = parseDOM(html, 'li', ret='data-vs')[0]
            html = scrapePage(link).text
            matchs = re.findall('''&url=(.+?)" target=''', html)
            for match in matchs:
                match = base64.b64decode(match)
                # logger(f'type match {type(match)}  match: {match}')
                match = ensure_str(match, errors='ignore')
                # logger(f'type match {type(match)}  match: {match}')
                for source in process(hostDict, match):
                    AD({'title': source['source'], 'name': params['title'], 'url': source['url'], 'image': None, 'mode': 'watchonline_ltp'}, 'play_source')
        except:
            logger(f'1 scrape_source Exception: \n{traceback.print_exc()}')
        try: # the rest use this.
            post_link = 'https://%s/wp-admin/admin-ajax.php' % domain
            results = re.compile("data-type='(.+?)' data-post='(.+?)' data-nume='(\d+)'>", re.DOTALL).findall(html)
            for data_type, data_post, data_nume in results:
                payload = {'action': 'doo_player_ajax', 'post': data_post, 'nume': data_nume, 'type': data_type}
                r = session.post(post_link, headers=customheaders, data=payload)
                # logger(f'scrape_source type r: {type(r)} r: {r}')
                # logger(f'scrape_source type r.text: {r.text}')
                try:
                    i = r.json()
                    if not i['type'] == 'iframe': continue
                    p = i['embed_url'].replace('\\', '')
                except: p = parseDOM(r.text, 'iframe', ret='src')[0]
                # logger(f'scrape_source type p: {type(p)} p: {p}')
                link = prepare_link(p)
                host = __top_domain(link)
                AD({'title': host, 'name': params['title'], 'url': link, 'image': None, 'mode': 'watchonline_ltp'}, 'play_source')
        except: logger(f'2 scrape_source Exception: {traceback.print_exc()}')
        _end_directory()
    except: logger(f'outter scrape_source Exception: {traceback.print_exc()}')

def AD(url_params, list_name, icon='DefaultFolder.png', isFolder=True):
    # cm = []
    # cm_append = cm.append
    if url_params['image']:
        if url_params['image'].startswith('http'): icon = url_params['image']
    url_params['image'] = icon
    url = build_url(url_params)
    listitem = make_listitem()
    listitem.setLabel(url_params['title'])
    listitem.setArt({'icon': icon, 'poster': icon, 'thumb': icon, 'fanart': addon_fanart, 'banner': icon, 'landscape': icon})
    # if not 'exclude_external' in url_params:
        # list_name = url_params['list_name'] if 'list_name' in url_params else list_name
        # cm_append((add_menu_str,'RunPlugin(%s)'% build_url({'mode': 'menu_editor.add_external', 'name': list_name, 'iconImage': iconImage})))
        # cm_append((s_folder_str,'RunPlugin(%s)' % build_url({'mode': 'menu_editor.shortcut_folder_add_item', 'name': list_name, 'iconImage': iconImage})))
        # listitem.addContextMenuItems(cm)
    add_item(int(argv[1]), url, listitem, isFolder)

def _end_directory():
    handle = int(argv[1])
    set_content(handle, '')
    end_directory(handle)
    # set_view_mode(view, '')

def play(params):
    try:
        # logger(f'play params: {params}')
        hmf = resolveurl.HostedMediaFile(url=params['url'], include_disabled=True, include_universal=False)
        url = None
        if hmf.valid_url() is True:
            url = hmf.resolve()
            logger(f'watchonline_ltp play url: {url}')
        from modules.player import infinitePlayer
        if url: return infinitePlayer().run(url, 'video', {'title': str(params['name'])})
        else: return notification('Error : No Stream Available.:', 1000)
    except:
        logger(f'addDirectory Exception: \n{traceback.print_exc()}')
        notification('Error : No Stream Available.:', 900)
