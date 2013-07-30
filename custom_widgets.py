#! /usr/bin/env python3

# Custom widgets.

from PyQt4.QtGui import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QLineEdit, QToolBar, QStyle, QStylePainter, QStyleOptionToolBar

# Row widget.
class Row(QWidget):
    def __init__(self, parent=None):
        super(Row, self).__init__(parent)
        newLayout = QHBoxLayout()
        self.setLayout(newLayout)
        self.layout().setContentsMargins(0,0,0,0)
    def addWidget(self, widget):
        self.layout().addWidget(widget)

# This is a row with a label and a QLineEdit.
class LineEditRow(Row):
    def __init__(self, text="Enter something here:", parent=None):
        super(LineEditRow, self).__init__(parent)
        self.label = QLabel(text, self)
        self.addWidget(self.label)
        self.lineEdit = QLineEdit(self)
        self.addWidget(self.lineEdit)

# Column widget.
class Column(QWidget):
    def __init__(self, parent=None):
        super(Column, self).__init__(parent)
        newLayout = QVBoxLayout()
        self.setLayout(newLayout)
        self.layout().setContentsMargins(0,0,0,0)
    def addWidget(self, widget):
        self.layout().addWidget(widget)

# Blank widget to take up space.
class Expander(QLabel):
    def __init__(self, parent=None):
        super(Expander, self).__init__(parent)
        self.setText("")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

# Toolbar that looks like a menubar.
class MenuToolBar(QToolBar):
    def __init__(self, *args, **kwargs):
        super(MenuToolBar, self).__init__(*args, **kwargs)
    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionToolBar()
        self.initStyleOption(option)
        style = self.style()
        style.drawControl(QStyle.CE_MenuBarEmptyArea, option, painter, self)
