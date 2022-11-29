# -*- coding: utf-8 -*-
import json
import re
import traceback

from urllib.parse import quote_plus, urljoin


try:
    from indexers.hindi.live_client import scrapePage, requests, find_season_in_title, keepclean_title
    from caches.h_cache import metacache
    from modules.kodi_utils import logger, item_next
except:
    import os, sys

    file = os.path.realpath(__file__)
    sys.path.append(os.path.join(os.path.dirname(file), "modules"))
    from live_client import scrapePage, requests, find_season_in_title, keepclean_title, read_write_file
    from h_cache import metacache
    from modules.utils import logger

    item_next = ''

from modules.dom_parser import parseDOM
from modules.utils import replace_html_codes


def gettmdb_id(mediatype, title, year, studio):
    return (
        f'{title.lower()}|{year}'
        if mediatype == 'movie'
        else f'{studio}|{title.lower()}'
    )


def fetch_meta(mediatype, title, tmdb_id, homepage, studio='Hindi', poster='hindi_movies.png', plot='', genre=[], year=2022, cast=[], imdb_id='', rating=5.0):
    # title_tm = keepclean_title(title)
    # tmdb_id = gettmdb_id(mediatype, title, year, studio)
    meta, fanarttv_data, changed_artwork = metacache.get(mediatype, 'tmdb_id', tmdb_id)
    # logger(f'shows desirulez meta: {str(meta)}')
    if meta is None:
        imdbdata = {}
        if not plot and re.search('desi-serials|playdesi', str(homepage), re.I):
            plot, rating, genre = get_plot_tvshow(homepage)
        meta = populet_dict(mediatype=mediatype, title=title, homepage=homepage, studio=studio, poster=poster, tmdb_id=tmdb_id, imdb_id=imdb_id, plot=plot, genre=genre, year=year, cast=cast, rating=rating)
        if imdbdata := get_datajson_imdb(meta):
            logger(f'imdb_id imdbdata: {imdbdata}')
            meta = meta_merge_update(meta, imdbdata)
        # metacache.set(mediatype, 'tmdb_id', meta)
        set_meta(mediatype, meta)
    return meta


def uniquify(string):
    """
    Remove duplicates
    :param string: 'Comedy, Drama, Biography, Drama, Sport'
    :return: 'Comedy, Biography, Drama, Sport'
    """
    output = []
    # seen = set()
    # for word in string.split(','):
    #     if word not in seen:
    #         output.append(word.strip())
    #         seen.add(word)
    # logger(seen)
    [output.append(n.strip()) for n in string.split(',') if n.strip() not in output]
    return ', '.join(output)


def meta_merge_update(meta, imdbdata):
    # logger(f'meta_merge_update meta: {meta}\n imdbdata: {imdbdata}')
    try:
        if isinstance(meta['genre'], list) and isinstance(imdbdata['genre'], list):
            genre = meta['genre'] + imdbdata['genre']
            if len(genre) > 1: genre = list(set(genre))
            meta.update({'genre': genre})
    except: logger(f'shows desirulez Error: {traceback.print_exc()}')
    if meta['plot'] == '' and imdbdata['plot'] != '': meta.update({'plot': imdbdata['plot']})
    if 'hindi_' in meta['poster'] and imdbdata['poster'] != '': meta.update({'poster': imdbdata['poster']})
    if imdbdata['duration']: meta.update({'duration': imdbdata['duration']})
    if imdbdata['mpaa']: meta.update({'mpaa': imdbdata['mpaa']})
    if imdbdata['imdb_id']: meta.update({'imdb_id': imdbdata['imdb_id']})
    if imdbdata['year']: meta.update({'year': imdbdata['year']})
    if imdbdata['rating']: meta.update({'rating': imdbdata['rating']})
    if imdbdata['episodes'] != 0: meta.update({'episodes': imdbdata['episodes']})
    if imdbdata['seasons'] != 0: meta.update({'seasons': imdbdata['seasons']})
    return meta


def populet_dict(mediatype, title, homepage, studio, poster, tmdb_id, imdb_id, plot, genre, year, cast, rating):
    """
    :useges
    meta = populet_dict(mediatype='movie', title=title, year=year,
                        studio=ch_name, plot='', fanart=imgurl,
                        genre='', tvshowtitle=None, imdb_id=imdb)
    :param mediatype:
    :param title:
    :param studio:
    :param homepage:
    :param poster:
    :param tmdb_id:
    :param plot:
    :param year:
    :param genre:
    :param cast:
    :param imdb_id:
    :param rating:
    :return: dict
    """
    if imdb_id == '': imdb_id = tmdb_id
    try:
        if 'addons\\plugin.video.infinite' in poster:
            special_path = 'special://home/addons'
            poster = f"{special_path}{poster.split('addons')[1]}"
            poster = poster.replace('\\', '/')
    except: logger(f"homepath not found: {traceback.print_exc()}")
    if cast is None: cast = [{'role': '', 'name': '', 'thumbnail': ''}]
    if rating is None: rating = 4
    plot = replace_html_codes(plot)
    plot = plot.replace('\\n', ' ').replace('\\u2009', ' ').replace("\\'", "'").replace('\\r', '').strip()
    if isinstance(studio, str): studio = studio.split(',')
    if not genre: genre = []
    if isinstance(genre, str):
        genre = replace_html_codes(genre)
        genre = genre.split(',')
    fgenre = []
    for genre in genre:
        genre = genre.replace('<span data-sheets-value="{"1"', '')
        genre = replace_html_codes(genre)
        fgenre.append(genre.strip())
    if not fgenre:
        fgenre = ['movie'] if mediatype == 'movie' else ['tv']
    if len(fgenre) > 1: fgenre = list(set(fgenre))  #remove duplicate items from list
    dic_meta = {'mediatype': mediatype,
                'year': year,
                'plot': plot,
                'title': title,
                'studio': studio,
                'poster': poster,
                'homepage': homepage,
                'genre': fgenre,  #['Animation, Music, Documentary']
                'cast': cast,
                'tmdb_id': tmdb_id,
                'imdb_id': imdb_id,
                'rating': rating,
                'clearlogo': '', 'trailer': '',
                'votes': 50, 'tagline': '', 'director': [],
                'writer': [], 'episodes': 0, 'seasons': 0,
                'extra_info': {'status': '', 'collection_id': ''}}
    if mediatype == 'movie':
        dic_meta |= {'tvdb_id': 'None', 'duration': 5400, 'mpaa': 'R'}
    else:
        season = find_season_in_title(title)
        dic_meta |= {
            'tvdb_id': imdb_id,
            'duration': 1320,
            'mpaa': 'TV-MA',
            'season': season,
            'episodes': '1',
            'seasons': '1',
            'episode': 1,
            'tvshowtitle': title,
        }


    return dic_meta


