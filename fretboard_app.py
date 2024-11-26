from PyQt5 import QtWidgets, QtCore, QtGui
from fretboard_ui import Ui_MainWindow
from fretboard import Fretboard
import fretboard_rc
from musthe import *
import sys
import pandas as pd
from overloadedQtClasses import QLabelClickable
from helpDialog import HelpDialog
import json
import argparse
import os
import subprocess

settingsFile = "fretboard_settings.json"

helpMessages = [
    ['<space>', 'Toggle between scale and chord'],
    ['I',       'Show notes or (I)ntervals'],
    ['N',       'Revert number of frets to (N)ormal'],
    ['Arrows',  'Select root note and type'],
    ['M',       'Toggle between (M)ajor and (M)inor modes'],
    ['Fret buttons',    'Click to zoom in on frets'],
    ['Left click', 'Set/unset transparency on a note/interval'],
    ['Right click', 'Set root note to the note below the cursor'],
    ['?',       'Display this message']
]


fullFretboard = 2000
firstFret = fullFretboard / 18
remaining = fullFretboard - firstFret
fretWidths = [round(firstFret)]
for i in range(25):
    nextFret = remaining/18
    remaining = remaining - nextFret
    fretWidths.append(round(nextFret))

labelColors = [
    "background-color: rgba(205, 253, 205, 80%);",
    "background-color: rgba(147, 223, 199, 80%);",
    "background-color: rgba(173, 215, 229, 80%);",
    "background-color: rgba(247, 247, 185, 80%);",
    "background-color: rgba(255, 210, 127, 80%);",
    "background-color: rgba(254, 160, 122, 80%);",
    "background-color: rgba(217, 170, 174, 80%);"
]

interval_colors = {
    'm':        "background-color: lightBlue; color: black;",   #labelColors[2],
    'M':        "background-color: lightGreen; color: black;",  #labelColors[0],
    'd':        labelColors[6],
    'P':        "background-color: yellow; color: black;",       #"background-color: rgba(220, 220, 170, 80%);",  #labelColors[0],
    'A':        labelColors[5],
    'P1':       "background-color: red; color: white; border-color: black;"
}

replacementStrings = {
    'dim ':  'diminished ',
    '_':    ' ',
    'min ':  'minor ',
    'maj ':  'major ',
    'aug ':  'augmented '
}

def translate(string):
    string=string.replace('b', '♭')
    string=string.replace('#', '♯')
    return string

