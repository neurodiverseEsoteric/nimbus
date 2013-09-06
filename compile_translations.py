#!/usr/bin/env python3

# -----------------------
# compile_translations.py
# -----------------------
# Author:      Daniel Sim (foxhead128)
# License:     See <http://unlicense.org/> for more details.
# Description: This script compiles all of Nimbus' translations on Unix.

import os

def main():
    os.system("lrelease ./lib/translations/*")

if __name__ == "__main__":
    main()
