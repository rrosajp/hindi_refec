# -*- coding: utf-8 -*-

import datetime
import base64
import re
import traceback
import requests
import json
from urllib.parse import urljoin

try:
    from indexers.hindi.live_client import scrapePage, agent
    from modules.kodi_utils import notification, logger, build_url, set_info, make_listitem, add_items, set_content, end_directory, set_view_mode, get_infolabel, addon_icon
    from caches.h_cache import main_cache, cache_object
except:
    from modules.live_client import scrapePage, agent, read_write_file
    from modules.utils import logger
    from modules.h_cache import main_cache, cache_object

    addon_icon = ''

from modules.dom_parser import parseDOM

base_link = 'https://ustvgo.tv'  # https://ustv247.tv/

ustv247_channels = [
    {"title": "Fox News", "mode": "ltp_ustv", "url": "/foxnewslive/", "image": "/wp-content/uploads/2018/08/foxnews.jpg"},
    {"title": "Fox Business", "mode": "ltp_ustv", "url": "/foxbusinesslive/", "image": "/wp-content/uploads/2018/08/foxbusiness.jpg"},
    {"title": "ABC", "mode": "ltp_ustv", "url": "/watch-abc-live-stream/", "image": "/wp-content/uploads/2018/12/abc-269x151.jpg"},
    {"title": "AE", "mode": "ltp_ustv", "url": "/ae-live-stream/", "image": "/wp-content/uploads/2018/12/ae-269x151.png"},
    {"title": "AMC", "mode": "ltp_ustv", "url": "/amc-live-stream/", "image": "/wp-content/uploads/2018/12/AMC.png"},
    {"title": "Animal Planet", "mode": "ltp_ustv", "url": "/animal-planet/", "image": "/wp-content/uploads/2019/03/animal-planet.png"},
    {"title": "BBC America", "mode": "ltp_ustv", "url": "/bbc-america/", "image": "/wp-content/uploads/2019/03/BBC.jpg"},
    {"title": "BET", "mode": "ltp_ustv", "url": "/bet/", "image": "/wp-content/uploads/2021/01/bet.jpg"},
    {"title": "Bravo", "mode": "ltp_ustv", "url": "/bravo/", "image": "/wp-content/uploads/2019/03/bravo-269x151.png"},
    {"title": "Cartoon Network", "mode": "ltp_ustv", "url": "/cartoon-network/", "image": "/wp-content/uploads/2019/03/cartoon-network.jpg"},
    {"title": "CBS", "mode": "ltp_ustv", "url": "/watch-cbs-live-stream/", "image": "/wp-content/uploads/2018/12/CBS-1.png"},
    {"title": "Cinemax", "mode": "ltp_ustv", "url": "/cinemax/", "image": "/wp-content/uploads/2021/01/cinemax.jpg"},
    {"title": "CMT", "mode": "ltp_ustv", "url": "/cmt/", "image": "/wp-content/uploads/2021/01/cmt.jpg"},
    {"title": "CNBC", "mode": "ltp_ustv", "url": "/cnbclive/", "image": "/wp-content/uploads/2018/08/cnbc.jpg"},
    {"title": "CNN", "mode": "ltp_ustv", "url": "/cnn-live-stream/", "image": "/wp-content/uploads/2018/08/CNN-1.png"},
    {"title": "Comedy Central", "mode": "ltp_ustv", "url": "/comedy-central/", "image": "/wp-content/uploads/2019/03/comedy-central-269x151.png"},
    {"title": "Discovery Channel", "mode": "ltp_ustv", "url": "/discovery-channel-live-stream/", "image": "/wp-content/uploads/2018/12/Discovery.png"},
    {"title": "Disney Channel", "mode": "ltp_ustv", "url": "/disney-channel/", "image": "/wp-content/uploads/2019/03/disney-269x151.png"},
    {"title": "Disney XD", "mode": "ltp_ustv", "url": "/disney-xd/", "image": "/wp-content/uploads/2021/01/disney-xd.jpg"},
    {"title": "Do it yourself", "mode": "ltp_ustv", "url": "/do-it-yourself/", "image": "/wp-content/uploads/2021/01/diy.jpg"},
    {"title": "E!", "mode": "ltp_ustv", "url": "/eonline/", "image": "/wp-content/uploads/2021/01/E.jpg"},
    {"title": "ESPN2", "mode": "ltp_ustv", "url": "/espn2/", "image": "/wp-content/uploads/2021/01/espn2.jpg"},
    {"title": "ESPN", "mode": "ltp_ustv", "url": "/espn/", "image": "/wp-content/uploads/2018/12/ESPN.png"},
    {"title": "ESPNU", "mode": "ltp_ustv", "url": "/espnu/", "image": "/wp-content/uploads/2021/01/espnu.jpg"},
    {"title": "Food Network", "mode": "ltp_ustv", "url": "/food-network/", "image": "/wp-content/uploads/2019/03/food-network-269x151.png"},
    {"title": "Fox Sports 1", "mode": "ltp_ustv", "url": "/fox-sports-1/", "image": "/wp-content/uploads/2020/08/fs1-269x151-1.png"},
    {"title": "Fox Sports 2", "mode": "ltp_ustv", "url": "/fox-sports-2/", "image": "/wp-content/uploads/2020/08/fs2-269x151-1.png"},
    {"title": "FOX", "mode": "ltp_ustv", "url": "/watch-fox-channel-live-stream/", "image": "/wp-content/uploads/2018/12/FOX-1.png"},
    {"title": "Freeform", "mode": "ltp_ustv", "url": "/freeform/", "image": "/wp-content/uploads/2019/03/freeform-269x151.png"},
    {"title": "FX Movie Channel", "mode": "ltp_ustv", "url": "/fx-movie-channel/", "image": "/wp-content/uploads/2021/01/FXM.jpg"},
    {"title": "FX", "mode": "ltp_ustv", "url": "/fx-channel-live-stream/", "image": "/wp-content/uploads/2018/12/fx-269x151.png"},
    {"title": "FXX", "mode": "ltp_ustv", "url": "/fxx/", "image": "/wp-content/uploads/2021/01/FXX.jpg"},
    {"title": "Game Show Network", "mode": "ltp_ustv", "url": "/game-show-network/", "image": "/wp-content/uploads/2021/01/GSN.jpg"},
    {"title": "Golf Channel", "mode": "ltp_ustv", "url": "/golf-channel/", "image": "/wp-content/uploads/2019/03/golf-269x151.png"},
    {"title": "Hallmark Movies and Mysteries", "mode": "ltp_ustv", "url": "/hallmark-movies-mysteries/", "image": "/wp-content/uploads/2019/03/HMM_logo_black-700x245.jpg"},
    {"title": "Hallmark", "mode": "ltp_ustv", "url": "/hallmark-channel-live-stream/", "image": "/wp-content/uploads/2018/12/hallmark-chanel-logo.jpg"},
    {"title": "HBO", "mode": "ltp_ustv", "url": "/hbo/", "image": "/wp-content/uploads/2019/03/hbo-269x151.png"},
    {"title": "HGTV", "mode": "ltp_ustv", "url": "/hgtv-live-stream/", "image": "/wp-content/uploads/2018/12/HGTV-269x151.png"},
    {"title": "History", "mode": "ltp_ustv", "url": "/history-channel-live-stream/", "image": "/wp-content/uploads/2018/12/History.png"},
    {"title": "Investigation Discovery", "mode": "ltp_ustv", "url": "/investigation-discovery/", "image": "/wp-content/uploads/2019/03/id-269x151.jpg"},
    {"title": "Lifetime Movies", "mode": "ltp_ustv", "url": "/lifetime-movies/", "image": "/wp-content/uploads/2021/01/lifetimeM.jpeg"},
    {"title": "Lifetime", "mode": "ltp_ustv", "url": "/lifetime/", "image": "/wp-content/uploads/2019/03/Lifetime-269x151.png"},
    {"title": "MSNBC", "mode": "ltp_ustv", "url": "/msnbclive/", "image": "/wp-content/uploads/2018/08/msnbc_logo-269x151.jpg"},
    {"title": "MTV", "mode": "ltp_ustv", "url": "/mtv/", "image": "/wp-content/uploads/2021/01/mtv.jpg"},
    {"title": "National Geographic", "mode": "ltp_ustv", "url": "/national-geographic-live-stream/", "image": "/wp-content/uploads/2018/12/NAtGeo.jpg"},
    {"title": "NBC", "mode": "ltp_ustv", "url": "/watch-nbc-live-stream/", "image": "/wp-content/uploads/2018/12/nbc-logo.jpg"},
    {"title": "NBCSN", "mode": "ltp_ustv", "url": "/nbcsn/", "image": "/wp-content/uploads/2021/01/nbcsn.jpg"},
    {"title": "NFL Network", "mode": "ltp_ustv", "url": "/nfl-network/", "image": "/wp-content/uploads/2019/03/nfln-logo-dark.png"},
    {"title": "Nickelodeon", "mode": "ltp_ustv", "url": "/nickelodeon/", "image": "/wp-content/uploads/2019/03/Nickelodeon_2009.png"},
    {"title": "One America News Network", "mode": "ltp_ustv", "url": "/one-america-news-network/", "image": "/wp-content/uploads/2019/03/OANN.jpg"},
    {"title": "OWN", "mode": "ltp_ustv", "url": "/own/", "image": "/wp-content/uploads/2021/01/own.jpg"},
    {"title": "Oxygen", "mode": "ltp_ustv", "url": "/oxygen/", "image": "/wp-content/uploads/2021/01/Oxygen.jpg"},
    {"title": "Paramount Network", "mode": "ltp_ustv", "url": "/paramount-network/", "image": "/wp-content/uploads/2021/01/spike.jpg"},
    {"title": "PBS", "mode": "ltp_ustv", "url": "/pbs-live-stream/", "image": "/wp-content/uploads/2018/12/PBS.jpg"},
    {"title": "POP", "mode": "ltp_ustv", "url": "/pop/", "image": "/wp-content/uploads/2021/01/pop.jpg"},
    {"title": "Science", "mode": "ltp_ustv", "url": "/science/", "image": "/wp-content/uploads/2021/01/Science.jpg"},
    {"title": "Showtime", "mode": "ltp_ustv", "url": "/showtime/", "image": "/wp-content/uploads/2019/03/Showtime-269x151.png"},
    {"title": "Starz", "mode": "ltp_ustv", "url": "/starz/", "image": "/wp-content/uploads/2019/03/StarZ-269x151.png"},
    {"title": "Sundance TV", "mode": "ltp_ustv", "url": "/sundance-tv/", "image": "/wp-content/uploads/2021/01/sundance-tv.jpg"},
    {"title": "Syfy", "mode": "ltp_ustv", "url": "/syfy/", "image": "/wp-content/uploads/2019/03/syfy-269x151.png"},
    {"title": "TBS", "mode": "ltp_ustv", "url": "/tbs/", "image": "/wp-content/uploads/2019/03/tbs-269x151.png"},
    {"title": "Telemundo", "mode": "ltp_ustv", "url": "/telemundo/", "image": "/wp-content/uploads/2021/01/Telemundo.jpg"},
    {"title": "Tennis Channel", "mode": "ltp_ustv", "url": "/tennis-channel/", "image": "/wp-content/uploads/2019/03/TennisChannel.whiteBg.png"},
    {"title": "The CW", "mode": "ltp_ustv", "url": "/the-cw-live-stream/", "image": "/wp-content/uploads/2018/12/cw-269x151.png"},
    {"title": "The Weather Channel", "mode": "ltp_ustv", "url": "/watch-weather-channel-live-stream/", "image": "/wp-content/uploads/2018/09/Weather-Channel-269x151.png"},
    {"title": "TLC", "mode": "ltp_ustv", "url": "/tlc/", "image": "/wp-content/uploads/2019/03/tlc-269x151.png"},
    {"title": "TNT", "mode": "ltp_ustv", "url": "/tnt/", "image": "/wp-content/uploads/2019/03/TNT.jpg"},
    {"title": "Travel Channel", "mode": "ltp_ustv", "url": "/travel-channel/", "image": "/wp-content/uploads/2019/03/Travel-269x151.png"},
    {"title": "truTV", "mode": "ltp_ustv", "url": "/trutv/", "image": "/wp-content/uploads/2021/01/TruTV.jpg"},
    {"title": "Turner Classic Movies", "mode": "ltp_ustv", "url": "/turner-classic-movies/", "image": "/wp-content/uploads/2019/03/TCM.png"},
    {"title": "TV Land", "mode": "ltp_ustv", "url": "/tv-land/", "image": "/wp-content/uploads/2019/03/TVLand-269x151.png"},
    {"title": "Univision", "mode": "ltp_ustv", "url": "/univision/", "image": "/wp-content/uploads/2021/01/univision.jpg"},
    {"title": "USA Network", "mode": "ltp_ustv", "url": "/usa-network-live-stream/", "image": "/wp-content/uploads/2018/12/USA-Network-269x151.png"},
    {"title": "VH1", "mode": "ltp_ustv", "url": "/vh1/", "image": "/wp-content/uploads/2021/01/vh1.jpg"},
    {"title": "We TV", "mode": "ltp_ustv", "url": "/we-tv/", "image": "/wp-content/uploads/2021/01/wetv.jpg"}
    ]

