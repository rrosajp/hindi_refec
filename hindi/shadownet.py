# -*- coding: utf-8 -*-

import re
import sys
import random
import traceback
try:
    from indexers.hindi.live_client import request, agent, keepclean_title
    from modules.kodi_utils import logger, build_url, add_items, end_directory, set_content, set_view_mode, get_infolabel, notification, add_item, make_listitem, addon_fanart, player, hide_busy_dialog
    import resolveurl
    from modules.player import infinitePlayer
    opensettings_params = build_url({'mode': 'open_settings', 'query': '0.0'})
except:
    from modules.live_client import request, agent, keepclean_title, read_write_file
    from modules.utils import logger
    from modules.h_cache import main_cache, metacache
    from hindi_meta import fetch_meta, get_plot_tvshow
    logger(f'import Exception: \n{traceback.print_exc()}')

from modules.dom_parser import parseDOM
from openscrapers.modules.source_utils import __top_domain
from openscrapers.modules.scrape_sources import prepare_link, process
from openscrapers.modules.py_tools import ensure_str
icon='DefaultFolder.png'


class iptv:
    def __init__(self):
        self.base_link = 'http://www.sdw-net.me'
        self.channels = []
        self.list = []
        self.UK_TV = [
            {"title": "Animal Planet UK", "url": "/channels/Animal-Planet-UK.html", "image": None},
            {"title": "BBC 1", "url": "/channels/BBC%252d1.html", "image": None},
            {"title": "BBC 2", "url": "/channels/BBC-2.html", "image": None},
            {"title": "BBC 3", "url": "/channels/BBC-3.html", "image": None},
            {"title": "BBC 4", "url": "/channels/BBC-4.html", "image": None},
            {"title": "BBC News", "url": "/channels/BBC%252dNews.html", "image": None},
            {"title": "BBC Wold News", "url": "/channels/BBC-Wold-News.html", "image": None},
            {"title": "Box Nation", "url": "/channels/Box%252dNation.html", "image": None},
            {"title": "Capital", "url": "/channels/Capital.html", "image": None},
            {"title": "Cartoon Network UK", "url": "/channels/Cartoon%252dNetwork%252dUK.html", "image": None},
            {"title": "CBS Action", "url": "/channels/CBS-Action.html", "image": None},
            {"title": "CBS Drama", "url": "/channels/CBS.Drama.html", "image": None},
            {"title": "CBS Reality", "url": "/channels/CBS-Reality.html", "image": None},
            {"title": "Channel 4", "url": "/channels/Channel%252d4.html", "image": None},
            {"title": "Channel 5", "url": "/channels/Channel-5.html", "image": None},
            {"title": "Chelsea TV", "url": "/channels/Chelsea-TV.html", "image": None},
            {"title": "Comedy Central UK", "url": "/channels/Comedy-Central-UK.html", "image": None},
            {"title": "Cycling 1", "url": "/channels/Cycling-1.html", "image": None},
            {"title": "Cycling 2", "url": "/channels/Cycling2.html", "image": None},
            {"title": "Dave", "url": "/channels/Dave.html", "image": None},
            {"title": "Discovery History", "url": "/channels/Discovery-History.html", "image": None},
            {"title": "Discovery Investigation UK", "url": "/channels/Discovery-Investigation-UK.html", "image": None},
            {"title": "Discovery Science UK", "url": "/channels/Discovery-Science-UK.html", "image": None},
            {"title": "Discovery UK", "url": "/channels/Discovery%252dUK.html", "image": None},
            {"title": "Disney Channel UK", "url": "/channels/Disney%252dChannel%252dUK.html", "image": None},
            {"title": "E4", "url": "/channels/E4.html", "image": None},
            {"title": "E! Entertainment", "url": "/channels/E%21-Entertainment.html", "image": None},
            {"title": "Euronews", "url": "/channels/Euronews.html", "image": None},
            {"title": "Film 4", "url": "/channels/Film-4.html", "image": None},
            {"title": "Food Network UK", "url": "/channels/Food-Network-UK.html", "image": None},
            {"title": "Gold Channel", "url": "/channels/Gold-Channel.html", "image": None},
            {"title": "Heart TV", "url": "/channels/Heart-TV.html", "image": None},
            {"title": "History UK", "url": "/channels/History-UK.html", "image": None},
            {"title": "ITV2", "url": "/channels/ITV%252d2.html", "image": None},
            {"title": "ITV3", "url": "/channels/ITV3.html", "image": None},
            {"title": "ITV4", "url": "/channels/ITV4.html", "image": None},
            {"title": "ITV", "url": "/channels/ITV.html", "image": None},
            {"title": "ITV.Be", "url": "/channels/ITV.Be.html", "image": None},
            {"title": "London Live", "url": "/channels/London-Live.html", "image": None},
            {"title": "Manchester United TV", "url": "/channels/Manchester-United-TV.html", "image": None},
            {"title": "More 4", "url": "/channels/More-4.html", "image": None},
            {"title": "Motors TV", "url": "/channels/Motors-TV.html", "image": None},
            {"title": "MTV Classic UK", "url": "/channels/MTV%252dClassic%252dUK.html", "image": None},
            {"title": "MTV Dance", "url": "/channels/MTV%252dDance.html", "image": None},
            {"title": "MTV Hits", "url": "/channels/MTV-Hits.html", "image": None},
            {"title": "MTV Rocks", "url": "/channels/MTV%252dRocks.html", "image": None},
            {"title": "Nat Geo Wild UK", "url": "/channels/Nat-Geo-Wild-UK.html", "image": None},
            {"title": "Premier", "url": "/channels/Premier.html", "image": None},
            {"title": "Racing UK", "url": "/channels/Racing-UK.html", "image": None},
            {"title": "Really", "url": "/channels/Really.html", "image": None},
            {"title": "RTE 1", "url": "/channels/RTE-1.html", "image": None},
            {"title": "RTE 2", "url": "/channels/RTE-2.html", "image": None},
            {"title": "Setanta", "url": "/channels/Setanta.html", "image": None},
            {"title": "Sky Atlantic", "url": "/channels/Sky-Atlantic.html", "image": None},
            {"title": "Sky News", "url": "/channels/Sky-News.html", "image": None},
            {"title": "Sky One", "url": "/channels/Sky-One.html", "image": None},
            {"title": "Sky Two", "url": "/channels/Sky-Two.html", "image": None},
            {"title": "TLC UK", "url": "/channels/TLC-UK.html", "image": None},
            {"title": "Travel Channel +1", "url": "/channels/Travel-Channel-%252b1.html", "image": None},
            {"title": "Tru TV", "url": "/channels/Tru-TV.html", "image": None},
            {"title": "VH1 EU", "url": "/channels/VH1-EU.html", "image": None}
        ]
        self.USA_TV = [
            {"title": "A&E", "url": "/channels/A-%26-E.html", "image": None},
            {"title": "ABC 7 NY", "url": "/channels/ABC-7-NY.html", "image": None},
            {"title": "ABC Family", "url": "/channels/ABC%252dFamily.html", "image": None},
            {"title": "ABC News", "url": "/channels/ABC%252dNews.html", "image": None},
            {"title": "ABC", "url": "/channels/ABC.html", "image": None},
            {"title": "Al Jazeera America", "url": "/channels/Al-Jazeera-America.html", "image": None},
            {"title": "AMC East", "url": "/channels/AMC%252dEast.html", "image": None},
            {"title": "American Heroes", "url": "/channels/American-Heroes.html", "image": None},
            {"title": "Animal Planet", "url": "/channels/Animal-Planet.html", "image": None},
            {"title": "BBC America", "url": "/channels/BBC.America.html", "image": None},
            {"title": "BET East", "url": "/channels/BET-East.html", "image": None},
            {"title": "Bloomberg", "url": "/channels/Bloomberg.html", "image": None},
            {"title": "Bravo US", "url": "/channels/Bravo-US.html", "image": None},
            {"title": "Cartoon Network", "url": "/channels/Cartoon-Network.html", "image": None},
            {"title": "CBS 2 NY", "url": "/channels/CBS-2-NY.html", "image": None},
            {"title": "CBS 47", "url": "/channels/CBS-47.html", "image": None},
            {"title": "CBS News", "url": "/channels/CBS%252dNews.html", "image": None},
            {"title": "CNN UK", "url": "/channels/CNN-UK.html", "image": None},
            {"title": "CNN", "url": "/channels/CNN.html", "image": None},
            {"title": "Comedy Central", "url": "/channels/Comedy%252dCentral.html", "image": None},
            {"title": "CW 11 NY", "url": "/channels/CW-11-NY.html", "image": None},
            {"title": "CW East", "url": "/channels/CW-East.html", "image": None},
            {"title": "Discovery ID US", "url": "/channels/Discovery-ID-US.html", "image": None},
            {"title": "Discovery", "url": "/channels/Discovery.html", "image": None},
            {"title": "Disney Channel US", "url": "/channels/Disney-Channel-US.html", "image": None},
            {"title": "ESPN2", "url": "/channels/ESPN2.html", "image": None},
            {"title": "ESPN.1", "url": "/channels/ESPN.1.html", "image": None},
            {"title": "Food Network US", "url": "/channels/Food-Network-US.html", "image": None},
            {"title": "FOX 2 St. Louis", "url": "/channels/FOX-2-St.-Louis.html", "image": None},
            {"title": "Fox 5 Washington DC", "url": "/channels/Fox-5-Washington-DC.html", "image": None},
            {"title": "FOX 13 News Tampa Bay", "url": "/channels/FOX-13-News-Tampa-Bay.html", "image": None},
            {"title": "Golf TV", "url": "/channels/Golf-TV.html", "image": None},
            {"title": "Hallmark TV", "url": "/channels/Hallmark%252dTV.html", "image": None},
            {"title": "HGTV", "url": "/channels/HGTV.html", "image": None},
            {"title": "History US", "url": "/channels/History-US.html", "image": None},
            {"title": "HLN", "url": "/channels/HLN.html", "image": None},
            {"title": "KRON 4 News San Francisco", "url": "/channels/KRON-4-News-San-Francisco.html", "image": None},
            {"title": "Lifetime US", "url": "/channels/Lifetime-US.html", "image": None},
            {"title": "MLB Network", "url": "/channels/MLB.Network.html", "image": None},
            {"title": "MSNBC News", "url": "/channels/MSNBC-News.html", "image": None},
            {"title": "MTV", "url": "/channels/MTV.html", "image": None},
            {"title": "NASA TV", "url": "/channels/NASA-TV.html", "image": None},
            {"title": "NBA", "url": "/channels/NBA.html", "image": None},
            {"title": "NBC 4 NY", "url": "/channels/NBC-4-NY.html", "image": None},
            {"title": "NBC Sports", "url": "/channels/NBC.Sports.html", "image": None},
            {"title": "NBC TV", "url": "/channels/NBC-TV.html", "image": None},
            {"title": "NFL", "url": "/channels/NFL.html", "image": None},
            {"title": "NHL Network", "url": "/channels/NHL-Network.html", "image": None},
            {"title": "Nickelodeon", "url": "/channels/Nickelodeon.html", "image": None},
            {"title": "Oprah Winfrey Network", "url": "/channels/Oprah-Winfrey-Network.html", "image": None},
            {"title": "Pac 12 Arizona", "url": "/channels/Pac-12-Arizona.html", "image": None},
            {"title": "Pac 12 Bay Area", "url": "/channels/Pac-12-Bay-Area.html", "image": None},
            {"title": "Pac 12 Los Angeles", "url": "/channels/Pac.12-Los-Angeles.html", "image": None},
            {"title": "Pac 12 Mountain", "url": "/channels/Pac-12-Mountain.html", "image": None},
            {"title": "Pac 12 Network", "url": "/channels/Pac-12-Network.html", "image": None},
            {"title": "Pac 12 Oregon", "url": "/channels/Pac-12-Oregon.html", "image": None},
            {"title": "Pac 12 Washington", "url": "/channels/Pac-12-Washington.html", "image": None},
            {"title": "PBS US", "url": "/channels/PBS-US.html", "image": None},
            {"title": "RT America", "url": "/channels/RT-America.html", "image": None},
            {"title": "Showtime US", "url": "/channels/Showtime-US.html", "image": None},
            {"title": "Spike", "url": "/channels/Spike.html", "image": None},
            {"title": "Sportsnet 1", "url": "/channels/Sportsnet-1.html", "image": None},
            {"title": "Sportsnet 360", "url": "/channels/Sportsnet-360.html", "image": None},
            {"title": "Sportsnet World", "url": "/channels/Sportsnet-World.html", "image": None},
            {"title": "Starz US", "url": "/channels/Starz%252dUS.html", "image": None},
            {"title": "Syfy", "url": "/channels/Syfy.html", "image": None},
            {"title": "TBS East", "url": "/channels/TBS.East.html", "image": None},
            {"title": "TLC US", "url": "/channels/TLC-US.html", "image": None},
            {"title": "TNT East", "url": "/channels/TNT-East.html", "image": None},
            {"title": "TSN 1", "url": "/channels/TSN%252d1.html", "image": None},
            {"title": "TSN 2", "url": "/channels/TSN%252d2.html", "image": None},
            {"title": "TSN 3", "url": "/channels/TSN%252d3.html", "image": None},
            {"title": "TSN 4", "url": "/channels/TSN%252d4.html", "image": None},
            {"title": "USA Network", "url": "/channels/USA%252dNetwork.html", "image": None},
            {"title": "VH1 US", "url": "/channels/VH1%252dUS.html", "image": None},
            {"title": "WeatherNation", "url": "/channels/WeatherNation.html", "image": None},
            {"title": "WGN 9 CW Chicago", "url": "/channels/WGN-9-CW-Chicago.html", "image": None},
            {"title": "WJHL Tennessee", "url": "/channels/WJHL-Tennessee.html", "image": None},
            {"title": "WTHI Terre Haute", "url": "/channels/WTHI-Terre-Haute.html", "image": None},
            {"title": "WWE", "url": "/channels/WWE.html", "image": None}
        ]
        self.MUSIC_TV = [
            {"title": "BET East", "url": "/channels/BET-East.html", "image": None},
            {"title": "BritAsia TV", "url": "/channels/BritAsia-TV.html", "image": None},
            {"title": "Busuioc TV", "url": "/channels/Busuioc-TV.html", "image": None},
            {"title": "Capital", "url": "/channels/Capital.html", "image": None},
            {"title": "Heart TV", "url": "/channels/Heart-TV.html", "image": None},
            {"title": "MTV Classic-UK", "url": "/channels/MTV%252dClassic%252dUK.html", "image": None},
            {"title": "MTV Dance", "url": "/channels/MTV%252dDance.html", "image": None},
            {"title": "MTV Hits", "url": "/channels/MTV-Hits.html", "image": None},
            {"title": "MTV Rocks", "url": "/channels/MTV%252dRocks.html", "image": None},
            {"title": "MTV", "url": "/channels/MTV.html", "image": None},
            {"title": "Noroc TV", "url": "/channels/Noroc-TV.html", "image": None},
            {"title": "UTV", "url": "/channels/UTV.html", "image": None},
            {"title": "VH1 EU", "url": "/channels/VH1-EU.html", "image": None},
            {"title": "VH1 US", "url": "/channels/VH1%252dUS.html", "image": None}
        ]
        self.NEWS_TV = [
            {"title": "RT America", "url": "/channels/RT-America.html", "image": None},
            {"title": "Sky News Arab", "url": "/channels/Sky-News-Arab.html", "image": None},
            {"title": "Sky News", "url": "/channels/Sky-News.html", "image": None},
            {"title": "Sky TG 24", "url": "/channels/Sky-TG-24.html", "image": None},
            {"title": "Tagesschau24", "url": "/channels/tagesschau24.html", "image": None},
            {"title": "WeatherNation", "url": "/channels/WeatherNation.html", "image": None},
            {"title": "WJHL Tennessee", "url": "/channels/WJHL-Tennessee.html", "image": None},
            {"title": "WTHI Terre Haute", "url": "/channels/WTHI-Terre-Haute.html", "image": None}
        ]
        self.SPORTS_TV = [
            {"title": "Astro SS 1", "url": "/channels/Astro-SS-1.html", "image": None},
            {"title": "Astro SS 3", "url": "/channels/Astro-SS3.html", "image": None},
            {"title": "Astro SS 4", "url": "/channels/Astro-SS-4.html", "image": None},
            {"title": "Chelsea TV", "url": "/channels/Chelsea-TV.html", "image": None},
            {"title": "Cycling 1", "url": "/channels/Cycling-1.html", "image": None},
            {"title": "Cycling 2", "url": "/channels/Cycling2.html", "image": None},
            {"title": "ESPN2", "url": "/channels/ESPN2.html", "image": None},
            {"title": "ESPN.1", "url": "/channels/ESPN.1.html", "image": None},
            {"title": "Eurosport1 FR", "url": "/channels/Eurosport1-FR.html", "image": None},
            {"title": "Eurosport", "url": "/channels/Eurosport.html", "image": None},
            {"title": "Golf TV", "url": "/channels/Golf-TV.html", "image": None},
            {"title": "L-Equipe 21", "url": "/channels/L%252dEquipe%252d21.html", "image": None},
            {"title": "Manchester United TV", "url": "/channels/Manchester-United-TV.html", "image": None},
            {"title": "MLB Network", "url": "/channels/MLB.Network.html", "image": None},
            {"title": "Motors TV", "url": "/channels/Motors-TV.html", "image": None},
            {"title": "NBA", "url": "/channels/NBA.html", "image": None},
            {"title": "NBC Sports", "url": "/channels/NBC.Sports.html", "image": None},
            {"title": "NFL", "url": "/channels/NFL.html", "image": None},
            {"title": "NHL Network", "url": "/channels/NHL-Network.html", "image": None},
            {"title": "Pac 12 Arizona", "url": "/channels/Pac-12-Arizona.html", "image": None},
            {"title": "Pac 12 Bay Area", "url": "/channels/Pac-12-Bay-Area.html", "image": None},
            {"title": "Pac 12 Los Angeles", "url": "/channels/Pac.12-Los-Angeles.html", "image": None},
            {"title": "Pac 12 Mountain", "url": "/channels/Pac-12-Mountain.html", "image": None},
            {"title": "Pac 12 Network", "url": "/channels/Pac-12-Network.html", "image": None},
            {"title": "Pac 12 Oregon", "url": "/channels/Pac-12-Oregon.html", "image": None},
            {"title": "Pac 12 Washington", "url": "/channels/Pac-12-Washington.html", "image": None},
            {"title": "Premier", "url": "/channels/Premier.html", "image": None},
            {"title": "Racing UK", "url": "/channels/Racing-UK.html", "image": None},
            {"title": "Rai Sport", "url": "/channels/Rai-Sport.html", "image": None},
            {"title": "Real Madrid TV", "url": "/channels/Real-Madrid-TV.html", "image": None},
            {"title": "SCalcio", "url": "/channels/SCalcio.html", "image": None},
            {"title": "Setanta", "url": "/channels/Setanta.html", "image": None},
            {"title": "Sky Sport 2", "url": "/channels/Sky%252dSport2.html", "image": None},
            {"title": "Sky Sport Uno", "url": "/channels/Sky-Sport%252dUno.html", "image": None},
            {"title": "Sportsnet 1", "url": "/channels/Sportsnet-1.html", "image": None},
            {"title": "Sportsnet 360", "url": "/channels/Sportsnet-360.html", "image": None},
            {"title": "Sportsnet World", "url": "/channels/Sportsnet-World.html", "image": None},
            {"title": "SSport 1", "url": "/channels/SSport-1.html", "image": None},
            {"title": "TSN-1", "url": "/channels/TSN%252d1.html", "image": None},
            {"title": "TSN-2", "url": "/channels/TSN%252d2.html", "image": None},
            {"title": "TSN-3", "url": "/channels/TSN%252d3.html", "image": None},
            {"title": "TSN-4", "url": "/channels/TSN%252d4.html", "image": None},
            {"title": "WWE", "url": "/channels/WWE.html", "image": None}
        ]
        self.categories = [
            {'title': 'USA TV', 'url': 'self.USA_TV', 'image': None},
            {'title': 'UK TV', 'url': 'self.UK_TV', 'image': None},
            {'title': 'All Channels', 'url': 'all_channels', 'image': None},
            {'title': 'Random Channel', 'url': 'random_channel', 'image': None},
            {'title': 'MUSIC TV', 'url': 'self.MUSIC_TV', 'image': None},
            {'title': 'NEWS TV', 'url': 'self.NEWS_TV', 'image': None},
            {'title': 'SPORTS TV', 'url': 'self.SPORTS_TV', 'image': None}
        ]


    def root(self):
        try:
            for i in self.categories:
                # title = client.replaceHTMLCodes(i['title'])
                url = i['url']
                image = self.base_link + i['image'] if i['image'] else i['image']
                if url == 'random_channel':
                    mode = 'shadownet_scrape_channel'
                else:
                    mode = 'shadownet_scrape_category'
                self.list.append({'title': i['title'], 'url': url, 'image': image, 'mode': mode})
            addDirectory(self.list)
            return self.list
        except:
            logger(f'root Exception: \n{traceback.print_exc()}')
            return self.list

    def scrape_category(self, url):
        try:
            if url == 'all_channels':
                self.channels += self.UK_TV
                self.channels += self.USA_TV
                self.channels += self.MUSIC_TV
                self.channels += self.NEWS_TV
                self.channels += self.SPORTS_TV
            elif url == 'self.MUSIC_TV':
                self.channels = self.MUSIC_TV
            elif url == 'self.NEWS_TV':
                self.channels = self.NEWS_TV
            elif url == 'self.SPORTS_TV':
                self.channels = self.SPORTS_TV
            elif url == 'self.UK_TV':
                self.channels = self.UK_TV
            elif url == 'self.USA_TV':
                self.channels = self.USA_TV
            for i in self.channels:
                # title = unescape(i['title'])
                link = self.base_link + i['url']
                image = self.base_link + i['image'] if i['image'] else i['image']
                self.list.append({'title': i['title'], 'url': link, 'image': image, 'mode': 'shadownet_scrape_channel'})
            self.list = sorted(self.list, key=lambda k: k['title'])
            addDirectory(self.list)
            return self.list
        except:
            logger(f'scrape_category Exception: \n{traceback.print_exc()}')
            notification('Error : No Stream Available.:', 900)
            return self.list

    def scrape_channel(self, url):
        try:
            if url == 'random_channel':
                choice = random.choice(self.USA_TV)
                url = self.base_link + choice['url']
            if not url.startswith('http'):
                url = self.base_link + url
            html = request(url)
            try:
                title = parseDOM(html, 'meta', attrs={'property': 'og:title'}, ret='content')[0]
            except:
                title = url.replace(self.base_link, '')
            title = keepclean_title(title)
            # logger(f'title: {title} html: {html}')
            link = parseDOM(html, 'iframe', ret='src')[0]
            html2 = request(link)
            if link2 := re.findall('{source: "(.+?)",', html2)[0]:
                link2 += f'|Referer={link}'
                # infinitePlayer().run(link2, 'video', {'title': title})
                # listitem = make_listitem()
                # listitem.setLabel(title)
                # listitem.setPath(path=link2)
                # listitem.setInfo(type='Video', infoLabels={'title': title})
                # listitem.setProperty('IsPlayable', 'true')
                infinitePlayer().run(link2, 'video', {'title': title})
            hide_busy_dialog()
            return
        except:
            logger(f'scrape_channel Exception: \n{traceback.print_exc()}')
            notification('Error : No Stream Available.:', 900)
            hide_busy_dialog()
            return


def addDirectory(items, queue=False, isFolder=True):
    from sys import argv
    for i in items:
        try:
            # url = '%s?action=%s&url=%s' % (sysaddon, i['action'], i['url'])
            # if i['mode'] == 'shadownet_scrape_channel': isFolder=False
            url = build_url(i)
            title = i['title']
            thumb = i['image'] or 'DefaultVideo.png'
            listitem = make_listitem()
            listitem.setLabel(title)
            listitem.setProperty('IsPlayable', 'true')
            listitem.setArt({'icon': thumb, 'thumb': thumb, 'fanart': addon_fanart})
            add_item(int(argv[1]), url, listitem, isFolder)
        except Exception as err: logger(f'addDirectory error: {err}')
    _end_directory()


def _end_directory():
    from sys import argv
    handle = int(argv[1])
    set_content(handle, '')
    end_directory(handle)
    # set_view_mode(view, '')
