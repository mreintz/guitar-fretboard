import json
import argparse
import os
import subprocess
import platform
import sys
import re
from musthe import Note, Chord, Scale
from PyQt5 import QtWidgets, QtCore, QtGui
from fretboard_ui import Ui_MainWindow
from fretboard import Fretboard
from overloadedQtClasses import QLabelClickable
from helpDialog import HelpDialog
import fretboard_rc

play_sounds = False

try:
    from play_sounds import *
    play_sounds = True
except ModuleNotFoundError:
    print("Install the tinysoundfont package if you want sound support.")

SETTINGSFILENAME = "fretboard_settings.json"

CIRCLE_OF_FIFTHS = [
    'Db', 'Ab', 'Eb', 'Bb', 'F', 'C', 'G', 'D', 'A', 'E', 'B', 'F#',
]

help_messages = [
    ['<space>', 'Toggle between scale and chord'],
    ['I',       'Show notes or (I)ntervals'],
    ['N',       'Revert number of frets to (N)ormal'],
    ['Arrows',  'Select root note and type'],
    ['M',       'Toggle between (M)ajor and (M)inor modes'],
    ['Fret buttons',    'Click to zoom in on frets'],
    ['Left click on note', 'Play note if sound support, otherwise toggle transparency'],
    ['Ctrl+Left click on note', 'If sound support, toggle transparency'],
    ['Right click on note', 'Set root note to the note below the cursor'],
    ['Left click on chord or scale', 'Play chord or scale.'],
    ['Right click on chord', 'Arpeggiate the chord'],
    ['<Enter>', 'Play chord or scale'],
    ['?',       'Display this message'],
    ['', ''],
]

LABEL_COLORS = [
    "background-color: rgba(205, 253, 205, 80%);",
    "background-color: rgba(147, 223, 199, 80%);",
    "background-color: rgba(173, 215, 229, 80%);",
    "background-color: rgba(247, 247, 185, 80%);",
    "background-color: rgba(255, 210, 127, 80%);",
    "background-color: rgba(254, 160, 122, 80%);",
    "background-color: rgba(217, 170, 174, 80%);"
]

INTERVAL_COLORS = {
    'm':        "background-color: lightBlue; color: black;",   #labelColors[2],
    'M':        "background-color: lightGreen; color: black;",  #labelColors[0],
    'd':        LABEL_COLORS[6],
    'P':        "background-color: yellow; color: black;",       #"background-color: rgba(220, 220, 170, 80%);",  #labelColors[0],
    'A':        LABEL_COLORS[5],
    'P1':       "background-color: red; color: white; border-color: black;"
}

REPLACEMENT_STRINGS = {
    'dim ':  'diminished ',
    '_':    ' ',
    'min ':  'minor ',
    'maj ':  'major ',
    'aug ':  'augmented '
}

def eighteen_rule():
    """Create fret widths according to the 'rule of eighteen'."""
    full_fretboard = 2000
    first_fret = full_fretboard / 18
    remaining = full_fretboard - first_fret
    fretWidths = [round(first_fret)]
    for i in range(25):
        next_fret = remaining/18
        remaining = remaining - next_fret
        fretWidths.append(round(next_fret))

    return fretWidths

def translate(string):
    """Translate to ascii characters for flats and sharps."""
    string=string.replace('b', '♭')
    string=string.replace('#', '♯')
    return string

