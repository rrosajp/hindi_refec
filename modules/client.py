# -*- coding: utf-8 -*-
"""
	OpenScrapers Module
"""

import gzip
import random
from random import choice, randrange
import re
# from sys import version_info
import traceback
from time import sleep, time

import requests
import simplejson as json

from requests import Session, exceptions
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
# from urllib3.exceptions import MaxRetryError, ReadTimeoutError


from openscrapers.modules import cache
from openscrapers.modules.dom_parser import parseDOM
from openscrapers.modules.log_utils import log, error
from openscrapers.modules.utils import byteify, get_headersfrom_url
from http import cookiejar
from html import unescape
from io import BytesIO

from urllib.parse import quote_plus, urlencode, parse_qs, urlparse, urljoin, quote
from urllib.response import addinfourl
from urllib.error import HTTPError, URLError
from urllib.request import build_opener, install_opener, ProxyHandler, Request, urlopen, HTTPHandler, HTTPSHandler, HTTPRedirectHandler, HTTPCookieProcessor
import ssl

UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'
MobileUserAgent = 'Mozilla/5.0 (Android 10; Mobile; rv:83.0) Gecko/83.0 Firefox/83.0'

dnt_headers = {
    'User-Agent': UserAgent,
    'Accept': '*/*',
    'Accept-Encoding': 'identity;q=1, *;q=0',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'DNT': '1'
}


def list_request(doms, query='', scheme='https://'):
	if isinstance(doms, list):
		for i in range(len(doms)):
			dom = random.choice(doms)
			try:
				base_link = scheme + dom if not dom.startswith('http') else dom
				url = urljoin(base_link, query)
				# log(f'list_request i: {i} url: {url}')
				r = requests.get(url, headers={'User-Agent': agent(), 'Referer': base_link}, timeout=7)
				if r.ok:
					#log('list_request chosen base: ' + base_link)
					return r.text, base_link
				raise Exception()
			except Exception:
				doms = [d for d in doms if not d == dom]
				log('list_request failed dom: ' + repr(i) + ' - ' + dom)
				pass
	else:
		base_link = scheme + doms if not doms.startswith('http') else doms
		url = urljoin(base_link, query)
		# log(f'list_request url: {url}')
		r = requests.get(url, headers={'User-Agent': agent(), 'Referer': base_link}, timeout=10)
		if r.ok:
			#log('list_request chosen base: ' + base_link)
			return r.text, base_link
		raise Exception()


