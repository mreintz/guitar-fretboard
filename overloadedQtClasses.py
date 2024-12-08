from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import *

class QComboBoxWithKeyEvents(QtWidgets.QComboBox):

    def __init__(self, parent):
        super().__init__(parent)

    notesOrIntervals, chordOrScale, nut, root, mode, tuning, majmin, help = [ pyqtSignal() for i in range(8) ]

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
        elif event.key() == QtCore.Qt.Key_Question:
            self.help.emit()
        else:
            super(QComboBoxWithKeyEvents, self).keyPressEvent(event)

class QLineEditTabReact(QtWidgets.QLineEdit):
    def __init__(self, parent):
        self.rootNote = None
        super().__init__(parent)

    escape, selected, edit = [ pyqtSignal() for i in range(3) ]

    def event(self,event):
        if event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Tab:
            self.returnPressed.emit()
            super(QLineEditTabReact, self).keyPressEvent(event)
            return True
        elif event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Escape:
            self.escape.emit()
            super(QLineEditTabReact, self).keyPressEvent(event)            
            return True
        else:
            return QtWidgets.QLineEdit.event(self,event)

    def mousePressEvent(self, a0):
        if a0.button() == Qt.RightButton:
            self.selected.emit()
        else:
            self.edit.emit()
        
    def contextMenuEvent(self, event):
        # Suppress the context menu
        event.ignore()        
        
class QLabelClickable(QtWidgets.QLabel):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.transparency = False

    clicked, selected = [ pyqtSignal() for i in range(2) ]

    def mousePressEvent(self, ev):
        if ev.button() == Qt.RightButton:
            self.selected.emit()
        else:
            self.clicked.emit()

class QPushButtonRightClick(QtWidgets.QPushButton):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

    rightClicked = pyqtSignal()

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            self.rightClicked.emit()
        else:
            return super().mousePressEvent(e)