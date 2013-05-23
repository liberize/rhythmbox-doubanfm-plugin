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

from gi.repository import Gtk, Gio, GObject
from doubanfm_keys import *

DIALOG_FILE = 'config_dialog.glade'

class ConfigDialog(GObject.Object):
	__gtype_name__ = 'ConfigDialog'
	object = GObject.property(type=GObject.Object)
	
	def __init__(self):
		GObject.Object.__init__(self)

		self.ui = Gtk.Builder()
		self.ui.add_from_file(PLUGIN_DIR + DIALOG_FILE)

		self.config_box = self.ui.get_object('config_box')
		self.enable_indicator_checkbox = self.ui.get_object('enable_indicator_checkbox')
		self.user_name_entry = self.ui.get_object('user_name_entry')
		self.user_pwd_entry = self.ui.get_object('user_pwd_entry')
	
		self.settings = Gio.Settings(DOUBANFM_SCHEMA)
		self.user_name_entry.set_text(self.settings[USER_NAME_KEY])	
		self.user_pwd_entry.set_text(self.settings[USER_PWD_KEY])
		self.enable_indicator_checkbox.set_active(self.settings[ENABLE_INDICATOR_KEY])

		self.enable_indicator_checkbox.connect('clicked', self.on_enable_indicator_checkbox_clicked)
		self.user_name_entry.connect('changed', self.on_user_name_entry_changed)
		self.user_pwd_entry.connect('changed', self.on_user_pwd_entry_changed)
		
	def on_enable_indicator_checkbox_clicked(self, widget):
		self.settings[ENABLE_INDICATOR_KEY] = self.enable_indicator_checkbox.get_active()
		
	def on_user_name_entry_changed(self, widget):
		self.settings[USER_NAME_KEY] = self.user_name_entry.get_text()
		
	def on_user_pwd_entry_changed(self, widget):
		self.settings[USER_PWD_KEY] = self.user_pwd_entry.get_text()