def populate_fretboard(ui, notes, intervals, midi, frets):
    """Set up all the labels with notes or intervals on them"""
    ui.labels = []
    if ui.showInterval:
        fretboard = intervals
    else:
        fretboard = notes

    # We don't want to show the tuning after the nut as a fret, so we cut that column out.
    if min(frets) == 0:
        board = []
        for row in fretboard:
            board.append(row[1: frets[1]+1])
        fretboard = board

    # "Flatten" the notes and intervals into a single list for easy lookup.
    flattened_notes = []
    flattened_intervals = []
    for row in notes:
        flattened_notes += row
    for row in intervals:
        flattened_intervals += row

    # Setting up the labels...
    for i, row in enumerate(fretboard):
        label_row = []
        for j, column in enumerate(row, start=1):
            label = QLabelClickable(ui.centralwidget, text=translate(column))
            if column != '':
                if play_sounds:
                    if ui.frets[0] == 0:
                        # Leave out the first fret, as it's the nut.
                        note = midi[i][j]
                    else:
                        note = midi[i][j-1]
                    label.clicked.connect(lambda thing='note', note=note: play(thing, note))
                    label.ctrl_clicked.connect(lambda x=label: toggle_transparency(x))
                else:
                    label.clicked.connect(lambda x=label: toggle_transparency(x))
            else:
                if play_sounds:
                    # Play chord or scale if empty label is clicked.
                    label.clicked.connect(lambda thing='scale': play(thing))
                    label.selected.connect(lambda thing='arpeggio': play(thing))
            label.selected.connect(lambda x=label: select_root_from_label(x))
            label.setMinimumSize(QtCore.QSize(fretWidths[j+1], 40)) #(40, 40))
            label.setMaximumSize(QtCore.QSize(fretWidths[j+1], 40)) #(40, 40))
            label.setObjectName(column)
            font = QtGui.QFont()
            font.setPointSize(12)
            label.setFont(font)
            ui.gridLayout.addWidget(label, i, 2*j+1, 1, 1)
            label_row.append(label)
        ui.labels.append(label_row)

    # Setting up the colors corresponding to the intervals.
    for row in ui.labels:
        for label in row:
            if label.text() != '':
                label.setAlignment(QtCore.Qt.AlignCenter)
                label.setFrameShape(QtWidgets.QFrame.Box)
                label.setLineWidth(3)
                if ui.tooltip:
                    if play_sounds:
                        label.setToolTip('Left click to play note, Ctrl+left click to toggle transparency, right click to set root note.')
                    else:
                        label.setToolTip('Left click to toggle transparency, right click to set root note.')
                if ui.showInterval:
                    interval =  label.objectName()
                    if interval != "P1":
                        intervalType = interval[0]
                    else:
                        intervalType = interval
                else:
                    try:
                        interval = flattened_intervals[flattened_notes.index(label.objectName())]
                        if interval != "P1":
                            intervalType = interval[0]
                        else:
                            intervalType = interval
                    except ValueError:
                        intervalType = ''
                label.setStyleSheet("QLabel"
                            "{"
                            "border : 3px solid ;"
                            f"{INTERVAL_COLORS.get(intervalType, LABEL_COLORS[6])}"
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
    fret_marker = "●"
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
            if ui.tooltip:
                button.setToolTip('Click two fret buttons to set the portion of fretboard to view.')
            ui.gridLayout.addWidget(button, ui.strings, 2*j+1, 1, 1)
            ui.fretButtons.append(button)
            button.clicked.connect(lambda state, x=fret: set_fret(x))
            j = j + 1
        if fret in ( ui.markers['single'] + ui.markers['double'] ):
            dot = QtWidgets.QLabel(ui.centralwidget, text=translate(column))
            dot.setAlignment(QtCore.Qt.AlignCenter)
            if fret in ui.markers['single']:
                dot.setText(fret_marker)
            else:
                dot.setText(fret_marker+fret_marker)
            ui.gridLayout.addWidget(dot, ui.strings+1, 2*j-1, 1, 1)
            ui.fretMarkers.append(dot)

    # Set up the "tuning peg" values and interval colors if open strings are on the chord or scale.
    for i, peg in enumerate(ui.tuningButtons):
        text = ui.tuning[i]
        peg.setStyleSheet("QLineEdit")

        try:
            interval = flattened_intervals[flattened_notes.index(text)]
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
                                f"{INTERVAL_COLORS.get(intervalType, LABEL_COLORS[6])}"
                                "border-color : black"
                                "}")
                else:
                    for enharmonicRow in ui.enharmonics:
                        if (text in enharmonicRow and note in enharmonicRow):
                            interval = flattened_intervals[flattened_notes.index(note)]
                            if interval != "P1":
                                intervalType = interval[0]
                            else:
                                intervalType = interval
                            peg.setStyleSheet("QLineEdit"
                                        "{"
                                        "border : 3px solid ;"
                                        f"{INTERVAL_COLORS.get(intervalType, LABEL_COLORS[6])}"
                                        "border-color : black"
                                        "}")
        peg.rootNote = text
        peg.setText(translate(text))