def populateFretboard(ui, notes, intervals, frets):
    # Set up all the labels with notes or intervals on them
    ui.labels = []
    if ui.showInterval:
        fretboard = intervals
    else:
        fretboard = notes

    # We don't want to show the tuning after the nut as a fret, so we cut that column out.
    if min(frets) == 0:
        fret_slice = range(1, frets[1]+1)
        df = pd.DataFrame(fretboard)
        fretboard = df[ fret_slice ].values.tolist()

    # Setting up the labels...
    for i, row in enumerate(fretboard):
        labelRow = []
        for j, column in enumerate(row, start=1):
            label = QLabelClickable(ui.centralwidget, text=translate(column))
            label.clicked.connect(lambda x=label: toggleTransparency(x))
            label.selected.connect(lambda x=label: selectRootFromLabel(x))
            label.setMinimumSize(QtCore.QSize(fretWidths[j+1], 40)) #(40, 40))
            label.setMaximumSize(QtCore.QSize(fretWidths[j+1], 40)) #(40, 40))
            label.setObjectName(column)
            font = QtGui.QFont()
            font.setPointSize(12)
            label.setFont(font)
            ui.gridLayout.addWidget(label, i, 2*j+1, 1, 1)
            labelRow.append(label)
        ui.labels.append(labelRow)

    # "Flatten" the notes and intervals into a single list for easy lookup.
    flattenedNotes = []
    flattenedIntervals = []
    for row in notes:
        flattenedNotes += row
    for row in intervals:
        flattenedIntervals += row

    # Setting up the colors corresponding to the intervals.
    for row in ui.labels:
        for label in row:
            if label.text() != '':
                label.setAlignment(QtCore.Qt.AlignCenter)
                label.setFrameShape(QtWidgets.QFrame.Box)
                label.setLineWidth(3)
                if ui.showInterval:
                    interval =  label.objectName()
                    if interval != "P1":
                        intervalType = interval[0]
                    else:
                        intervalType = interval
                else:
                    try:
                        interval = flattenedIntervals[flattenedNotes.index(label.objectName())]
                        if interval != "P1":
                            intervalType = interval[0]
                        else:
                            intervalType = interval
                    except ValueError:
                        intervalType = ''
                label.setStyleSheet("QLabel"
                            "{"
                            "border : 3px solid ;"
                            f"{interval_colors.get(intervalType, labelColors[6])}"
                            "border-color : black"
                            "}")

    # Set up the frets themselves as ui lines.
    ui.lines = []
    for i in range(1, len(ui.labels[0])+1):
        line = QtWidgets.QFrame(ui.centralwidget)
        line.setMinimumSize(QtCore.QSize(5, 5))
        line.setFrameShadow(QtWidgets.QFrame.Raised)
        line.setLineWidth(3)
        line.setMidLineWidth(0)
        line.setFrameShape(QtWidgets.QFrame.VLine)
        line.setObjectName(f"freLine{i}")
        ui.gridLayout.addWidget(line, 0, 2*i, ui.strings, 1)
        ui.lines.append(line)
        i = i + 1

    # Set up the fret buttons.
    fretMarker = "●"
    ui.fretMarkers = []
    ui.fretButtons = []
    j = 1
    for fret in range(frets[0], frets[1]+1):
        if fret > 0:
            button = QtWidgets.QPushButton(ui.centralwidget)
            button.setMinimumSize(QtCore.QSize(fretWidths[fret - frets[0]+1], 40)) #(40, 40))
            button.setMaximumSize(QtCore.QSize(fretWidths[fret - frets[0]+1], 40)) #(40, 40))
            font = QtGui.QFont()
            font.setPointSize(12)
            button.setFont(font)
            button.setObjectName("fretButton" + str(fret))
            button.setText(str(fret))
            button.setFocusPolicy(QtCore.Qt.ClickFocus)
            ui.gridLayout.addWidget(button, ui.strings, 2*j+1, 1, 1)
            ui.fretButtons.append(button)
            button.clicked.connect(lambda state, x=fret: setFret(x))
            j = j + 1
        if fret in ( ui.markers['single'] + ui.markers['double'] ):
            dot = QtWidgets.QLabel(ui.centralwidget, text=translate(column))
            dot.setAlignment(QtCore.Qt.AlignCenter)
            if fret in ui.markers['single']:
                dot.setText(fretMarker)
            else:
                dot.setText(fretMarker+fretMarker)
            ui.gridLayout.addWidget(dot, ui.strings+1, 2*j-1, 1, 1)
            ui.fretMarkers.append(dot)

    # Set up the "tuning peg" values and interval colors if open strings are on the chord or scale.
    for i, peg in enumerate(ui.tuningButtons):
        text = ui.tuning[i]
        peg.setStyleSheet("QLineEdit")

        try:
            interval = flattenedIntervals[flattenedNotes.index(text)]
            if interval != "P1":
                intervalType = interval[0]
            else:
                intervalType = interval
        except ValueError:
            interval = ''

        for row in notes:
            for note in row:
                if text == note:
                    peg.setStyleSheet("QLineEdit"
                                "{"
                                "border : 3px solid ;"
                                f"{interval_colors.get(intervalType, labelColors[6])}"
                                "border-color : black"
                                "}")
                else:
                    for enharmonicRow in ui.enharmonics:
                        if (text in enharmonicRow and note in enharmonicRow):
                            interval = flattenedIntervals[flattenedNotes.index(note)]
                            if interval != "P1":
                                intervalType = interval[0]
                            else:
                                intervalType = interval
                            peg.setStyleSheet("QLineEdit"
                                        "{"
                                        "border : 3px solid ;"
                                        f"{interval_colors.get(intervalType, labelColors[6])}"
                                        "border-color : black"
                                        "}")
        peg.setText(translate(text))

