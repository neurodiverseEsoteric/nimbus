#! /usr/bin/env python3

# Description:
# This script is a big, ugly hack to copy over required files after compiling
# Nimbus.

import os, shutil
from distutils.sysconfig import get_python_lib

app_dir = os.path.dirname(os.path.realpath(__file__))

os.chdir(os.path.join(os.path.dirname(os.path.dirname(get_python_lib()))))
print("copying " + os.path.join(os.path.dirname(os.path.dirname(get_python_lib())), "python33.dll") + " -> .\python33.dll")
shutil.copy2("python33.dll", os.path.join(app_dir, "python33.dll"))
os.chdir(os.path.join(get_python_lib(), "PyQt4"))
print("copying " + os.path.join(get_python_lib(), "PyQt4", "plugins") + " -> .\PyQt4\plugins")
shutil.copytree("plugins", os.path.join(app_dir, "PyQt4", "plugins"))
