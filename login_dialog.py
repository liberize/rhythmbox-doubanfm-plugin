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

import urllib, socket
from gi.repository import Gio, Gtk, GdkPixbuf, GObject, GLib
from libdoubanfm import *
from doubanfm_keys import *

DIALOG_FILE = 'login_dialog.glade'
ERROR_LOGIN_FAILED = ('登录douban.fm失败！', '请检查你的用户名和密码。')
ERROR_SOCKET_EXECPTION = ('Socket错误！', '请检查你的网络连接。')
ERROR_USER_INFO_NOT_SET = ('用户名和密码未设置！', 
	'请到“编辑”“插件”“首选项”下设置用户名和密码，然后在左侧重新选择“豆瓣电台”。')

class LoginDialog(GObject.Object):
	__gtype_name__ = 'LoginDialog'
	object = GObject.property(type=GObject.Object)

	__gsignals__ = {
		'login-completed' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
			(GObject.TYPE_PYOBJECT,))
	}

	def __init__(self, shell):
		GObject.Object.__init__(self)
		self.shell = shell

		self.ui = Gtk.Builder()
		self.ui.add_from_file(PLUGIN_DIR + DIALOG_FILE)

		self.login_dialog = self.ui.get_object('login_dialog')
		self.ok_button = self.ui.get_object('ok_button')
		self.captcha_image = self.ui.get_object('captcha_image')
		self.captcha_entry = self.ui.get_object('captcha_entry')
		
		self.ok_button.connect('clicked', self.on_ok_button_clicked)
		
	def on_ok_button_clicked(self, widget):
		captcha_solution = self.captcha_entry.get_text()
		self.login_dialog.hide()
		GLib.idle_add(self.try_login, captcha_solution)

	def get_captcha_image(self):
		"""
		download captcha image.
		"""
		captcha_url = "http://www.douban.com/misc/captcha?id=%s&amp;size=s" % self.captcha_id
		response = urllib.urlopen(captcha_url)
		loader = GdkPixbuf.PixbufLoader()
		loader.write(response.read())
		loader.close()
		self.captcha_image.set_from_pixbuf(loader.get_pixbuf())

	def try_login(self, captcha_solution=None):
		"""
		try to login. show a dialog if captcha is needed.
		"""
		try:
			doubanfm = DoubanFM(self.shell.props.shell_player, self.user_name,
				self.user_pwd, self.captcha_id, captcha_solution)
			self.emit('login-completed', doubanfm)
		except DoubanLoginException as e:
			if 'captcha_id' not in e.data or e.data['captcha_id'] == None:
				self.error_dialog(ERROR_LOGIN_FAILED)
			else:
				self.captcha_id = e.data['captcha_id']
				self.captcha_entry.set_text('')
				GLib.idle_add(self.get_captcha_image)
				self.login_dialog.show_all()
		except socket.error:
			self.error_dialog(ERROR_SOCKET_EXECPTION)

	def login(self):
		"""
		login to douban.fm with user name and password.
		"""
		settings = Gio.Settings(DOUBANFM_SCHEMA)
		self.user_name = settings[USER_NAME_KEY]
		self.user_pwd = settings[USER_PWD_KEY]
		self.captcha_id = None

		if self.user_name == '' or self.user_pwd == '':
			self.error_dialog(ERROR_USER_INFO_NOT_SET)
		else:
			GLib.idle_add(self.try_login)

	def error_dialog(self, error_msg):
		"""
		show a dialog when error occurred.
		"""
		dialog = Gtk.MessageDialog(self.shell.props.window, 0, Gtk.MessageType.ERROR,
				Gtk.ButtonsType.CLOSE, error_msg[0])
		dialog.format_secondary_text(error_msg[1])
		dialog.run()
		dialog.destroy()
