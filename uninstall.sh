#!/bin/sh
sudo python3 setup.py install --record files.txt
cat files.txt | sudo xargs rm -rf
sudo xdg-desktop-menu uninstall fh-nimbus.desktop
rm files.txt
