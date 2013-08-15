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

from gi.repository import Gtk, Gio, GObject, RB, Peas, PeasGtk
from doubanfm_keys import *
from doubanfm_source import DoubanFMSource
from config_dialog import ConfigDialog
from channels_sidebar import ChannelsSidebar
from mini_window import MiniWindow

UI_FILE = 'doubanfm_ui.xml'

class DoubanFMEntryType(RB.RhythmDBEntryType):
	def __init__(self):
		RB.RhythmDBEntryType.__init__(self, name='DoubanFMEntryType')

class DoubanFMPlugin(GObject.Object, Peas.Activatable, PeasGtk.Configurable):
	__gtype_name__ = 'DoubanFMPlugin'
	object = GObject.Property(type=GObject.Object)
	
	def __init__(self):
		super(DoubanFMPlugin, self).__init__()
		self.current_song = None
		self.config_dialog = None
		self.channels_sidebar = None
		self.mini_window = None

	def do_create_configure_widget(self):
		if self.config_dialog == None:
			self.config_dialog = ConfigDialog()
		return self.config_dialog.config_box

	def do_activate(self):
		self.shell = self.object
		self.player = self.shell.props.shell_player

		# create and register an entry type
		self.db = self.shell.props.db
		self.entry_type = DoubanFMEntryType()
		self.db.register_entry_type(self.entry_type)
		self.entry_type.can_sync_metadata = True
		self.entry_type.sync_metadata = None

		# find and load doubanfm icon
		theme = Gtk.IconTheme.get_default()
		width, height = Gtk.icon_size_lookup(Gtk.IconSize.LARGE_TOOLBAR)[1:]
		icon = theme.load_icon('doubanfm', width, 0)

		# create a source under 'stores' group
		group = RB.DisplayPageGroup.get_by_id ('stores')
		self.source = GObject.new(DoubanFMSource, shell=self.shell,
			entry_type=self.entry_type, pixbuf=icon, plugin=self)
		self.shell.register_entry_type_for_source(self.source, self.entry_type)
		self.shell.append_display_page(self.source, group)

		# create ui, connect ui to actions, and add them to ui manager
		self.ui_manager = self.shell.props.ui_manager
		self.build_actions()
		self.ui_manager.insert_action_group(self.action_group)
		self.ui_merge_id = self.ui_manager.add_ui_from_file(PLUGIN_DIR + UI_FILE)
		self.change_menu_item_state(False)
		self.ui_manager.ensure_update()

		# connect signals
		self.player.connect('playing-source-changed', self.on_playing_source_changed)
		self.set_handle_signals(True)
		
	def do_deactivate(self):
		self.ui_manager.remove_ui(self.ui_merge_id)
		self.ui_manager.remove_action_group(self.action_group)
		self.ui_manager.ensure_update()
		self.action_group = None
		self.actions = None
		self.ui_manager = None
		self.db.commit()
		self.db = None
		self.entry_type = None
		self.source.delete_thyself()
		self.source = None
		self.player = None
		self.handlers = None
		self.shell = None

	def set_handle_signals(self, handle):
		if handle:
			self.handlers = [
				self.player.connect('playing-song-changed', self.on_playing_song_changed),
				self.player.connect('elapsed-changed', self.on_elapsed_changed)
			]
		else:
			for handler in self.handlers:
				self.player.disconnect(handler)

	def build_actions(self):
		self.actions = [
			Gtk.Action('FMMenu', '豆瓣FM(_D)', None, None),
			Gtk.Action('FavSong', '喜欢(_F)', None, None),
			Gtk.Action('DelSong', '不再播放(_D)', None, None),
			Gtk.Action('SkipSong', '跳过(_S)', None, None),
			Gtk.Action('NewPlaylist', '刷新列表(_N)', None, None),
			Gtk.Action('ShowMiniWindow', 'Mini窗口(_M)', None, Gtk.STOCK_LEAVE_FULLSCREEN)
		]
		methods = [self.on_fav_song, self.on_del_song, self.on_skip_song,
			self.on_new_playlist, self.show_mini_window]

		for (action, method) in zip(self.actions[1:], methods):
			action.connect('activate', method)

		self.action_group = Gtk.ActionGroup('DoubanFMActions')
		for action in self.actions:
			self.action_group.add_action(action)

	def change_menu_item_state(self, state):
		for action in self.actions[1:]:
			action.set_sensitive(state)

	def build_submenu(self, menu):
		channels = self.source.doubanfm.channels
		for channel_id in sorted(channels):
			sub_item = Gtk.MenuItem(channels[channel_id])
			sub_item.connect('activate', self.on_set_channel, channel_id)
			menu.append(sub_item)
			sub_item.show()
	
	def show_sidebar(self, show):
		if show:
			if self.channels_sidebar == None:
				self.channels_sidebar = ChannelsSidebar(self.source)
			self.shell.add_widget(self.channels_sidebar.channels_box,
				RB.ShellUILocation.RIGHT_SIDEBAR,
				False, True)
		else:
			self.shell.remove_widget(self.channels_sidebar.channels_box,
				RB.ShellUILocation.RIGHT_SIDEBAR)

	def show_mini_window(self, action):
		if self.mini_window == None:
			self.mini_window = MiniWindow(self)
		self.mini_window.set_visibile(True)

	def on_set_channel(self, action, channel_id):
		self.source.set_channel(channel_id)

	def on_fav_song(self, action):
		if self.current_song.like:
			self.actions[1].set_label('喜欢(_F)')
		 	self.source.unfav_song(self.current_song)
		else:
			self.actions[1].set_label('取消喜欢(_U)')
			self.source.fav_song(self.current_song)

	def on_del_song(self, action):
		self.source.del_song(self.current_song)

	def on_skip_song(self, action):
		self.source.skip_song(self.current_song)

	def on_new_playlist(self, action):
		self.source.new_playlist()

	def initialize(self):
		entry = self.player.get_playing_entry()
		self.on_playing_song_changed(self.player, entry)

	def on_playing_source_changed(self, player, source):
		source_match = source is self.source
		self.change_menu_item_state(source_match)
		self.set_handle_signals(source_match)

	def on_playing_song_changed(self, player, entry):
		if entry != None:
			song_title = entry.get_string(RB.RhythmDBPropType.TITLE)
			self.current_song = self.source.get_song_by_title(song_title)
			self.actions[1].set_label('取消喜欢(_U)' if self.current_song.like else '喜欢(_F)')
		else:
			self.source.new_playlist()

	def on_elapsed_changed(self, player, elapsed):
		if self.current_song != None:
			if elapsed == self.current_song.length:
				self.source.played_song(self.current_song)