def getimdbid(meta):
    title = meta['title']
    year = meta['year']
    title = keepclean_title(title)
    if imdb_id := imdbid(title):
        meta.update({'imdb_id': imdb_id})
        return meta
    # title = re.sub(r'\<[^>]*\>|\([^>]*\)', '', title)  # remove like this <anything> or (any thing)
    # title = re.sub(r'[sS]eason.+?(\d+)|[sS]eason(\d+)|[sS](\d+)', '', title)
    if meta['mediatype'] == 'movie': search_url = f'https://www.imdb.com/find?q={quote_plus(title)}&s=tt&ttype=ft&countries=in&adult=include'
    else: search_url = f'https://www.imdb.com/find?q={quote_plus(title)}&s=tt&ttype=tv&countries=in'
    # if mediatype == 'movie': search_url = f'https://www.imdb.com/search/title/?title={quote_plus(title)}&title_type=feature,tv_movie,documentary,short&countries=in&adult=include'
    # else: search_url = f'https://www.imdb.com/search/title/?title={quote_plus(title)}&title_type=tv_series,tv_episode,tv_special,tv_miniseries,documentary,tv_short&countries=in&adult=include'
    logger(f'search_url: {search_url}')
    try: html = requests.get(search_url).text
    except: return meta
    if scripts := parseDOM(html, 'script', attrs={'id': '__NEXT_DATA__'}):
        try:
            item_meta = json.loads(scripts[0])
            # logger(f'item_meta1: {item_meta}')
            item_metas = item_meta["props"]["pageProps"]["titleResults"]
            # logger(f'item_metas: {item_metas}')
            for item in item_metas["results"]:
                # logger(f'item: {item}')
                id_title = keepclean_title(item["titleNameText"])
                id_year = (item["titleReleaseText"])#.replace(' ', '')
                id_year = re.sub(r'[^\x00-\x7f]', r'', id_year) # remove all non-ASCII characters
                if '-' in id_year: id_year = id_year.split('-')[0]
                title = re.sub(r'\d{1,2}', '', title)
                # logger(f'title: {repr(title)} id_title: {repr(id_title)} year: {repr(year)} id_year: {repr(id_year)}')
                try:
                    if title in id_title:
                        # logger(f'item: {item["titleNameText"]}')
                        meta.update({'title': id_title, 'year': int(id_year), 'imdb_id': item["id"]})
                        break
                except: pass
        except: logger(f'Error: {traceback.print_exc()}')
    return meta


