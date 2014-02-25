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

from gi.repository import Gtk, GObject
from ConfigParser import ConfigParser
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
		self.username_entry = self.ui.get_object('username_entry')
		self.password_entry = self.ui.get_object('password_entry')
	
		self.config = ConfigParser()
		self.config.read(PLUGIN_DIR + CONFIG_FILE)
		self.username_entry.set_text(self.config.get(MAIN_SECTION, USERNAME_KEY))	
		self.password_entry.set_text(self.config.get(MAIN_SECTION, PASSWORD_KEY))

		self.username_entry.connect('changed', self.on_username_entry_changed)
		self.password_entry.connect('changed', self.on_password_entry_changed)
		
	def on_username_entry_changed(self, widget):
		self.config.set(MAIN_SECTION, USERNAME_KEY, self.username_entry.get_text())
		self.config.write(open(PLUGIN_DIR + CONFIG_FILE, 'w'))
		
	def on_password_entry_changed(self, widget):
		self.config.set(MAIN_SECTION, PASSWORD_KEY, self.password_entry.get_text())
		self.config.write(open(PLUGIN_DIR + CONFIG_FILE, 'w'))
