#!/bin/bash
schema_file="/usr/share/glib-2.0/schemas/org.gnome.rhythmbox.plugins.doubanfm.gschema.xml"
icon_file="$HOME/.local/share/icons/doubanfm.png"
pulgin_folder="$PWD"

echo "removing schema file ..."
sudo rm -f "$schema_file"
sudo glib-compile-schemas "$(dirname "$schema_file")"

echo "removing icon file ..."
rm -f "$icon_file"

echo "removing plugin folder ..."
rm -rf "$pulgin_folder"

echo "done!"