def get_datajson_imdb(metadict):
    oimdb_id = metadict['imdb_id']
    if not oimdb_id.startswith('tt'): metadict = getimdbid(metadict)
    oimdb_id = metadict['imdb_id']
    if not oimdb_id.startswith('tt'): return
    url = f'https://www.imdb.com/title/{oimdb_id}/'
    logger(f'for : {metadict["title"]} data may b on url: {url}')
    result = scrapePage(url).text
    # result = read_write_file(file_n='www.imdb.com.html')
    # metadict = {'title': title, 'year': year, 'rating': 5.0, 'plot': '', 'imdb_id': oimdb_id, 'mpaa': cmpaa, 'duration': cduration, 'genre': [], 'poster': 'hindi_movies.png', 'episodes': 0, 'seasons': 0}
    try:
        scripts = parseDOM(result, 'script', attrs={'id': '__NEXT_DATA__'})
        item_meta = json.loads(scripts[0])
        item_meta1 = item_meta["props"]["pageProps"]["aboveTheFoldData"]
        # logger(f'item_meta1: {item_meta1}')
        try:
            if year := item_meta1['releaseYear']['year']:
                metadict.update({'year': year})
        except: pass
        try:
            if ratings := item_meta1['ratingsSummary']['aggregateRating']:
                metadict.update({'rating': ratings})
        except: pass
        try:
            rgen = item_meta1['genres']['genres']
            # genres = ', '.join(str(x['text']) for x in rgen if x != '')
            genres = [str(x['text']) for x in rgen if x != '']
            metadict.update({'genre': genres})

            plot = item_meta1['plot']['plotText']['plainText']
            if plot := replace_html_codes(plot):
                metadict.update({'plot': plot})
        except: pass
        try:
            if certf := item_meta1['certificate']['rating']:
                metadict.update({'mpaa': certf})
        except: pass
        item_meta2 = item_meta["props"]["pageProps"]["mainColumnData"]
        # logger(f'item_meta2: {item_meta2}')
        try:
            if runtime := item_meta2['runtime']['seconds']:
                metadict.update({'duration': runtime})
        except: pass
        try:
            if poster := item_meta2['titleMainImages']['edges'][0]['node'][
                'url'
            ]:
                metadict.update({'poster': poster})
        except: pass
        try:
            episodes = item_meta2['episodes']['episodes']['total']
            seasons = item_meta2['episodes']['seasons']
            seasons = ', '.join(str(x['number']) for x in seasons if str(x) != '')  # seasons = [x['number'] for x in seasons if x != '']
            if episodes and seasons: metadict.update({'episodes': episodes, 'seasons': seasons})
        except: pass
        if ctitle := item_meta1['titleText']['text']:
            metadict.update({'title': ctitle})
    except:
        logger(f"get_datajson_imdb Error: {traceback.print_exc()}")
        items = parseDOM(result, 'div', attrs={'class': 'ipc-page-content-container.+?'})
        try:
            duration_wrapper = parseDOM(items, 'ul', attrs={'class': '.+?TitleBlockMetaDat.+?'})
            duration = parseDOM(duration_wrapper, 'li', attrs={'class': 'ipc-inline-list__item'})
            duration = duration[1] if metadict['mediatype'] == 'movie' else duration[2]
            dur = duration.replace('<!-- -->', '')
            if duration := get_sec_string(dur):
                metadict.update({'duration': duration})
        except: pass
        try:
            poster = parseDOM(items, 'img', attrs={'class': '.+?ipc-image.+?'}, ret='src')[0]
            if '/nopicture/' in poster: poster = '0'
            poster = re.sub(r'(?:_SX|_SY|_UX|_UY|_CR|_AL)(?:\d+|_).+?\.', '_SX500.', poster)
            if poster := replace_html_codes(poster):
                metadict.update({'poster': poster})
        except: pass
        try:
            # genresplot_wrapper = parseDOM(items, 'div', attrs={'class': '.+?GenresAndPlot__ContentParent.+?'})
            # logger(f'Total: {len(genresplot_wrapper)} duration_wrapper: {genresplot_wrapper}')
            genres_wrapper = parseDOM(items, 'a', attrs={'class': '.+?GenresAndPlot__GenreChip.+?'})
            if genre := [
                item.replace(
                    '<span class="ipc-chip__text" role="presentation">', ''
                ).replace('</span>', '')
                for item in genres_wrapper
                if item
            ]:
                metadict.update({'genre': genre})
        except: pass
        try:
            plot_wrapper = parseDOM(items, 'p', attrs={'class': '.+?GenresAndPlot__Plot.+?'})
            plot = parseDOM(plot_wrapper, 'span', attrs={'class': 'GenresAndPlot__TextContainerBreakpoint.+?'})[0]
            if plot := span_clening(plot):
                metadict.update({'plot': plot})
        except: pass
        try:
            rating_wrapper = parseDOM(items, 'div', attrs={'class': 'AggregateRatingButton__ContentWrap.+?'})
            if rating := parseDOM(
                rating_wrapper,
                'span',
                attrs={'class': 'AggregateRatingButton__RatingScore.+?'},
            )[0]:
                metadict.update({'rating': rating})
        except: pass
        try:
            mpaa_wrapper = parseDOM(items, 'div', attrs={'class': 'UserRatingButton.+?'})
            mpaa = parseDOM(mpaa_wrapper, 'div', attrs={'data-testid': 'hero-rating-bar.+?'})
            mpaa = mpaa[0].strip()
            if mpaa == 'Rate': pass
            elif mpaa: metadict.update({'mpaa': mpaa})
        except: pass
        try:
            title_wrapper = parseDOM(items, 'div', attrs={'class': 'TitleBlock__TitleContainer.+?'})
            if title := parseDOM(
                title_wrapper,
                'h1',
                attrs={'class': 'TitleHeader__TitleText.+?'},
            )[0]:
                metadict.update({'title': title})
        except: pass
        try:
            year_wrapper = parseDOM(items, 'span', attrs={'class': 'TitleBlockMetaData__ListItemText.+?'})
            try: year = re.search(r'\d{4}', year_wrapper).group()
            except: year = 2023
            if year: metadict.update({'year': year})
        except: pass
            # metadict.update({'title': title, 'year': year, 'rating': rating, 'plot': plot, 'mpaa': mpaa, 'duration': duration, 'genre': genres, 'poster': poster})
    # logger(f'>>> {metadict}')
    return metadict


def imdbid(title):
    imdb_id = None
    if title == 'war': imdb_id = 'tt7430722'
    elif title == 'line of descent': imdb_id = 'tt2257284'
    elif title == 'ishq aaj kal ': imdb_id = 'tt11199474'
    elif title == 'is she raju': imdb_id = 'tt9861220'
    elif title == 'good newwz': imdb_id = 'tt8504014'
    elif title == 'bhoot part one: The Haunted Ship': imdb_id = 'tt10463030'
    elif title == 'gandi baat': imdb_id = 'tt8228316'
    elif title == 'meera mathur': imdb_id = 'tt14941996'
    elif title == 'haseen dillruba': imdb_id = 'tt11027830'
    elif title == 'kem chho': imdb_id = 'tt11569584'
    return imdb_id


def get_sec_string(str_time):
    min_str = re.compile(r'(\d+)[m|min]')
    hrs_str = re.compile(r'(\d+)h')
    hrs_s = min_s = 0
    hrs_s = re.findall(hrs_str, str_time)
    if hrs_s: hrs_s = int(hrs_s[0]) * 60 * 60
    min_s = re.findall(min_str, str_time)
    if min_s: min_s = int(min_s[0]) * 60
    return hrs_s + min_s


def span_clening(span_text):
    span_text = span_text.rsplit('<span>', 1)[0].strip()
    span_text = re.sub('<.+?>|</.+?>', '', span_text)
    span_text = re.sub('\xa0', ' ', span_text)
    span_text = re.sub('See all certifications', '', span_text)
    # if '...' in span_text: span_text = span_text.split('...')[0]
    if 'add a plot' not in span_text.lower():
        span_text = replace_html_codes(span_text)
        # span_text = unescape(span_text)
        span_text.strip().replace('\\n', '')
    else: span_text = ''
    return span_text