def selectRootFromLabel(label):
    # Set the root note to the note right-clicked.
    selected = label.objectName()
    if selected in ui.rootNotes:
        ui.rootNoteSelector.setCurrentText(selected)
    else:
        # If needed: Look up enharmonics.
        for row in ui.enharmonics:
            if selected in row:
                for note in row:
                    if note in ui.rootNotes:
                        ui.rootNoteSelector.setCurrentText(note)
                        break
    changeScaleOrChord()

def toggleTransparency(label):
    if not label.transparency:
        ui.opacity_effect = QtWidgets.QGraphicsOpacityEffect()
        ui.opacity_effect.setOpacity(0.3)
    else:
        ui.opacity_effect = QtWidgets.QGraphicsOpacityEffect()
        ui.opacity_effect.setOpacity(1.0)
    label.setGraphicsEffect(ui.opacity_effect)
    label.transparency = not label.transparency

def setFret(fret):
    # Set new fret selection
    if not ui.fretSelected:
        # Is this the first or the second fret selected in the range?
        ui.fretSelected = True
        ui.firstFretSelected = fret
        for row in ui.labels:
            try:
                index = fret - ui.frets[0]
                if ui.frets[0] == 0:
                    index = index - 1
                row[index].setStyleSheet("QLabel"
                    "{"
                    f"{interval_colors['m']}"
                    "}")
                ui.statusbar.showMessage("Click the next fret to zoom in on the fretboard.", 10000)
            except IndexError:
                pass
    else:
        # If second, we set up the new fret tuple and rebuild.
        ui.fretSelected = False
        ui.secondFretSelected = fret
        if ui.firstFretSelected != ui.secondFretSelected:
            ui.frets_old = ui.frets
            ui.frets = (ui.firstFretSelected, ui.secondFretSelected)
            ui.frets = tuple(sorted(ui.frets)) # You can select in any order.
            update()
            ui.statusbar.showMessage(f"Zooming in on frets {str(ui.frets[0])} to {str(ui.frets[1])}.", 10000)
        else:
            update()
            ui.statusbar.showMessage("Reverting to previous fret selection.", 10000)

    ui.rootNoteSelector.setFocus()

def clearFromGrid(widget):
    ui.gridLayout.removeWidget(widget)
    widget.setParent(None)
    widget.deleteLater()

