#!/usr/bin/env python
#-*- coding: UTF-8 -*-

# Copyright (C) 2013 liberize <liberize@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from gi.repository import GObject, RB, GLib
from login_dialog import LoginDialog
import datetime, thread

SOURCE_NAME = '豆瓣电台'

class DoubanFMSource(RB.BrowserSource):
	__gtype_name__ = 'DoubanFMSource'
	object = GObject.property(type=GObject.Object)	
	
	def __init__(self):
		RB.BrowserSource.__init__(self, name=SOURCE_NAME)

		self.activated = False
		self.db = None
		self.doubanfm = None
		self.songs_map = {}
		self.songs = []
		self.history = []
		self.login_dialog = None
	
	def do_selected(self):
		"""
		do some work when this source is selected.
		"""
		if not self.activated:
			self.activated = True
			self.shell = self.props.shell
			self.plugin = self.props.plugin
			self.player = self.shell.props.shell_player
			self.db = self.shell.props.db
			self.entry_type = self.props.entry_type
		if self.doubanfm == None:
			if self.login_dialog == None:
				self.login_dialog = LoginDialog(self.shell)
				self.login_dialog.connect('login-completed', self.on_login_completed)
			self.login_dialog.login()
		self.plugin.show_sidebar(True)
		
	def do_deselected(self):
		"""
		do some work when this source is deselected.
		"""
		self.plugin.show_sidebar(False)
		
	def on_login_completed(self, dialog, doubanfm):
		"""
		refresh playlist when logged in successfully.
		"""
		self.doubanfm = doubanfm
		self.plugin.change_menu_item_state(True)

	def set_channel(self, channel):
		"""
		set current channel.
		"""
		self.doubanfm.channel = channel
		self.new_playlist()

	def get_song_by_title(self, song_title):
		"""
		get a song by its title.
		"""
		return self.songs_map.get(song_title.decode('utf-8'), None)

	def add_song(self, song):
		"""
		add a new entry for a song.
		"""
		entry = self.db.entry_lookup_by_location(song.url)
		if entry == None:
			entry = RB.RhythmDBEntry.new(self.db, self.entry_type, song.url)
		self.db.entry_set(entry, RB.RhythmDBPropType.TITLE, song.title.encode('utf-8'))
		self.db.entry_set(entry, RB.RhythmDBPropType.ALBUM, song.albumtitle.encode('utf-8'))
		self.db.entry_set(entry, RB.RhythmDBPropType.ARTIST, song.artist.encode('utf-8'))
		self.db.entry_set(entry, RB.RhythmDBPropType.DURATION, song.length)
		if song.rating_avg:
			self.db.entry_set(entry, RB.RhythmDBPropType.RATING, song.rating_avg)
		if song.kbps:
			self.db.entry_set(entry, RB.RhythmDBPropType.BITRATE, int(song.kbps.encode('utf-8')))
		if song.company:
			self.db.entry_set(entry, RB.RhythmDBPropType.GENRE, song.company.encode('utf-8'))
		if song.public_time:
			date = datetime.date(int(song.public_time.encode('utf-8')), 1, 1).toordinal()
			self.db.entry_set(entry, RB.RhythmDBPropType.DATE, date)

	def reset_songs(self, songs):
		"""
		clear and reset all entries.
		"""
		for row in self.props.query_model:
			entry = row[0]
			self.db.entry_delete(entry)
		self.songs = songs
		self.songs_map = {}
		for song in self.songs:
			self.songs_map[song.title] = song
			self.add_song(song)
		self.db.commit()
		GLib.idle_add(self.start_playing)
		
	def start_playing(self):
		"""
		start playing from the beginning.
		"""
		if self.player.get_playing_entry() == None:
			self.player.set_playing_source(self)
			self.player.do_next()

	def new_playlist(self):
		"""
		get a new playlist.
		"""
		thread.start_new_thread(self.doubanfm.new_playlist, (self.history,
			self.reset_songs))

	def del_song(self, song):
		"""
		delete a song (mark as 'never play') by its title.
		"""
		sids = [each.sid for each in self.songs]
		next = sids.index(song.sid) + 1
		thread.start_new_thread(self.doubanfm.del_song, (song.sid, song.aid,
			sids[next:], self.reset_songs))

	def fav_song(self, song):
		"""
		favor a song (mark as 'like') by its title.
		"""
		thread.start_new_thread(self.doubanfm.fav_song, (song.sid, song.aid))
		song.like = True

	def unfav_song(self, song):
		"""
		unfavor a song (remove 'like' mark) by its title.
		"""
		thread.start_new_thread(self.doubanfm.unfav_song, (song.sid, song.aid))
		song.like = False

	def skip_song(self, song):
		"""
		skip a song by its title.
		"""
		thread.start_new_thread(self.doubanfm.skip_song, (song.sid, song.aid,
			self.history, self.reset_songs))
		self.history.append((song.sid, 's'))

	def played_song(self, song):
		"""
		mark a song as 'played'.
		"""
		thread.start_new_thread(self.doubanfm.played_song, (song.sid, song.aid))
		self.history.append((song.sid, 'p'))
		
	def played_list(self, song):
		"""
		playlist ended. request more songs.
		"""
		thread.start_new_thread(self.doubanfm.played_list, (song.sid, self.history,
			self.reset_songs))
		
GObject.type_register(DoubanFMSource)
