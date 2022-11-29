# -*- coding: utf-8 -*-

import re
import traceback
from string import printable

from modules.kodi_utils import translate_path, logger, addon_fanart, addon_icon
from openscrapers.modules.client import scrapePage, request, agent, requests


exctract_date = re.compile(r'(\d{1,2}[th|st|nd|rd]* [Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|August|Sep|September|Oct|October|Nov|November|Dec|December]* \d{2,4})')
# exctract_date = re.compile(r'(?:\d{1,2}[-/th|st|nd|rd\s]*)?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?[a-z\s,.]*(?:\d{1,2}[-/th|st|nd|rd)\s,]*)+(?:\d{2,4})+')
exctract_episod = re.compile(r'Episode \d{1,2}')
season_data = re.compile(r'[sS]eason.+?(\d+)|[sS]eason(\d+)|[sS](\d+)')
# month_comp = re.compile(r'[Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|August|Sep|September|Oct|October|Nov|November|Dec|December]')


def get_episode_date(name, title=''):
    # name = unescape(text)
    # logger(f"ep_name In: {name}")
    episode_name = xname = ''
    if 'watch online' in name.lower(): xname = name.replace(title, '').replace('Watch Online', '').replace('-', '').replace('  ', ' ')
    try:
        episode_name = exctract_date.findall(xname)[0]
        episode_name = re.sub(r"(\w)([A-Z])", r"\1 \2", episode_name)
    except:
        episode_name = exctract_episod.findall(xname)
    if type(episode_name) is list:
        try: episode_name = episode_name[0]
        except: episode_name = ''
    if episode_name == '' and 'watch online' in name.lower():
        episode_name = name.replace(title, '').replace('Watch Online', '').replace('-', '').replace('  ', ' ')
        episode_name = re.sub(r"(\w)([A-Z])", r"\1 \2", episode_name)
        # logger(f'{episode_name}')
    # logger(f"ep_name Out: {episode_name}")
    # episode_name = episode_name.title()
    return episode_name.strip()


monthdict = {
    'January': '01',
    'February': '02',
    'March': '03',
    'April': '04',
    'May': '05',
    'June': '06',
    'July': '07',
    'August': '08',
    'September': '09',
    'October': '10',
    'November': '11',
    'December': '12'}


def get_int_epi(episode):
    if episode_int := re.search(
        r'(\d{1,2}(st|nd|rd|th))(.*?)(\d{2,4})', episode
    ):
        episode_int = episode_int.group()
        month = monthdict.get(episode_int.split(' ')[1])
        try:
            d = re.search(r'^\d+(st|nd|rd|th)', episode).group()
            day = re.sub(r"(st|nd|rd|th)", "", d)
            day = day.rjust(2, '0')
            # day = re.search(r'\d{2}', episode).group()
            year = re.search(r'\d{4}$', episode).group()
        except: day, year = '0', '0'
        season = day if month is None else f'{month}{day}'
        # logger(f'{season}, {year}')
        return season, year
    else:
        epis_no = re.search(r'\d{1,2}', episode)
        epis_no = epis_no.group() if epis_no else 0
        # logger(f'day: {epis_no}')
        return epis_no, 0


def find_season_in_title(release_title):
    match = 1
    release_title = re.sub(r'\d{4}', '', release_title)  # remove year from title
    regex_list = [r'.+?(\d{1,2})', r'[sS]eason.+?(\d+)', r'[sS]eason(\d+)', r'[sS](\d+)', r'[cC]hapter.+?(\d+)']
    for item in regex_list:
        try:
            match = re.search(item, release_title)
            if match:
                match = int(str(match[1]).lstrip('0'))
                break
            else: match = 1
                    # logger(f'not match: {item}')
        except: pass
    return match


def string_date_to_num(string):
    if date_str := re.search(exctract_date, string):
        date_str = date_str.group()
        month = monthdict.get(date_str.split(' ')[1])
        d = re.search(r'^\d+(st|nd|rd|th)', date_str).group()
        day = re.sub("(st|nd|rd|th)", "", d)
        year = re.search(r'\d{4}$', date_str).group()
        return f"{year}-{month:0>2}-{day:0>2}"
    else:
        return "2022-01-01"