ustvgo_channels = [
    {"title": "FoxNews", "mode": "ltp_ustv", "url": "/fox-news-live-streaming-free/", "image": "/wp-content/uploads/2018/10/foxnews.jpg"},
    {"title": "FoxBusiness", "mode": "ltp_ustv", "url": "/fox-business-live-streaming-free/", "image": "/wp-content/uploads/2018/10/foxbusiness.jpg"},
    {"title": "ABC", "mode": "ltp_ustv", "url": "/abc-live-streaming-free/", "image": "/wp-content/uploads/2018/10/abc-269x151.jpg"},
    {"title": "ABC 7 New York", "mode": "ltp_ustv", "url": "/abc-7-new-york/", "image": "/wp-content/uploads/2020/09/cropped-icon_small-192x192.jpg"},
    {"title": "ACC Network", "mode": "ltp_ustv", "url": "/acc-network/", "image": "/wp-content/uploads/2021/06/accn.jpg"},
    {"title": "AE", "mode": "ltp_ustv", "url": "/ae-networks-live-streaming-free/", "image": "/wp-content/uploads/2019/01/AE.png"},
    {"title": "AMC", "mode": "ltp_ustv", "url": "/amc-live/", "image": "/wp-content/uploads/2019/01/AMC-1.png"},
    {"title": "Animal Planet", "mode": "ltp_ustv", "url": "/animal-planet-live/", "image": "/wp-content/uploads/2019/01/animal-planet.png"},
    {"title": "BBCAmerica", "mode": "ltp_ustv", "url": "/bbc-america-live/", "image": "/wp-content/uploads/2019/01/BBC.jpg"},
    {"title": "BET", "mode": "ltp_ustv", "url": "/bet/", "image": "/wp-content/uploads/2019/08/bet-269x151.png"},
    {"title": "Big Ten Network", "mode": "ltp_ustv", "url": "/big-ten-network/", "image": "/wp-content/uploads/2020/09/BTN.jpg"},
    {"title": "Boomerang", "mode": "ltp_ustv", "url": "/boomerang/", "image": "/wp-content/uploads/2019/08/Boomerang.png"},
    {"title": "Bravo", "mode": "ltp_ustv", "url": "/bravo-channel-live-free/", "image": "/wp-content/uploads/2019/01/bravo-269x151.png"},
    {"title": "C-SPAN", "mode": "ltp_ustv", "url": "/c-span/", "image": "/wp-content/uploads/2020/09/cspan-269x151-1.png"},
    {"title": "Cartoon Network", "mode": "ltp_ustv", "url": "/cartoon-network/", "image": "/wp-content/uploads/2019/01/cartoon-network.jpg"},
    {"title": "CBS", "mode": "ltp_ustv", "url": "/cbs-live-streaming-free/", "image": "/wp-content/uploads/2018/10/CBS-1.png"},
    {"title": "CBS 2 New York", "mode": "ltp_ustv", "url": "/cbs-2-new-york/", "image": "/wp-content/uploads/2020/09/cropped-icon_small-192x192.jpg"},
    {"title": "CBS Sports Network", "mode": "ltp_ustv", "url": "/cbs-sports-network/", "image": "/wp-content/uploads/2020/09/cbssn.jpg"},
    {"title": "Cinemax", "mode": "ltp_ustv", "url": "/cinemax/", "image": "/wp-content/uploads/2020/04/cinemax.jpg"},
    {"title": "CMT", "mode": "ltp_ustv", "url": "/cmt/", "image": "/wp-content/uploads/2019/08/cmt-1.png"},
    {"title": "CNBC", "mode": "ltp_ustv", "url": "/cnbc-live-streaming-free/", "image": "/wp-content/uploads/2018/10/cnbc-1.jpg"},
    {"title": "CNN", "mode": "ltp_ustv", "url": "/cnn-live-streaming-free/", "image": "/wp-content/uploads/2018/10/CNN-1.png"},
    {"title": "Comedy Central", "mode": "ltp_ustv", "url": "/comedy-central-live-free/", "image": "/wp-content/uploads/2019/01/comedy-central-269x151.png"},
    {"title": "CW", "mode": "ltp_ustv", "url": "/the-cw-live-streaming-free/", "image": "/wp-content/uploads/2019/01/cw-269x151.png"},
    {"title": "CW 11 New York", "mode": "ltp_ustv", "url": "/the-cw-11-new-york/", "image": "/wp-content/uploads/2020/09/cropped-icon_small-192x192.jpg"},
    {"title": "Destination America", "mode": "ltp_ustv", "url": "/destination-america/", "image": "/wp-content/uploads/2019/08/Destination_America.png"},
    {"title": "Discovery", "mode": "ltp_ustv", "url": "/discovery-channel-live/", "image": "/wp-content/uploads/2019/01/Discovery.png"},
    {"title": "Disney", "mode": "ltp_ustv", "url": "/disney-channel-live-streaming-free/", "image": "/wp-content/uploads/2019/01/disney-269x151.png"},
    {"title": "DisneyJr", "mode": "ltp_ustv", "url": "/disneyjr/", "image": "/wp-content/uploads/2019/08/disney-jr-768x432-1.png"},
    {"title": "DisneyXD", "mode": "ltp_ustv", "url": "/disneyxd/", "image": "/wp-content/uploads/2019/08/disney-xd-768x432-1.png"},
    {"title": "Do it yourself (DIY)", "mode": "ltp_ustv", "url": "/diy/", "image": "/wp-content/uploads/2019/08/diy.png"},
    {"title": "E!", "mode": "ltp_ustv", "url": "/eonline/", "image": "/wp-content/uploads/2019/08/E.png"},
    {"title": "ESPN", "mode": "ltp_ustv", "url": "/espn-live/", "image": "/wp-content/uploads/2019/01/espn-269x151.png"},
    {"title": "ESPN2", "mode": "ltp_ustv", "url": "/espn2/", "image": "/wp-content/uploads/2019/08/espn2-269x151.png"},
    {"title": "ESPNews", "mode": "ltp_ustv", "url": "/espnews/", "image": "/wp-content/uploads/2020/09/espnews-269x151-1.png"},
    {"title": "ESPNU", "mode": "ltp_ustv", "url": "/espnu/", "image": "/wp-content/uploads/2020/09/espnu-269x151-1.png"},
    {"title": "FoodNetwork", "mode": "ltp_ustv", "url": "/food-network-live-free/", "image": "/wp-content/uploads/2019/01/food-network-269x151.png"},
    {"title": "FOX", "mode": "ltp_ustv", "url": "/fox-hd-live-streaming/", "image": "/wp-content/uploads/2018/10/FOX-1.png"},
    {"title": "FOX 5 New York", "mode": "ltp_ustv", "url": "/fox-5-new-york/", "image": "/wp-content/uploads/2020/09/cropped-icon_small-192x192.jpg"},
    {"title": "Fox Sports 1 (FS1)", "mode": "ltp_ustv", "url": "/fox-sports-1/", "image": "/wp-content/uploads/2019/01/fs1-269x151.png"},
    {"title": "Fox Sports 2 (FS2)", "mode": "ltp_ustv", "url": "/fox-sports-2/", "image": "/wp-content/uploads/2019/01/fs2-269x151.png"},
    {"title": "Freeform", "mode": "ltp_ustv", "url": "/freeform-channel-live-free/", "image": "/wp-content/uploads/2019/01/freeform-269x151.png"},
    {"title": "FX", "mode": "ltp_ustv", "url": "/fx-channel-live/", "image": "/wp-content/uploads/2019/01/fx-269x151.png"},
    {"title": "FX Movie Channel", "mode": "ltp_ustv", "url": "/fxm/", "image": "/wp-content/uploads/2019/08/FXM.png"},
    {"title": "FXX", "mode": "ltp_ustv", "url": "/fxx/", "image": "/wp-content/uploads/2019/08/FXX.png"},
    {"title": "Game Show Network", "mode": "ltp_ustv", "url": "/gsn/", "image": "/wp-content/uploads/2019/08/GSN.jpg"},
    {"title": "Golf Channel", "mode": "ltp_ustv", "url": "/golf-channel-live-free/", "image": "/wp-content/uploads/2019/01/golf-269x151.png"},
    {"title": "Hallmark Channel", "mode": "ltp_ustv", "url": "/hallmark-channel-live-streaming-free/", "image": "/wp-content/uploads/2019/01/hallmark-chanel-logo.jpg"},
    {"title": "Hallmark Movies and Mysteries", "mode": "ltp_ustv", "url": "/hallmark-movies-mysteries-live-streaming-free/", "image": "/wp-content/uploads/2019/01/HMM_logo_black-700x245.jpg"},
    {"title": "HBO", "mode": "ltp_ustv", "url": "/hbo/", "image": "/wp-content/uploads/2019/01/hbo-269x151.png"},
    {"title": "HGTV", "mode": "ltp_ustv", "url": "/hgtv-live-streaming-free/", "image": "/wp-content/uploads/2019/01/HGTV-269x151.png"},
    {"title": "History", "mode": "ltp_ustv", "url": "/history-channel-live/", "image": "/wp-content/uploads/2019/01/History.png"},
    {"title": "HLN", "mode": "ltp_ustv", "url": "/hln/", "image": "/wp-content/uploads/2019/08/HLN.jpg"},
    {"title": "Investigation Discovery", "mode": "ltp_ustv", "url": "/investigation-discovery-live-streaming-free/", "image": "/wp-content/uploads/2019/01/id-269x151.jpg"},
    {"title": "ION (WPXN) New York", "mode": "ltp_ustv", "url": "/ion-wpxn-new-york/", "image": "/wp-content/uploads/2020/09/cropped-icon_small-192x192.jpg"},
    {"title": "Lifetime", "mode": "ltp_ustv", "url": "/lifetime-channel-live/", "image": "/wp-content/uploads/2019/01/Lifetime-269x151.png"},
    {"title": "Lifetime Movie Network", "mode": "ltp_ustv", "url": "/lifetime-movies/", "image": "/wp-content/uploads/2019/08/lifetimeM.jpeg"},
    {"title": "MLB Network", "mode": "ltp_ustv", "url": "/mlb-network/", "image": "/wp-content/uploads/2019/05/MLB.png"},
    {"title": "Motor Trend", "mode": "ltp_ustv", "url": "/motortrend/", "image": "/wp-content/uploads/2019/08/Motortrend-1.png"},
    {"title": "MSNBC", "mode": "ltp_ustv", "url": "/msnbc-live-streaming-free/", "image": "/wp-content/uploads/2018/10/msnbc_logo-269x151.jpg"},
    {"title": "MTV", "mode": "ltp_ustv", "url": "/mtv/", "image": "/wp-content/uploads/2019/08/mtv.jpg"},
    {"title": "Nat Geo Wild", "mode": "ltp_ustv", "url": "/nat-geo-wild-live/", "image": "/wp-content/uploads/2019/01/NatGeoWild.jpeg"},
    {"title": "National Geographic", "mode": "ltp_ustv", "url": "/national-geographic-live/", "image": "/wp-content/uploads/2019/01/National-Geographic-269x151.png"},
    {"title": "NBA TV", "mode": "ltp_ustv", "url": "/nba-tv/", "image": "/wp-content/uploads/2019/01/nbatv-269x151.jpg"},
    {"title": "NBC", "mode": "ltp_ustv", "url": "/nbc/", "image": "/wp-content/uploads/2018/10/nbc-logo.jpg"},
    {"title": "NBC 4 New York", "mode": "ltp_ustv", "url": "/nbc-4-new-york/", "image": "/wp-content/uploads/2020/09/cropped-icon_small-192x192.jpg"},
    {"title": "NBC Sports (NBCSN)", "mode": "ltp_ustv", "url": "/nbc-sports/", "image": "/wp-content/uploads/2019/01/nbcsn-269x151.jpg"},
    {"title": "NFL Network", "mode": "ltp_ustv", "url": "/nfl-network-live-free/", "image": "/wp-content/uploads/2019/01/nfln-logo-dark.png"},
    {"title": "NFL RedZone", "mode": "ltp_ustv", "url": "/nfl-redzone/", "image": "/wp-content/uploads/2020/09/NFLRZ.jpg"},
    {"title": "Nickelodeon", "mode": "ltp_ustv", "url": "/nickelodeon-live-streaming-free/", "image": "/wp-content/uploads/2019/01/Nickelodeon_2009.png"},
    {"title": "Nicktoons", "mode": "ltp_ustv", "url": "/nicktoons/", "image": "/wp-content/uploads/2019/08/nicktoons.png"},
    {"title": "Olympic Channel", "mode": "ltp_ustv", "url": "/olympic-channel/", "image": "/wp-content/uploads/2020/09/oly.jpg"},
    {"title": "One America News Network", "mode": "ltp_ustv", "url": "/one-america-news-network/", "image": "/wp-content/uploads/2019/09/OAN.jpg"},
    {"title": "Oprah Winfrey Network (OWN)", "mode": "ltp_ustv", "url": "/own/", "image": "/wp-content/uploads/2019/08/own.jpg"},
    {"title": "Oxygen", "mode": "ltp_ustv", "url": "/oxygen/", "image": "/wp-content/uploads/2019/08/Oxygen-1.png"},
    {"title": "Paramount", "mode": "ltp_ustv", "url": "/paramount-network/", "image": "/wp-content/uploads/2019/08/paramount.jpg"},
    {"title": "PBS", "mode": "ltp_ustv", "url": "/pbs-live/", "image": "/wp-content/uploads/2019/01/PBS.jpg"},
    {"title": "POP", "mode": "ltp_ustv", "url": "/pop/", "image": "/wp-content/uploads/2019/08/Pop_Network-1.png"},
    {"title": "Science", "mode": "ltp_ustv", "url": "/science/", "image": "/wp-content/uploads/2019/08/Science.jpg"},
    {"title": "SEC Network", "mode": "ltp_ustv", "url": "/sec-network/", "image": "/wp-content/uploads/2020/09/sec.jpg"},
    {"title": "Showtime", "mode": "ltp_ustv", "url": "/showtime/", "image": "/wp-content/uploads/2019/01/Showtime-269x151.png"},
    {"title": "StarZ", "mode": "ltp_ustv", "url": "/starz-channel-live/", "image": "/wp-content/uploads/2019/01/StarZ-269x151.png"},
    {"title": "SundanceTV", "mode": "ltp_ustv", "url": "/sundance-tv/", "image": "/wp-content/uploads/2019/08/sundance-tv.jpg"},
    {"title": "SYFY", "mode": "ltp_ustv", "url": "/syfy-channel-live/", "image": "/wp-content/uploads/2019/01/syfy-269x151.png"},
    {"title": "TBS", "mode": "ltp_ustv", "url": "/tbs-channel-live-free/", "image": "/wp-content/uploads/2019/01/tbs-269x151.png"},
    {"title": "Telemundo", "mode": "ltp_ustv", "url": "/telemundo/", "image": "/wp-content/uploads/2019/08/Telemundo.png"},
    {"title": "Tennis Channel", "mode": "ltp_ustv", "url": "/tennis-channel-live-free/", "image": "/wp-content/uploads/2019/01/TennisChannel.whiteBg.png"},
    {"title": "The Weather Channel", "mode": "ltp_ustv", "url": "/the-weather-channel-live-streaming-free/", "image": "/wp-content/uploads/2018/10/Weather-Channel-269x151.png"},
    {"title": "TLC", "mode": "ltp_ustv", "url": "/tlc-live-free/", "image": "/wp-content/uploads/2019/01/tlc-269x151.png"},
    {"title": "TNT", "mode": "ltp_ustv", "url": "/tnt/", "image": "/wp-content/uploads/2019/01/TNT.jpg"},
    {"title": "Travel Channel", "mode": "ltp_ustv", "url": "/travel-channel-live-free/", "image": "/wp-content/uploads/2019/01/Travel-269x151.png"},
    {"title": "truTV", "mode": "ltp_ustv", "url": "/trutv/", "image": "/wp-content/uploads/2019/08/TruTV-269x151.png"},
    {"title": "Turner Classic Movies (TCM)", "mode": "ltp_ustv", "url": "/tcm/", "image": "/wp-content/uploads/2019/05/TCM.png"},
    {"title": "TV Land", "mode": "ltp_ustv", "url": "/tv-land-live-free/", "image": "/wp-content/uploads/2019/01/TVLand-269x151.png"},
    {"title": "Univision", "mode": "ltp_ustv", "url": "/univision/", "image": "/wp-content/uploads/2019/08/univisionlogo.jpg"},
    {"title": "USA Network", "mode": "ltp_ustv", "url": "/usa-network-live/", "image": "/wp-content/uploads/2019/01/USA-Network-269x151.png"},
    {"title": "VH1", "mode": "ltp_ustv", "url": "/vh1/", "image": "/wp-content/uploads/2019/08/vh1.png"},
    {"title": "We TV", "mode": "ltp_ustv", "url": "/we-tv/", "image": "/wp-content/uploads/2019/08/wetv.jpg"},
    {"title": "WWE Network", "mode": "ltp_ustv", "url": "/wwe-network/", "image": "/wp-content/uploads/2019/09/wwe-269x151.png"},
    {"title": "YES Network", "mode": "ltp_ustv", "url": "/yes-network/", "image": "/wp-content/uploads/2020/04/yes.jpg"}
    ]


