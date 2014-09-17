try: common.git_image_repo
except:
    gitImageRepo = settings.settings.value("settings/GitImageRepo")
    if not gitImageRepo:
        location = QInputDialog.getText(self, "Location", "Enter the path of your Git repo here:")
        if location[1]:
            common.git_image_repo = location[0]
            settings.settings.setValue("settings/GitImageRepo", location[0])
    else:
        common.git_image_repo = gitImageRepo
try: common.git_image_repo
except: pass
else:
    fnames = QFileDialog.getOpenFileNames(None, tr("Select files..."), os.path.expanduser("~"), tr("All files (*)"))
    if len(fnames) > 0:
        for fname in fnames:
            os.system("cp %s %s" % (fname, common.git_image_repo))
        os.system("cd %s && git add . && git commit -m \"Added new images.\"" % (common.git_image_repo,))
        os.system("cd %s && xterm -e \"git push --all\"" % (common.git_image_repo,))
