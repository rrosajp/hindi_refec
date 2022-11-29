# -*- coding: utf-8 -*-
import datetime
import json
import random
import re
import traceback


from openscrapers import urlparse, quote_plus, parse_qs, urlencode, urljoin, testing

from openscrapers.modules.dom_parser import parseDOM
from openscrapers.modules.utils import byteify
from openscrapers.modules.py_tools import isPY3, ensure_str
from openscrapers.modules.client import scrapePage, agent, request
from openscrapers.modules.log_utils import log, error
from resolveurl import HostedMediaFile

bytes = bytes
str = unicode = basestring = str


def keep_readable(text):
    text = text.replace('&#8216;', "'")
    text = text.replace('&#8217;', "'")
    text = text.replace('&#8220;', '"')
    text = text.replace('&#8221;', '"')
    text = text.replace('&#8211;', ' ')
    text = text.replace('&#8230;', ' ')
    text = text.replace("&amp;", "&")
    text = text.replace("-", "")
    # text = text.encode('ascii', 'ignore').decode('unicode_escape').strip()
    return text


def getVideoID(url):
    try: return re.compile('(id|url|v|si|sin|sim|data-config|file|dm|wat|vid)=(.+?)##').findall(url + '##')[0][1]
    except: return


def get_mod_url(url):
    url_id = getVideoID(url)
    if not url_id: return
    if 'vkprime.php' in url: return f'http://vkprime.com/embed-{url_id}.html'
    elif 'vkspeed.php' in url: return f'http://vkspeed.com/embed-{url_id}.html'
    elif 'speed.php' in url: return f'http://vkspeed.com/embed-{url_id}-600x380.html'
    # elif 'viralnews.site/tech/xstrm.php' in url: return f'https://techautomate.in/news.php?cid={url_id}&type=xstrm'
    # elif 'viralnews.site/tech/vp.php' in url: return f'https://techautomate.in/technology.php?id={url_id}'
    # elif 'viralnews.site/tech/vk.php' in url: return f'https://techautomate.in/media.php?id={url_id}'
    # elif 'tere-sheher-mein' in url: return f'https://flow.business-loans.pw/plyr2/{url_id}'
    # elif 'ishqbaaz' in url: return f'http://flow.bestarticles.me/embed2//{url_id}'
    return url


def byte_to_str(bytes_or_str):
    # Check if it's in bytes
    if isinstance(bytes_or_str, bytes): bytes_or_str = bytes_or_str.decode('utf-8')
    # else: log("Object not of byte type")
    return bytes_or_str


def host(url):
    try: url = byte_to_str(url)
    except: pass
    host = re.findall(r'([\w]+[.][\w]+)$', urlparse(url.strip().lower()).netloc)[0]
    return str(host.split('.')[0])


def to_utf8(obj):
    try:
        if isinstance(obj, unicode): obj = obj.encode('utf-8', 'ignore')
        elif isinstance(obj, dict):
            import copy
            obj = copy.deepcopy(obj)
            for key, val in obj.items():
                obj[key] = to_utf8(val)
        elif obj is not None and hasattr(obj, "__iter__"): obj = obj.__class__([to_utf8(x) for x in obj])
        else: pass
    except: pass
    return obj


def stringify_nodes(data):
    if isinstance(data, list): return [stringify_nodes(x) for x in data]
    elif isinstance(data, dict):
        dkeys = list(data.keys())
        for i, k in enumerate(dkeys):
            try: dkeys[i] = k.decode()
            except: pass
        data = dict(zip(dkeys, list(data.values())))
        return {stringify_nodes(key): stringify_nodes(val) for key, val in data.items()}
    elif isinstance(data, bytes):
        try: return data.decode()
        except: return data
    else: return data


def clean_title(title):
    cleanup = ['Watch', 'Onilne', 'Tamil', 'Dubbed', 'WAtch ', 'Free', 'Full', 'AMZN', 'SCR', 'DvDRip', 'DvDScr', 'Full Movie Online Free', 'Uncensored', 'Full Movie Online', 'Watch Online ', 'Free HD', 'Online Full Movie', 'Downlaod', 'Bluray', 'Full Free', 'Malayalam Movie', ' Malayalam ', 'Full Movies', 'Full Movie', 'Free Online', 'Movie Online',
               'Watch', 'movie', 'Movie ', 'Songs', 'Hindi', 'Korean', 'Web', 'tamil', 'RIP', 'Tamil Movie', ' Hindi', 'Hilarious Comedy Scenes', 'Super Comedy Scenes', 'Ultimate Comedy Scenes', 'Watch...', 'BDRip', 'Super comedy Scenes', 'Comedy Scenes', 'hilarious comedy Scenes', '...', 'Telugu Movie', 'Sun TV Show', 'Vijay TV Show',
               'Gujarati', 'WebDL', 'WEB', 'Film', 'ESUBS', 'Web', '~', 'Sun Tv Show', 'Download', 'Starring', u'\u2013', 'Tamil Full Movie', 'Tamil Horror Movie', 'Tamil Dubbed Movie', '|', '-', ' Full ', u'\u2019', '/', 'Pre HDRip', '(DVDScr Audio)', 'PDVDRip', 'DVDSCR', '(HQ Audio)', 'HQ', ' Telugu', 'BRRip', 'DVDScr', 'DVDscr', 'PreDVDRip', 'DVDRip',
               'DVDRIP', 'WEBRip', 'Rip', ' Punjabi', 'TCRip', 'HDRip', 'HDTVRip', 'HD-TC', 'HDTV', 'TVRip', '720p', 'DVD', 'HD', ' Dubbed', '( )', '720p', '(UNCUT)', 'UNCUT', '(Clear Audio)', 'DTHRip', '(Line Audio)', ' Kannada', ' Hollywood', 'TS', 'CAM', 'Online Full', '[+18]', 'Streaming Free', 'Permalink to ', 'And Download', '()', 'Full English', ' English', 'Online', ' Tamil', ' Bengali',
               ' Bhojpuri', 'Print Free', 'DL']

    for word in cleanup:
        if word in title: title = title.replace(word, '')
    return title.strip()