def ustv_root(params):
    base_link = 'https://ustvgo.tv'
    list_data = ustvgo_channels
    if params['list_name'] == 'US tv247':
        base_link = 'https://ustv247.tv'
        list_data = ustv247_channels

    from sys import argv  # some functions like ActivateWindow() throw invalid handle less this is imported here.
    handle = int(argv[1])
    add_items(handle, list(_process(list_data, base_link)))
    set_content(handle, 'episodes')
    end_directory(handle)
    set_view_mode('view.episodes', 'episodes')


def _process(list_data, base_link):
    for i in list_data:
        # logger(f"desirulez _process item: {i}")
        try:
            listitem = make_listitem()
            cm = []
            cm_append = cm.append
            name = i['title']
            thumb = i['image'] if i['image'].startswith('http') else base_link + i['image']
            if thumb in ('', None): thumb = addon_icon
            url = f'{base_link}{i["url"]}'
            url_params = {'mode': i['mode'], 'title': name, 'url': url}
            url = build_url(url_params)
            options_params = {'mode': 'options_menu_choice', 'suggestion': name, 'play_params': json.dumps(url_params)}
            cm_append(("[B]Options...[/B]", f'RunPlugin({build_url(options_params)})'))
            cm_append(("[B]Add to a Shortcut Folder[/B]", 'RunPlugin(%s)' % build_url({'mode': 'menu_editor.shortcut_folder_add_item', 'name': name, 'iconImage': thumb})))
            listitem.setLabel(name)
            listitem.addContextMenuItems(cm)
            listitem.setArt({'thumb': thumb})
            i.update({'imdb_id': name, 'mediatype': 'episode', 'episode': 1, 'season': 0})
            setUniqueIDs = {'imdb': str(name)}
            listitem = set_info(listitem, i, setUniqueIDs)
            yield url, listitem, False
        except: logger(f'item: {i} ---USTVgo _process - Exception: {traceback.print_exc()}')
    return