def update():
    # Updates the GUI.
    # Track if we are switching between chord and scale or not.
    showChord_old = ui.showChord
    ui.showChord = ui.scaleOrChordSlider.value()
    ui.showInterval = ui.notesOrIntervalsSlider.value()

    # If the note/chord slider is changed, update the corresponding combo box to reflect the change.
    if ui.showChord != showChord_old:
        selection = ui.scaleOrChordTypeSelector.currentText()
        if ui.showChord:
            ui.scaleOrChordTypeSelector.clear()
            ui.scaleOrChordTypeSelector.addItems(ui.allChords)
            # Try to switch to minor if we're in minor.
            if ('minor' in selection) or (selection == 'aeolian'):
                ui.scaleOrChordTypeSelector.setCurrentText('min')
            type = ui.scaleOrChordTypeSelector.currentText()
            root = ui.rootNoteSelector.currentText()
            ui.chord = Chord(Note(root), type)
        else:
            ui.scaleOrChordTypeSelector.clear()
            ui.scaleOrChordTypeSelector.addItems(ui.allScales)
            if 'min' in selection:
                ui.scaleOrChordTypeSelector.setCurrentText('natural_minor')
            type = ui.scaleOrChordTypeSelector.currentText()
            root = ui.rootNoteSelector.currentText()
            ui.scale = Scale(Note(root), type)

    # Re-build the labels. First remove the old ones.
    for row in ui.labels:
        for label in row:
            clearFromGrid(label)

    # Remove the buttons as well.
    for button in ui.fretButtons:
        clearFromGrid(button)

    # And the fret lines:
    for line in ui.lines:
        clearFromGrid(line)

    # And the dots:
    for dot in ui.fretMarkers:
        clearFromGrid(dot)

    # Generate the new notes and intervals.
    f = Fretboard(tuning=ui.tuning)
    if ui.showChord:
        notes, intervals = f.build(chord=ui.chord, frets=ui.frets)
    else:
        notes, intervals = f.build(scale=ui.scale, frets=ui.frets)

    # Generate and populate the new fretboard.
    populateFretboard(ui, notes, intervals, ui.frets)

    # Show the notes in the chord or scale in the title label.
    if ui.showChord:
        type = "chord"
        notesString = "  ".join([str(n) for n in ui.chord.notes])
        #intervalsString = ", ".join(ui.chord.recipes[ui.chord.chord_type])
    else:
        type = "scale"
        notesString = "  ".join([str(n) for n in ui.scale.notes])
        #intervalsString = ", ".join([str(i) for i in ui.scale.intervals])

    ui.titleLabel.setText(f"{translate(ui.rootNoteSelector.currentText())} {ui.scaleOrChordTypeSelector.currentText()} {type}: {translate(notesString)}") # {translate(intervalsString)}")
    title = ui.titleLabel.text()
    try:
        for string in replacementStrings.keys():
            title = title.replace(string, replacementStrings[string])
        ui.titleLabel.setText(title)
    except:
        pass

    # Resize window if number of frets has changed.
    if ( (ui.frets_old != ui.frets) or (ui.resize == True) ):
        MainWindow.resize(MainWindow.minimumSizeHint())
        MainWindow.adjustSize()
        ui.frets_old = ui.frets
        ui.resize = False

def tuning(string):
    # Deal with changes in tuning from one of the tuning peg input boxes.
    old = ui.tuning[string]
    ui.tuningButtons[string].setText(ui.tuningButtons[string].text().capitalize())
    new = ui.tuningButtons[string].text()

    match = False
    for row in ui.enharmonics:
        for note in row:
            if new == note:
                match = True

    if not match:
        ui.statusbar.showMessage(f"Not a valid tuning, reverting to {old}", 10000)
        ui.tuningButtons[string].setText(translate(old))
    elif old != new:
        ui.tuning[string] = new
        ui.statusbar.showMessage(f"Tuning is now {''.join(ui.tuning)}", 10000)
        update()

def resetFrets():
    ui.frets = ui.resetFrets
    update()
    ui.rootNoteSelector.setFocus()

def changeScaleOrChord():
    # Change from scale to chord or back.
    try:
        delattr(ui, chord)
    except NameError:
        try:
            delattr(ui, scale)
        except NameError:
            pass

    type = ui.scaleOrChordTypeSelector.currentText()
    root = ui.rootNoteSelector.currentText()
    if ui.showChord:
        ui.chord = Chord(Note(root), type)
        ui.statusbar.showMessage(f"{root} {type}", 10000)
    else:
        ui.scale = Scale(Note(root), type)
        ui.statusbar.showMessage(f"{root} {type}", 10000)
    update()

