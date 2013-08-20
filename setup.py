#! /usr/bin/env python3

import os
import shutil
from setuptools import setup

files_to_copy = ("AUTHORS.txt", "LICENSE.md", "README.md", "THANKS.txt")
for fname in files_to_copy:
    shutil.copy2(fname, "lib")
setup(name='nimbus',
      version="0.2.0pre",
      description='Qt4 Web browser coded in Python 3, compatible with both',
      author='Daniel Sim',
      url='https://github.com/foxhead128/nimbus',
      packages=['nimbus'],
      package_dir={"nimbus": "lib"},
      scripts=['nimbus'],
      include_package_data=True
     )
for fname in files_to_copy:
    os.remove(os.path.join("lib", fname))