def get_duplic(links_list):
    # links_list = [{'title': 'Anwar Ka Ajab Kissa','tmdb_id': 'Anwar Ka Ajab Kissa|2013'}, {'title': 'Anwar Ka Ajab Kissa','tmdb_id': 'Anwar Ka Ajab Kissa|2020'}, {'title': 'Ardhangini','tmdb_id': 'Ardhangini|1959'}, {'title': "Class Of '83",'tmdb_id': "Class Of '83|2020"}, {'title': 'Class Of 83','tmdb_id': 'Class Of 83|2020'}, {'title': 'Julie','tmdb_id': 'Julie|1975'}, {'title': 'Julie','tmdb_id': 'Julie|Season 1'} ]
    # logger(f"strating len: {len(links_list)}")
    uniqueValues = []
    duplicateValues = []
    duplicatedict = []
    for d in links_list:
        if d["title"].lower() not in uniqueValues: uniqueValues.append(d["title"].lower())
        else:
            duplicateValues.append(d["title"])
            duplicatedict.append(d)
    # logger(f"List of Duplicate values in Dictionary: {duplicateValues} \n {duplicatedict}")
    return duplicateValues


def analyze_imdbid(href):
    """Return an imdbID from a URL.
    useges:
    movieID=analyze_imdbid(x.get('link') or '')
    """
    re_imdbid = re.compile(r'(title/tt|name/nm|company/co|user/ur)([0-9]+)')
    if not href: return None
    match = re_imdbid.search(href)
    return str(match[2]) if match else None


def get_plot_tvshow(show_url=None):
    episo_page = scrapePage(show_url).text
    # episo_page = read_write_file(file_n='www.desi-serials.cc.html')
    # logger(f"episo_page: {episo_page}")
    result1 = parseDOM(episo_page, "div", attrs={"class": "main-content col-lg-9"})
    result1 += parseDOM(episo_page, "div", attrs={"class": "blog-posts posts-large posts-container"})
    # logger(f"result1: {result1}")
    # ## for overview <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    plot = ''
    genres = []
    rating = 5.0

    result = parseDOM(result1, "div", attrs={"id": "content"})
    # logger(f"result: {result[0]}")
    p = parseDOM(result, 'div', attrs={"class": "page-content"})
    if p := parseDOM(p, 'div', attrs={"class": "page-content"}):
        title_overview = re.findall(r'<p>(.+?)</p>', str(p))
        # logger(f"title_overview: {title_overview}")
        try: plot = title_overview[0].replace('<br/><br/>', '').replace('\\n', '').strip()
        except: pass
        # logger(f"plot: {plot}")
        try:
            rest_ofp = title_overview[1].replace('<br/><br/>', '').replace('\\n', '').strip()
            # logger(f"rating: {rest_ofp}")
            rating = re.findall(r'Show Rating: </span>\s+(.+?)/.+? <p>', rest_ofp)[0]
            # logger(f"rating: {rating}")
            genres = re.findall(r'Genre: </span>\s+(.+?)$', rest_ofp)  #[0]
            # logger(f"plot: {plot}\nrating: {rating}, genre: {genre}")
        except: pass
    else:
        # logger(f'result:  {result}')
        try: plot = re.findall(r'loading="lazy" \/><\/div>(.*?)<p>.+?<span', str(result), re.M)[0].strip()
        except: pass
        try:
            genress = re.findall(r'<span.+?font-weight:bold">(.+?)<\/span>', str(result), re.M)  #[0]
            for genre in genress:
                if 'on:' in genre: genre = genre.split(':')[1].strip()
                if genre: genres.append(genre)
                # genre = genre.replace('Show is Aired on:', '').strip()
        except: pass
    # logger(f"genre: {genre} plot: {plot}")

    # if type(genre) is list: genre = ', '.join(x.strip() for x in genre if x != '')
    # genre = genre.replace('.', '').replace(' :', ',').replace('&#8211;', ' ').replace('&#8230;', '').strip()
    plot = replace_html_codes(plot)
    # plot = f'{genre}\n{plot}'
    return plot, rating, genres


def get_movies(params):
    # logger(f'from : get_movies params: {params}')
    desirule_url = "https://www.desirulez.cc:443"
    non_str_list = ['+', 'season', 'episode']
    url = params['url']
    ch_name = params['ch_name']
    # iconImage = params['iconImage']
    pg_no = params['pg_no']
    movies = results = next_p = []
    if movies_page := scrapePage(url):
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
            url = url if url.startswith(desirule_url) else urljoin(desirule_url, url)
            if title and all(x not in title for x in non_str_list):
                title = keepclean_title(title)
                tmdb_id = gettmdb_id('movie', title, year, None)
                meta = fetch_meta(mediatype='movie', title=title, tmdb_id=tmdb_id, homepage=url, year=year)
                movies.append({'year': year, 'ch_name': ch_name, 'url': url, 'tmdb_id': tmdb_id, 'meta': meta, 'pg_no': pg_no, 'title': title})
        except: logger(f"desirulez get_movies {traceback.print_exc()}")

    if next_p:
        next_p_url = parseDOM(next_p, "a", attrs={"rel": "next"}, ret="href")[0]
        url = next_p_url.split("?")[0] if "?" in next_p_url else next_p_url
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
    if movies_page := scrapePage(m_url):
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


def get_tv_shows_desitelly(params):
    # logger(f'from : get_tv_shows_desitelly params: {params}')
    base_url = params['url']
    ch_name = params['ch_name']
    iconImage = params['iconImage']
    shows = results = []
    if show_page := scrapePage(base_url):
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


def get_meta_from_db(type):
    metas = metacache.get_all_data(type, 'metadata', 1000)
    # metas = metacache.get_all_data('tvshow', 'metadata', 500)
    # # logger(metas)
    metalist = []
    for meta in metas:
        result = eval(meta)
        metalist.append(result)
        # logger(result.get('title'))
    return metalist


def get_duplicate_dict_from_db_and_fixed():
    mediatype = 'tvshow'
    # mediatype = 'movie'
    metalist = get_meta_from_db(mediatype)
    keyValList = get_duplic(metalist)
    logger(f"len of keyValList: {len(keyValList)} keyValList: {keyValList}")
    expectedResult = [d for d in metalist if d['title'] in keyValList]
    logger(f"len of expectedResult: {len(expectedResult)} expectedResult: {expectedResult}")
    # expectedResult = []

    newdict = []
    for d1 in expectedResult:
        for d2 in expectedResult:
            if d1["title"] == d2["title"]:
                if d1["plot"] == "" and d2["plot"] != "": d1.update({"plot": d2["plot"], "genre": d2["genre"], "cast": d2["cast"]})
                if d1["year"] == "0000": d1.update({"year": d2["year"]})
                logger(d1["tmdb_id"], d2["tmdb_id"])
            if d1 not in newdict: newdict.append(d1)
    logger(f"final len newdict: {len(newdict)} newdict: {newdict}")
    # newdict = []
    # for i in newdict:
    #     metacache.set(mediatype, 'tmdb_id', i)