def retrieve_new_token(argf=None):
    renew_token_node = 'https://ustvgo.tv/data.php'
    renew_token_node_post_data = {"stream": "NFL"}
    # logger("retrieve_new_token Working some black magic..")
    stream_url = requests.post(renew_token_node, headers={"User-Agent": agent()}, data=renew_token_node_post_data, ).text
    # auth_token = stream_url.split("wmsAuthSign=")[1]
    # logger("stream_url: %s"% stream_url)
    result = re.compile('https://(.+?)/.+?wmsAuthSign=(.+?)$', re.MULTILINE | re.DOTALL).findall(stream_url)
    return {"cdn_nodes": result[0][0], "auth_token": result[0][1]}


def play(params):
    # logger(f"params : {params}")
    title = params['title']
    auth_token = cache_object(function=retrieve_new_token, string='content_list_ustvgo_auth_token', url='', json=False, expiration=3)
    try:
        if title == "The Weather Channel": link = params['url']
        else: link = params['vid_url'] % (auth_token['cdn_nodes'], auth_token['auth_token'])
        link = f'{link}|User-Agent={agent()}&Referer={params["url"]}'
        logger(f"link3: {link}")
        from modules.player import infinitePlayer
        infinitePlayer().run(link, 'video', {'info': title, 'source': ''})
    except:
        # auth_token = cache_object(function=retrieve_new_token, string='content_list_ustvgo_auth_token', url='', json=False, expiration=0.1)
        logger(f'---USTVgo - Exception: {traceback.print_exc()}')
        notification('USTVgo - VPN Locked Or The Code Has Changed:', 2000)
        return


