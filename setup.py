#! /usr/bin/env python3

from setuptools import setup

setup(name='nimbus',
      version="0.2.0pre",
      description='Qt4 Web browser coded in Python 3, compatible with both',
      author='Daniel Sim',
      url='https://github.com/foxhead128/nimbus',
      packages=['nimbus'],
      package_dir={"nimbus": "lib"},
      scripts=['nimbus'],
      package_data={"nimbus": ["extensions/*/*/*/*", "extensions/*/*/*", "extensions/*/*", "icons/*.png", "translations/*", "*.css", "*.txt", "*.md", "hosts", "nimbus-hosts", "qt.conf", "start.html"]},
      exclude_package_data={"nimbus": ["extensions/svg-edit/jgraduate/css", "extensions/svg-edit/jgraduate/images", "extensions/svg-edit/canvg", "extensions/svg-edit/extensions", "extensions/svg-edit/images", "extensions/svg-edit/jgraduate", "extensions/svg-edit/jquerybbq", "extensions/svg-edit/jquery-ui", "extensions/svg-edit/js-hotkeys", "extensions/svg-edit/locale", "extensions/svg-edit/spinbtn", "extensions/svg-edit/svgicons", "extensions/charcount/s/images", "extensions/charcount/s/html", "extensions/charcount/s", "extensions/graphr/images", "extensions/readability/css", "extensions/readability/images", "extensions/readability/js", "extensions/readability/js/es"]}
     )