def request(url, close=True, redirect=True, proxy=None, post=None, jpost=False, headers={}, mobile=False, XHR=False, limit=None, referer='', cookie=None, compression=True, output='', timeout='30', verifySsl=True, flare=True, ignoreErrors=None):
	if not url: return None
	if url.startswith('//'): url = 'http:' + url
	if post:
		if isinstance(post, dict): post = bytes(urlencode(post), encoding='utf-8')
		elif isinstance(post, str): post = bytes(post, encoding='utf-8')

	try:
		_headers = {}
		if headers: _headers.update(headers)
		url, oheaders = get_headersfrom_url(url)
		if oheaders: _headers.update(oheaders)
		if _headers.get('verifypeer', '') == 'false':
			verifySsl = False
			_headers.pop('verifypeer')

		handlers = []
		if proxy is not None: handlers += [ProxyHandler({'http': '%s' % proxy}), HTTPHandler()]
		if output == 'cookie' or output == 'extended' or close is not True or redirect:
			cookies = cookiejar.LWPCookieJar()
			handlers += [HTTPHandler(), HTTPSHandler(), HTTPCookieProcessor(cookies)]
		if output == 'elapsed': start_time = time() * 1000
		ctx = _get_unverified_context(verifySsl)
		if ctx: handlers += [HTTPSHandler(context=ctx, debuglevel=1)]
		opener = build_opener(*handlers)
		install_opener(opener)

		if 'User-Agent' in _headers: pass
		elif mobile: _headers['User-Agent'] = cache.get(mobileagent, 12)
		else: _headers['User-Agent'] = cache.get(agent, 12)
		if 'Referer' in _headers: pass
		elif referer: _headers['Referer'] = referer
		# if referer: _headers['Referer'] = '%s://%s/' % (urlparse(url).scheme, urlparse(url).netloc)
		if 'Accept-Language' not in _headers: _headers['Accept-Language'] = 'en-US,en'
		if 'Accept' not in _headers: _headers['Accept'] = '*/*'
		if 'X-Requested-With' in _headers: pass
		elif XHR: _headers['X-Requested-With'] = 'XMLHttpRequest'
		if 'Cookie' in _headers: pass
		elif cookie is not None:
			if isinstance(cookie, dict): cookie = '; '.join(['{0}={1}'.format(x, y) for x, y in iter(cookie.items())])
			_headers['Cookie'] = cookie
		if 'Accept-Encoding' in _headers: pass
		elif compression and limit is None: _headers['Accept-Encoding'] = 'gzip'

		if redirect is False:
			class NoRedirectHandler(HTTPRedirectHandler):
				def http_error_302(self, req, fp, code, msg, _headers):
					infourl = addinfourl(fp, _headers, req.get_full_url())
					infourl.code = code
					return infourl

				http_error_300 = http_error_302
				http_error_301 = http_error_302
				http_error_303 = http_error_302
				http_error_307 = http_error_302

			opener = build_opener(NoRedirectHandler())
			install_opener(opener)
			try: del _headers['Referer']
			except: pass

		# url = quote(url, safe=':/')
		req = Request(url, data=post)
		if jpost: req.add_header('Content-Type', 'application/json')
		if limit == '0': req.get_method = lambda: 'HEAD'
		_add_request_header(req, _headers)
		# log(f'sent headers: {req.headers}')

		try: response = opener.open(req, timeout=int(timeout))
		except HTTPError as error_response:  # if HTTPError, using "as response" will be reset after entire Exception code runs and throws error around line 247 as "local variable 'response' referenced before assignment", re-assign it
			response = error_response
			try: ignore = ignoreErrors and (int(response.code) == ignoreErrors or int(response.code) in ignoreErrors)
			except: ignore = False

			if not ignore:
				if response.code in (301, 307, 308, 503, 403):  # 403:Forbidden added 3/3/21 for cloudflare, fails on bad User-Agent
					cf_result = _get_result(response)
					# if not as_bytes:
						# cf_result = cf_result.decode(encoding='utf-8', errors='ignore')
					if flare and 'cloudflare' in str(response.info()).lower():
						log(f'client module calling cfscrape: url={url}')
						try:
							from openscrapers.modules import cfscrape
							if isinstance(post, dict): data = post
							else:
								try: data = parse_qs(post)
								except: data = None
							scraper = cfscrape.CloudScraper()
							# possible bad User-Agent in headers, let cfscrape assign
							if response.code == 403: response = scraper.request(method='GET' if post is None else 'POST', url=url, data=data, timeout=int(timeout))
							else: response = scraper.request(method='GET' if post is None else 'POST', url=url, headers=headers, data=data, timeout=int(timeout))
							result = response.content
							flare = 'cloudflare'  # Used below
							try: cookie = response.request._cookies
							except: cookie = ''
							if response.status_code == 403:  # if cfscrape server still responds with 403
								error(f'from: line# 154 url: {url} cfscrape-Error : ')  # HTTP Error 403: Forbidden
								return response
						except: error(f'from: {__name__} url: {url} cfscrape-Error ')
					elif 'cf-browser-verification' in str(cf_result):
						netloc = '%s://%s' % (urlparse(url).scheme, urlparse(url).netloc)
						ua = _headers['User-Agent']
						cookie = cache.get(cfcookie().get, 168, netloc, ua, timeout)
						_headers['Cookie'] = cookie
						req = Request(url, data=post)
						_add_request_header(req, _headers)
						response = urlopen(req, timeout=int(timeout))
						result = _get_result(response)
					else:
						if ignore is False:
							error(f'line# 177 from: {__name__}  url={url} Error: ')
							return None
				else:
					if ignore is False:
						error(f'line# 181 from: {__name__}  url={url} Error: ')
						return None
					elif ignore is True and response.code in (401, 404, 405):  # no point in continuing after this exception runs with these response.code's
						try: response_headers = dict([(item[0].title(), item[1]) for item in list(response.info().items())])  # behaves differently 18 to 19. 18 I had 3 "Set-Cookie:" it combined all 3 values into 1 key. In 19 only the last keys value was present.
						except:
							error()
							response_headers = response.headers
						return (str(response), str(response.code), response_headers)

		if output == 'cookie':
			if isinstance(cookie, dict): result = '; '.join(['{0}={1}'.format(x, y) for x, y in iter(cookie.items())])
			else: result = cookie
			if close: response.close()
			return result
		elif output == 'elapsed':
			result = (time() * 1000) - start_time
			if close: response.close()
			return int(result)

		elif output == 'geturl':
			result = response.geturl()
			if close: response.close()
			return result
		elif output == 'headers':
			result = response.headers
			if close: response.close()
			return result
		elif output == 'response':
			result = _get_result(response)
			return str(response.code), result
		elif output == 'chunk':
			try: content = int(response.headers['Content-Length'])
			except: content = (2049 * 1024)
			if content < (2048 * 1024): return
			try: result = response.read(16 * 1024)
			except: result = response  # testing
			if close: response.close()
			return result
		elif output == 'file_size':
			try: content = int(response.headers['Content-Length'])
			except: content = '0'
			response.close()
			return content
		if flare != 'cloudflare':
			result = _get_result(response)

		if 'sucuri_cloudproxy_js' in str(result):  # who da fuck?
			su = sucuri().get(result)
			_headers['Cookie'] = su
			req = Request(url, data=post)
			_add_request_header(req, _headers)
			response = urlopen(req, timeout=int(timeout))
			result = _get_result(response)
		if 'Blazingfast.io' in str(result) and 'xhr.open' in str(result):  # who da fuck?
			netloc = '%s://%s' % (urlparse(url).scheme, urlparse(url).netloc)
			ua = _headers['User-Agent']
			_headers['Cookie'] = cache.get(bfcookie().get, 168, netloc, ua, timeout)
			result = _basic_request(url, headers=_headers, post=post, timeout=timeout, limit=limit)
		if output == 'extended':
			try: response_headers = dict([(item[0].title(), item[1]) for item in list(response.info().items())])  # behaves differently 18 to 19. 18 I had 3 "Set-Cookie:" it combined all 3 values into 1 key. In 19 only the last keys value was present.
			except: response_headers = response.headers
			response_url = response.url
			try: response_code = str(response.code)
			except: response_code = str(response.status_code)  # object from CFScrape Requests object.
			try: cookie = '; '.join(['%s=%s' % (i.name, i.value) for i in cookie])
			except: pass
			if close: response.close()
			return (result, response_code, response_headers, _headers, cookie, response_url)
		elif output == 'json':
			result = _get_result(response)
			content = json.loads(result)
			response.close()
			return content
		if close is True: response.close()
		return result
	except Exception as err:
		log(f'line# 257 from: {__name__} Error: {err} {traceback.print_exc()}>> url: {url} _headers: {_headers}')
		return None