def play_old(params):
    try:
        # logger(f"params : {params}")
        title = params['title']
        url = params['url']
        headers = {'User-Agent': agent(), 'Referer': base_link}
        link = scrapePage(url, headers=headers).text
        # link = base_link + str([i for i in re.findall("<iframe src='(.+?)'", link)][0].split("'")[0])
        # link = str([i for i in re.findall("<iframe src='(.+?)'", link)][0].split("'")[0])
        link = parseDOM(link, 'iframe', ret='src')[0]
        # logger("link: %s"% link)
        if not link.startswith('http'): link = urljoin(base_link, link)
        # logger("link: %s"% link)
        link = scrapePage(link, headers=headers).text
        try:
            # code = link[link.find("encrypted"):]
            # code = code[:code.find("</script>")]
            # file_code = re.findall(r"file.+", code)[0]
            # file_code = "var link = " + file_code[file_code.find(":") + 1: file_code.find(",")]
            # code = code[:code.find("var player")]
            # code = code + file_code
            # crypto_min = base_link + "/Crypto/crypto.min.js"
            # addional_code = scrapePage(crypto_min, headers = headers).text
            # code = addional_code + code
            # context = js2py.EvalJs(enable_require=True)
            # link = context.eval(code)
            # logger('link1: %s' % link.replace("\r","").replace("\n",""))
            # link = ''.join(['{}'.format(line.rstrip('\n')) for line in str(link)])
            # link = link.replace("\r","").replace("\n","")
            # logger(f'link2: {link}')
            # logger("code: %s"% link)
            # code = re.findall(r'atob\(\'(.+?)\'', link)
            code = re.findall(r'var hls_src=\'(.+?)\';', link)
            # logger("urls: %s"% code)
            # link = base64.b64decode(code[0])
            # if not isinstance(link, str):
            # link = link.decode('utf-8')
            link = f'{code[0]}|User-Agent={agent()}&Referer={base_link}'
            # logger(f"link to play: {link}")
            from modules.player import infinitePlayer
            infinitePlayer().run(link, 'video', {'title': title})
        except:
            notification('USTVgo - VPN Locked Or The Code Has Changed:', 2000)
            return
    except:
        logger(f'---USTVgo - Exception: \n{traceback.print_exc()}\n')
        notification('USTVgo - Exception:', 900)
        return


