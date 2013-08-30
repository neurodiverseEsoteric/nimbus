#! /usr/bin/env python3

import common
from translate import tr

try:
    from PyQt4.QtCore import pyqtSignal, Qt
    Signal = pyqtSignal
    from PyQt4.QtGui import QAction, QDoubleSpinBox, QToolBar
except:
    from PySide.QtCore import Signal, Qt
    from PySide.QtGui import QAction, QDoubleSpinBox, QToolBar

# Zoom bar.
class ZoomBar(QToolBar):
    zoomFactorChanged = Signal(float)
    def __init__(self, parent=None):
        super(ZoomBar, self).__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setMovable(False)
        self.zoomFactorDisplay = QDoubleSpinBox(self)
        self.zoomFactorDisplay.setValue(1.0)
        self.zoomFactorDisplay.valueChanged.connect(self.zoomFactorChanged.emit)
        self.addWidget(self.zoomFactorDisplay)

        # Zoom out button.
        self.zoomOutAction = QAction(common.complete_icon("zoom-out"), tr("Zoom Out"), self)
        self.zoomOutAction.triggered.connect(lambda: self.zoomFactorDisplay.setValue(self.zoomFactorDisplay.value() - 0.1))
        self.addAction(self.zoomOutAction)

        # Reset zoom button.
        self.zoomOriginalAction = QAction(common.complete_icon("zoom-original"), tr("Reset Zoom"), self)
        self.zoomOriginalAction.triggered.connect(lambda: self.zoomFactorDisplay.setValue(1.0))
        self.addAction(self.zoomOriginalAction)

        # Zoom in button.
        self.zoomInAction = QAction(common.complete_icon("zoom-in"), tr("Zoom In"), self)
        self.zoomInAction.triggered.connect(lambda: self.zoomFactorDisplay.setValue(self.zoomFactorDisplay.value() + 0.1))
        self.addAction(self.zoomInAction)
    def setZoomFactor(self, value):
        self.zoomFactorDisplay.setValue(value)