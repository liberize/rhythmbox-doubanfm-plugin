Rhythmbox-DoubanFM-Plugin
======================

Rhythmbox doubanfm plugin is a desktop client for the online music service, [Douban radio](http://douban.fm "Douban FM"). It provides full functionality of douban radio service, and linux desktop integration.

Intro
-------

This plugin will create a source in the left sidebar of rhythmbox. When activated, you can

* Mark a song as favorite, skip a song, delete a song and refresh playlist through main menu.
* Switch between channels in the right sidebar.

There is a minimized view for DoubanFM tracks. When activated, you can:

* Douban covers support, automatically retrieve album art from douban.com.
* Share music and album to douban, sina, kaixin001, renren, fanfou and twitter.

MainWindow:

![MainWindow](http://farm8.staticflickr.com/7364/8786450403_9fa0f4e67a.jpg)

MiniWindow:

![MiniWindow](http://farm6.staticflickr.com/5446/8797029704_94d8b58e94.jpg)

Install
-------

Tested with rhythmbox version 2.98.

Clone the repository to your local disk, and do as follows:

	cd /path/to/your/folder
	./install.sh

*Notice: root privilege is required because username and password are stored with gsettings.*

Problems
-------

* It may crash sometimes.
* It may get stuck if your netspeed is not very good.

Thanks
-------

* [@sunny87](http://github.com/sunng87) and his [exaile doubanfm plugin](https://github.com/sunng87/exaile-doubanfm-plugin).
