#!/usr/bin/env python3

import qsettings
from PyQt4.QtCore import QCoreApplication, QSettings

def chop(thestring, beginning):
  if thestring.startswith(beginning):
    return thestring[len(beginning):]
  return thestring

def main():
    app = QCoreApplication([])
    settings4 = QSettings(QSettings.IniFormat, QSettings.UserScope, "nimbus", "config", QCoreApplication.instance())
    data4 = QSettings(QSettings.IniFormat, QSettings.UserScope, "nimbus", "data", QCoreApplication.instance())
    settings5 = qsettings.QSettings(QSettings.IniFormat, QSettings.UserScope, "nimbus", "config", QCoreApplication.instance())
    data5 = qsettings.QSettings(QSettings.IniFormat, QSettings.UserScope, "nimbus", "data", QCoreApplication.instance())

    keys = settings4.allKeys()
    for key in keys:
        settings5.setValue(key, settings4.value(key))
        if key.startswith("general/"):
            settings5.setValue(chop(key, "general/"), settings4.value(key))
        elif key.startswith("General/"):
            settings5.setValue(chop(key, "General/"), settings4.value(key))

    settings5.sync()

    keys = data4.allKeys()
    for key in keys:
        data5.setValue(key, data4.value(key))
        if key.startswith("general/"):
            data5.setValue(chop(key, "general/"), data4.value(key))
        elif key.startswith("General/"):
            data5.setValue(chop(key, "General/"), data4.value(key))

    data5.sync()

if __name__ == "__main__":
    main()