def _basic_request(url, headers={}, post=None, timeout='30', limit=None):
	try:
		if post is not None: post = post.encode()
		# url = quote(url, safe=':/')
		request = Request(url, data=post)
		_add_request_header(request, headers)
		response = urlopen(request, timeout=int(timeout))
		return _get_result(response, limit)
	except: log(f'line# 269 from: {__name__} url: {url} Error: {traceback.print_exc()}')


def _add_request_header(_request, headers={}):
	try:
		scheme = urlparse(_request.get_full_url()).scheme
		host = _request.host
		referer = headers.get('Referer', '') or '%s://%s/' % (scheme, host)
		_request.add_unredirected_header('Host', host)
		_request.add_unredirected_header('Referer', referer)
		for key in headers:
			if isinstance(headers[key], dict): continue
			# log(f'type headers[key]: {type(headers[key])} headers[key]: {headers[key]}')
			_request.add_header(key, headers[key])
	except: log(f'from: {__name__} Error: {traceback.print_exc()}')


def _get_result(response, limit=None, ret_code=None):
	try:
		if ret_code: return response.code
		if limit == '0': result = response.read(224 * 1024)
		elif limit: result = response.read(int(limit) * 1024)
		else: result = response.read(5242880)
		encoding = _get_encoding(response)
		if encoding == 'gzip': result = gzip.GzipFile(fileobj=BytesIO(result)).read()
		result = result.decode(encoding='utf-8', errors='ignore')
		return result
	except: log(f'from: {__name__} Error: {traceback.print_exc()}')


def replaceHTMLCodes(txt):
	# Some HTML entities are encoded twice. Decode double.
	return _replaceHTMLCodes(_replaceHTMLCodes(txt))


