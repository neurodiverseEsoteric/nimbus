nimbus
======

Nimbus is a somewhat hacky Web browser coded in Python 3, using either Qt 5 via
PyQt5, or Qt 4 via either PyQt4 or PySide. It is tailored specifically for my
use case, but I have open-sourced it due to 1) personal ideology, and
2) personal convenience. Maybe someone will find it useful for something.

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
* Really hacky support for RSS and Atom feeds, if feedparser is installed. You
  can enable the feed button in the Settings dialog under the General tab.
* Using Netscape plugins to handle some HTML5 audio and video (useful on
  Windows, where QtWebKit doesn't support audio and video tags)
* Options to toggle features such as JavaScript, Netscape plugins, DNS
  prefetching, and XSS auditing, among others
* A tank you can enable and use to "wreck up" sites you don't like (no,
  seriously. It's in the Settings dialog, under the Extensions tab)

Running 
======

Nimbus depends on Python >=3.2 and either PyQt5, PyQt4, or PySide, with
python3-dbus and feedparser as optional dependencies. It does not work in
Python 2.x. It is possible that it will work in versions of Python 3 below
3.2 as well, but this has not been tested before.

You can install all of Nimbus's dependencies on Debian-based platforms
using the following command:

    sudo apt-get install python3 python3-pyqt5 python3-pyqt5.qtwebkit python3-dbus python3-dbus.mainloop.pyqt5 python3-feedparser

Running Nimbus on Windows
======

Nimbus also works using [Portable Python](http://portablepython.com/); this is
currently the recommended way of running it on Windows. To start Nimbus, open
the /lib folder and run nimbus.py.

Enabling portable mode
======

Portable Python makes it possible to run Nimbus off a flash drive. For true
portability, Nimbus also supports a portable mode in which settings are saved
to whatever folder Nimbus itself is contained in, as opposed to the user's
home folder on the local hard drive. To enable this mode, simply create a file
named portable.conf and insert it into the /lib folder.

Installing Nimbus on Linux
======

If you want to install Nimbus system-wide, you will need setuptools. On
Debian-based platforms, you can install it with the following command:

    sudo apt-get install python3-setuptools

Once that's done, run the following:

    sudo python3 ./setup.py install

Translations
======

Nimbus supports translations by way of QTranslator. To write a new
translation for Nimbus, make a copy of translations/en_US.ts, rename it to the
ISO code for the desired locale, and edit away. Once you're done, run
compile_translations.py on Linux/OS X/Unix, or lrelease on Windows. You will
need lrelease to be installed.

Licensing information
======

See LICENSE.md for more details.