def get_dict_per_name(list_of_dict, key_value):
    my_item = None
    for item in list_of_dict:
        if item['title'] == key_value:
            my_item = item
            list_of_dict.remove(my_item)
            break
    return list_of_dict, my_item


def get_ch_data():
    uri = "https://bitbucket.org/jai_s/repojp/raw/HEAD/etc/allxml/ustvgo_new.json"
    data = scrapePage(uri).text
    list_of_dict = json.loads(data)
    ch_lists = []
    result = scrapePage(base_link).text
    # read_write_file(file_n='ustv.html', read=False, result=result)
    # result = read_write_file(file_n='ustv.html')
    ch_url = re.findall('<li><strong><a href="(.+?)">(.+?)</a>', result)
    # logger(f">>> nos of url : {len(ch_url)}")
    ch_no = 3
    for item in ch_url:
        # logger(f">>> nos of item : {item}")
        ch_name = item[1].replace('#038;', '').replace('&amp;', '&').replace('Animal', 'Animal Planet').replace('CW', 'The CW').strip()
        # ch_name = ch_name.replace('Animal', 'Animal Planet').replace('CW', 'The CW').strip()
        list_of_dict, ch_dict = get_dict_per_name(list_of_dict, ch_name)
        # logger(f">>> item: {ch_dict}")
        if ch_name == 'FoxBusiness':
            ch_no = 2
        elif ch_name == 'FoxNews':
            if ch_name == 'FoxNews': ch_no = 1
        else:
            ch_no += 1

        if ch_dict:
            ch_dict.update({'url': item[0], 'ch_no': ch_no})
            ch_lists.append(ch_dict)
        else:
            result = scrapePage(item[0]).text
            if ch_stub := re.findall(
                r'<iframe src=[\'|"]\/clappr\.php\?stream=(.+?)[\'|"] allowfullscreen',
                result,
            ):
                vid_url = f'https://%s/{ch_stub[0]}/myStream/playlist.m3u8?wmsAuthSign=%s'
            else:
                vid_url = "https://%s/Boomerang/myStream/playlist.m3u8?wmsAuthSign=%s"
            ch_lists.append({'ch_no': ch_no, 'action': 'ltp_ustv', 'poster': '', 'title': ch_name, 'url': item[0], 'vid_url': vid_url})
    # logger(f">>> nos of item in local but not found new : {len(list_of_dict)} list_of_dict: {list_of_dict}")
    ch_lists += list_of_dict
    ch_lists = sorted(ch_lists, key=lambda k: k['ch_no'])
    # ch_lists = json.loads(str(ch_lists))
    # logger(f">>> list_of_dict: {json.dumps(ch_lists)}")
    # logger(f">>> nos of item in ch_lists : {len(ch_lists)}")
    return ch_lists


# if __name__ == "__main__":
#     get_ch_data()