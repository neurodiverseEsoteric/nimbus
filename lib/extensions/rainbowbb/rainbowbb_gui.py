#! /usr/bin/env python3

import sys
from os.path import dirname, realpath
try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication, QAction, QCheckBox, QComboBox, QPushButton, QDockWidget, QTextEdit, QMainWindow, QToolBar
except:
    try:
        from PyQt4.QtCore import Qt
        from PyQt4.QtGui import QApplication, QAction, QCheckBox, QComboBox, QPushButton, QDockWidget, QTextEdit, QMainWindow, QToolBar
    except:
        from PySide.QtCore import Qt
        from PySide.QtGui import QApplication, QAction, QCheckBox, QComboBox, QPushButton, QDockWidget, QTextEdit, QMainWindow, QToolBar

try: __file__
except: __file__ = sys.executable
app_lib = dirname(realpath(__file__))

sys.path.append(app_lib)

import rainbowbb

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }

def html_escape(text):
    return "".join(html_escape_table.get(c,c) for c in text)

def create_gradient(cycle, reverse=False, bounce=False):
    try: rainbowbb.cycles[cycle]
    except: return "transparent"
    else:
        picked_cycle = rainbowbb.cycles[cycle][::-1] if reverse else rainbowbb.cycles[cycle]
        if bounce:
            picked_cycle = picked_cycle + picked_cycle[::-1]
        increment = round(1/(len(picked_cycle)-1), 2)
        gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:0"
        counter = 0
        for color in picked_cycle:
            gradient += ", stop:%s #%s" % (counter, color)
            counter += increment
            if counter > 1:
                counter = 1
        gradient += ")"
    return gradient

stylesheet = "QToolBar { background: %s; border: 0; }"

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        self.setWindowTitle("RainbowBB")
        self.setParent(parent)
        self.initUI()

    def initUI(self):
        self.setStyleSheet("QCheckBox { background: palette(window); border-radius: 4px; padding: 2px; margin-right: 2px; }")

        self.toolBar = QToolBar(self)
        self.toolBar.setStyleSheet(stylesheet % (create_gradient("pastel"),))
        self.toolBar.setMovable(False)
        self.toolBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.addToolBar(self.toolBar)

        self.closeWindowAction = QAction(self)
        self.closeWindowAction.setShortcuts(["Ctrl+W", "Ctrl+Q"])
        self.closeWindowAction.triggered.connect(self.close)
        self.addAction(self.closeWindowAction)

        self.reverseBox = QCheckBox("&Reverse", self)
        self.reverseBox.clicked.connect(lambda: self.updateGradient())
        self.toolBar.addWidget(self.reverseBox)

        self.byWordBox = QCheckBox("By &word", self)
        self.toolBar.addWidget(self.byWordBox)

        self.bounceBox = QCheckBox("&Bounce", self)
        self.bounceBox.clicked.connect(lambda: self.updateGradient())
        self.toolBar.addWidget(self.bounceBox)
        
        self.sizeList = QComboBox(self)
        self.sizeList.addItem("None")
        for num in range(1, 8):
            self.sizeList.addItem(str(num))
        self.toolBar.addWidget(self.sizeList)
        
        self.cycleList = QComboBox(self)
        self.cycleList.addItem("pastel")
        for cycle in sorted(list(rainbowbb.cycles.keys())):
            if cycle != "pastel":
                self.cycleList.addItem(cycle)
        self.toolBar.addWidget(self.cycleList)
        self.cycleList.currentIndexChanged.connect(self.updateGradient)
        
        self.convertButton = QPushButton("&Convert", self)
        self.convertButton.clicked.connect(self.convert)
        self.toolBar.addWidget(self.convertButton)

        self.inputDock = QDockWidget("Input", self)
        self.inputDock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.inputDock.setContextMenuPolicy(Qt.CustomContextMenu)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.inputDock)

        self.inputField = QTextEdit(self)
        self.inputField.setAcceptRichText(False)
        self.inputDock.setWidget(self.inputField)

        self.outputField = QTextEdit(self)
        self.outputField.setReadOnly(True)
        self.setCentralWidget(self.outputField)

    def updateGradient(self, index=None):
        if not index:
            index = self.cycleList.currentIndex()
        self.toolBar.setStyleSheet(stylesheet % (create_gradient(self.cycleList.itemText(index), self.reverseBox.isChecked(), self.bounceBox.isChecked()),))

    def show(self):
        self.setVisible(True)
        self.inputField.setFocus()

    def convert(self):
        self.outputField.setPlainText(rainbowbb.size(rainbowbb.colorize(self.inputField.toPlainText(), self.cycleList.currentText(), self.reverseBox.isChecked(), not self.byWordBox.isChecked(), self.bounceBox.isChecked()), self.sizeList.currentText() if self.sizeList.currentText() != "None" else None))

def main():
    app = QApplication(sys.argv)

    win = MainWindow()
    win.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
