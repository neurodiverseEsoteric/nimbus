#! /usr/bin/env python3

# Description:
# This script is a big, ugly hack that compiles Nimbus on Windows.

import os, shutil
from distutils.sysconfig import get_python_lib

app_dir = os.path.dirname(os.path.realpath(__file__))
python_dir = os.path.dirname(os.path.dirname(get_python_lib()))

os.chdir(app_dir)
print("This script will compile Nimbus. Before you continue, make sure that:")
print("1) Python 3 is installed.")
print("2) Either PyQt4 or PySide is installed.")
print("3) cx_Freeze is installed.")
os.system("""PAUSE""")
os.system(os.path.join(python_dir, "Scripts", "cxfreeze.bat") + """ "nimbus.py" --target-dir="." --base-name="Win32GUI\"""")
os.chdir(python_dir)
print("copying " + os.path.join(os.path.dirname(os.path.dirname(get_python_lib())), "python*.dll") + " -> .\python*.dll")
x = os.listdir(".")
for dll in x:
    if dll.startswith("python") and dll.endswith(".dll"):
        shutil.copy2(dll, os.path.join(app_dir, dll))
os.chdir(os.path.join(get_python_lib(), "PyQt4"))
print("copying " + os.path.join(get_python_lib(), "PyQt4", "plugins") + " -> .\PyQt4\plugins")
shutil.copytree("plugins", os.path.join(app_dir, "PyQt4", "plugins"))
os.system("echo Compilation successful. && PAUSE")