def select_root_from_label(thing):
    """Selects root note from label click."""
    if isinstance(thing, QLabelClickable):
        selected = thing.objectName()
    elif isinstance(thing, int):
        selected = CIRCLE_OF_FIFTHS[thing-1]
    else:
        selected = thing.rootNote

    # Set the root note to the note right-clicked.
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
    change_scale_or_chord()
    ui.rootNoteSelector.setFocus()

def toggle_transparency(label):
    """Toggle the transparency of a label."""
    if not label.transparency:
        ui.opacity_effect = QtWidgets.QGraphicsOpacityEffect()
        ui.opacity_effect.setOpacity(0.3)
    else:
        ui.opacity_effect = QtWidgets.QGraphicsOpacityEffect()
        ui.opacity_effect.setOpacity(1.0)
    label.setGraphicsEffect(ui.opacity_effect)
    label.transparency = not label.transparency

def set_fret(fret):
    """Set new fret selection."""
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
                    f"{INTERVAL_COLORS['m']}"
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

def clear_from_grid(widget):
    """Clear a widget from the grid."""
    ui.gridLayout.removeWidget(widget)
    widget.setParent(None)
    widget.deleteLater()

def update():
    """Updates the GUI."""
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
            clear_from_grid(label)

    # Remove the buttons as well.
    for button in ui.fretButtons:
        clear_from_grid(button)

    # And the fret lines:
    for line in ui.lines:
        clear_from_grid(line)

    # And the dots:
    for dot in ui.fretMarkers:
        clear_from_grid(dot)

    # Generate the new notes and intervals.
    f = Fretboard(tuning=ui.tuning_with_octave)
    if ui.showChord:
        notes, intervals, midi = f.build(chord=ui.chord, frets=ui.frets)
    else:
        notes, intervals, midi = f.build(scale=ui.scale, frets=ui.frets)

    # Generate and populate the new fretboard.
    populate_fretboard(ui, notes, intervals, midi, ui.frets)

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
        for string in REPLACEMENT_STRINGS.keys():
            title = title.replace(string, REPLACEMENT_STRINGS[string])
        ui.titleLabel.setText(title)
    except:
        pass

    # Resize window if number of frets has changed.
    if ( (ui.frets_old != ui.frets) or (ui.resize == True) ):
        main_window.resize(main_window.minimumSizeHint())
        main_window.adjustSize()
        ui.frets_old = ui.frets
        ui.resize = False

def tune_with_octave(tuning):
    """Set the tuning with octave."""
    ui.tuning_with_octave = tuning
    ui.tuning = [ str(Note(n)) for n in tuning ]
    ui.octaves = []
    for note in tuning:
        try:
            octave = re.findall(r'\d+', note)[0]
        except IndexError:
            octave = ''
        ui.octaves.append(octave)

def tuning(string):
    """Deal with changes in tuning from one of the tuning peg input boxes."""
    old = ui.tuning_with_octave[string]
    string_tuned_with_octave = ui.tuningButtons[string].text().capitalize()
    new = string_tuned_with_octave
    new_text = ''
    new_octave = re.findall(r'\d+', new)
    if new_octave == []:
        new_octave = ui.octaves[string]
        new = new + new_octave
    else:
        new_octave = new_octave[0]
        ui.octaves[string] = new_octave

    try:
        new_text = str(Note(new))
    except ValueError:
        new = old
        new_text = str(Note(new))
    ui.tuningButtons[string].setText(new_text)

    match = False
    for row in ui.enharmonics:
        for note in row:
            if new_text == note:
                match = True

    if not match:
        ui.statusbar.showMessage(f"Not a valid tuning, reverting to {old}", 10000)
        ui.tuningButtons[string].setText(translate(old))
    elif old != new:
        ui.tuning_with_octave[string] = new
        ui.tuning[string] = new_text
        ui.statusbar.showMessage(f"Tuning is now {''.join(ui.tuning)}", 10000)
        update()