def toggle(thing):
    if thing == 'intervals':
        if ui.notesOrIntervalsSlider.value() == 1:
            ui.notesOrIntervalsSlider.setValue(0)
        else:
            ui.notesOrIntervalsSlider.setValue(1)
    elif thing == 'chord':
        if ui.scaleOrChordSlider.value() == 1:
            ui.scaleOrChordSlider.setValue(0)
        else:
            ui.scaleOrChordSlider.setValue(1)
    elif thing == 'majmin':
        if ui.scaleOrChordSlider.value() == 1:
            if 'maj' in ui.scaleOrChordTypeSelector.currentText():
                ui.scaleOrChordTypeSelector.setCurrentText('min')
                changeScaleOrChord()
            else:
                ui.scaleOrChordTypeSelector.setCurrentText('maj')
                changeScaleOrChord()
        else:
            if ('major' in ui.scaleOrChordTypeSelector.currentText()) or (ui.scaleOrChordTypeSelector.currentText() == 'ionian'):
                ui.scaleOrChordTypeSelector.setCurrentText('natural_minor')
                changeScaleOrChord()
            else:
                ui.scaleOrChordTypeSelector.setCurrentText('major')
                changeScaleOrChord()

    ui.rootNoteSelector.setFocus()
    return

def select(thing):
    if thing == 'mode':
        ui.scaleOrChordTypeSelector.setFocus()
    elif thing == 'root':
        ui.rootNoteSelector.setFocus()
    elif thing == 'tuning':
        ui.tuningButtons[0].setFocus()
        ui.tuningButtons[0].selectAll()
        ui.statusbar.showMessage("Change tuning. Tab or Enter to set new tuning, Esc to return.", 10000)
    return

def helpMessage(showWindow):
    ui.statusbar.showMessage("Press '?' to see list of commands and hotkeys.", 100000)
    if showWindow:
        helpDialog.show()

def initialSetup(ui):
    ui.showChord = False
    ui.showInterval = False
    ui.fretSelected = False
    ui.resize = False

    # List of all the options for Chord() and Scale()
    ui.allScales = [ s for s in Scale.scales.keys() ]
    ui.allChords = [ c for c in Chord.valid_types ]
    ui.scaleOrChordTypeSelector.addItems(ui.allScales)

    ui.notesOrIntervalsSlider.valueChanged['int'].connect(update)
    ui.scaleOrChordSlider.valueChanged['int'].connect(update)
    ui.nutButton.clicked.connect(resetFrets)
    ui.rootNoteSelector.activated.connect(changeScaleOrChord)
    ui.scaleOrChordTypeSelector.activated.connect(changeScaleOrChord)

    ui.rootNoteSelector.notesOrIntervals.connect(lambda thing='intervals': toggle(thing) )
    ui.rootNoteSelector.chordOrScale.connect(lambda thing='chord': toggle(thing) )
    ui.rootNoteSelector.nut.connect(resetFrets)
    ui.rootNoteSelector.mode.connect(lambda thing='mode': select(thing))
    ui.rootNoteSelector.tuning.connect(lambda thing='tuning': select(thing))
    ui.rootNoteSelector.majmin.connect(lambda thing='majmin': toggle(thing))
    ui.rootNoteSelector.help.connect(lambda window=True: helpMessage(window))

    ui.scaleOrChordTypeSelector.notesOrIntervals.connect(lambda thing='intervals': toggle(thing) )
    ui.scaleOrChordTypeSelector.chordOrScale.connect(lambda thing='chord': toggle(thing) )
    ui.scaleOrChordTypeSelector.nut.connect(resetFrets)
    ui.scaleOrChordTypeSelector.root.connect(lambda thing='root': select(thing))
    ui.scaleOrChordTypeSelector.tuning.connect(lambda thing='tuning': select(thing))
    ui.scaleOrChordTypeSelector.majmin.connect(lambda thing='majmin': toggle(thing))
    ui.scaleOrChordTypeSelector.help.connect(helpMessage)

    ui.nutButton.setFocusPolicy(QtCore.Qt.ClickFocus)

    ui.scale = Scale(Note('C'), 'major')

    for i, t in enumerate(ui.tuningButtons):
        t.returnPressed.connect(lambda string=i: tuning(string))
        t.escape.connect(lambda thing='root': select(thing))

    ui.frets_old = ui.frets

    f = Fretboard(tuning=ui.tuning)
    notes, intervals = f.build(scale=ui.scale, frets=ui.frets)

    ui.enharmonics = f.enharmonics

    ui.rootNotes = ['C',
                 'C#',
                 'Db',
                 'D',
                 'D#',
                 'Eb',
                 'E',
                 'F',
                 'F#',
                 'Gb',
                 'G',
                 'G#',
                 'Ab',
                 'A',
                 'A#',
                 'Bb',
                 'B',]

    ui.rootNoteSelector.addItems(ui.rootNotes)
    populateFretboard(ui, notes, intervals, ui.frets)

    MainWindow.resize(MainWindow.minimumSizeHint())
    MainWindow.adjustSize()

    helpMessage(False)  # Just show the prompt in the status bar.

    ui.rootNoteSelector.setFocus()
    return(True)

