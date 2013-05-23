#!/bin/bash
schema_dir="/usr/share/glib-2.0/schemas"
schema_file="./org.gnome.rhythmbox.plugins.doubanfm.gschema.xml"
icon_dir="$HOME/.local/share/icons"
icon_file="./doubanfm.png"
plugin_dir="$HOME/.local/share/rhythmbox/plugins"
pulgin_folder="../doubanfm"

echo "copying schema file ..."
if [ ! -d "$schema_dir" ]; then
	sudo mkdir -p "$schema_dir"
fi
sudo cp "$schema_file" "$schema_dir"
sudo glib-compile-schemas "$schema_dir"

echo "copying icon file ..."
if [ ! -d "$icon_dir" ]; then
	mkdir -p "$icon_dir"
fi
cp "$icon_file" "$icon_dir"

echo "copying plugin folder ..."
if [ ! -d "$plugin_dir" ]; then
	mkdir -p "$plugin_dir"
fi
cp -a "$pulgin_folder" "$plugin_dir"

echo "done!"
