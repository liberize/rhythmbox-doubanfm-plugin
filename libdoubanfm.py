#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2008-2012 Sun Ning <classicning@gmail.com>
# Copyright (C) 2012 Yu Shijun <yushijun110@gmail.com>
# Copyright (C) 2012 Liu Guyue <watermelonlh@gmail.com>
# Copyright (C) 2013 liberize <liberize@gmail.com>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import urllib, httplib, json, re, random, contextlib, thread
from Cookie import SimpleCookie
from gi.repository import GLib

__all__ = ['DoubanFM', 'DoubanLoginException', 'DoubanTrack']

class DoubanTrack(object):
	def __init__(self, **data):
		self.props = {}
		for name in data:
			self.props[name] = data[name]

	def get_start_value(self):
		return "%sg%sg0" % (self.sid, self.ssid)

	def get_uri(self):
		return "http://douban.fm/?start=%s&cid=0" % (self.get_start_value())

	def __getattr__(self, name):
		if name in self.props:
			return self.props[name]
		else:
			return None

class DoubanLoginException(Exception):
	def __init__(self, **kwargs):
		self.data = kwargs


class DoubanFM(object):
	def __init__ (self, player, username, password):
		"""
		initialize a douban.fm session
		* username - the user's email on douban.com
		* password - the user's password on douban.com
		"""

		self.uid = None
		self.dbcl2 = None
		self.bid = None
		self.channel = 0
		self.lock = thread.allocate_lock()
		self.player = player
		self.username = username
		self.password = password

	def __load_channels(self):
		f = urllib.urlopen('http://www.douban.com/j/app/radio/channels')
		# f = urllib.urlopen('http://www.douban.com/j/app/radio/channels?version=100&app_name=radio_desktop_win')
		data = f.read()
		f.close()
		channels = json.loads(data)
		self.channels = {}
		# Red Heart
		# self.channels[-3] = 'Red Heart'
		self.channels[-3] = '红心兆赫'
		# Personal Radio High
		# self.channels[-4] = 'Personal Radio High'
		# Personal Radio Easy
		# self.channels[-5] = 'Personal Radio Easy'
		for channel in channels['channels']:
			self.channels[channel['channel_id']] = channel['name']

	def login(self, captcha_id, captcha_solution, callback):
		"""
		login to douban, get the session token
		"""
		try:
			if self.bid is None:
				self.__get_login_data()
			login_form = {'source':'simple', 'form_email':self.username,
				'form_password':self.password}
			if captcha_id is not None:
				login_form['captcha-id'] = captcha_id
				login_form['captcha-solution'] = captcha_solution
			data = urllib.urlencode(login_form)
			content_type = "application/x-www-form-urlencoded"
			cookie = 'bid="%s"' % self.bid
			headers = {"Content-Type":content_type, "Cookie": cookie}

			with contextlib.closing(httplib.HTTPSConnection("www.douban.com")) as conn:
				conn.request("POST", "/accounts/login", data, headers)
				r1 = conn.getresponse()
				resultCookie = SimpleCookie(r1.getheader('Set-Cookie'))

				if not resultCookie.has_key('dbcl2'):
					data = {}
					redir = r1.getheader('location')
					if redir:
						redir_page = urllib.urlopen(redir).read()
						captcha_data = self.__check_login_captcha(redir_page)
						data['captcha_id'] = captcha_data
					raise DoubanLoginException(**data)

				dbcl2 = resultCookie['dbcl2'].value
				if dbcl2 is not None and len(dbcl2) > 0:
					self.dbcl2 = dbcl2
					uid = self.dbcl2.split(':')[0]
					self.uid = uid

		except Exception as e:
			GLib.idle_add(callback, e)
		else:
			self.__load_channels()
			GLib.idle_add(callback, None)

	def __check_login_captcha(self, webpage):
		captcha_re = re.compile(r'captcha\?id=([\w\d]+?)&amp;')
		finder = captcha_re.search(webpage)
		return finder.group(1) if finder else None

	def __get_login_data(self):
		conn = httplib.HTTPConnection("www.douban.com")
		conn.request("GET", "/")
		resp = conn.getresponse()
		cookie = resp.getheader('Set-Cookie')
		cookie = SimpleCookie(cookie)
		conn.close()
		if not cookie.has_key('bid'):
			raise DoubanLoginException()
		else:
			self.bid = cookie['bid'].value
			return self.bid

	def __format_list(self, sidlist, withtag=True):
		"""
		format sidlist
		* withtag - determine whether sidlist has tag
		"""
		if sidlist is None or len(sidlist) == 0:
			return ''
		elif withtag:
			return '|'.join(['%s:%s' % s for s in sidlist])
		else:
			return '|'.join([str(s) for s in sidlist])

	def __get_default_params (self, typename=None):
		"""
		default request parameters, for override
		"""
		params = {}
		for i in ['aid', 'channel', 'du', 'h', 'r', 'rest', 'sid', 'type', 'uid']:
			params[i] = ''

		params['r'] = random.random()
		params['uid'] = self.uid
		params['channel'] = self.channel
		params['pb'] = 64
		try:
			params['pt'] = self.player.get_playing_time()[1]
		except:
			pass
		params['from'] = 'mainsite'
		
		if typename is not None:
			params['type'] = typename
		return params

	def __remote_fm(self, params, start=None):
		"""
		io with douban.fm
		"""
		data = urllib.urlencode(params)
		if start is not None:
			cookie = 'dbcl2="%s"; bid="%s"; start="%s"' % (self.dbcl2, self.bid, start)
		else:
			cookie = 'dbcl2="%s"; bid="%s"' % (self.dbcl2, self.bid)
		header = {"Cookie": cookie}
		with contextlib.closing(httplib.HTTPConnection("douban.fm")) as conn:
			conn.request('GET', "/j/mine/playlist?"+data, None, header)
			result = conn.getresponse().read()
			return result

	def json_to_douban_tracks(self, item):
		return DoubanTrack(**item)

	def new_playlist(self, history, callback):
		"""
		retrieve a new playlist
		* history - history song ids. optional.
		"""
		if self.lock.acquire(0):
			params = self.__get_default_params('n')
			params['h'] = self.__format_list(history)

			results = self.__remote_fm(params)
			GLib.idle_add(callback, map(self.json_to_douban_tracks, json.loads(results)['song']))
			self.lock.release()

	def del_song(self, sid, aid, rest, callback):
		"""
		delete a song from your playlist
		* sid - song id
		* aid - album id
		* rest - rest song ids in current playlist
		"""
		if self.lock.acquire(0):
			params = self.__get_default_params('b')
			params['sid'] = sid
			params['aid'] = aid
			params['rest'] = self.__format_list(rest, False)

			results = self.__remote_fm(params)
			GLib.idle_add(callback, map(self.json_to_douban_tracks, json.loads(results)['song']))
			self.lock.release()

	def fav_song(self, sid, aid):
		"""
		mark a song as favorite
		* sid - song id
		* aid - album id
		"""
		params = self.__get_default_params('r')
		params['sid'] = sid
		params['aid'] = aid

		self.__remote_fm(params)
		# ignore the response

	def unfav_song(self, sid, aid):
		"""
		unmark a favorite song
		* sid - song id
		* aid - album id
		"""
		params = self.__get_default_params('u')
		params['sid'] = sid
		params['aid'] = aid

		self.__remote_fm(params)

	def skip_song(self, sid, aid, history, callback):
		"""
		skip a song, tell douban that you have skipped the song.
		* sid - song id
		* aid - album id
		* history - your playlist history (played songs and skipped songs)
		"""
		if self.lock.acquire(0):
			params = self.__get_default_params('s')
			params['h'] = self.__format_list(history)
			params['sid'] = sid
			params['aid'] = aid

			results = self.__remote_fm(params)
			GLib.idle_add(callback, map(self.json_to_douban_tracks, json.loads(results)['song']))
			self.lock.release()

	def played_song(self, sid, aid):
		"""
		tell douban that you have finished a song
		* sid - song id
		* aid - album id
		"""
		params = self.__get_default_params('e')
		params['sid'] = sid
		params['aid'] = aid

		self.__remote_fm(params)

	def played_list(self, sid, history, callback):
		"""
		request more playlist items
		* history - your playlist history(played songs and skipped songs)
		"""
		if self.lock.acquire(0):
			params = self.__get_default_params('p')
			params['h'] = self.__format_list(history)
			params['sid'] = sid

			results = self.__remote_fm(params)
			GLib.idle_add(callback, map(self.json_to_douban_tracks, json.loads(results)['song']))
			self.lock.release()