def editSettings():
    #webbrowser.open(settingsFile)
    DEFAULT_EDITOR = '/usr/bin/vi' # backup, if not defined in environment vars
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    file = os.path.join(__location__, settingsFile)
    editor = os.environ.get('EDITOR', DEFAULT_EDITOR)
    subprocess.call([editor, file])
    sys.exit()

def setupHelpDialog(helpDialog):
    helpDialogUi = HelpDialog()
    helpDialogUi.setupUi(helpDialog)
    helpDialogUi.OKButton.clicked.connect(helpDialog.hide)
    helpDialogUi.editButton.clicked.connect(editSettings)

    for i, row in enumerate(helpMessages):
        text1 = row[0]
        text2 = row[1]
        label1, label2 = [ QtWidgets.QLabel(helpDialog) for i in range(2) ]
        label1.setText(text1)
        label1.setAlignment(QtCore.Qt.AlignCenter)
        label2.setText(text2)
        helpDialogUi.gridLayout.addWidget(label1, i, 0, 1, 1)
        helpDialogUi.gridLayout.addWidget(label2, i, 1, 1, 1)

    helpDialog.setWindowTitle("Commands and hotkeys")
    helpDialog.setWindowIcon(QtGui.QIcon(":/icons/guitar.png"))
    helpDialog.resize(helpDialog.minimumSizeHint())
    helpDialog.adjustSize()
    helpDialog.hide()

def writeSettings(settings):
    with open(settingsFile, 'w') as f:
        json.dump(settings, f)

class MyMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

    def closeEvent(self, event):
        settings = {
            'tuning':   ui.tuning,
            'strings':  ui.strings,
            'frets':    ui.frets,
            'resetFrets': ui.resetFrets,
            'title':    MainWindow.windowTitle(),
            'markers':  ui.markers,
        }
        print(f"Writing settings to {settingsFile}.")
        writeSettings(settings)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MyMainWindow()

    helpDialog = QtWidgets.QDialog()
    setupHelpDialog(helpDialog)
    ui = Ui_MainWindow()

    # First load settings from file if available
    try:
        with open(settingsFile, 'r') as f:
            settings = json.load(f)
            ui.tuning = settings['tuning']
            ui.strings = settings['strings']
            ui.frets = settings['frets']
            ui.title = settings['title']
            ui.markers = settings['markers']
            ui.resetFrets = settings['resetFrets']
    except:
        ui.tuning = ['B', 'E', 'A', 'D', 'G', 'B', 'E']
        ui.tuning = ui.tuning[1:]
        ui.strings = 6
        ui.frets = (0,24)
        ui.title = "Guitar fretboard, scales and chords"
        ui.markers = {
            'single':   [3, 5, 7, 9, 15, 17, 19, 21],
            'double':   [12]
        }
        ui.resetFrets = ui.frets

    # Set up and parse CLI arguments
    allScales = [ s for s in Scale.scales.keys() ]
    allChords = [ c for c in Chord.valid_types ]
    rootNotes = ['C','C#','Db','D','D#','Eb','E','F','F#','Gb','G','G#','Ab','A','A#','Bb','B',]
    parser = argparse.ArgumentParser(description=f"Select rootnote and type for the scale or chord, as well as other parameters as listed below. The available scales are {allScales} and the available chords are {allChords}.")
    parser.add_argument('-r', '--rootnote',
                        choices=rootNotes,
                        default='C',
                        help="The root note of the scale or chord.")
    parser.add_argument('-t', '--type',
                        choices=allScales+allChords,
                        default='major',
                        help="The type of scale or chord.")
    parser.add_argument('-ff', '--fromfret', type=int, help="The first fret of the fret interval.",
                        choices=range(1,25))
    parser.add_argument('-tf', '--tofret', type=int, help="The last fret of the fret interval.",
                        choices=range(1,25))
    parser.add_argument('-p', '--preset', choices=['ukulele', 'guitar', '7-string', 'banjo'], help="Presets for type of instrument. Edit the fretboard_settings.json for more options.")
    parser.parse_args()

    args = parser.parse_args()

    if args.preset:
        if args.preset == 'ukulele':
            ui.tuning = ['G', 'C', 'E', 'A']
            ui.strings = 4
            ui.frets = (0,17)
            ui.resetFrets = ui.frets
            ui.title = "Ukulele"
            ui.markers = {
                'single':   [3, 5, 7, 10, 15, 17, 19],
                'double':   [12]
            }
        elif args.preset == 'guitar':
            ui.tuning = ['B', 'E', 'A', 'D', 'G', 'B', 'E']
            ui.tuning = ui.tuning[1:]
            ui.strings = 6
            ui.frets = (0,24)
            ui.resetFrets = ui.frets
            ui.title = "6-string guitar"
            ui.markers = {
                'single':   [3, 5, 7, 9, 15, 17, 19, 21],
                'double':   [12]
            }
        elif args.preset == '7-string':
            ui.tuning = ['B', 'E', 'A', 'D', 'G', 'B', 'E']
            ui.strings = 7
            ui.frets = (0,24)
            ui.resetFrets = ui.frets
            ui.title = "7-string guitar"
            ui.markers = {
                'single':   [3, 5, 7, 9, 15, 17, 19, 21],
                'double':   [12]
            }
        elif args.preset == 'banjo':
            ui.tuning = ['G', 'D', 'G', 'B', 'D']
            ui.strings = 5
            ui.frets = (0,24)
            ui.resetFrets = ui.frets
            ui.title = "Banjo"
            ui.markers = {
                'single':   [3, 5, 7, 10, 15, 17, 19, 22],
                'double':   [12]
            }

    # Initial setup of the UI
    ui.setupUi(MainWindow, strings=ui.strings)
    MainWindow.setWindowIcon(QtGui.QIcon(":/icons/guitar.png"))
    MainWindow.setWindowTitle(ui.title)
    success = initialSetup(ui)

    # Set frets from CLI if available
    if ( not args.preset ):
        if ( args.tofret and args.fromfret):
            ui.frets = tuple([args.fromfret, args.tofret])
            ui.frets = tuple(sorted(ui.frets))
            ui.resize = True

    root = args.rootnote
    type = args.type

    if type in ui.allScales:
        ui.scale = Scale(Note(root), type)
        ui.rootNoteSelector.setCurrentText(root)
        ui.scaleOrChordTypeSelector.setCurrentText(type)
    else:
        ui.chord = Chord(Note(root), type)
        ui.showChord = True
        ui.scaleOrChordSlider.setValue(1)
        ui.scaleOrChordTypeSelector.clear()
        ui.scaleOrChordTypeSelector.addItems(ui.allChords)
        ui.rootNoteSelector.setCurrentText(root)
        ui.scaleOrChordTypeSelector.setCurrentText(type)

    update()

    if success:
        MainWindow.show()
        sys.exit(app.exec_())
    else:
        sys.exit()