def keepclean_title(title, episod=False):
    if title is None: return
    episode_data = re.compile(r'[Ee]pisodes.+?(\d+)|[Ee]p (\d+)|[Ee](\d+)')
    # ansi_pattern = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
    ansi_pattern = re.compile(r'[^\x00-\x7f]')
    try:
        if ':' in title: title = title.split(':')[0]
        if not episod:
            title = re.sub(exctract_date, '', title)  # remove date like 18th April 2021
            title = re.sub(episode_data, '', title)  # remove episod 12 or [Ee]p 1 etc
        title = re.sub(season_data, '', title)  # remove [Ss]eason 12 or [sS]1 etc
        title = re.sub(ansi_pattern, '', title)  # remove ansi_pattern
        title = re.sub(r'&#(\d+);', '', title)
        title = re.sub(r'(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
        title = title.replace('&quot;', '\"').replace('&amp;', '&')
        title = re.sub(r'([:;\-"\',!_.?~$@])', '', title)  # remove all characters in bracket
        title = re.sub(r'\<[^>]*\>|\([^>]*\)', '', title) # remove like this <anything> or (any thing)
        # title = re.sub(r'\([^>]*\)', '', title)  # remove in bracket like (anything) etc
        # title = re.sub(r'\n|([[].+?[]])|([(].+?[)])|\s(vs|v[.])\s|(:|;|-|"|,|\'|\_|\.|\?)|\(|\)|\[|\]|\{|\}|\s', '', title).lower()
        # title = re.sub(r'\n|([\[({].+?[})\]])|([:;\-"\',!_.?~$@])|\s', '', title)
        title = title.replace('  ', ' ').replace('-', '').replace('...', '')
        return title.strip()
    except: return title.strip()


def multiple_replace(dict, text):
    """

    :type dict: object
    dict = {
        "&amp;": "&",
        "&quot;": '"',
        "&apos;": "\'",
        "&#8217;": "\'",
        "&#8211;": "",
        "&gt;": ">",
        "&lt;": "<", }
    """
    # Create a regular expression  from the dictionary keys
    regex = re.compile(f'({"|".join(map(re.escape, dict.keys()))})')
    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)


def wrigtht_json(file_path, data):
    # file_path = translate_path(file_path)
    with open(file_path, mode='w', encoding='utf-8') as f:
        f.write(data)


def strip_non_ascii_and_unprintable(text):
    try:
        result = ''.join(char for char in text if char in printable)
        return result.encode('ascii', errors='ignore').decode('ascii', errors='ignore')
    except: return str(text)


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
                f.write(result)
        except: logger(f'error: {traceback.print_exc()}')


def convert_time_str_to_seconds(timestr):
    # pattern = r'\d{1,2}:\d{2}:\d{2}'
    # logger(re.findall(pattern, timestr))
    if re.findall(r'\d{1,2}:\d{2}:\d{2}', timestr): timestr = timestr
    elif re.findall(r'\d{2}:\d{2}', timestr): timestr = f"00:{timestr}"
    ftr = [3600, 60, 1]
    return sum(a*b for a, b in zip(ftr, map(int, timestr.split(':'))))


def removeNonAscii(s):
    return "".join(filter(lambda x: ord(x) < 128, s))


def string_escape(s, encoding='utf-8'):
    return s.encode('latin1', 'backslashreplace').decode('unicode-escape')
    # return (s.encode('latin1')         # To bytes, required by 'unicode-escape'
    #          .decode('unicode-escape') # Perform the actual octal-escaping decode
    #          .encode('latin1')         # 1:1 mapping back to bytes
    #          .decode(encoding))        # Decode original encoding


def get_by_id(dict_list, expid=False):
    """
    :param dict_list:
    :param expid:
    :return: dict list with key service is False
    """
    return [item for item in dict_list if item['service'] == expid]


def _get_timefrom_timestamp(timestamp):
    from datetime import datetime
    return datetime.utcfromtimestamp(timestamp)
