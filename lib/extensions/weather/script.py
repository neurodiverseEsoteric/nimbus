try: common.weather_location
except:
    weatherLocation = settings.settings.value("data/WeatherLocation")
    if not weatherLocation:
        location = QInputDialog.getText(self, "Location", "Enter your current location here:")
        if location[1]:
            common.weather_location = location[0]
            settings.settings.setValue("data/WeatherLocation", location[0])
    else:
        common.weather_location = weatherLocation
try: common.weather_location
except: pass
else:
    mainWindow = browser.activeWindow()
    currentWidget = mainWindow.tabWidget().currentWidget()
    stdout_handle = os.popen("weather %s" % (common.weather_location,))
    forecast = stdout_handle.read()
    QMessageBox.information(self, tr("Weather"), forecast)
