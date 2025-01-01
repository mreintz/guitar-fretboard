from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import *

class QComboBoxWithKeyEvents(QtWidgets.QComboBox):

    def __init__(self, parent):
        super().__init__(parent)

    notesOrIntervals, chordOrScale, nut, root, circle, mode, tuning, majmin, help, play, signature = [ pyqtSignal() for i in range(11) ]

    def focusInEvent(self, event):
        self.set_glow_effect(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.set_glow_effect(False)
        super().focusOutEvent(event)

    def set_glow_effect(self, enabled):
        if enabled:
            shadow = QtWidgets.QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setColor(QtGui.QColor(255, 215, 0))  # Gold color
            shadow.setOffset(0, 0)
            self.setGraphicsEffect(shadow)
        else:
            self.setGraphicsEffect(None)

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
        elif event.key() == QtCore.Qt.Key_Return:
            self.play.emit()
        elif event.key() == QtCore.Qt.Key_S:
            self.signature.emit()            
        else:
            super(QComboBoxWithKeyEvents, self).keyPressEvent(event)

class QDialWithKeyEvents(QtWidgets.QDial):

    def __init__(self, parent):
        super().__init__(parent)
        self.user_interaction = False

    notesOrIntervals, chordOrScale, nut, root, mode, tuning, majmin, help, play, signature = [ pyqtSignal() for i in range(10) ]

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
        elif event.key() == QtCore.Qt.Key_Up:
            self.user_interaction = True
            super(QDialWithKeyEvents, self).keyPressEvent(event)
        elif event.key() == QtCore.Qt.Key_Down:
            self.user_interaction = True
            super(QDialWithKeyEvents, self).keyPressEvent(event)
        elif event.key() == QtCore.Qt.Key_T:
            self.tuning.emit()
        elif event.key() == QtCore.Qt.Key_M:
            self.majmin.emit()
        elif event.key() == QtCore.Qt.Key_Question:
            self.help.emit()
        elif event.key() == QtCore.Qt.Key_Return:
            self.play.emit()
        elif event.key() == QtCore.Qt.Key_S:
            self.signature.emit()
        else:
            super(QDialWithKeyEvents, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        super(QDialWithKeyEvents, self).keyReleaseEvent(event)
        self.user_interaction = False

    def mousePressEvent(self, event):
        self.user_interaction = True
        super(QDialWithKeyEvents, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super(QDialWithKeyEvents, self).mouseReleaseEvent(event)
        self.user_interaction = False    

class QLineEditTabReact(QtWidgets.QLineEdit):
    def __init__(self, parent):
        self.rootNote = None
        super().__init__(parent)

    escape, selected, edit = [ pyqtSignal() for i in range(3) ]

    def focusInEvent(self, event):
        self.set_glow_effect(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.set_glow_effect(False)
        super().focusOutEvent(event)

    def set_glow_effect(self, enabled):
        if enabled:
            shadow = QtWidgets.QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setColor(QtGui.QColor(255, 215, 0))  # Gold color
            shadow.setOffset(0, 0)
            self.setGraphicsEffect(shadow)
        else:
            self.setGraphicsEffect(None)

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

    clicked, selected, ctrl_clicked = [ pyqtSignal() for i in range(3) ]

    def mousePressEvent(self, ev):
        modifiers = QtGui.QGuiApplication.keyboardModifiers()
        if modifiers & QtCore.Qt.ControlModifier:
            self.ctrl_clicked.emit()
        elif ev.button() == Qt.RightButton:
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