def get_non_plot():
    mediatype = 'movie'
    mediatype = 'tvshow'
    metalist = get_meta_from_db(mediatype)
    # metalist = get_meta_from_db('tvshow')
    upd_data = 0
    non_data_list = []
    for d in metalist:
        if 'Awards' in d['title']: continue
        logger(f'\ntitle: {d["title"]} >>>> plot: {d["plot"]}')
        # plot = unescape(d["plot"])
        # logger(f'final data: {plot}')
        # d.update({'plot': plot})
        # logger('')

        if d["genre"] is None or d["genre"] == '' or d["genre"] == ['-'] or d["plot"] is None:
            logger('')
            logger(f"title: {d['title']} genre: {d['genre']} plot: {d['plot']}")
            upd_data += 1
            # if upd_data > 2: break
            logger(d)
            logger(f'init data: {d}')
            imdbdata = get_datajson_imdb(d['title'], d['year'], mediatype)
            logger(f'imdbdata: {imdbdata}')
            if imdbdata: d = meta_merge_update(d, imdbdata)
            logger(f'final data: {d}')
            set_meta(d['mediatype'], d)
            # if d['mediatype'] == 'tvshow': metacache.set('tvshow', 'tmdb_id', d)
            # else: metacache.set('movie', 'tmdb_id', d)
    # logger(non_data_list)


def set_meta(mediatype, meta):
    if mediatype == 'movie': metacache.set('movie', 'tmdb_id', meta)
    else: metacache.set('tvshow', 'tmdb_id', meta)


def getmeta_n_update_common():
    # mediatype = 'tvshow'
    mediatype = 'movie'
    metalist = get_meta_from_db(mediatype)
    upd_data = 0
    ansi_pattern = re.compile(r'[^\x00-\x7f]')
    items = non_data_list = []
    new_search = False
    for d in metalist:
        # if 'House Of Cards' in d['title']: d.update({'imdb_id': 'tt1856010'})
        # elif 'Elite' in d['title']: d.update({'imdb_id': 'tt7134908'})
        # elif 'Aashram' in d['title']: d.update({'imdb_id': 'tt12805346'})
        # elif 'Hai Taubba' in d['title']: d.update({'imdb_id': 'tt14564446'})
        # elif 'Dil Hi Toh Hai' in d['title']: d.update({'imdb_id': 'tt8523124'})
        # elif 'Bang Baang' in d['title']: d.update({'imdb_id': 'tt13155198'})
        # elif 'Modi Cm To Pm' in d['title']: d.update({'imdb_id': 'tt10094918'})
        # elif 'What Are The Odds' in d['title']: d.update({'imdb_id': 'tt12327140'})
        # elif 'Gullak' in d['title']: d.update({'imdb_id': 'tt10530900'})
        # elif 'Super Dancer' in d['title']: d.update({'imdb_id': 'tt10370866'})
        # elif 'Sa Re Ga Ma Pa' in d['title']: d.update({'imdb_id': 'tt1755864'})
        # elif 'Hawkeye' in d['title']: d.update({'genre': 'Action'})

        if d["genre"] is None or d["genre"] == '':
            logger(f"title: {d['title']} genre: {d['genre']}  imdb_id: {d['imdb_id']}")
            new_search = True
        if d["plot"] is None or d["plot"] == ':  :-':
            logger(f"title: {d['title']} plot: {d['plot']}  imdb_id: {d['imdb_id']}")
            new_search = True
        if d["duration"] is None or d["duration"] == 0:
            logger(f"title: {d['title']} duration: {d['duration']}  imdb_id: {d['imdb_id']}")
            new_search = True
        # if ':' in d["genre"] or '.' in d["genre"]:
        #     logger(f"title: {d['title']} genre: {d['genre']}")
        #     d.update({'genre': d["genre"].replace(' :', ',').replace('.', '')})
        # if '\nPlot:' in d["plot"] or 'Add a Plot' in d["plot"]:
        #     logger(f"title: {d['title']} plot: {d['plot']}")
        #     plot = d["plot"].replace('\nPlot:', '\n:')
        #     d.update({'plot': plot})
        #     if 'Add a Plot' in d["plot"]:
        #         plot = d["plot"].replace('Add a Plot', ':')
        #         d.update({'plot': plot})
        # logger(f"title: {d['title']} genre: {d['genre']}")
        if d['plot']:
            plot = re.sub(ansi_pattern, '', d['plot'])
            plot = plot.replace('&quot;', '\"').replace('&amp;', '&')
            d.update({'plot': plot})
        try: imdb_id = analyze_imdbid(str(d['imdb_id']) or '') # re.search(r'(tt\d*)', str(d['imdb_id'])).group()
        except: imdb_id = None
        if new_search or not imdb_id:
            upd_data += 1
            if upd_data > 15: break
            logger(f"new_search: {new_search} title: {d['title']}  imdb_id : {imdb_id}")
            if imdbdata := get_datajson_imdb(d):
                logger(f'imdb_id imdbdata: {imdbdata}')
                d = meta_merge_update(d, imdbdata)
            # metacache.set(mediatype, 'tmdb_id', d)
            set_meta(mediatype, d)
            new_search = False
            # logger(f" meta: {meta}")
        # genre = uniquify(d["genre"])
        # logger(f" genre: {genre}")
        # d.update({'genre': genre})
        # items += d["genre"].split(',')
        # non_data_list.append(items)
        # set_meta(mediatype, d)


