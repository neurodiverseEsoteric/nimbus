#!/usr/bin/env python3

import qsettings
from PyQt4.QtCore import QCoreApplication, QSettings

def main():
    app = QCoreApplication([])
    settings4 = QSettings(QSettings.IniFormat, QSettings.UserScope, "nimbus", "config", QCoreApplication.instance())
    data4 = QSettings(QSettings.IniFormat, QSettings.UserScope, "nimbus", "data", QCoreApplication.instance())
    settings5 = qsettings.QSettings(QSettings.IniFormat, QSettings.UserScope, "nimbus", "config", QCoreApplication.instance())
    data5 = qsettings.QSettings(QSettings.IniFormat, QSettings.UserScope, "nimbus", "data", QCoreApplication.instance())

    keys = settings5.allKeys()
    for key in keys:
        settings4.setValue(key, settings5.value(key))

    settings4.sync()

    keys = data5.allKeys()
    for key in keys:
        data4.setValue(key, data5.value(key))

    data4.sync()

if __name__ == "__main__":
    main()
