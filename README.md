# Rhythmbox 豆瓣 FM 插件

**本插件停止开发。如果你有兴趣继续开发，我可以尽我所能提供一些指导。在此向已安装的用户致歉。**

本项目是一个 Rhythmbox 插件，旨在将[豆瓣 FM ](http://douban.fm)功能集成到 Rhythmbox 中。

## 简介

安装插件后，Rhythmbox 左侧边栏会增加一个豆瓣 FM 入口。你可以：

* 加红心、不再播放、下一首
* 显示当前播放列表以及歌曲的详细信息
* 在右边栏中切换频道，支持公共兆赫、红心兆赫、私人兆赫

另外，还有一个迷你窗口，可以通过菜单或工具栏按钮打开。你可以：

* 控制音乐播放，加红心、不再播放、下一首，设置窗口置顶
* 自动获取并显示专辑封面
* 分享到豆瓣、新浪、开心网、人人、饭否等网站

主界面：

![MainWindow](https://github.com/liberize/rhythmbox-doubanfm-plugin/raw/master/screenshots/main.jpg)

迷你窗口：

![MiniWindow](https://github.com/liberize/rhythmbox-doubanfm-plugin/raw/master/screenshots/mini.jpg)

## 安装

已测试的 rhythmbox 版本：**2.96 - 2.98**. 不兼容 **2.99.1** 及以后的版本。

下载到本地后解压到 `~/.local/share/rhythmbox/plugins` 目录（不存在则创建）。

或者在终端执行：

	cd ~/.local/share/rhythmbox/plugins
	git clone https://github.com/liberize/rhythmbox-doubanfm-plugin

## TODO

* 兼容 2.99.1 及以后的版本
* 无需登录即可使用
* 无需 PRO 账号即可使用高码率，参考[这里](http://v2ex.com/t/101093)
* <del>无需安装，修改图标加载和用户信息存储的方式</del>
* 登录方式改为模拟客户端登陆，无需验证码，参考[这里](https://github.com/zonyitoo/doubanfm-qt/wiki/%E8%B1%86%E7%93%A3FM-API)
* 在主窗口模式下显示专辑封面，参考[这里](https://github.com/luqmana/rhythmbox-plugins/blob/master/AlbumArtSearch/AlbumArtSearch.py)
* 频道分类、搜索、显示详细信息
* 迷你窗口下点击专辑封面查看专辑信息
* 快捷键操作
* 开放 DBus 接口
* 显示歌词
* 顶栏指示器

## 关于

* 博客: <http://liberize.me/>
* 电邮: <liberize@gmail.com>

