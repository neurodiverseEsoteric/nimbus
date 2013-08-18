nimbus
======

Nimbus is a simple, somewhat hacky Web browser coded in Python 3, using the
Qt 4 and QtWebKit libraries via either PyQt4 or PySide. It is quite basic, but
it should be suitable for basic browsing.

Features include:
* Tabbed browsing
* Browser history, including a cache
* Very limited support for loading pages offline
* Incognito (private browsing) tabs
* Printing pages
* Ad blocking
* Basic extensions
* Support for HTTP and Socks5 proxies
* Partial support for HTML5 geolocation
* Using Netscape plugins to handle HTML5 audio and video (useful on Windows,
  where QtWebKit doesn't support them)
* Options to toggle features such as JavaScript, Netscape plugins, DNS
  prefetching, and XSS auditing.

Dependencies
======

Nimbus depends on Python 3 and either PySide or PyQt4, with python3-dbus as
an optional dependency. It does not work in Python 2.x.

You can install its dependencies on Ubuntu using the following command:
    sudo apt-get install python3 python3-pyqt4 python3-dbus python3-dbus.mainloop.qt

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