def getmeta_n_update_byid():
    mediatype = 'tvshow'
    #mediatype =  'movie'
    tmdb_id = 'Eros Now|Modi: Journey of a common man'
    imdb_id = 'Eros Now|Modi: Journey of a common man'
    meta, fanarttv_data, changed_artwork = metacache.get(mediatype, 'tmdb_id', tmdb_id)
    n_genre = 'Biography, Drama'
    n_plot = "An inspiring journey of Narendra Modi, from his childhood to his entry into politics."
    year = 2020
    duration = 1320
    rating = 8.0
    mpaa = 'TV-MA'

    plot = f': {n_plot}'
    if not meta["genre"]: meta.update({'genre': n_genre})
    if not meta["plot"]:
        logger(f"title: {meta['title']} plot: {meta['plot']}")
        # meta.update({'plot': plot})
    meta.update({'imdb_id': imdb_id, 'duration': duration, 'rating': rating, 'year': year, 'mpaa': mpaa,
                 'plot': plot, 'genre': n_genre,
                 'poster': 'https://www.desi-serials.cc/wp-content/uploads/2020/11/indian-idol-season-12-300x169.jpg'})
    logger(meta)
    # set_meta(mediatype, meta)


def getmeta_n_check_common():
    # mediatype = 'tvshow'
    mediatype = 'movie'
    metalist = get_meta_from_db(mediatype)
    upd_data = 0
    items = non_data_list = []
    for d in metalist:
        # if d["plot"] is None or d["plot"] == '':
        if 'Awards & Concerts' in d['title']: d.update({'genre': ['tv']})
        elif 'Dhadkan Zindagi Ki' in d['title']:
            logger(f"genre:  {d['genre'].replace('&#8211;', '-')}")
            logger(f"plot:  {d['plot'].replace('&#8211;', '-')}")
            d.update({'genre': d['genre'].replace('&#8211;', '-'), 'plot': d['plot'].replace('&#8211;', '-')})

        if not d['genre']:
            logger('')
            logger(f"title: {d['title']} genre: {d['genre']}")
            logger(f"duration: {d['duration']} mpaa: {d['mpaa']} rating: {d['rating']} genre: {d['genre']}")
            if 'Ek Thi Begum' in d['title']: d.update({'genre': ['Crime', 'Drama']})
            elif 'Hawkeye' in d['title']: d.update({'genre': ['Action']})
            elif 'Aashram' in d['title']: d.update({'genre': ['Crime']})
            elif 'Bandish Bandits' in d['title']: d.update({'mediatype': 'movie', 'year': '2020', 'plot': 'Indian classical singer Radhe and pop star Tamanna. Despite their contrasting personalities, the two "set out together on a journey of self-discovery to see if opposites, though they might attract, can also adapt and go the long haul.', 'title': 'Bandish Bandits', 'studio': ['Hindi'], 'poster': 'hindi_movies.png', 'homepage': 'https://www.desirulez.cc:443/showthread.php/1344300-Bandish-Bandits-(2020)-WEB-DL-Watch-Online-Download-ESubs', 'genre': ['Music', 'Drama'], 'cast': [], 'tmdb_id': 'bandish bandits|2020', 'imdb_id': 'tt9814458', 'rating': 5.0, 'clearlogo': '', 'trailer': '', 'votes': 50, 'tagline': '', 'director': [], 'writer': [], 'episodes': 0, 'seasons': 0, 'extra_info': {'status': '', 'collection_id': ''}, 'tvdb_id': 'None', 'duration': 5400, 'mpaa': 'R'})
            else: d.update({'genre': ['tv']})
        if mediatype == "movie":
            if 'Not Rated' in d["mpaa"] or 'TV-MA' in d["mpaa"] or 'MA' in d["mpaa"]:
                # logger(f"title: {d['title']} genre: {d['mpaa']}")
                d.update({'mpaa': 'R'})
            if 'TV-14' in d["mpaa"]:
                # logger(f"title: {d['title']} genre: {d['mpaa']}")
                d.update({'mpaa': 'PG-13'})
            if not d['genre']:
                d.update({'genre': ['movie']})
        else:
            if 'Not Rated' in d["mpaa"] or 'MA-17' in d["mpaa"] or 'MA' in d["mpaa"]:
                # logger(f"title: {d['title']} genre: {d['mpaa']}")
                d.update({'mpaa': 'TV-MA'})
            if 'TV-14' in d["mpaa"]:
                # logger(f"title: {d['title']} genre: {d['mpaa']}")
                d.update({'mpaa': 'TV-PG'})
        if not d['rating']:
            logger(f'>>>> d: {d}')
            d.update({'rating': 4.0})
        set_meta(mediatype, d)


def get_tmdb_id_common():
    mediatype = 'tvshow'
    mediatype = 'movie'
    # metalist = get_meta_from_db(mediatype)

    from h_cache import MetaCache
    old_metacache = MetaCache('list_data/hindi_metacache.db')
    old_metas = old_metacache.get_all_data(mediatype, 'metadata', 2000)
    # metas = metacache.get_all_data('tvshow', 'metadata', 500)
    # # logger(metas)
    old_meta_list = []
    for meta in old_metas:
        result = eval(meta)
        old_meta_list.append(result)

    upd_data = 0
    items = non_data_list = []
    for d in old_meta_list:
        meta, fanarttv_data, changed_artwork = metacache.get(mediatype, 'tmdb_id', d['tmdb_id'])
        if not meta:
            logger(f'd: {d["tmdb_id"]}')
            items.append(d)
        # chnname, tmdb_id = d['tmdb_id'].split('|')
        # if mediatype != 'movie':
        #     namecl = keepclean_title(tmdb_id, mediatype)
        #     newtmdb = "{}|{}".format(chnname, namecl.lower())
        # else:
        #     namecl = keepclean_title(chnname, mediatype)
        #     newtmdb = "{}|{}".format(namecl.lower(), tmdb_id)
        # logger(f"title: {d['tmdb_id']} tmdb_id: {newtmdb}")
        # # if d["plot"] is None or d["plot"] == '':
        # d.update({'tmdb_id': newtmdb})
        # set_meta(mediatype, d)
        # if mediatype == 'movie': old_metacache.set('movie', 'tmdb_id', d)
        # else: old_metacache.set('tvshow', 'tmdb_id', d)
    logger(items)


