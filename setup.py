#! /usr/bin/env python3

import shutil
from setuptools import setup

for fname in ("AUTHORS.txt", "LICENSE.md", "README.md", "THANKS.txt"):
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