def reset_frets():
    """Reset the frets to the number specified in the model for the instrument."""
    ui.frets = ui.resetFrets
    update()
    ui.rootNoteSelector.setFocus()

def change_scale_or_chord():
    """Change from scale to chord or back."""
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
    """Method to toggle several switches."""
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
                change_scale_or_chord()
            else:
                ui.scaleOrChordTypeSelector.setCurrentText('maj')
                change_scale_or_chord()
        else:
            if ('major' in ui.scaleOrChordTypeSelector.currentText()) or (ui.scaleOrChordTypeSelector.currentText() == 'ionian'):
                ui.scaleOrChordTypeSelector.setCurrentText('natural_minor')
                change_scale_or_chord()
            else:
                ui.scaleOrChordTypeSelector.setCurrentText('major')
                change_scale_or_chord()

    ui.rootNoteSelector.setFocus()

def edit_tuning_peg(string):
    """Start editing from the topmost string."""
    ui.tuningButtons[string].setFocus()
    ui.tuningButtons[string].selectAll()

def select(thing):
    """Method to select different widgets."""
    if thing == 'mode':
        ui.scaleOrChordTypeSelector.setFocus()
    elif thing == 'root':
        ui.rootNoteSelector.setFocus()
    elif thing == 'tuning':
        ui.tuningButtons[0].setFocus()
        ui.tuningButtons[0].selectAll()
        ui.statusbar.showMessage("Change tuning. Tab or Enter to set new tuning, Esc to return.", 10000)

def help_message(show_window):
    """Displays help message in statusbar, optionally in separate window."""
    ui.statusbar.showMessage("Press '?' to see list of commands and hotkeys.", 100000)
    if show_window:
        help_dialog.show()
    select('root')

def play(type, *play_args):
    """If sound support, play chords and notes."""
    if play_sounds:
        if type=='note':
            try:
                note = play_args[0]
                play_note(note)
            except ValueError:
                pass
        else:
            if ui.showChord:
                if type == 'arpeggio':
                    play_arpeggio(ui.chord.notes)
                else:
                    play_chord(ui.chord.notes)
            else:
                note = Note(str(ui.scale.notes[0]))
                scale_notes = [(note + i) for i in ui.scale.intervals]
                play_arpeggio(scale_notes)

def echo(val):
    """Echo the value of the circle of fifths slider."""
    ui.statusbar.showMessage(f"Circle of fifths: {CIRCLE_OF_FIFTHS[val-1]}", 10000)