def seach_omdbapi(title, year, mediatype='movie', oimdb_id=None):
    title = re.sub(r'\<[^>]*\>|\([^>]*\)', '', title)  # remove like this <anything> or (any thing)
    title = re.sub(r'[sS]eason.+?(\d+)|[sS]eason(\d+)|[sS](\d+)', '', title)
    title = title.strip()
    api_url = f'http://www.omdbapi.com/?apikey=dd7e2fc7&s={quote_plus(title)}'
    logger(f'url: {api_url}')
    from modules.client import requests
    session = requests.Session()
    result = session.get(api_url, timeout=20.0)
    item_meta = json.loads(result.text)
    # logger(f'result: {result.text}')
    # rt = '{"Search":[{"Title":"Guns of Banaras","Year":"2020","imdbID":"tt11573410","Type":"movie","Poster":"https://m.media-amazon.com/images/M/MV5BMDM2NjlhNWYtY2Q2MS00ZDgyLWEyMGItMDY3NzAzOTczZWE2XkEyXkFqcGdeQXVyMTA5NzIyMDY5._V1_SX300.jpg"},{"Title":"Banaras","Year":"2006","imdbID":"tt0449189","Type":"movie","Poster":"https://m.media-amazon.com/images/M/MV5BNjI1MjI5ZTUtNTMxMC00MjRkLTg5OWYtOTZkODJmOGUwODg3XkEyXkFqcGdeQXVyODE5NzE3OTE@._V1_SX300.jpg"},{"Title":"Banaras","Year":"2009","imdbID":"tt1638265","Type":"movie","Poster":"https://m.media-amazon.com/images/M/MV5BYjg2NTgyZWYtYjMwYS00YzRjLThkYWEtNmFkM2JmMGQ4MjRkXkEyXkFqcGdeQXVyNDE2MDU0MDA@._V1_SX300.jpg"},{"Title":"Banaras ke Rasiya","Year":"2022","imdbID":"tt18970130","Type":"movie","Poster":"https://m.media-amazon.com/images/M/MV5BMjAwZjJmMTYtNmRhZi00ZjUxLWFiMDEtZGRjYWNlNTFmMzVhXkEyXkFqcGdeQXVyMTExMDk4MzYz._V1_SX300.jpg"},{"Title":"Banaras Me","Year":"2010","imdbID":"tt1670941","Type":"movie","Poster":"https://m.media-amazon.com/images/M/MV5BYThkN2I0ZGItYTY4Ni00YWY1LWIyOTUtZWExNzQzZDYwMzMzXkEyXkFqcGdeQXVyMjMzNzMyNTg@._V1_SX300.jpg"},{"Title":"The Battle of Banaras","Year":"2015","imdbID":"tt3705084","Type":"movie","Poster":"https://m.media-amazon.com/images/M/MV5BYTM4NmU5YmEtYjY1OS00MzljLWI3MDEtYjM3MDE1NzNlOTNkXkEyXkFqcGdeQXVyODE5NzE3OTE@._V1_SX300.jpg"},{"Title":"The Mornings of Banaras","Year":"2016","imdbID":"tt6085762","Type":"movie","Poster":"N/A"},{"Title":"Banaras","Year":"2017","imdbID":"tt7309408","Type":"movie","Poster":"N/A"},{"Title":"Hamar Mission Hamar Banaras","Year":"2018","imdbID":"tt10888680","Type":"movie","Poster":"https://m.media-amazon.com/images/M/MV5BMjNjZmM3ZDYtNDIwMC00ZjcyLTk3MWItMWVjZWE0YjljMzRkXkEyXkFqcGdeQXVyODM5Mzk0MTU@._V1_SX300.jpg"},{"Title":"Banaras Wilderness","Year":"2012","imdbID":"tt12079246","Type":"movie","Poster":"https://m.media-amazon.com/images/M/MV5BMzkwNGY0MTAtMzVlMy00NjQzLWFmMzAtNTY2ZWI1N2I4YWY1XkEyXkFqcGdeQXVyODY2MDY3NDg@._V1_SX300.jpg"}],"totalResults":"11","Response":"True"}'
    # item_meta = json.loads(rt)
    for item in item_meta["Search"]:
        otitle = item['Title']
        logger(f'otitle: {otitle.lower()} year: {item["Year"]} title: {title} year: {year} ')
        if year in str(item) and otitle.lower() == title:
            title = item['Title']
            imdb_id = item['imdbID']
            Poster = item['Poster']
            logger(f'item: {item}')
    return


