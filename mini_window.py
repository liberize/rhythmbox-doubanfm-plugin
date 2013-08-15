#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import os, urllib, thread
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject, Pango, RB, GLib
from doubanfm_keys import *

WINDOW_FILE = 'mini_window.glade'

class MiniWindow(GObject.Object):
	__gtype_name__ = 'MiniWindow'
	object = GObject.property(type=GObject.Object)

	def __init__(self, plugin):
		self.plugin = plugin
		self.shell = plugin.shell
		self.source = plugin.source
		self.player = plugin.player
		self.current_song = None
		self.keep_above = False

		self.ui = Gtk.Builder()
		self.ui.add_from_file(PLUGIN_DIR + WINDOW_FILE)
		self.ui.connect_signals({
			'on_fav_song': self.on_fav_song,
			'on_skip_song': self.on_skip_song,
			'on_del_song': self.on_del_song,
			'on_go_home': self.on_go_home,
			'on_volume_changed': self.on_volume_changed,
			'on_change_play_time': self.on_change_play_time,
			'on_play_time_button_press': self.on_play_time_button_press,
			'on_play_time_button_release': self.on_play_time_button_release,
			'on_cover_button_press': self.on_cover_button_press,
			'on_settings': self.on_settings,
			'on_album': self.on_album,
			'on_report': self.on_report,
			'on_show_menu': self.on_show_menu,
			'on_keep_above': self.on_keep_above,
			'on_quit': self.on_quit,
			'on_pause': self.on_pause,
			'on_recommend_song': self.on_recommend_song,
			'on_share_sina': self.on_share_sina,
			'on_share_renren': self.on_share_renren,
			'on_share_kaixin001': self.on_share_kaixin001,
			'on_share_twitter': self.on_share_twitter,
			'on_share_fanfou': self.on_share_fanfou,
			'on_copy_permalink': self.on_copy_permalink
		})

		self.mini_window = self.ui.get_object('mini_window')
		self.mini_window.connect('destroy', self.on_destroy)

		self.cover_image = self.ui.get_object('cover_image')
		self.song_title_label = self.ui.get_object('song_title_label')
		font_description = self.song_title_label.get_pango_context().get_font_description()
		font_description.set_size(1024 * 12)
		font_description.set_weight(Pango.Weight.BOLD)
		self.song_title_label.override_font(font_description)
		self.song_info_label = self.ui.get_object('song_info_label')

		self.fav_button = self.ui.get_object('fav_button')
		self.del_button = self.ui.get_object('del_button')
		self.skip_button = self.ui.get_object('skip_button')
		self.pause_button = self.ui.get_object('pause_button')
		self.keep_above_button = self.ui.get_object('keep_above_button')

		self.volume_button = self.ui.get_object('volume_button')
		self.play_time_scale = self.ui.get_object('play_time_scale')
		self.play_time_scale.connect('format-value', self.on_format_value)
		self.button_down = False

		self.popup_menu = self.ui.get_object('more_menu')
		self.report_menuitem = self.ui.get_object('report_menuitem')
		self.album_menuitem = self.ui.get_object('album_menuitem')
		self.share_menuitem = self.ui.get_object('share_menuitem')
		self.channels_menu = self.ui.get_object('channels_menu')
		self.plugin.build_submenu(self.channels_menu)

		self.button_images = {
			'fav': Gtk.Image.new_from_icon_name('emblem-favorite', Gtk.IconSize.BUTTON),
			'nofav': Gtk.Image.new_from_icon_name('bookmark-new', Gtk.IconSize.BUTTON),
			'pause': Gtk.Image.new_from_stock('gtk-media-pause', Gtk.IconSize.BUTTON),
			'play': Gtk.Image.new_from_stock('gtk-media-play', Gtk.IconSize.BUTTON),
			'down': Gtk.Image.new_from_stock('gtk-go-down', Gtk.IconSize.BUTTON),
			'above': Gtk.Image.new_from_stock('gtk-goto-top', Gtk.IconSize.BUTTON)
		}

		self.sensitive_widgets = [
			self.fav_button,
			self.del_button,
			self.skip_button,
			self.report_menuitem,
			self.album_menuitem,
			self.share_menuitem
		]

		self.share_templates = {
			'kaixin001': "http://www.kaixin001.com/repaste/bshare.php?rurl=%s&rcontent=&rtitle=%s",
			'renren': "http://www.connect.renren.com/share/sharer?title=%s&url=%s",
			'sina': "http://v.t.sina.com.cn/share/share.php?appkey=3015934887&url=%s&title=%s&source=&sourceUrl=&content=utf-8&pic=%s",
			'twitter': "http://twitter.com/share?text=%s&url=%s",
			'fanfou': "http://fanfou.com/sharer?u=%s&t=%s&d=&s=bm",
			'douban': "http://shuo.douban.com/!service/share?name=%s&href=%s&image=%s&text=&desc=(%s)&apikey=0ace3f74eb3bd5d8206abe5ec1b38188&target_type=rec&target_action=0&object_kind=3043&object_id=%s"
		}

	def set_visibile(self, visible):
		self.set_handle_signals(visible)
		if visible:
			self.initialize()
			self.mini_window.show_all()
			self.shell.props.window.hide()
		else:
			self.plugin.initialize()
			self.shell.props.window.show_all()
			self.mini_window.hide()

	def initialize(self):
		entry = self.player.get_playing_entry()
		if entry == None:
			self.player.set_playing_source(self.source)
			self.player.do_next()
		else:
			self.on_playing_song_changed(self.player, entry)
			self.on_elapsed_changed(self.player, self.player.get_playing_time()[1])
			self.on_playing_changed(self.player, self.player.get_playing()[1])
		self.volume_button.set_value(self.player.get_volume()[1])

	def set_handle_signals(self, handle):
		if handle:
			self.handlers = [
				self.player.connect('playing-song-changed', self.on_playing_song_changed),
				self.player.connect('elapsed-changed', self.on_elapsed_changed),
				self.player.connect('playing-changed', self.on_playing_changed)
			]
		else:
			for handler in self.handlers:
				self.player.disconnect(handler)
		self.plugin.set_handle_signals(not handle)

	def set_sensitive(self, sensitive):
		for widget in self.sensitive_widgets:
			widget.set_sensitive(sensitive)

	def on_destroy(self, *e):
		self.set_visibile(False)

	def on_quit(self, *e):
		self.shell.quit()

	def on_fav_song(self, *e):
		if self.current_song.like:
			self.fav_button.set_image(self.button_images['nofav'])
			self.source.unfav_song(self.current_song)
		else:
			self.fav_button.set_image(self.button_images['fav'])
			self.source.fav_song(self.current_song)

	def on_skip_song(self, *e):
		self.source.skip_song(self.current_song)

	def on_del_song(self, *e):
		self.source.del_song(self.current_song)

	def on_go_home(self, *e):
		self.set_visibile(False)

	def on_volume_changed(self, *e):
		self.player.set_volume(self.volume_button.get_value())

	def on_format_value(self, scale, value):
		if self.current_song != None:
			pos_in_secs = int(value * self.current_song.length)
			return '%02d:%02d/%s ' % (pos_in_secs / 60, pos_in_secs % 60,
				self.formatted_song_length)
		return ''

	def on_play_time_button_press(self, *e):
		self.button_down = True

	def on_play_time_button_release(self, *e):
		self.button_down = False

	def on_change_play_time(self, *e):
		if not self.button_down:
			self.play_pos = self.play_time_scale.get_value()
			pos_in_secs = int(self.current_song.length * self.play_pos)
			self.player.set_playing_time(pos_in_secs)

	def on_playing_song_changed(self, player, entry):
		if entry != None:
			title = entry.get_string(RB.RhythmDBPropType.TITLE)
			self.current_song = self.source.get_song_by_title(title)
			self.formatted_song_length = '%02d:%02d' % (self.current_song.length / 60,
				self.current_song.length % 60)
			self.song_title_str = ('%s - %s' % (self.current_song.title, self.current_song.artist)
				).encode('utf-8')
			self.song_info_str = ('< %s >  %s' % (self.current_song.albumtitle, self.current_song.public_time)
				).encode('utf-8')
			self.song_url = self.current_song.get_uri()
			self.mini_window.set_title(self.song_title_str + ' - Rhythmbox 豆瓣FM')
			self.song_title_label.set_label(self.song_title_str)
			self.song_info_label.set_label(self.song_info_str)
			self.fav_button.set_image(self.button_images['fav'] if self.current_song.like else
				self.button_images['nofav'])
			thread.start_new_thread(self.update_cover_image, ())
		else:
			self.source.new_playlist()

	def on_elapsed_changed(self, player, elapsed):
		if self.current_song != None:
			if not self.button_down:
				self.play_pos = float(elapsed) / float(self.current_song.length)
				self.play_time_scale.set_value(self.play_pos)
			if elapsed == self.current_song.length:
				self.source.played_song(self.current_song)

	def on_pause(self, *e):
		self.player.playpause(True)

	def on_playing_changed(self, player, playing):
		self.pause_button.set_image(self.button_images['pause'] if playing else
			self.button_images['play'])
		self.set_sensitive(playing)

	def update_cover_image(self):
		url = self.current_song.picture
		GLib.idle_add(self.update_cover_image_cb, urllib.urlopen(url).read())

	def update_cover_image_cb(self, data):
		loader = GdkPixbuf.PixbufLoader()
		loader.write(data)
		loader.close()
		self.cover_image.set_from_pixbuf(loader.get_pixbuf())

	def on_cover_button_press(self, widget, event):
		if event.type == Gdk.EventType._2BUTTON_PRESS and event.button == Gdk.BUTTON_PRIMARY:
			self.on_album()

	def on_settings(self, *e):
		os.popen(' '.join(['xdg-open', 'http://douban.fm/mine']))

	def on_album(self, *e):
		url = "http://music.douban.com/subject/%s/" % self.current_song.aid
		os.popen(' '.join(['xdg-open', url]))

	def on_report(self, *e):
		url = ("http://music.douban.com/subject/%s/report?song_id=%s" %
			(self.current_song.aid, self.current_song.sid))
		os.popen(' '.join(['xdg-open', url]))

	def on_keep_above(self, *e):
		self.keep_above = not self.keep_above
		self.mini_window.set_keep_above(self.keep_above)
		self.keep_above_button.set_image(self.button_images['down'] if self.keep_above else
			self.button_images['above'])
		
	def on_show_menu(self, widget, event):
		self.popup_menu.popup(None, None, None, None, event.button, event.time)
		return True

	def on_share_sina(self, *e):
		url = self.share_templates['sina'] % tuple(map(urllib.quote_plus, 
			[self.song_url, self.song_title_str, self.current_song.picture]))
		os.popen(' '.join(['xdg-open', '"%s"' % url]))

	def on_share_kaixin001(self, *e):
		url = self.share_templates['kaixin001'] % tuple(map(urllib.quote_plus,
			[self.song_url, self.song_title_str]))
		os.popen(' '.join(['xdg-open', '"%s"' % url]))

	def on_share_renren(self, *e):
		url = self.share_templates['renren'] % tuple(map(urllib.quote_plus,
			[self.song_title_str, self.song_url]))
		os.popen(' '.join(['xdg-open', '"%s"' % url]))

	def on_share_twitter(self, *e):
		url = self.share_templates['twitter'] % tuple(map(urllib.quote_plus,
			[self.song_title_str, self.song_url]))
		os.popen(' '.join(['xdg-open', '"%s"' % url]))

	def on_share_fanfou(self, *e):
		url = self.share_templates['fanfou'] % tuple(map(urllib.quote_plus,
			[self.song_url, self.song_title_str]))
		os.popen(' '.join(['xdg-open', '"%s"' % url]))

	def on_recommend_song(self, *e):
		url = self.share_templates['douban'] % tuple(map(urllib.quote_plus, [
				self.current_song.title.encode('utf8'),
				self.song_url,
				self.current_song.picture,
				"Rhythmbox DoubanFM Plugin",
				self.current_song.sid
			]))
		os.popen(' '.join(['xdg-open', '"%s"' % url]))

	def on_copy_permalink(self, *e):
		clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
		clipboard.set_text(self.song_url, -1)
