nimbus
======

Nimbus is a simple, somewhat hacky Web browser coded in Python 3 and based
around the PyQt4 libraries. It has most of the basic features expected from a
modern browser, including tabbed browsing, history, incognito (private
browsing) tabs, ad blocking, and support for basic extensions.

Dependencies
======

Nimbus depends on Python 3 and PyQt4, with python3-dbus as an optional
dependency. It does not work in Python 2.x.

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
