#!/bin/bash
schema_dir="~/.local/share/glib-2.0/schemas"
schema_file="./org.gnome.rhythmbox.plugins.doubanfm.gschema.xml"
icon_dir="~/.local/share/icons"
icon_file="./doubanfm.png"

echo "copying schema file ..."
if [ ! -d "$schema_dir" ]; then
	mkdir -p "$schema_dir"
fi
cp "$schema_file" "$schema_dir"
glib-compile-schemas "$schema_dir"

echo "copying icon file ..."
if [ ! -d "$icon_dir" ]; then
	mkdir -p "$icon_dir"
fi
cp "$icon_file" "$icon_dir"

echo "done!"
