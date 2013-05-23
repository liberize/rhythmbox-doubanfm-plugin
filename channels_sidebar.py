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

from gi.repository import Gtk, Gio, GObject, GLib
from doubanfm_keys import *

SIDEBAR_FILE = 'channels_sidebar.glade'

class ChannelsSidebar(GObject.Object):
	__gtype_name__ = 'ChannelsSidebar'
	object = GObject.property(type = GObject.Object)
	
	def __init__(self, source):
		GObject.Object.__init__(self)
		self.source = source

		self.ui = Gtk.Builder()
		self.ui.add_from_file(PLUGIN_DIR + SIDEBAR_FILE)

		self.channels_box = self.ui.get_object('channels_box')
		self.channels_treeview = self.ui.get_object('channels_treeview')
		self.channels_liststore = self.ui.get_object('channels_liststore')

		tree_selection = self.channels_treeview.get_selection()
		tree_selection.connect("changed", self.on_tree_selection_changed)
		self.source.login_dialog.connect('login-completed', self.on_login_completed)
		
	def on_tree_selection_changed(self, selection):
		model, treeiter = selection.get_selected()
		if treeiter != None:
			GLib.idle_add(self.source.set_channel, model[treeiter][0])

	def on_login_completed(self, dialog, doubanfm):
		# add channels via source
		channels = doubanfm.channels
		for channel_id in sorted(channels):
			self.channels_liststore.append([channel_id, channels[channel_id]])