def _replaceHTMLCodes(txt):
	try:
		if not txt: return ''
		txt = re.sub(r"(&#[0-9]+)([^;^0-9]+)", "\\1;\\2", txt)  # fix html codes with missing semicolon
		txt = unescape(txt)
		txt = txt.replace("&quot;", "\"")
		txt = txt.replace("&amp;", "&")
		txt = txt.replace("&lt;", "<")
		txt = txt.replace("&gt;", ">")
		txt = txt.replace("&apos;", "'")
		txt = txt.replace("&#38;", "&")
		txt = txt.replace("&#39;", "'")
		txt = txt.replace("\\'", "'")
		blacklist = ['\n', '\r', '\t']
		for ch in blacklist:
			txt = txt.replace(ch, '')
		txt = txt.replace("&nbsp;", "")
		txt = txt.replace('&#8230;', '...')
		txt = txt.replace('&#8217;', '\'')
		txt = txt.replace('&#8211;', '-')
		txt = txt.strip()
		return txt
	except:
		error()
		return txt


def cleanHTML(txt):
	txt = re.sub(r'<.+?>|</.+?>|\n', '', txt)
	return _replaceHTMLCodes(_replaceHTMLCodes(txt))


def randomagent():
	BR_VERS = [
		['%s.0' % i for i in range(95, 100)],
		['97.0.4692.71', '97.0.4692.99', '98.0.4758.82', '98.0.4758.102', '99.0.4844.151', '100.0.4896.75', '100.0.4896.88 ', '101.0.4951.41', '101.0.4951.64', '102.0.5005.63'],
		['11.0']]
	WIN_VERS = ['Windows NT 11.0', 'Windows NT 10.0', 'Windows NT 8.1', 'Windows NT 8.0', 'Windows NT 7.0']
	FEATURES = ['; WOW64', '; Win64; IA64', '; Win64; x64', '']
	RAND_UAS = ['Mozilla/5.0 ({win_ver}{feature}; rv:{br_ver}) Gecko/20100101 Firefox/{br_ver}',
				'Mozilla/5.0 ({win_ver}{feature}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{br_ver} Safari/537.36',
				'Mozilla/5.0 ({win_ver}{feature}; Trident/7.0; rv:{br_ver}) like Gecko']  # (compatible, MSIE) removed, dead browser may no longer be compatible and it fails for glodls with "HTTP Error 403: Forbidden"
	index = randrange(len(RAND_UAS))
	return RAND_UAS[index].format(
			win_ver=choice(WIN_VERS),
			feature=choice(FEATURES),
			br_ver=choice(BR_VERS[index]))


def mobileagent(mobile='android'):
	_mobagents = [
		'Mozilla/5.0 (Linux; Android 7.1; vivo 1716 Build/N2G47H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.98 Mobile Safari/537.36',
		'Mozilla/5.0 (Linux; Android 7.0; SM-J710MN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.80 Mobile Safari/537.36',
		'Mozilla/5.0 (Android 10; Mobile; rv:84.0) Gecko/84.0 Firefox/84.0',
		'Mozilla/5.0 (Android 12; Mobile; rv:68.0) Gecko/68.0 Firefox/94.0',
		'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.50 Mobile Safari/537.36',
		'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.50 Mobile Safari/537.36 EdgA/95.0.1020.42',
		'Mozilla/5.0 (Linux; Android 10; SM-G970F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.50 Mobile Safari/537.36 OPR/63.3.3216.58675',
		'Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
		'Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 EdgiOS/95.0.1020.40 Mobile/15E148 Safari/605.1.15',
		'Mozilla/5.0 (iPad; CPU OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
		'Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/96.0.4664.36 Mobile/15E148 Safari/604.1',
		'Mozilla/5.0 (iPad; CPU OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/96.0.4664.36 Mobile/15E148 Safari/604.1',
		'Mozilla/5.0 (iPhone; CPU iPhone OS 13_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Mobile/15E148 Safari/605.1',
		'Mozilla/5.0 (iPad; CPU OS 10_2_1 like Mac OS X) AppleWebKit/602.4.6 (KHTML, like Gecko) Version/10.0 Mobile/14D27 Safari/602.1']

	if mobile == 'android': return choice(_mobagents[:7])
	else: return choice(_mobagents[8:14])


def agent():
	return choice(
			["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
			 "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
			 "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
			 "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0",
			 "Mozilla/5.0 (Macintosh; Intel Mac OS X 12.0; rv:94.0) Gecko/20100101 Firefox/94.0",
			 "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
			 "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
			 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.44",
			 "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/94.0.992.31",
			 "Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 OPR/81.0.4196.31",
			 "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 OPR/81.0.4196.31",
			 "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 OPR/81.0.4196.31"])


