#!/usr/bin/env python3

import sys
import os

app_folder = os.path.dirname(os.path.realpath(__file__)) if sys.executable != os.path.dirname(__file__) else os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

portable = os.path.exists(os.path.join(app_folder, "portable.conf"))

startpage = os.path.join(app_folder, "start.html")

extensions_folder = os.path.join(app_folder, "extensions")

app_icons_folder = os.path.join(app_folder, "icons")

app_version_file = os.path.join(app_folder, "version.txt")