def initial_setup(ui):
    """Initial setup of the UI."""
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
    ui.nutButton.clicked.connect(reset_frets)
    ui.nutButton.rightClicked.connect(lambda window=True: help_message(window))
    ui.rootNoteSelector.activated.connect(change_scale_or_chord)
    ui.scaleOrChordTypeSelector.activated.connect(change_scale_or_chord)

    ui.rootNoteSelector.notesOrIntervals.connect(lambda thing='intervals': toggle(thing) )
    ui.rootNoteSelector.chordOrScale.connect(lambda thing='chord': toggle(thing) )
    ui.rootNoteSelector.nut.connect(reset_frets)
    ui.rootNoteSelector.mode.connect(lambda thing='mode': select(thing))
    ui.rootNoteSelector.tuning.connect(lambda thing='tuning': select(thing))
    ui.rootNoteSelector.majmin.connect(lambda thing='majmin': toggle(thing))
    ui.rootNoteSelector.help.connect(lambda window=True: help_message(window))
    ui.rootNoteSelector.play.connect(lambda thing='scale': play(thing))

    ui.circle_of_fifths.valueChanged['int'].connect(lambda val = ui.circle_of_fifths.value(): select_root_from_label(val))

    ui.scaleOrChordTypeSelector.notesOrIntervals.connect(lambda thing='intervals': toggle(thing) )
    ui.scaleOrChordTypeSelector.chordOrScale.connect(lambda thing='chord': toggle(thing) )
    ui.scaleOrChordTypeSelector.nut.connect(reset_frets)
    ui.scaleOrChordTypeSelector.root.connect(lambda thing='root': select(thing))
    ui.scaleOrChordTypeSelector.tuning.connect(lambda thing='tuning': select(thing))
    ui.scaleOrChordTypeSelector.majmin.connect(lambda thing='majmin': toggle(thing))
    ui.scaleOrChordTypeSelector.help.connect(lambda window=True: help_message(window))
    ui.scaleOrChordTypeSelector.play.connect(lambda thing='scale': play(thing))

    ui.titleLabel.clicked.connect(lambda thing='scale': play(thing))
    ui.titleLabel.selected.connect(lambda thing='arpeggio': play(thing))

    ui.nutButton.setFocusPolicy(QtCore.Qt.ClickFocus)

    ui.scale = Scale(Note('C'), 'major')

    for i, t in enumerate(ui.tuningButtons):
        t.returnPressed.connect(lambda string=i: tuning(string))
        t.escape.connect(lambda thing='root': select(thing))
        t.selected.connect(lambda x=t: select_root_from_label(x))
        t.edit.connect(lambda string=i: edit_tuning_peg(string))

    ui.frets_old = ui.frets

    f = Fretboard(tuning=ui.tuning)
    notes, intervals, midi = f.build(scale=ui.scale, frets=ui.frets)

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
    populate_fretboard(ui, notes, intervals, midi, ui.frets)

    main_window.resize(main_window.minimumSizeHint())
    main_window.adjustSize()

    help_message(False)  # Just show the prompt in the status bar.

    ui.rootNoteSelector.setFocus()
    return(True)

def edit_settings():
    """Edit the settings file."""
    help_dialog.hide()
    main_window.hide()
    main_window.writeSettings = False
    try:
        system = platform.system()
        if system == 'Windows':
            DEFAULT_EDITOR = 'notepad.exe'
        else:
            DEFAULT_EDITOR = 'editor' # backup, if not defined in environment vars

        __location__ = os.getcwd() #os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        editor = os.environ.get('EDITOR', DEFAULT_EDITOR)
        subprocess.call([editor, settingsfile])
    except:
        try:
            import webbrowser
            webbrowser.open(settingsfile)
        except:
            print(f"No default editor found. You need to edit {settingsfile} manually.")
    finally:
        sys.exit()

def setup_help_dialog(help_dialog):
    """Sets up the help dialog."""
    helpDialogUi = HelpDialog()
    helpDialogUi.setupUi(help_dialog)
    helpDialogUi.OKButton.clicked.connect(help_dialog.hide)
    helpDialogUi.editButton.clicked.connect(edit_settings)

    for i, row in enumerate(help_messages):
        text1 = row[0]
        text2 = row[1]
        label1, label2 = [ QtWidgets.QLabel(help_dialog) for i in range(2) ]
        label1.setText(text1)
        label1.setAlignment(QtCore.Qt.AlignCenter)
        label2.setText(text2)
        helpDialogUi.gridLayout.addWidget(label1, i, 0, 1, 1)
        helpDialogUi.gridLayout.addWidget(label2, i, 1, 1, 1)

    help_dialog.setWindowTitle("Commands and hotkeys")
    help_dialog.setWindowIcon(QtGui.QIcon(":/icons/guitar.png"))
    help_dialog.resize(help_dialog.minimumSizeHint())
    help_dialog.adjustSize()
    help_dialog.hide()

