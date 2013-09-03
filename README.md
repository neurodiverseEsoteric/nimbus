nimbus
======

Nimbus is a somewhat hacky Web browser coded in Python 3, using the Qt 4 and
QtWebKit libraries via either PyQt4 or PySide. It attempts to use a "batteries
included" approach, not unlike that of Python, and thus includes various odd
functionality out of the box. It probably failed at doing so, however.

Features include:
* Tabbed browsing
* Browser history, including a cache
* Very limited support for loading pages offline
* Incognito (private browsing) tabs
* Printing pages
* Automatic saving/loading of the user's browsing session, reducing the damage
  done by a crash
* Ad blocking via either Adblock Plus filters or a modified *hosts* file
* Basic support for extensions and user scripts
* YouTube video downloads via user script (you can enable this in the Settings
  dialog under the Extensions tab)
* Support for HTTP and Socks5 proxies
* Partial support for the HTML5 geolocation, fullscreen and offline mode APIs
* Really hacky support for RSS feeds, if feedparser is installed. You can
  enable the RSS feed button in the Settings dialog under the General tab.
* Using Netscape plugins to handle some HTML5 audio and video (useful on
  Windows, where QtWebKit doesn't support audio and video tags)
* Options to toggle features such as JavaScript, Netscape plugins, DNS
  prefetching, and XSS auditing, among others
* A graphing calculator
* A tank you can enable and use to "wreck up" sites you don't like (no,
  seriously. It's in the Settings dialog, under the Extensions tab)

Dependencies
======

Nimbus depends on Python >=3.2 and either PyQt4 or PySide, with python3-dbus
and feedparser as optional dependencies. It does not work in Python 2.x. It is
possible that it will work in versions of Python 3 below 3.2 as well, but this
has not been tested before.

On Windows, you can download Python 3 from http://www.python.org/getit/ and
PyQt4 from http://www.riverbankcomputing.com/software/pyqt/download.

You can install all of Nimbus's dependencies on Ubuntu using the following
command:

    sudo apt-get install python3 python3-pyqt4 python3-dbus python3-dbus.mainloop.qt python3-feedparser

Installing/compiling Nimbus on Windows
======

There is no installer for Windows, but you can (or should be able to) compile
Nimbus on Windows. In addition to its normal dependencies, you will need
cx_Freeze. You can download it from http://cx-freeze.sourceforge.net/. Once
that's done, run compile_windows.py in Python 3.

Installing Nimbus on Linux
======

If you want to install Nimbus system-wide, you will need setuptools. On
Ubuntu, you can install it with the following command:

    sudo apt-get install python3-setuptools

Once that's done, run the following:

    sudo python3 ./setup.py install

Translations
======

Nimbus now supports translations by way of QTranslator. To write a new
translation for Nimbus, make a copy of translations/en_US.ts, rename it to the
ISO code for the desired locale, and edit away. Once you're done, run
compile_translations.py on Linux/OS X/Unix, or lrelease on Windows. You will
need lrelease to be installed.

Licensing information
======

See LICENSE.md for more details.
