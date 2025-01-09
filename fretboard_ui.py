# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'fretboard.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from overloadedQtClasses import QComboBoxWithKeyEvents, QLineEditTabReact, QPushButtonRightClick, QLabelClickable, QDialWithKeyEvents

class Ui_MainWindow(object):
    def setupUi(self, MainWindow, tooltip, strings=...):
        if strings==...:
            strings=6
        self.strings=strings

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1301, 581)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.titleLabel = QLabelClickable(self.centralwidget)
        self.titleLabel.setMaximumSize(QtCore.QSize(16777215, 100))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.titleLabel.setFont(font)
        self.titleLabel.setObjectName("titleLabel")
        self.verticalLayout.addWidget(self.titleLabel)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")

        self.tuningButtons = [ QLineEditTabReact(self.centralwidget) for i in range(strings) ]

        for i, button in enumerate(self.tuningButtons):
            button.setMinimumSize(QtCore.QSize(40, 40))
            button.setMaximumSize(QtCore.QSize(40, 16777215))
            font = QtGui.QFont()
            font.setPointSize(12)
            button.setFont(font)
            button.setAlignment(QtCore.Qt.AlignCenter)
            if tooltip:
                button.setToolTip('Left click to change tuning, right click to set root note.')
            self.gridLayout.addWidget(button, i, 0, 1, 1)

        self.tuningButtons.reverse()            

        self.nutButton = QPushButtonRightClick(self.centralwidget)
        self.nutButton.setMinimumSize(QtCore.QSize(40, 40))
        self.nutButton.setMaximumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.nutButton.setFont(font)
        self.nutButton.setObjectName("nutButton")
        if tooltip:
            self.nutButton.setToolTip('Left click to revert to full fretboard, right click for help.')
        self.gridLayout.addWidget(self.nutButton, strings, 0, 1, 1)

        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.notesOrIntervalsSlider = QtWidgets.QSlider(self.centralwidget)
        self.notesOrIntervalsSlider.setMaximum(1)
        self.notesOrIntervalsSlider.setPageStep(1)
        if tooltip:
            self.notesOrIntervalsSlider.setToolTip('Display notes or intervals?')
        self.notesOrIntervalsSlider.setOrientation(QtCore.Qt.Horizontal)
        self.notesOrIntervalsSlider.setObjectName("notesOrIntervalsSlider")
        self.horizontalLayout.addWidget(self.notesOrIntervalsSlider)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.horizontalLayout_4.addLayout(self.horizontalLayout)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout_4.addWidget(self.line)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.scaleOrChordSlider = QtWidgets.QSlider(self.centralwidget)
        self.scaleOrChordSlider.setMaximum(1)
        self.scaleOrChordSlider.setPageStep(1)
        if tooltip:
            self.scaleOrChordSlider.setToolTip('Display scale or chord?')
        self.scaleOrChordSlider.setOrientation(QtCore.Qt.Horizontal)
        self.scaleOrChordSlider.setObjectName("scaleOrChordSlider")
        self.horizontalLayout_2.addWidget(self.scaleOrChordSlider)
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_2.addWidget(self.label_5)
        self.horizontalLayout_4.addLayout(self.horizontalLayout_2)
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout_4.addWidget(self.line_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.rootNoteSelector = QComboBoxWithKeyEvents(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.rootNoteSelector.setFont(font)
        self.rootNoteSelector.setObjectName("rootNoteSelector")
        if tooltip:
            self.rootNoteSelector.setToolTip('Select root note of the scale or chord.')
        self.horizontalLayout_3.addWidget(self.rootNoteSelector)

        self.circle_of_fifths = QDialWithKeyEvents(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.circle_of_fifths.sizePolicy().hasHeightForWidth())
        self.circle_of_fifths.setSizePolicy(sizePolicy)
        self.circle_of_fifths.setMaximumSize(QtCore.QSize(60, 16777215))
        self.circle_of_fifths.setMinimum(0)
        self.circle_of_fifths.setMaximum(12)
        self.circle_of_fifths.setPageStep(1)
        self.circle_of_fifths.setProperty("value", 6)
        self.circle_of_fifths.setOrientation(QtCore.Qt.Vertical)
        self.circle_of_fifths.setWrapping(True)
        self.circle_of_fifths.setNotchesVisible(True)
        self.circle_of_fifths.setObjectName("circle_of_fifths")
        self.horizontalLayout_3.addWidget(self.circle_of_fifths)

        self.signature_label = QLabelClickable(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.signature_label.setFont(font)
        self.signature_label.setAlignment(QtCore.Qt.AlignCenter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.signature_label.sizePolicy().hasHeightForWidth())
        self.signature_label.setSizePolicy(sizePolicy)
        self.signature_label.setMaximumSize(QtCore.QSize(40, 40))
        self.signature_label.setMinimumSize(QtCore.QSize(40, 40))
        self.signature_label.setObjectName("signature_label")
        self.horizontalLayout_3.addWidget(self.signature_label)
        self.signature_label.setText('N')

        self.scaleOrChordTypeSelector = QComboBoxWithKeyEvents(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.scaleOrChordTypeSelector.setFont(font)
        self.scaleOrChordTypeSelector.setObjectName("scaleOrChordTypeSelector")
        if tooltip:
            self.scaleOrChordTypeSelector.setToolTip('Select type of scale or chord.')
        self.horizontalLayout_3.addWidget(self.scaleOrChordTypeSelector)
        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4.setStretch(4, 10)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        for i in range(strings-1):
            MainWindow.setTabOrder(self.tuningButtons[i], self.tuningButtons[i+1])

        MainWindow.setTabOrder(self.tuningButtons[strings-1], self.rootNoteSelector)
        MainWindow.setTabOrder(self.rootNoteSelector, self.circle_of_fifths)
        MainWindow.setTabOrder(self.circle_of_fifths, self.scaleOrChordTypeSelector)
        MainWindow.setTabOrder(self.scaleOrChordTypeSelector, self.notesOrIntervalsSlider)
        MainWindow.setTabOrder(self.notesOrIntervalsSlider, self.scaleOrChordSlider)
        MainWindow.setTabOrder(self.scaleOrChordSlider, self.nutButton)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.titleLabel.setText(_translate("MainWindow", "C major scale: C  D  E  F  G  A  B"))
        self.nutButton.setText(_translate("MainWindow", "N/?"))
        self.label_2.setText(_translate("MainWindow", "Notes"))
        self.label_3.setText(_translate("MainWindow", "Intervals"))
        self.label_4.setText(_translate("MainWindow", "Scale"))
        self.label_5.setText(_translate("MainWindow", "Chord"))
