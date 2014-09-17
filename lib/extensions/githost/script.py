try: common.git_repo
except:
    gitRepo = settings.settings.value("settings/GitRepo")
    if not gitRepo:
        gitRepo = "None"
        QMessageBox.information(self, tr("Githost"), tr("Please select the directory of your Git repository."))
        gitRepo = QFileDialog.getExistingDirectory(self, "Select directory", os.path.expanduser("~"))
        if not os.path.isdir(gitRepo):
            pass
        else:
            common.git_repo = gitRepo
            settings.settings.setValue("settings/GitRepo", gitRepo)
    else:
        common.git_repo = gitRepo
try: common.git_repo
except: pass
else:
    fnames = QFileDialog.getOpenFileNames(self, tr("Select files to upload"), os.path.expanduser("~"), tr("All files (*)"))
    if len(fnames) > 0:
        for fname in fnames:
            os.system("cp %s %s" % (fname, common.git_repo))
        os.system("cd %s && git add . && git commit -m \"Added new files (%s).\"" % (common.git_repo, ", ".join(fnames)))
        os.system("cd %s && xterm -e \"git push --all\"" % (common.git_repo,))
