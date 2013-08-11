#! /usr/bin/env python3

# Custom widgets.

try:
    from PySide.QtGui import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QLineEdit, QSpinBox, QToolBar, QStyle, QStylePainter, QStyleOptionToolBar
except:
    from PyQt4.QtGui import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QLineEdit, QSpinBox, QToolBar, QStyle, QStylePainter, QStyleOptionToolBar

# Blank widget to take up space.
class Expander(QLabel):
    def __init__(self, parent=None):
        super(Expander, self).__init__(parent)
        self.setText("")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

class HorizontalExpander(QLabel):
    def __init__(self, parent=None):
        super(HorizontalExpander, self).__init__(parent)
        self.setText("")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

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

# This is a row with a label and a QSpinBox.
class SpinBoxRow(Row):
    def __init__(self, text="Enter something here:", parent=None):
        super(SpinBoxRow, self).__init__(parent)
        self.label = QLabel(text, self)
        self.addWidget(self.label)
        self.spinBox = QSpinBox(self)
        self.addWidget(self.spinBox)
        self.expander = HorizontalExpander()
        self.addWidget(self.expander)

# Column widget.
class Column(QWidget):
    def __init__(self, parent=None):
        super(Column, self).__init__(parent)
        newLayout = QVBoxLayout()
        self.setLayout(newLayout)
        self.layout().setContentsMargins(0,0,0,0)
    def addWidget(self, widget):
        self.layout().addWidget(widget)

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