class cfcookie:
	def __init__(self):
		self.cookie = None

	def get(self, netloc, ua, timeout):
		from threading import Thread
		threads = []
		for i in list(range(0, 15)):
			threads.append(Thread(target=self.get_cookie, args=(netloc, ua, timeout)))
		[i.start() for i in threads]
		for i in list(range(0, 30)):
			if self.cookie is not None: return self.cookie
			sleep(1)

	def get_cookie(self, netloc, ua, timeout):
		try:
			headers = {'User-Agent': ua}
			req = Request(netloc)
			_add_request_header(req, headers)

			try: response = urlopen(req, timeout=int(timeout))
			except HTTPError as response:
				result = response.read(5242880)
				encoding = _get_encoding(response)
				if encoding == 'gzip': result = gzip.GzipFile(fileobj=BytesIO(result)).read()

			jschl = re.findall(r'name\s*=\s*["\']jschl_vc["\']\s*value\s*=\s*["\'](.+?)["\']/>', result, re.I)[0]
			init = re.findall(r'setTimeout\(function\(\){\s*.*?.*:(.*?)};', result, re.I)[-1]
			builder = re.findall(r"challenge-form\'\);\s*(.*)a.v", result, re.I)[0]
			decryptVal = self.parseJSString(init)
			lines = builder.split(';')

			for line in lines:
				if len(line) > 0 and '=' in line:
					sections = line.split('=')
					line_val = self.parseJSString(sections[1])
					decryptVal = int(eval(str(decryptVal) + sections[0][-1] + str(line_val)))

			answer = decryptVal + len(urlparse(netloc).netloc)
			query = '%s/cdn-cgi/l/chk_jschl?jschl_vc=%s&jschl_answer=%s' % (netloc, jschl, answer)

			if 'type="hidden" name="pass"' in result:
				passval = re.findall(r'name\s*=\s*["\']pass["\']\s*value\s*=\s*["\'](.*?)["\']', result, re.I)[0]
				query = '%s/cdn-cgi/l/chk_jschl?pass=%s&jschl_vc=%s&jschl_answer=%s' % (netloc, quote_plus(passval), jschl, answer)
				sleep(6)
			cookies = cookiejar.LWPCookieJar()
			handlers = [HTTPHandler(), HTTPSHandler(), HTTPCookieProcessor(cookies)]
			opener = build_opener(*handlers)
			opener = install_opener(opener)
			try:
				req = Request(query)
				_add_request_header(req, headers)
				response = urlopen(req, timeout=int(timeout))
			except: pass

			cookie = '; '.join(['%s=%s' % (i.name, i.value) for i in cookies])
			if 'cf_clearance' in cookie: self.cookie = cookie
		except: log('get_cookie-Error: (%s) ' % (traceback.print_exc()), __name__, LOGDEBUG)

	def parseJSString(self, s):
		try:
			offset = 1 if s[0] == '+' else 0
			val = int(eval(s.replace('!+[]', '1').replace('!![]', '1').replace('[]', '0').replace('(', 'str(')[offset:]))
			return val
		except: log('parseJSString-Error: (%s) ' % (traceback.print_exc()), __name__, LOGDEBUG)


class bfcookie:
	def __init__(self):
		self.COOKIE_NAME = 'BLAZINGFAST-WEB-PROTECT'

	def get(self, netloc, ua, timeout):
		try:
			headers = {'User-Agent': ua, 'Referer': netloc}
			result = _basic_request(netloc, headers=headers, timeout=timeout)
			match = re.findall(r'xhr\.open\("GET","([^,]+),', result, re.I)
			if not match: return False
			url_Parts = match[0].split('"')
			url_Parts[1] = '1680'
			url = urljoin(netloc, ''.join(url_Parts))
			match = re.findall(r'rid\s*?=\s*?([0-9a-zA-Z]+)', url_Parts[0])
			if not match: return False
			headers['Cookie'] = 'rcksid=%s' % match[0]
			result = _basic_request(url, headers=headers, timeout=timeout)
			return self.getCookieString(result, headers['Cookie'])
		except: log('bfcookie-Error: (%s) ' % (traceback.print_exc()), __name__, LOGDEBUG)

	# not very robust but lazieness...
	def getCookieString(self, content, rcksid):
		vars = re.findall(r'toNumbers\("([^"]+)"', content)
		value = self._decrypt(vars[2], vars[0], vars[1])
		cookie = '%s=%s;%s' % (self.COOKIE_NAME, value, rcksid)
		return cookie

	def _decrypt(self, msg, key, iv):
		from binascii import unhexlify, hexlify
		from openscrapers.modules import pyaes
		msg = unhexlify(msg)
		key = unhexlify(key)
		iv = unhexlify(iv)
		if len(iv) != 16: return False
		decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, iv))
		plain_text = decrypter.feed(msg)
		plain_text += decrypter.feed()
		f = hexlify(plain_text)
		return f


