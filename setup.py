#! /usr/bin/env python3

import sys
import os
import subprocess
import shutil
from setuptools import setup

version = "0.3.3pre"
applications_folder = os.path.join("/", "usr", "share", "applications")
app_icon = os.path.join("lib", "icons", "nimbus.svg")
try: f = open(os.path.join("lib", "version.txt"), "w")
except: pass
else:
    try: f.write(version)
    except: pass
    f.close()
files_to_copy = ("AUTHORS.txt", "LICENSE.md", "README.md", "THANKS.txt")
for fname in files_to_copy:
    try: shutil.copy2(fname, "lib")
    except: pass
if len(sys.argv) > 1:
    setup(name='nimbus',
          version=version,
          description='Qt4 Web browser coded in Python 3, compatible with both',
          author='Daniel Sim',
          url='https://github.com/foxhead128/nimbus',
          packages=['nimbus'],
          package_dir={"nimbus": "lib"},
          scripts=['nimbus'],
          include_package_data=True
         )
    if "install" in sys.argv and sys.platform.startswith("linux"):
        subprocess.Popen(["xdg-desktop-menu", "install", "fh-nimbus.desktop"])
        for size in (16, 22, 24, 32, 48, 64, 72, 128, 256):
            subprocess.Popen(["xdg-icon-resource", "install", "--size", str(size), app_icon.replace(".svg", "-%s.png" % (size,)), "fh-nimbus"])
for fname in files_to_copy:
    try: os.remove(os.path.join("lib", fname))
    except: pass
