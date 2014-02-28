#!/usr/bin/env python3

"""RainbowBB

==Description==
This Python script generates BBCode in rainbows! =D

==License==
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>"""

import sys, getopt

cycles = {"pastel": ("FF7F7F", "FFBF7F", "FFFF7F", "BFFF7F", "7FFF7F", "7FFFBF", "7FFFFF", "7FBFFF", "7F7FFF", "BF7FFF", "FF7FFF", "FF7FBF"),
          "hard": ("FF0000", "FFFF00", "00FF00", "00FFFF", "0000FF", "FF00FF"),
          "grayscale": ("000000", "3F3F3F", "7F7F7F", "BFBFBF"),
          "fail": ("7F3F3F", "7F5F3F", "7F7F3F", "57FF3F", "37FF3F", "37FF5F", "37F7FF", "3F57FF", "3F37FF", "5F37FF", "7F37FF", "7F3F5F"),
          "desaturated": ("7F3F3F", "7F5F3F", "7F7F3F", "5F7F3F", "3F7F3F", "3F7F5F", "3F7F7F", "3F5F7F", "3F3F7F", "5F3F7F", "7F3F7F", "7F3F5F"),
          "dawn": ("FFFFBF", "FFDFBF", "FFBFBF", "FFBFDF", "FFBFFF"),
          "dawn2": ("FFFFBF", "FFEFBF", "FFDFBF", "FFCFBF", "FFBFBF", "FFBFCF", "FFBFDF", "FFBFEF", "FFBFFF"),
          "terminal": ("000000", "003F00", "005F00", "007F00", "009F00", "00BF00", "00DF00", "00FF00"),
          "terminalred": ("000000", "3F0000", "5F0000", "7F0000", "9F0000", "BF0000", "DF0000", "FF0000"),
          "magic": ("000080", "00ffff", "ff0000", "4b0082", "800080", "ee82ee", "dda0dd", "0000ff", "ffd700", "008000", "ff8c00", "00ff00")}

def colorize(text, cycle="pastel", reverse=False, by_char=True, bounce=False):
    if type(text) is not str:
        return
    elif cycle not in cycles.keys():
        print("Invalid color cycle.")
        print("Valid color cycles: " + ", ".join(list(cycles.keys())))
        return
    splittext = list(text) if by_char else text.split()
    counter = 0
    adder = 1
    thestring = ""
    for char in splittext:
        thestring += char if char == " " else "[color=#%s]%s[/color]" % (cycles[cycle][counter if not reverse else len(cycles[cycle]) - (counter + 1)], char)
        if char == " ":
            continue
        if not bounce:
            if counter == len(cycles[cycle]) - 1:
                counter = 0
            else:
                counter += adder
        else:
            if counter == len(cycles[cycle]) - 1:
                adder = -1
            elif counter == 0:
                adder = 1
            counter += adder
        if not by_char:
            thestring += " "
    return thestring

def size(text, size=None):
    if not size:
        return text
    else:
        return "[size=%s]" % (size,) + text + "[/size]"

def main(argv=[]):
    try:
        opts, args = getopt.getopt(argv, "rbwc:s:", ["reverse", "bounce", "cycle=", "size=", "by-word"])
    except getopt.GetoptError:
        sys.exit(2)
    cycle = "pastel"
    fontsize = None
    by_char = True
    bounce = False
    reverse = False
    for opt, arg in opts:
        if opt in ("-c", "--cycle"):
            cycle = arg
        elif opt in ("-s", "--size"):
            fontsize = arg
        elif opt in ("-w", "--by-word"):
            by_char = False
        elif opt in ("-b", "--bounce"):
            bounce = True
        elif opt in ("-r", "--reverse"):
            reverse = True
    if len(args) > 0:
        text = " ".join(args)
    else:
        text = input("Enter some text here: ")
    print(size(colorize(text, cycle, reverse, by_char, bounce), fontsize))

if __name__ == "__main__":
    main(sys.argv[1:])