class sucuri:
	def __init__(self):
		self.cookie = None

	def get(self, result):
		from base64 import b64decode
		try:
			s = re.compile(r"S\s*=\s*'([^']+)").findall(result)[0]
			s = b64decode(s)
			s = s.replace(' ', '')
			s = re.sub(r'String\.fromCharCode\(([^)]+)\)', r'chr(\1)', s)
			s = re.sub(r'\.slice\((\d+),(\d+)\)', r'[\1:\2]', s)
			s = re.sub(r'\.charAt\(([^)]+)\)', r'[\1]', s)
			s = re.sub(r'\.substr\((\d+),(\d+)\)', r'[\1:\1+\2]', s)
			s = re.sub(r';location.reload\(\);', '', s)
			s = re.sub(r'\n', '', s)
			s = re.sub(r'document\.cookie', 'cookie', s)
			cookie = ''
			exec(s)
			self.cookie = re.compile(r'([^=]+)=(.*)').findall(cookie)[0]
			self.cookie = '%s=%s' % (self.cookie[0], self.cookie[1])
			return self.cookie
		except: log('sucuri-Error: (%s) ' % (traceback.print_exc()), __name__, LOGDEBUG)


def cf_responce(url, headers=None, post=None, timeout='20'):
	try:
		from openscrapers.modules import cfscrape
		# url = quote(url, safe=':/')
		headers = get_fheaders(url, headers)
		data = None
		if post:
			if isinstance(post, dict): data = post
			else:
				try: data = parse_qs(post)
				except: pass
		scraper = cfscrape.CloudScraper()
		try: response = scraper.request(method='GET' if post is None else 'POST', url=url, headers=headers, data=data, timeout=int(timeout))
		except: response = scraper.request(method='GET' if post is None else 'POST', url=url, headers=headers, data=data, verify=False, timeout=int(timeout))
		return response
	except: error()


fheaders = {
			'Accept-Language': 'en-US,en',
			'Accept': '*/*',
			'Connection': 'keep-alive',
			# 'Pragma': 'no-cache',
			# 'Cache-Control': 'no-cache',
			'DNT': '1',
			'Upgrade-Insecure-Requests': '1',
			'x-requested-with': 'XMLHttpRequest',
			'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
			'sec-fetch-dest': 'document',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-site': 'cross-site'
			}


def R_Session():
	try:
		session = Session()
		retries = Retry(total=3,  # number of total retries
				connect=2,  # retry once in case we can't connect to url
				read=2,  # retry once in case we can't read the response from url
				redirect=3,  # retry once in case we're redirected by url
				backoff_factor=1,  # The pause between for each retry
				status_forcelist=[429, 500, 502, 503, 504],  # this is a list of statuses to consider to be an error and retry. definitely retry if url is unwell
				method_whitelist=frozenset(['GET', 'POST']))

		session.mount('https://', HTTPAdapter(max_retries=retries))
		session.mount('http://', HTTPAdapter(max_retries=retries))
		# session.headers.update(fheaders)
		# session.headers.update({'User-Agent': agent()})
		return session
	except:
		log(f'R_Session - Exception: {traceback.print_exc()}')
		return None


def get_fheaders(url=None, headers=None):
	if headers: headers.update(headers)
	else: headers = {'User-Agent': agent(), }
	if url and 'Referer' not in headers:
		elements = urlparse(url)
		base = '%s://%s' % (elements.scheme, (elements.netloc or elements.path))
		headers['Referer'] = base
	if 'User-Agent' not in headers: headers['User-Agent'] = agent()
	fheaders.update(headers)
	return fheaders