def write_settings(settings):
    """Write settings to file."""
    with open(settingsfile, 'w') as f:
        json.dump(settings, f)

class MyMainWindow(QtWidgets.QMainWindow):
    """Extended class for the main window."""
    def __init__(self):
        super().__init__()
        self.writeSettings = True

    def closeEvent(self, event):
        settings = {
            'tuning':   ui.tuning_with_octave,
            'strings':  ui.strings,
            'frets':    ui.frets,
            'resetFrets': ui.resetFrets,
            'title':    main_window.windowTitle(),
            'markers':  ui.markers,
        }
        if self.writeSettings:
            print(f"Writing settings to {SETTINGSFILENAME}.")
            write_settings(settings)
        else:
            print('Not writing settings to file.')

if __name__ == "__main__":
    __location__ = os.getcwd() #os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    settingsfile = os.path.join(__location__, SETTINGSFILENAME)

    fretWidths = eighteen_rule()

    app = QtWidgets.QApplication(sys.argv)
    main_window = MyMainWindow()

    help_dialog = QtWidgets.QDialog()
    setup_help_dialog(help_dialog)
    ui = Ui_MainWindow()
    ui.enharmonics = []
    ui.allScales = []
    ui.allChords = []

    # First load settings from file if available
    try:
        with open(settingsfile, 'r') as f:
            settings = json.load(f)
            loaded_tuning_with_octave = settings['tuning']
            ui.strings = settings['strings']
            ui.frets = settings['frets']
            ui.title = settings['title']
            ui.markers = settings['markers']
            ui.resetFrets = settings['resetFrets']
    except FileNotFoundError:
        print(f"Settings file {settingsfile} not found. Using default settings.")
        loaded_tuning_with_octave = ['B1', 'E2', 'A2', 'D3', 'G3', 'B3', 'E4']
        loaded_tuning_with_octave = loaded_tuning_with_octave[1:]
        ui.strings = 6
        ui.frets = (0,24)
        ui.title = "Guitar fretboard, scales and chords"
        ui.markers = {
            'single':   [3, 5, 7, 9, 15, 17, 19, 21],
            'double':   [12]
        }
        ui.resetFrets = ui.frets
    except json.JSONDecodeError:
        print(f"Error decoding JSON from settings file {settingsfile}. Using default settings.")
        loaded_tuning_with_octave = ['B1', 'E2', 'A2', 'D3', 'G3', 'B3', 'E4']
        loaded_tuning_with_octave = loaded_tuning_with_octave[1:]
        ui.strings = 6
        ui.frets = (0,24)
        ui.title = "Guitar fretboard, scales and chords"
        ui.markers = {
            'single':   [3, 5, 7, 9, 15, 17, 19, 21],
            'double':   [12]
        }
        ui.resetFrets = ui.frets
    except Exception as e:
        print(f"An unexpected error occurred: {e}. Using default settings.")
        loaded_tuning_with_octave = ['B1', 'E2', 'A2', 'D3', 'G3', 'B3', 'E4']
        loaded_tuning_with_octave = loaded_tuning_with_octave[1:]
        ui.strings = 6
        ui.frets = (0,24)
        ui.title = "Guitar fretboard, scales and chords"
        ui.markers = {
            'single':   [3, 5, 7, 9, 15, 17, 19, 21],
            'double':   [12]
        }
        ui.resetFrets = ui.frets

    # Set up and parse CLI arguments
    all_scales = [ s for s in Scale.scales.keys() ]
    all_chords = [ c for c in Chord.valid_types ]
    root_notes = ['C','C#','Db','D','D#','Eb','E','F','F#','Gb','G','G#','Ab','A','A#','Bb','B',]
    parser = argparse.ArgumentParser(description=f"Select rootnote and type for the scale or chord, as well as other parameters as listed below. The available scales are {all_scales} and the available chords are {all_chords}.")
    parser.add_argument('-r', '--rootnote',
                        choices=root_notes,
                        default='C',
                        help="The root note of the scale or chord.")
    parser.add_argument('-t', '--type',
                        choices=all_scales+all_chords,
                        default='major',
                        help="The type of scale or chord.")
    parser.add_argument('-ff', '--fromfret', type=int, help="The first fret of the fret interval.",
                        choices=range(1,25))
    parser.add_argument('-tf', '--tofret', type=int, help="The last fret of the fret interval.",
                        choices=range(1,25))
    parser.add_argument('-p', '--preset', choices=['ukulele', 'guitar', '7-string', 'banjo'], help="Presets for type of instrument. Edit the fretboard_settings.json for more options.")
    parser.add_argument('--notooltip', action='store_true', help="Turns off tooltips.")
    parser.parse_args()

    args = parser.parse_args()

    if args.preset:
        if args.preset == 'ukulele':
            loaded_tuning_with_octave = ['G4', 'C4', 'E4', 'A4']
            ui.strings = 4
            ui.frets = (0,17)
            ui.resetFrets = ui.frets
            ui.title = "Ukulele"
            ui.markers = {
                'single':   [3, 5, 7, 10, 15, 17, 19],
                'double':   [12]
            }
        elif args.preset == 'guitar':
            loaded_tuning_with_octave = ['B1', 'E2', 'A2', 'D3', 'G3', 'B3', 'E4']
            loaded_tuning_with_octave = loaded_tuning_with_octave[1:]
            ui.strings = 6
            ui.frets = (0,24)
            ui.resetFrets = ui.frets
            ui.title = "6-string guitar"
            ui.markers = {
                'single':   [3, 5, 7, 9, 15, 17, 19, 21],
                'double':   [12]
            }
        elif args.preset == '7-string':
            loaded_tuning_with_octave = ['B1', 'E2', 'A2', 'D3', 'G3', 'B3', 'E4']
            ui.strings = 7
            ui.frets = (0,24)
            ui.resetFrets = ui.frets
            ui.title = "7-string guitar"
            ui.markers = {
                'single':   [3, 5, 7, 9, 15, 17, 19, 21],
                'double':   [12]
            }
        elif args.preset == 'banjo':
            loaded_tuning_with_octave = ['G4', 'D3', 'G3', 'B3', 'D4']
            ui.strings = 5
            ui.frets = (0,24)
            ui.resetFrets = ui.frets
            ui.title = "Banjo"
            ui.markers = {
                'single':   [3, 5, 7, 10, 15, 17, 19, 22],
                'double':   [12]
            }

    tune_with_octave(loaded_tuning_with_octave)

    ui.tooltip = not args.notooltip

    # Initial setup of the UI
    ui.setupUi(main_window, ui.tooltip, strings=ui.strings)
    main_window.setWindowIcon(QtGui.QIcon(":/icons/guitar.png"))
    main_window.setWindowTitle(ui.title)
    success = initial_setup(ui)

    # Set frets from CLI if available
    if ( not args.preset ):
        if ( args.tofret and args.fromfret):
            ui.frets = tuple([args.fromfret, args.tofret])
            ui.frets = tuple(sorted(ui.frets))
            ui.resize = True

    root = args.rootnote
    type_of_scale_or_chord = args.type

    if type_of_scale_or_chord in ui.allScales:
        ui.scale = Scale(Note(root), type_of_scale_or_chord)
        ui.rootNoteSelector.setCurrentText(root)
        ui.scaleOrChordTypeSelector.setCurrentText(type_of_scale_or_chord)
    else:
        ui.chord = Chord(Note(root), type_of_scale_or_chord)
        ui.showChord = True
        ui.scaleOrChordSlider.setValue(1)
        ui.scaleOrChordTypeSelector.clear()
        ui.scaleOrChordTypeSelector.addItems(ui.allChords)
        ui.rootNoteSelector.setCurrentText(root)
        ui.scaleOrChordTypeSelector.setCurrentText(type_of_scale_or_chord)

    update()

    if success:
        main_window.show()
        sys.exit(app.exec_())
    else:
        sys.exit()