# if __name__ == "__main__":
#     testing = True
#     metacache.check_database()
#     param = {'ch_name': 'Hindi', 'pg_no': '1', 'url': 'https://desicinemas.tv/movies/'}
#     param1 = {'ch_name': 'Hindi', 'pg_no': '1', 'url': 'http://www.desirulez.cc/forumdisplay.php?f=20'}
#     try:
#         logger(sys.version_info)
#         regul_tv = [{'ch_name': 'Sab TV', 'url': 'https://www.desi-serials.cc/sab-tv-hd/', 'iconImage': None},
#                     {'ch_name': 'Sony', 'url': 'https://www.desi-serials.cc/sony-tv/', 'iconImage': None},
#                     {'ch_name': 'Colors', 'url': 'https://www.desi-serials.cc/color-tv-hd/', 'iconImage': None},
#                     {'ch_name': 'Zee', 'url': 'https://www.desi-serials.cc/zee-tv/', 'iconImage': None},
#                     {'ch_name': 'Star Plus', 'url': 'https://www.desi-serials.cc/star-plus-hdepisodes/', 'iconImage': None}]
#         web_tv = [{'ch_name': 'SonyLiv', 'url': 'https://playdesi.tv/sonyliv/', 'iconImage': None},
#                   {'ch_name': 'Gujarati web series', 'url': 'https://playdesi.tv/gujarati-web-series/', 'iconImage': None},
#                   {'ch_name': 'Voot', 'url': 'https://playdesi.tv/voot/', 'iconImage': None},
#                   {'ch_name': 'Zee5 Web Series', 'url': 'https://playdesi.tv/zee5/', 'iconImage': None},
#                   {'ch_name': 'Mx Player', 'url': 'https://playdesi.tv/mx-player/', 'iconImage': None},
#                   {'ch_name': 'Amazon Prime', 'url': 'https://playdesi.tv/amazon-prime/', 'iconImage': None},
#                   {'ch_name': 'Netflix', 'url': 'https://playdesi.tv/netflix/', 'iconImage': None},
#                   {'ch_name': 'ALT Balaji Web Series', 'url': 'https://playdesi.tv/alt-balaji/', 'iconImage': None},
#                   {'ch_name': 'HotStar Web Series', 'url': 'https://playdesi.tv/hotstar/', 'iconImage': None},
#                   {'ch_name': 'HotStar Quix Web Series', 'url': 'https://playdesi.tv/hot-star-quix/', 'iconImage': None},
#                   {'ch_name': 'Eros Now', 'url': 'https://playdesi.tv/eros-now/', 'iconImage': None}]
#         # >>>>>> for test
#         if testing:
#             chnl = 0
#             param = {'ch_name': 'Sony', 'url': 'https://www.desi-serials.cc/sony-tv/', 'iconImage': None}
#             # getimdbid('banaras', '2022', 'movie')
#             # getmeta_n_update_common()
#             # get_tv_shows_desitelly(param)
#             # meta = {'mediatype': 'tvshow', 'year': 2022, 'plot': 'Naagin 6 is an Indian television serial. This tv serial is based on a drama thriller and this is produced by Ekta Kapoor. This show has been released on Colors TV. This tv serial is set to be released on 30th January 2022.', 'title': 'Naagin 6', 'studio': [
#             #     'Colors'], 'poster': 'https://www.desi-serials.cc/wp-content/uploads/2022/02/Naagin-6-300x169.jpg', 'homepage': 'https://www.desi-serials.cc/watch-online/colors/naagin-6/', 'genre': [], 'cast': [
#             #     'Saturday   Sunday'], 'tmdb_id': 'Colors|naagin 6', 'imdb_id': 'Colors|naagin 6', 'rating': 5.0, 'clearlogo': '', 'trailer': '', 'votes': 50, 'tagline': '', 'director': '', 'writer': '', 'episodes': 0, 'seasons': 0, 'extra_info': {'status': '', 'collection_id': ''}, 'tvdb_id': 'Colors|naagin 6', 'duration': 1320, 'mpaa': 'TV-MA', 'episode': '', 'tvshowtitle': 'Naagin 6'}
#             # imdbdata = {'title': 'Naagin', 'year': 2015, 'rating': 3.3, 'plot': 'A miraculous shape-shifting snake has the power to become a human. She can be anybody she wants: a wife, a seductress, a mistress, a damsel in distress--all in the name of revenge.', 'imdb_id': 'tt5323298', 'mpaa': 'TV-MA', 'duration': 3600, 'genre': [], 'poster': 'https://m.media-amazon.com/images/M/MV5BYTQzNTNiNmMtOWM0Ni00ZGJhLTk3MmUtN2ZkZDgwYjAyOGM2XkEyXkFqcGdeQXVyMTQyMTMwOTk0._V1_.jpg', 'episodes': 362, 'seasons': '1, 2, 3, 4, 5, 6'}
#             # logger(meta_merge_update(meta, imdbdata))
#             meta = {'mediatype': 'tvshow', 'year': 2022, 'plot': 'Appnapan - Badalte Rishton Ka Bandhan is an Indian Romance Drama television series. The series is co-produced by Ekta Kapoor and Shobha Kapoor under their banner Balaji Telefilms. The series stars Cezzane Khan and Rajshree Thakur and is set to premiere in 15 June 2022 on Sony Entertainment Television.', 'title': 'Appnapan  Badalte Rishton Ka Bandhan', 'studio': ['Sony'], 'poster': 'https://www.desi-serials.cc/wp-content/uploads/2022/06/Appnapan-Badalte-Rishton-Ka-Bandhan-300x169.jpg', 'homepage': 'https://www.desi-serials.cc/watch-online/sony-tv/appnapan-badalte-rishton-ka-bandhan/', 'genre': ['Monday  Friday.'], 'cast': [], 'tmdb_id': 'Sony|appnapan  badalte rishton ka bandhan', 'imdb_id': 'Sony|appnapan  badalte rishton ka bandhan', 'rating': 5.0, 'clearlogo': '', 'trailer': '', 'votes': 50, 'tagline': '', 'director': [], 'writer': [], 'episodes': '1', 'seasons': '1', 'extra_info': {'status': '', 'collection_id': ''}, 'tvdb_id': 'Sony|appnapan  badalte rishton ka bandhan', 'duration': 1320, 'mpaa': 'TV-MA', 'season': 1, 'episode': 1, 'tvshowtitle': 'Appnapan  Badalte Rishton Ka Bandhan'}
#             logger(get_datajson_imdb(meta))
#         else:
#             import time
# 
#             selec_tv_ch = [{'ch_name': 'Colors', 'url': 'https://www.desi-serials.cc/color-tv-hd/', 'iconImage': None},
#                            {'ch_name': 'Zee', 'url': 'https://www.desi-serials.cc/zee-tv/', 'iconImage': None}]
#             chnl = 0
#             # for param in web_tv:
#             #     chnl += 1
#             #     # if chnl > 1: break
#             #     get_tv_shows_desitelly(param)
#             #     time.sleep(5)
#             # get_movies(param1)
#             # get_movies_desicinemas(param)
#             # get_non_plot()
#             # get_duplicate_dict_from_db_and_fixed()
#     except Exception as e:
#         logger(f'Error {e}: {traceback.format_exc()}')