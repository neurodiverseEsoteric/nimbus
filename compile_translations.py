#!/usr/bin/env python3

# This script is a redundant way of compiling Nimbus' translation files.

import os

def main():
    os.system("lrelease ./translations/*")

if __name__ == "__main__":
    main()
