#! /usr/bin/env python

import os, shutil
from distutils.sysconfig import get_python_lib

app_dir = os.path.dirname(os.path.realpath(__file__))

os.chdir(os.path.join(get_python_lib(), "PyQt4"))
print "copying " + os.path.join(get_python_lib(), "PyQt4", "plugins") + " -> .\PyQt4\plugins"
shutil.copytree("plugins", os.path.join(app_dir, "PyQt4", "plugins"))