def keepclean_title(title):
    if title is None: return
    exctract_date = re.compile(r'(\d{1,2}[th|st|nd|rd]* [Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|August|Sep|September|Oct|October|Nov|November|Dec|December]* \d{2,4})')
    episode_data = re.compile(r'[Ee]pisodes.+?(\d+)|[Ee]p (\d+)|[Ee](\d+)|[sS]eason.+?(\d+)|[sS]eason(\d+)|[sS](\d+)')
    # ansi_pattern = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
    ansi_pattern = re.compile(r'[^\x00-\x7f]')
    try:
        if ':' in title: title = title.split(':')[0]
        title = re.sub(exctract_date, '', title)  # remove date like 18th April 2021
        title = re.sub(episode_data, '', title)  # remove episod 12 or season 1 etc
        title = re.sub(ansi_pattern, '', title)  # remove ansi_pattern
        title = re.sub(r'&#(\d+);', '', title)
        title = re.sub(r'(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
        title = title.replace('&quot;', '\"').replace('&amp;', '&')
        title = re.sub(r'([:;\-"\',!_.?~$@])', '', title)  # remove all characters in bracket
        title = re.sub(r'\<[^>]*\>|\([^>]*\)', '', title) # remove like this <any thing> or (any thing)
        # title = re.sub(r'\([^>]*\)', '', title)  # remove in bracket like (any thing) etc
        # title = re.sub(r'\n|([[].+?[]])|([(].+?[)])|\s(vs|v[.])\s|(:|;|-|"|,|\'|\_|\.|\?)|\(|\)|\[|\]|\{|\}|\s', '', title).lower()
        # title = re.sub(r'\n|([\[({].+?[})\]])|([:;\-"\',!_.?~$@])|\s', '', title)
        return title.strip()
    except: return title


def safe_string(obj):
    try:
        try: return str(obj)
        except UnicodeEncodeError: return obj.encode('utf-8', 'ignore').decode('ascii', 'ignore')
        except: return ""
    except: return obj


def replace_html_codes(txt):
    from html import unescape
    txt = safe_string(txt)
    txt = byteify(txt)
    txt = re.sub("(&#[0-9]+)([^;^0-9]+)", "\\1;\\2", txt)
    txt = unescape(txt)
    txt = txt.replace("&quot;", "\"")
    txt = txt.replace("&amp;", "&")
    return txt


non_str_list = ['olangal.', 'desihome.', 'thiruttuvcd', '.filmlinks4u', '#', '/t.me/',
                'cineview', 'bollyheaven', 'videolinkz', 'moviefk.co', 'goo.gl', '/ads/',
                'imdb.', 'mgid.', 'atemda.', 'movierulz.ht', 'facebook.', 'twitter.',
                'm2pub', 'abcmalayalam', 'india4movie.co', 'embedupload.', 'bit.ly',
                'tamilraja.', 'multiup.', 'filesupload.', 'fileorbs.', 'tamil.ws',
                'insurance-donate.', '.blogspot.', 'yodesi.net', 'desi-tashan.',
                'yomasti.co/ads', 'ads.yodesi', 'mylifeads.', 'yaartv.', '/cdn-cgi/',
                'steepto.', '/movierulztv', '/email-protection', 'oneload.xyz', 'about:',
                'tvnation.me/drive.php?', 'p2p.drivewires', 'tvcine.me', '/ad',
                'tvnation.me/include', 'drivewire.xyz',
                'magnet:']
remove_url = ['.js', 'ads.', '.ads', '/ad', '/ads/']

embed_list = ['cineview', 'bollyheaven', 'videolinkz', 'vidzcode', 'escr.',
              'embedzone', 'embedsr', 'fullmovie-hd', 'links4.pw', 'esr.',
              'embedscr', 'embedrip', 'movembed', 'power4link.us', 'adly.biz',
              'watchmoviesonline4u', 'nobuffer.info', 'yomasti.co', 'hd-rulez.',
              'techking.me', 'onlinemoviesworld.xyz', 'cinebix.com', 'vids.xyz',
              'desihome.', 'loan-', 'filmshowonline.', 'hinditwostop.', 'media.php',
              'hindistoponline', 'telly-news.', 'tellytimes.', 'tellynews.', 'tvcine.',
              'business-', 'businessvoip.', 'toptencar.', 'serialinsurance.',
              'youpdates', 'loanadvisor.', 'tamilray.', 'embedrip.', 'xpressvids.',
              'beststopapne.', 'bestinforoom.', '?trembed=', 'tamilserene.',
              'tvnation.', 'techking.', 'etcscrs.', 'etcsr1.', 'etcrips.',
              'etcsrs.', 'tvpost.cc', 'tellygossips.', 'tvarticles.']

apneembed = ['newstalks.co', 'newstrendz.co', 'newscurrent.co', 'newsdeskroom.co',
             'newsapne.co', 'newshook.co', 'newsbaba.co', 'articlesnewz.com',
             'articlesnew.com', 'webnewsarticles.com']


def get_source_dict(urls, sources, ihost=None, direct=False):
    # log(f'get_source_dict urls: {urls}')
    if isinstance(urls, str): urls = [urls]
    if any([x in str(urls) for x in remove_url]): return sources
    if ihost is None: ihost = host(urls[0])
    # log(f'ihost {ihost} len(urls) {len(urls)} type of urls {type(urls)}')
    for i in range(0, len(urls)):
        # if any(re.findall(r'speed|vkprime|business-loans.pw|bestarticles|tvnation.me', urls[i], re.IGNORECASE)):
        if (re.search(r'speed|vkprime|business-loans.pw|bestarticles|tvnation.me', urls[i], re.I)):
            iurl = get_mod_url(urls[i])
            if iurl: urls[i] = urls[i]
            else: urls[i] = None
        # log(f'In urls[i]: {urls[i]} Out iurl: {iurl}')

    if len(urls) > 1 and (re.search(r'speed|vkprime', link, re.I)):
        j = 0
        for ji in urls:
            j += 1
            sources.append({
                'source': ihost,
                'quality': '720p',
                'language': 'en',
                'info': f'Part:{j}',
                'url': ji,
                'direct': False,
                'debridonly': False})

    if len(urls) > 1: unfo, url = f'All parts: {str(len(urls))}', ' , '.join(urls)
    else: unfo, url = 'All part: Single', urls[0]
    sources.append({
        'source': ihost,
        'quality': '720p',
        'language': 'en',
        'info': unfo,
        'url': url,
        'direct': direct,
        'debridonly': False})
    return sources


def append_headers(headers):
    return '|%s' % '&'.join(['%s=%s' % (key, quote_plus(headers[key])) for key in headers])


def resolve_url(url):
    try:
        if HostedMediaFile(url): return url
        # else: log(f'Resolveurl cannot resolve : {url}')
    except: log(f'resolve_url from iframe not from non_str_list & embed_list  link : {url}\nError: {traceback.print_exc()}')
    return


def get_embed_url(url, headers):
    # log(f'get_embed_url url: {repr(url)}')
    try:
        # log(f'headers: {headers}')
        result = scrapePage(url, headers=headers).text
        # result = read_write_file(file_n='test_imdb_.html', read=False, result=result)
        redirect_url = meta_redirect(result)
        # log(f'redirect_url: {redirect_url}')
        if redirect_url: result = scrapePage(redirect_url, headers=headers).text
        # if redirect_url: result = cfScraper.get(redirect_url, headers=headers).text
        # result += get_packed_data(result)
        vidurl = get_vid_url(result, headers, url)
        if not vidurl: log(f'get_embed_url not returning vidurl: {vidurl} url: {repr(url)}')#\nresult: {result}\n')
        return vidurl
    except Exception as e: log(f'Error {e}: in get_embed_url: {traceback.print_exc()}')
    return


def meta_redirect(content):
    redirect_re = re.compile('<meta[^>]*?[refresh|]*?url=(.*?)["\']', re.IGNORECASE)
    match = redirect_re.search(str(content))
    # log(f'meta_redirect match: {repr(match)}')
    redirect_url = None
    if match: redirect_url = match.groups()[0].strip()
    return redirect_url


def refresh_redirect(url, headers={}):
    refresh = True
    html = ''
    refresh_retry = 0
    while refresh:
        refresh_retry += 1
        # if refresh_retry >= 3: return html
        url = url.replace('/go.', '/')
        if '/?' not in url: url = url.replace('?', '/?')
        # log(f'refresh_redirect url: {url} headers: {headers}')
        result = request(url, headers=headers, output='extended')
        # log(f'result[2]: {result[2]}\nresult[0]: {result[0]}')
        if result[2].get('Refresh'): url = result[2].get('Refresh').split(' ')[-1]
        else:
            html = result[0]
            redirect_url = meta_redirect(html)
            if redirect_url: url = redirect_url
            else: refresh = False
    return str(html)


def get_form_action(url, html, headers):
    try:
        r = re.findall(r'''<form.+?action="([^"]+).+?name='([^']+)'\s*value='([^']+)''', html, re.DOTALL)
        headers.update({'Referer': url})
        if r:
            log(f'get_form_action >>> r: {r}')
            purl, name, value = r[0]
            html = request(purl, post={name: value}, headers=headers)
        else:
            r2 = re.findall(r'''<form.+?action="([^"]+).+?''', html, re.DOTALL)
            if r2:
                log(f'get_form_action >>> r2: {r2}  headers: {headers}')
                purl = r2[0]
                html = request(purl, post=' ', headers=headers)
        return str(html)
    except Exception as e: log(f'Error {e}: in get_form_action: {traceback.print_exc()}')


def get_apneurl(link, headers):
    vidurl = None
    html = refresh_redirect(link, headers)
    html2 = get_form_action(link, html, headers)
    s = re.findall(r"<iframe.+?src='([^']+)", html2, re.I)
    if s:
        vidurl = s[0]
        # log(f'get_apneurl In vidurl  {vidurl}')
        if 'url=' in vidurl: vidurl = vidurl.split('url=')[-1]
        if 'hls' in vidurl: vidurl = vidurl.replace(',.urlset/master.m3u8', '/v.mp4').replace('hls/,', '')
    return vidurl


def get_directurl(link, headers, url):
    refr = urljoin(url, '/')
    vhdr = {'Referer': refr, 'Origin': refr[:-1], 'User-Agent': 'iPad'}
    vidurl = f'Direct_{vidurl}|{urlencode(vhdr)}'
    return vidurl


def get_vid_url(shtml, headers, url):
    try:
        # links = parseDOM(shtml, 'iframe', ret='src')
        # log(f'get_vid_url Total: {len(links)} links1: {links}')
        links = re.findall(r'''<iframe.+?src=['"]([^'"]+)''', shtml, re.I)
        # log(f'get_vid_url Total: {len(links)} links1: {links}')
        links += re.findall(r'"(?:file|src)":"([^"]+m3u8)', shtml, re.I)
        # log(f'get_vid_url Total: {len(links)} links2: {links}')
        for link in links:
            # log(f'get_vid_url link: {link}')
            # if 'player/index.php?' not in link and 'm3u8' in link:
                # headers.update({'Range': 'bytes=0-'})
                # return f'{link}{append_headers(headers)}'
            if (re.search(r'speed|vkprime', link, re.I)): return link
            elif not any([x in link for x in non_str_list]) and not any([x in link for x in embed_list]): return resolve_url(link)
            elif 'flow.' in link: return get_embed_url(link, headers)
            elif 'viralnews.' in link or 'serialghar.me' in link: return viralnews(link, headers)
            elif any([x in link for x in apneembed]): return get_apneurl(link, headers)
            elif 'tvlogy' not in link: return get_directurl(link, headers, url)
    except Exception as e: log(f'Error {e}: in get_vid_url: {traceback.print_exc()}')
    return


def resolve_gen(url, headers={}):
    # log(f'In resolve_gen(url) type of url {type(url)} url: {url}')
    # if not any(re.findall(r'dailymotion|vup|streamtape|vidoza|mixdrop|mystream|doodstream|watchvideo|vkprime|vkspeed', url, re.IGNORECASE)):
    if not (re.search(r'dailymotion|vup|streamtape|vidoza|mixdrop|mystream|doodstream|watchvideo|vkprime|vkspeed', str(url), re.I)):
        if ' , ' in url: urls = url.split(' , ')
        else: urls = [url]
        if not headers: headers = {'User-Agent': agent()}
        # log(f'In len of urls {len(urls)} urls: {urls} headers: {headers}')
        furl = []
        for iurl in urls:
            # log(f'resolve_gen iurl: {iurl}')
            if any([x in iurl for x in apneembed]): url = get_apneurl(iurl, headers)
            elif 'viralnews.' in iurl or 'serialghar.me' in iurl: url = viralnews(url, headers)
            else: url = get_embed_url(iurl, headers)
            if url: furl.append(url)
        # log(f'resolve_gen len furl: {len(furl)} type furl {type(furl)} furl: {furl}')
        if len(furl) > 0: return ' , '.join(furl)
        else: return furl[0]
    if testing: log(f'Out resolve_gen(url)type of url {type(url)} url: {url}')
    return


def viralnews(url, headers):
    # log(f'headers >>> : {headers}')
    try:
        if '/vid/' in url and 'multiup' not in url:
            ehtml = request(url, headers=headers)
        else:
            r = request(url, headers=headers, output='extended')
            url = r[2].get('Refresh').split(' ')[-1]
            ehtml = request(url, headers=headers)
        s = re.search(r'''<iframe.+?src=['"]([^'"]+)''', ehtml, re.I)
        log(f's >>> : {s}')
        if s: return resolve_url(s.group(1))
        else: return
    except Exception as e:
        error(f'{__name__}_ viralnews: ')


def threadwrap(func, extr_iurl, que):
    """
    :useges:
    from Queue import Queue
    que = Queue()
    furls = hindi_sources.threadwrap(hindi_sources.get_embed_url, extr_iurl, que)
    log(f'ilink: {str(que.get())}')
    :param func:
    :param extr_iurl:
    :param que:
    :param furls:

    :return:
    """
    threads = []
    # from Queue import Queue
    import threading
    # que = Queue()
    # log(f'extr_iurl: {extr_iurl}')
    for iurl in extr_iurl:
        # log(f'iurl: {iurl}')
        threads.append(threading.Thread(target=lambda q, arg: q.put(func(iurl)), args=(que, iurl)))
    [i.start() for i in threads]
    [i.join() for i in threads]
    # log(f'threads: {threads}')
    # if str(que.get()) is not None:
    # while not que.empty():
    #     log(f'ilink: {str(que.get())}')
    #     if str(que.get()) is not None:
    #         furls.append(que.get())
    # return furls


def scrape_sources(html, result_blacklist=None, scheme='http', patterns=None, generic_patterns=True):
    if patterns is None: patterns = []

    def __parse_to_list(_html, regex):
        _blacklist = ['.jpg', '.jpeg', '.gif', '.png', '.js', '.css', '.htm', '.html', '.php', '.srt', '.sub', '.xml', '.swf', '.vtt', '.mpd']
        _blacklist = set(_blacklist + result_blacklist)
        streams = []
        labels = []
        for r in re.finditer(regex, _html, re.DOTALL):
            match = r.groupdict()
            stream_url = match['url'].replace('&amp;', '&')
            file_name = urlparse(stream_url[:-1]).path.split('/')[-1] if stream_url.endswith("/") else urlparse(stream_url).path.split('/')[-1]
            label = match.get('label', file_name)
            if label is None: label = file_name
            blocked = not file_name or any(item in file_name.lower() for item in _blacklist) or any(item in label for item in _blacklist)
            if stream_url.startswith('//'): stream_url = scheme + ':' + stream_url
            if '://' not in stream_url or blocked or (stream_url in streams) or any(stream_url == t[1] for t in source_list): continue
            labels.append(label)
            streams.append(stream_url)

        matches = zip(labels, streams) if not isPY3 else list(zip(labels, streams))
        if matches: log('@@@@ Scrape sources |%s| found |%s|' % (regex, matches), __name__)
        return matches #labels, streams

    if result_blacklist is None: result_blacklist = []
    elif isinstance(result_blacklist, str): result_blacklist = [result_blacklist]

    html = html.replace(r"\/", "/")
    html += get_packed_data(html)

    source_list = []
    if generic_patterns or not patterns:
        source_list += __parse_to_list(html, r'''["']?label\s*["']?\s*[:=]\s*["']?(?P<label>[^"',]+)["']?(?:[^}\]]+)["']?\s*file\s*["']?\s*[:=,]?\s*["'](?P<url>[^"']+)''')
        source_list += __parse_to_list(html, r'''["']?\s*(?:file|src)\s*["']?\s*[:=,]?\s*["'](?P<url>[^"']+)(?:[^}>\]]+)["']?\s*label\s*["']?\s*[:=]\s*["']?(?P<label>[^"',]+)''')
        source_list += __parse_to_list(html, r'''video[^><]+src\s*[=:]\s*['"](?P<url>[^'"]+)''')
        source_list += __parse_to_list(html, r'''source\s+src\s*=\s*['"](?P<url>[^'"]+)['"](?:.*?res\s*=\s*['"](?P<label>[^'"]+))?''')
        source_list += __parse_to_list(html, r'''["'](?:file|url)["']\s*[:=]\s*["'](?P<url>[^"']+)''')
        source_list += __parse_to_list(html, r'''param\s+name\s*=\s*"src"\s*value\s*=\s*"(?P<url>[^"]+)''')
        # source_list += __parse_to_list(html, r'''["']?\s*(?:file|url)\s*["']?\s*[:=]\s*["'](?P<url>[^"']+)''')
        # source_list += __parse_to_list(html, '''(?i)<iframe.+?src=["']([^'"]+)''')
    for regex in patterns:
        source_list += __parse_to_list(html, regex)

    source_list = list(set(source_list))
    log(f'@@@@ last source_list [{source_list}]', __name__)
    # source_list = sort_sources_list(source_list)
    return source_list


def get_packed_data(html):
    packed_data = ''
    for match in re.finditer(r'(eval\s*\(function.*?)</script>', html, re.DOTALL | re.I):
        try:
            from openscrapers.modules.jsunpack import unpack
            js_data = unpack(match.group(1))
            js_data = js_data.replace('\\', '')
            packed_data += js_data
        except: pass
    return packed_data


def test_patterns(text, patterns=[]):
    """Given source text and a list of patterns, look for
    matches for each pattern within the text and print
    them to stdout.
    useges:
    test_patterns('abbaaabbbbaaaaa',
              [ 'ab*',     # a followed by zero or more b
                'ab+',     # a followed by one or more b
                'ab?',     # a followed by zero or one b
                'ab{3}',   # a followed by three b
                'ab{2,3}', # a followed by two to three b
                ])
    :return:
    """
    # Show the character positions and input text
    log(''.join(str(i / 10 or ' ') for i in range(len(text))))
    log(''.join(str(i % 10) for i in range(len(text))))
    log(text)

    # Look for each pattern in the text and print the results
    for pattern in patterns:
        log(f'Matching "{pattern}"')
        for match in re.finditer(pattern, text):
            s = match.start()
            e = match.end()
            # log('  %2d : %2d = "%s"' % (s, e - 1, text[s:e]))
            log(f'  {s:2d} : {e - 1:2d} = "{text[s:e]}"')
    return


def regex_patterns():
    """
    Use this regular expression to find all of consecutive whitespaces. Very useful for text editing purposes to cure text
    :return:
    """
    pattern = r'''(?:\s)\s'''
    text = '''330                                                                  
                                                                              
    layout (location = 0) in vec3 Position;                                       
                                                                                  
    void main()    '''
    data = re.sub(pattern, '', text)
    log(f'data: {data.strip()}')
    """
    remove Matches all non-ascii characters including spaces until reaching an ascii character in text
    """
    pattern = r'''[^\x00-\x7F]+\ *(?:[^\x00-\x7F]| )*'''
    text = '''ABCabc~ |	*	Õ×ë
                テ  スト。
                －Τα εννέα πουλιά －
                ＭＩＲＲＯＲ'''
    data = re.sub(pattern, '', text)
    log(f'data: {data.strip()}')
    """
    get text between 2 marker
    as-is will fail with an AttributeError if there are no "AAA" and "ZZZ" in text
    """
    text = 'gfgfdAAA1234ZZZuijjk'
    data = re.search(r"(?<=AAA).*?(?=ZZZ)", text).group(0)
    log(f'data: {data}')
    """Get URL and Lable from:
    value="87"/>
    <td class="line-content">  sources:[{file: 'https://hls2x.vidembed.net/load/hls/YcZQc1FGQYWuj_fAI2F7Pg/1625270480/242436/a8d172bb473a8ba8e2feddc34c478e4b/ep.11.1618011076.m3u8',label: 'hls P','type' : 'hls'}],</td>
    </tr>
    """
    result = """value="87"/>
    <td class="line-content">  sources:[{file: 'https://hls2x.vidembed.net/load/hls/YcZQc1FGQYWuj_fAI2F7Pg/1625270480/242436/a8d172bb473a8ba8e2feddc34c478e4b/ep.11.1618011076.m3u8',label: 'hls P','type' : 'hls'}],</td>
    </tr>"""
    data = re.search(r'''["']?\s*(?:file|src)\s*["']?\s*[:=,]?\s*["'](?P<url>[^"']+)(?:[^}>\]]+)["']?\s*label\s*["']?\s*[:=]\s*["']?(?P<label>[^"',]+)''', result)
    log(f'data: {data.group("url")}')
    log(f'data: {data.group("label")}')
    """It will remove all the control characters"""
    text = "Saina\xa0(2021)"
    # result = re.sub(r'[^\x00-\x7f]', '', text)
    result = re.sub(pattern, '', text)
    log(result)
    """clean title from (Season 1|Season 2|S01|S02)"""
    text = "suite Season 1|F.B.I. Season 2|S01|S02"
    result = re.sub(r'([Ss]eason) \d{1,2}|[Ss]\d{1,2}', '', text)
    log(result)
    """Removing Digits from a String"""
    text = "The film Pulp Fiction was released in year 1994"
    result = re.sub(r"\d", "", text)
    log(result) # The film Pulp Fiction was released in year
    """Removing Alphabet Letters from a String"""
    text = "The film Pulp Fiction was released in year 1994"
    result = re.sub(r"[a-z]", "", text, flags=re.I)
    log(result) # 1994
    """Removing Word Characters"""
    text = "The film, '@Pulp Fiction' was ? released in % $ year 1994."
    result = re.sub(r"\w", "", text, flags=re.I)
    log(result) # , '@ '  ?   % $  .
    """Removing Non-Word Characters"""
    text = "The film, '@Pulp Fiction' was ? released in % $ year 1994."
    result = re.sub(r"\W", "", text, flags=re.I)
    log(result) # ThefilmPulpFictionwasreleasedinyear1994
    """Grouping Multiple Patterns"""
    text = "The film, '@Pulp Fiction' was ? released _ in % $ year 1994."
    result = re.sub(r"[,@\'?\.$%_]", "", text, flags=re.I)
    log(result) # The film Pulp Fiction was  released  in   year 1994
    """Removing Multiple Spaces"""
    text = "The film      Pulp Fiction      was released in   year 1994."
    result = re.sub(r"\s+", " ", text, flags=re.I)
    log(result) # The film Pulp Fiction was released in year 1994.
    """Removing Spaces from Start and End"""
    text = "         The film Pulp Fiction was released in year 1994"
    result = re.sub(r"^\s+", "", text)
    log(result)
    """"remove space at the end of the string"""
    text = "The film Pulp Fiction was released in year 1994      "
    result = re.sub(r"\s+$", "", text)
    log(result) # The film Pulp Fiction was released in year 1994
    """Removing a Single Character"""
    text = "The film Pulp Fiction     s was b released in year 1994"
    result = re.sub(r"\s+[a-zA-Z]\s+", " ", text)
    log(result) # The film Pulp Fiction was released in year 1994
    """Splitting a String"""
    text = "The film      Pulp   Fiction was released in year 1994      "
    result = re.split(r"\s+", text)
    log(result) # ['The', 'film', 'Pulp', 'Fiction', 'was', 'released', 'in', 'year', '1994', '']
    text = "The film, Pulp Fiction, was released in year 1994"
    result = re.split(r"\,", text)
    log(result) # ['The film', ' Pulp Fiction', ' was released in year 1994']
    """Finding All Instances"""
    text = "I want to buy a mobile between 200 and 400 euros"
    result = re.findall(r"\d+", text)
    log(result) # ['200', '400']
    """"""


def extractJS(data, function=False, variable=False, match=False, evaluate=False, values=False):
    log("")
    scripts = parseDOM(data, "script")
    if len(scripts) == 0:
        log("Couldn't find any script tags. Assuming javascript file was given.")
        scripts = [data]

    lst = []
    log("Extracting", 0)
    for script in scripts:
        tmp_lst = []
        if function:
            tmp_lst = re.compile(r'\(.*?\).*?;', re.M | re.S).findall(script)
            # tmp_lst = re.compile(function + r'\(.*?\).*?;', re.M | re.S).findall(script)
        elif variable:
            # tmp_lst = re.compile(variable.replace("[", r"\[").replace("]", r"\]") + '[ ]+=.*?;', re.M | re.S).findall(script)
            # log("script: " + repr(script), 0)
            tmp_lst = re.compile(r'var.*?=.*?(.+)[,;]{1}', re.M | re.S).findall(script)
            # log('tmp_lst: ' + repr(tmp_lst))
            # log("????tmp_lst: " + repr(tmp_lst), 0)
        else:
            tmp_lst = [script]
        if len(tmp_lst) > 0:
            log(f"Found: {repr(tmp_lst)}", 0)
            lst += tmp_lst
        else:
            log(f"Found nothing on: {script}", 0)

    lst = [i for i in lst if i != u''] # remove empty item from list
    test = range(0, len(lst))
    log(f"lst: {lst}")

    # test.reverse()
    for i in test:
        if match and lst[i].find(match) == -1:
            log(f"Removing item: {repr(lst[i])}", 0)
            del lst[i]
        else:
            log(f"Cleaning item: {repr(lst[i])}", 0)
            if lst[i][0] == u"\n":
                lst[i] == lst[i][1:]
            if lst[i][len(lst) - 1] == u"\n":
                lst[i] == lst[i][:len(lst) - 2]
            lst[i] = lst[i].strip()

    if values or evaluate:
        for i in range(0, len(lst)):
            log(f"Getting values {lst[i]}")
            if function:
                if evaluate:  # include the ( ) for evaluation
                    data = re.compile(r"(\(.*?\))", re.M | re.S).findall(lst[i])
                else:
                    data = re.compile(r"\((.*?)\)", re.M | re.S).findall(lst[i])
            elif variable:
                tlst = re.compile(variable + r".*?=.*?;", re.M | re.S).findall(lst[i])
                data = []
                for tmp in tlst:  # This breaks for some stuff. "ad_tag": "http://ad-emea.doubleclick.net/N4061/pfadx/com.ytpwatch.entertainment/main_563326'' # ends early, must end with }
                    cont_char = tmp[0]
                    cont_char = tmp[tmp.find("=") + 1:].strip()
                    cont_char = cont_char[0]
                    if cont_char in "'\"":
                        log(f"Using {cont_char} as quotation mark", 1)
                        tmp = tmp[tmp.find(cont_char) + 1:tmp.rfind(cont_char)]
                    else:
                        log("No quotation mark found", 1)
                        tmp = tmp[tmp.find("=") + 1: tmp.rfind(";")]

                    tmp = tmp.strip()
                    if len(tmp) > 0:
                        data.append(tmp)
            else:
                log("ERROR: Don't know what to extract values from")

            log(f"Values extracted: {repr(data)}")
            if len(data) > 0:
                lst[i] = data[0]

    if evaluate:
        for i in range(0, len(lst)):
            log(f"Evaluating {lst[i]}")
            data = lst[i].strip()
            try:
                try:
                    lst[i] = json.loads(data)
                except:
                    log("Couldn't json.loads, trying eval")
                    lst[i] = eval(data)
            except:
                log(f"Couldn't eval: {repr(data)} from {repr(lst[i])}")

    log(f"Done: {len(lst)}")
    return lst


def find_match(regex, text, index=0):
    results = re.findall(text, regex, flags=re.DOTALL | re.IGNORECASE)
    return results[index]


def ordinal(integer):
    int_to_string = str(integer)
    # log(f'{int_to_string}st')
    if int_to_string == '1' or int_to_string == '-1': return int_to_string + 'st'
    elif int_to_string == '2' or int_to_string == '-2': return int_to_string + 'nd'
    elif int_to_string == '3' or int_to_string == '-3': return int_to_string + 'rd'
    elif int_to_string[-1] == '1' and int_to_string[-2] != '1': return int_to_string + 'st'
    elif int_to_string[-1] == '2' and int_to_string[-2] != '1': return int_to_string + 'nd'
    elif int_to_string[-1] == '3' and int_to_string[-2] != '1': return int_to_string + 'rd'
    else: return int_to_string + 'th'


def daterange(weekend=False):
    weekday_dict = []
    weekend_dict = []
    end_date = datetime.date.today()  # end_date = date(2018, 1, 1)
    start_date = (end_date - datetime.timedelta(.25*365 / 12))  # start_date = date(2017, 1, 1)
    # log(f"start_date : {start_date}")
    for n in range(int((end_date - start_date).days)):
        d = start_date + datetime.timedelta(n)
        weekno = d.weekday()
        # log(f"start_date : {d} :: {weekno}")
        day = d.strftime("%d").lstrip('0')
        day = ordinal(day)
        mont = d.strftime("%B")
        year = d.strftime("%Y")
        if weekend and weekno >= 5: weekend_dict.append(f'{day} {mont} {year}')
        if weekno < 5: weekday_dict.append(f'{day} {mont} {year}')
    if weekend: return weekend_dict
    else: return weekday_dict


def get_hindi_show_episod(tvshowtitle):
    if tvshowtitle in 'the kapil sharma show': episodes = daterange(weekend=True)
    else: episodes = daterange()
    episode = random.choice(episodes)
    serattearm = f'{tvshowtitle}-{episode}'
    return serattearm.lower().replace(' ', '-').replace('.', '-')


def read_write_file(file_n='test.html', read=True, result=''):
    """
    :useged:
    from openscrapers.modules.hindi_sources import read_write_file
    read_write_file('test_%s.html' % hdlr, read=False, result=r)
    :param file_n:
    :param read:
    :param result:
    :return:

    """
    if read:
        with open(file_n, mode='r', encoding='utf-8', errors='ignore') as f:
            result = f.read()
        return result
    else:
        try:
            result = result.replace('\n', ' ').replace('\t', '').replace('&nbsp;', '').replace('&#8211;', '')
            with open(file_n, mode='w', encoding='utf-8') as f:
                f.write(ensure_str(result))
        except: log(f'Error: in read_write_file: {traceback.print_exc()}')


def testing_write_html(url, responce):
    elements = urlparse(url)
    html_filename = f'{elements.netloc or elements.path}.html'
    html_filename = f'JSTesting/{html_filename}'
    log(f'USE html_filename: {html_filename}')
    try: data = responce.text
    except: data = responce
    read_write_file(file_n=html_filename, read=False, result=data)


def find_season_in_title(release_title):
    match = 1
    release_title = re.sub(r'\d{4}', '', release_title)  # remove year from title
    regex_list = [r'.+?(\d{1,2})', r'[sS]eason.+?(\d+)', r'[sS]eason(\d+)', r'[sS](\d+)', r'[cC]hapter.+?(\d+)']
    for item in regex_list:
        try:
            match = re.search(item, release_title)
            if match:
                match = int(str(match.group(1)).lstrip('0'))
                break
            else: match = 1
        except: pass
    return match


def urlRewrite(url):
    # "https://vkprime.com/embed-7pws6soif1cn.html"
    # "https://vkspeed.com/embed-nji2heqsr6y4.html"
    url_dics = [{'host': 'vkprime.php', 'url': 'http://vkprime.com/embed-%s.html'},
                {'host': 'vkspeed.php', 'url': 'http://vkspeed.com/embed-%s.html'},
                {'host': 'speed.php', 'url': 'http://vkspeed.com/embed-%s-600x380.html'}]
    try:
        videoID = getVideoID(url)
        for i in url_dics:
            try:
                if re.compile(i['host']).findall(url)[0]: return i['url'] % videoID
            except: pass
        return url
    except: return url


def findvid_url(text: str):
    """
    :type text: str
    """
    _regexs = [r'(?:iframe|source).+?(?:src)=(?:\"|\')(.+?)(?:\"|\')',
               r'(?:data-video|data-src|data-href)=(?:\"|\')(.+?)(?:\"|\')',
               r'(?:file|source|src)(?:\:)\s*(?:\"|\')(.+?)(?:\"|\')',
               r"<iframe.+?src='([^']+)",
               r'"(?:file|src)":"([^"]+m3u8)']
    links = []
    if not text: return
    for _regex in _regexs:
        try:
            # if re.search(_regex, text, flags=re.DOTALL | re.IGNORECASE):
            items = re.compile(_regex, flags=re.DOTALL | re.I).findall(text)
            # log(f'_regex: {_regex} items: {items}')
            if items:
                for link in items:
                    link = "https:" + link if not link.startswith('http') else link
                    if link in links: continue
                    if any([x in link for x in remove_url]): continue
                    links.append(link)
        except: log(f'Error: {traceback.print_exc()}')
    return links


# if __name__ == '__main__':
#     url = 'https://go.newstrendz.co/sony2?e=1156355&h=4nosaeswohsamrahslipakeht|Referer=https%3A%2F%2Fwatchapne.co'
#     # itemurl = random.choice(Sources)
#     text = scrapePage(url).text
#     print(f'url: {findvid_url(text)}')