def _get_encoding(response):
	try:
		try: return response.info().getheader('Content-Encoding')
		except: return response.headers['Content-Encoding']
	except: log(f'From: {__name__} Error: {traceback.print_exc()} ')
	return None


def _get_unverified_context(verifySsl):
	import ssl
	ctx = None
	if not verifySsl:
		ctx = ssl.create_default_context()
		ctx.check_hostname = False
		ctx.verify_mode = ssl.CERT_NONE
		ctx.set_alpn_protocols(['http/1.1'])
	else:
		try:
			from openscrapers.modules.control import get_kodi_certi_file
			ctx = ssl.create_default_context(cafile=get_kodi_certi_file())
			ctx.set_alpn_protocols(['http/1.1'])
		except: pass
	return ctx


def scrapePage(url, referer=None, headers=None, post=None, cookie=None, timeout=20, verify=True):
	try:
		if not url: return
		url = "https:" + url if url.startswith('//') else url
		headers = get_fheaders(url, headers)
		with R_Session() as session:
			session.headers.update(headers)
			if referer and 'Referer' not in session.headers: session.headers.update({'Referer': referer})
			else:
				elements = urlparse(url)
				base = f'{elements.scheme}://{(elements.netloc or elements.path)}'
				session.headers.update({'Referer': base})
			# not tested yet, just placed as an idea reminder.
			if cookie and 'Cookie' not in session.headers: session.headers.update({'Cookie': cookie})
			if 'User-Agent' not in session.headers: session.headers.update({'User-Agent': agent()})
			try:
				if post: response = session.post(url, data=post, timeout=timeout, verify=verify)
				else: response = session.get(url, timeout=timeout, verify=verify)
				response.encoding = 'utf-8'
				# response.raise_for_status()
			except exceptions.SSLError as err:
				log(f'scrapePage SSLError" Error: {err} url: {url}')
				scrapePage(url, headers=headers, post=post, timeout=timeout, verify=False)
			except exceptions.Timeout as err:
				log(f'scrapePage Timeout: Error: {err} url: {url}')
				scrapePage(url, headers=headers, post=post, timeout=timeout + 10, verify=verify)
			except exceptions.ConnectionError as err: log(f'scrapePage ConnectionError: Error: {err} url: {url} session.headers:{session.headers}')
			except exceptions.HTTPError as err: log(f'scrapePage HTTPError: Error: {err} url: {url} session.headers:{session.headers}')
			except exceptions.RequestException as err: log(f'scrapePage RequestException: Error: {err} url: {url} session.headers:{session.headers}')
			except Exception as e: log(f'scrapePage except Exception as e: {e} url: {url}')

		# session_cookies = session.cookies
		# cookies_dictionary = session_cookies.get_dict()
		# log(f'cookies_dictionary: {cookies_dictionary}')
		# log(f'session_headers send: {session.headers}')
		# log(f'response.headers recived: {response.headers}')
		if response.status_code in (301, 307, 308, 503, 403):
			response = cf_responce(url, fheaders)
			# log(f'repr(response) : {repr(response)}')
			if response.status_code > 400:  # if cfscrape server still responds with 403
				log(f'from: line# 640 url: {url} cfscrape-Error : ')  # HTTP Error 403: Forbidden
				return response
		# if testing: testing_write_html(url, response)
		return response
	except Exception:
		error(f'{__name__}_ scrapePage: ')
		return


def get_content(response, encoding=None):
	try:
		content_type = response.headers.get('content-type', '').lower()
		text_content = any(x in content_type for x in ['text', 'json', 'xml', 'mpegurl'])
		if 'charset=' in content_type: encoding = content_type.split('charset=')[-1]
		if encoding is None:
			epatterns = [r'<meta\s+http-equiv="Content-Type"\s+content="(?:.+?);\s+charset=(.+?)"', r'xml\s*version.+encoding="([^"]+)']
			for epattern in epatterns:
				epattern = epattern.encode('utf8')
				r = re.search(epattern, response.content, re.IGNORECASE)
				if r:
					encoding = r.group(1).decode('utf8')
					break
		if encoding is None:
			r = re.search(b'^#EXT', response.content, re.IGNORECASE)
			if r: encoding = 'utf8'
		if encoding is not None: return response.content.decode(encoding, errors='ignore')
		elif text_content and encoding is None: return response.content.decode('latin-1', errors='ignore')
		else: log('Unknown Page Encoding')
	except: error(f'{__name__}_ get_content: ')
	return