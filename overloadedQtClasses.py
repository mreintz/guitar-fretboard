from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import *

class QComboBoxWithKeyEvents(QtWidgets.QComboBox):

    def __init__(self, parent):
        super().__init__(parent)

    notesOrIntervals = pyqtSignal()
    chordOrScale = pyqtSignal()
    nut = pyqtSignal()
    root = pyqtSignal()
    mode = pyqtSignal()
    tuning = pyqtSignal()
    majmin = pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_I:
            self.notesOrIntervals.emit()
        elif event.key() == QtCore.Qt.Key_Space:
            self.chordOrScale.emit()
        elif event.key() == QtCore.Qt.Key_N:
            self.nut.emit()
        elif event.key() == QtCore.Qt.Key_R:
            self.root.emit()
        elif event.key() == QtCore.Qt.Key_Right:
            self.mode.emit()
        elif event.key() == QtCore.Qt.Key_Left:
            self.root.emit()
        elif event.key() == QtCore.Qt.Key_T:
            self.tuning.emit()
        elif event.key() == QtCore.Qt.Key_M:
            self.majmin.emit()
        else:
            super(QComboBoxWithKeyEvents, self).keyPressEvent(event)

class QLineEditTabReact(QtWidgets.QLineEdit):
    def __init__(self, parent):
        super().__init__(parent)

    tune = pyqtSignal()

    def event(self,event):
        if event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Tab:
            self.returnPressed.emit()
            super(QLineEditTabReact, self).keyPressEvent(event)
            return True
        else:
            return QtWidgets.QLineEdit.event(self,event)
        
class QLabelClickable(QtWidgets.QLabel):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.transparency = False

    clicked = pyqtSignal()
    selected = pyqtSignal()

    def mousePressEvent(self, ev):
        if ev.button() == Qt.RightButton:
            self.selected.emit()
        else:
            self.clicked.emit()