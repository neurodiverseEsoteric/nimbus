if sys.platform.startswith("linux"):
    subprocess.Popen(["xdg-open", browser.currentTab().url().toString()])
else:
    import webbrowser
    webbrowser.open(browser.currentTab().url().toString())
