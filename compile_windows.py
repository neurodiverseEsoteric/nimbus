#! /usr/bin/env python3

# ------------------
# compile_windows.py
# ------------------
# Author:      Daniel Sim (foxhead128)
# License:     See <http://unlicense.org/> for more details.
# Description: This script is a big, ugly hack that compiles Nimbus on Windows.

import os, shutil
from distutils.sysconfig import get_python_lib

app_dir = os.path.dirname(os.path.realpath(__file__))
app_lib = os.path.join(app_dir, "lib")
app_build = os.path.join(app_dir, "build")
python_dir = os.path.dirname(os.path.dirname(get_python_lib()))

print("This script will compile Nimbus. Before you continue, make sure that:")
print("1) Python 3 is installed.")
print("2) Either PyQt4 or PySide is installed.")
print("3) cx_Freeze is installed.")
os.system("""PAUSE""")
if not os.path.exists(app_build):
    shutil.copytree(app_lib, app_build)
files_to_copy = ("AUTHORS.txt", "LICENSE.md", "README.md", "THANKS.txt")
for fname in files_to_copy:
    try: shutil.copy2(fname, app_build)
    except: pass
os.chdir(app_build)
os.system(os.path.join(python_dir, "Scripts", "cxfreeze.bat") + """ nimbus.py --target-dir=".\"""")
os.chdir(python_dir)
print("copying " + os.path.join(os.path.dirname(os.path.dirname(get_python_lib())), "python*.dll") + " -> .\python*.dll")
x = os.listdir(".")
for dll in x:
    if dll.startswith("python") and dll.endswith(".dll"):
        shutil.copy2(dll, os.path.join(app_build, dll))
os.chdir(os.path.join(get_python_lib(), "PyQt4"))
print("copying " + os.path.join(get_python_lib(), "PyQt4", "plugins") + " -> .\PyQt4\plugins")
shutil.copytree("plugins", os.path.join(app_build, "PyQt4", "plugins"))
os.system("echo Compilation successful. && PAUSE")
