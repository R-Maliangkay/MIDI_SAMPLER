"""
MainWindow Module
=================
Main application window with UI controls and device selection.
"""

from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt, QTimer
from ui_files.selection_menu import SelectionMenu
from ui_files.lcd import LCD
import sounddevice as sd
import mido
import sys
import os


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class MainWindow(QtWidgets.QMainWindow):
    """Main application window."""

    # ── Initialization ─────────────────────────────────────────────────────

    def __init__(self, core):
        super().__init__()
        uic.loadUi(resource_path('UI1.ui'), self)
        self.core = core
        self.current_slot = 0
        self.lcd = LCD(self)
        self.current_project_path = None

        self.activated = {
            'attack': False, 'decay': False, 'sustain': False, 'release': False,
            'volume': False, 'pan': False,
            'eq_low': False, 'eq_mid': False, 'eq_high': False,
        }

        # Menu bar - File
        self.actionOpen.triggered.connect(self.menu_open)
        self.actionSave.triggered.connect(self.menu_save)
        self.actionSave_as.triggered.connect(self.core.bank.save_project_as)
        self.actionSave.setEnabled(False)

        # Menu bar - Edit
        self.actionUndo.triggered.connect(self.on_undo)
        self.actionRedo.triggered.connect(self.on_redo)

        # Menu bar - Settings
        self.actionSelect_Audio_Input.triggered.connect(self.select_audio_input)
        self.actionSelect_Audio_Output.triggered.connect(self.select_audio_output)
        self.actionSelect_Slot.triggered.connect(self.select_slot_dialog)
        self.actionSelect_MIDI_Channel.triggered.connect(self.select_midi_channel_dialog)

        # Selection menu
        self.selection_menu = SelectionMenu(core.bank, self, core)

        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self.on_undo)
        QShortcut(QKeySequence("Ctrl+Alt+Z"), self).activated.connect(self.on_redo)

        # Transport buttons
        self.select_left.clicked.connect(self.selection_menu.select_slot)
        self.select_right.clicked.connect(self.selection_menu.select_channel)
        self.enter.clicked.connect(self.selection_menu.handle_enter)

        # Number buttons
        for i in range(10):
            button = getattr(self, f'button_{i}')
            button.clicked.connect(lambda checked, num=i: self.selection_menu.number_input(num))

        # Dial configuration
        self.dial.setImage(resource_path('Images/dial.png'))
        self.dial.setScale(0.09)
        self.dial.setOffset(-2, 5)
        self.dial.setMaskScale(0.8)
        self.dial.setMaskOffset(0, 5)
        self.dial.setRotationOffset(135)

        # Lamp images
        img_on = resource_path('Images/lamp_on.png')
        img_off = resource_path('Images/lamp_off.png')
        for lamp in [self.label_lamp_rec, self.label_lamp_play, self.label_lamp_stop, self.label_lamp_mute]:
            lamp.setImages(img_on, img_off)

        # Transport connections
        self.rec.clicked.connect(self.on_record)
        self.play.clicked.connect(self.on_play)
        self.stop.clicked.connect(self.on_stop)
        self.mute.stateChanged.connect(self.on_mute)

        # Envelope sliders
        self.slider_a.valueChanged.connect(self.on_attack_changed)
        self.slider_d.valueChanged.connect(self.on_decay_changed)
        self.slider_s.valueChanged.connect(self.on_sustain_changed)
        self.slider_r.valueChanged.connect(self.on_release_changed)

        # Volume and pan
        self.dial.valueChanged.connect(self.on_volume_changed)
        self.horizontalSlider.valueChanged.connect(self.on_pan_changed)

        # EQ sliders
        self.slider_l.valueChanged.connect(self.on_low_changed)
        self.slider_m.valueChanged.connect(self.on_mid_changed)
        self.slider_h.valueChanged.connect(self.on_high_changed)

        # Device status
        self.audio_input()
        self.audio_output()
        self.show_midi_device()

    # ── Helpers ────────────────────────────────────────────────────────────

    def switch_lamp(self, active_lamp):
        """Turn off all lamps except the active one."""
        for lamp in [self.label_lamp_rec, self.label_lamp_play, self.label_lamp_stop]:
            lamp.turnOff()
        active_lamp.turnOn()

    def is_active(self, key):
        """Check if control needs first activation before editing."""
        if self.activated[key] == False:
            self.activated[key] = True
            return False
        else:
            return True

    def reset_activated(self):
        """Reset all controls to require first activation."""
        for key in self.activated:
            self.activated[key] = False

    # ── Undo / Redo ────────────────────────────────────────────────────────

    def on_undo(self):
        """Undo last edit operation."""
        snapshot = self.core.editor.undo()
        if snapshot is not None:
            self.sync_ui_from_snapshot(snapshot)

    def on_redo(self):
        """Redo last undone edit operation."""
        snapshot = self.core.editor.redo()
        if snapshot is not None:
            self.sync_ui_from_snapshot(snapshot)

    def sync_ui_from_snapshot(self, snapshot):
        """Update UI controls from a snapshot."""
        slot = self.current_slot

        for widget in [self.slider_a, self.slider_d, self.slider_s, self.slider_r,
                       self.slider_l, self.slider_m, self.slider_h,
                       self.horizontalSlider]:
            widget.blockSignals(True)

        self.slider_a.setValue(snapshot['attacks'][slot])
        self.slider_d.setValue(snapshot['decays'][slot])
        self.slider_s.setValue(int(snapshot['sustains'][slot] * 100))
        self.slider_r.setValue(snapshot['releases'][slot])
        self.slider_l.setValue(int((snapshot['eq_low'][slot] - 1.0) * 100))
        self.slider_m.setValue(int((snapshot['eq_mid'][slot] - 1.0) * 100))
        self.slider_h.setValue(int((snapshot['eq_high'][slot] - 1.0) * 100))
        self.horizontalSlider.setValue(int(snapshot['pans'][slot] * 100))
        self.dial.setValue(int(snapshot['volumes'][slot] * 100))

        for widget in [self.slider_a, self.slider_d, self.slider_s, self.slider_r,
                       self.slider_l, self.slider_m, self.slider_h,
                       self.horizontalSlider, self.dial]:
            widget.blockSignals(False)

        self.LCD_ATTACK.setText(f"ATTACK:{snapshot['attacks'][slot]}%")
        self.LCD_DECAY.setText(f"DECAY:{snapshot['decays'][slot]}%")
        self.LCD_SUSTAIN.setText(f"SUSTAIN:{int(snapshot['sustains'][slot] * 100)}%")
        self.LCD_RELEASE.setText(f"RELEASE:{snapshot['releases'][slot]}%")
        self.LCD_MAIN.setText(f"MAIN VOL:{int(snapshot['volumes'][slot] * 100)}%")
        self.LCD_PAN.setText(f"PAN:{int(snapshot['pans'][slot] * 100)}%")
        self.LCD_LOW.setText(f"LOW:{int((snapshot['eq_low'][slot] - 1.0) * 100)}%")
        self.LCD_MID.setText(f"MID:{int((snapshot['eq_mid'][slot] - 1.0) * 100)}%")
        self.LCD_HI.setText(f"HIGH:{int((snapshot['eq_high'][slot] - 1.0) * 100)}%")

    # ── Transport ──────────────────────────────────────────────────────────

    def on_record(self):
        """Handle record button press."""
        if self.core.recorder.is_recording == True:
            self.on_stop()
        else:
            self.switch_lamp(self.label_lamp_rec)
            self.core.start_recording()

    def on_play(self):
        """Handle play button press."""
        self.switch_lamp(self.label_lamp_play)
        self.core.play_slot(self.current_slot)

    def on_stop(self):
        """Handle stop button press."""
        self.switch_lamp(self.label_lamp_stop)
        if self.core.recorder.is_recording == True:
            sample = self.core.stop_recording()
            if sample is not None:
                self.core.add_sample(self.current_slot, sample)
                self.reset_activated()
                self.actionSave.setEnabled(True)
        else:
            self.core.stop_playback()

    def on_mute(self, state):
        """Handle mute toggle."""
        muted = state == Qt.Checked

        if muted:
            self.label_lamp_mute.turnOn()
            self.LCD_MUTE.setText("MUTE:ON")
        else:
            self.label_lamp_mute.turnOff()
            self.LCD_MUTE.setText("MUTE:OFF")

        self.core.editor.edit_mute(self.current_slot, muted)

    # ── EQ ─────────────────────────────────────────────────────────────────

    def on_low_changed(self, value):
        """Handle low EQ slider change."""
        if self.is_active('eq_low') == False:
            return
        self.core.editor.edit_eq_3band(self.current_slot, low=1.0 + (value / 100.0))
        self.lcd.update_low(value)

    def on_mid_changed(self, value):
        """Handle mid EQ slider change."""
        if self.is_active('eq_mid') == False:
            return
        self.core.editor.edit_eq_3band(self.current_slot, mid=1.0 + (value / 100.0))
        self.lcd.update_mid(value)

    def on_high_changed(self, value):
        """Handle high EQ slider change."""
        if self.is_active('eq_high') == False:
            return
        self.core.editor.edit_eq_3band(self.current_slot, high=1.0 + (value / 100.0))
        self.lcd.update_high(value)

    # ── Envelopes ──────────────────────────────────────────────────────────

    def on_attack_changed(self, value):
        """Handle attack slider change."""
        if self.is_active('attack') == False:
            return
        self.core.editor.edit_attack(self.current_slot, value)
        self.LCD_ATTACK.setText(f"ATTACK:{value}%")

    def on_decay_changed(self, value):
        """Handle decay slider change."""
        if self.is_active('decay') == False:
            return
        self.core.editor.edit_decay(self.current_slot, value)
        self.LCD_DECAY.setText(f"DECAY:{value}%")

    def on_sustain_changed(self, value):
        """Handle sustain slider change."""
        if self.is_active('sustain') == False:
            return
        self.core.editor.edit_sustain(self.current_slot, value / 100.0)
        self.LCD_SUSTAIN.setText(f"SUSTAIN:{value}%")

    def on_release_changed(self, value):
        """Handle release slider change."""
        if self.is_active('release') == False:
            return
        self.core.editor.edit_release(self.current_slot, value)
        self.LCD_RELEASE.setText(f"RELEASE:{value}%")

    # ── Volume / Pan ───────────────────────────────────────────────────────

    def on_volume_changed(self, value):
        """Handle volume dial change."""
        if self.is_active('volume') == False:
            return
        self.core.editor.edit_volume(self.current_slot, value / 100.0)
        self.LCD_MAIN.setText(f"MAIN VOL:{value}%")

    def on_pan_changed(self, value):
        """Handle pan slider change."""
        if self.is_active('pan') == False:
            return
        self.core.editor.edit_pan(self.current_slot, (value + 50) / 100.0)
        self.LCD_PAN.setText(f"PAN:{value}%")

    # ── Menu bar - File ────────────────────────────────────────────────────

    def menu_open(self):
        """Open project file dialog."""
        path = self.core.bank.open_project()
        if path:
            self.current_project_path = path
            self.reset_activated()

    def menu_save(self):
        """Save current project."""
        if self.current_project_path:
            self.core.bank.save_project(self.current_project_path)
        else:
            path = self.core.bank.save_project_as()
            if path:
                self.current_project_path = path

    # ── Menu bar - Settings ────────────────────────────────────────────────

    def select_audio_input(self):
        """Open dialog to select audio input device."""
        try:
            devices = sd.query_devices()
            input_devices = [d['name'] for d in devices if d['max_input_channels'] > 0]

            if not input_devices:
                self.show_error("No Devices", "No audio input devices found!")
                return

            device, ok = QInputDialog.getItem(self, "Select Device",
                                              "Choose audio input device:",
                                              input_devices, 0, False)
            if ok and device:
                for i, d in enumerate(devices):
                    if d['name'] == device:
                        if hasattr(self.core, 'recorder'):
                            self.core.recorder.device = i
                            self.show_warning("Device Changed",
                                              f"Audio input changed to: {device}")
                            self.audio_input()
                        break

        except Exception as e:
            self.show_error("Error", f"Failed to get devices: {str(e)}")

    def select_audio_output(self):
        """Open dialog to select audio output device."""
        try:
            devices = sd.query_devices()
            output_devices = [d['name'] for d in devices if d['max_output_channels'] > 0]

            if not output_devices:
                self.show_error("No Devices", "No audio output devices found!")
                return

            device, ok = QInputDialog.getItem(self, "Select Device",
                                              "Choose audio output device:",
                                              output_devices, 0, False)
            if ok and device:
                for i, d in enumerate(devices):
                    if d['name'] == device:
                        sd.default.device = (sd.default.device[0], i)
                        self.show_warning("Device Changed",
                                          f"Audio output changed to: {device}")
                        self.audio_output()
                        break

        except Exception as e:
            self.show_error("Error", f"Failed to get devices: {str(e)}")

    def select_slot_dialog(self):
        """Open dialog to select slot (1-64)."""
        try:
            current = self.current_slot + 1
            slot_str, ok = QInputDialog.getText(self, "Select Slot",
                                                f"Enter slot number (1-64):\nCurrent: {current}",
                                                text=str(current))
            if ok and slot_str:
                try:
                    slot_value = int(slot_str)
                    if 1 <= slot_value <= 64:
                        actual_slot = slot_value - 1
                        self.current_slot = actual_slot
                        self.LCD_SLOT.setText(f"SLOT:{slot_value:02d}")
                        self.show_warning("Slot Changed", f"Slot changed to {slot_value}")
                    else:
                        self.show_error("Invalid Input", "Slot must be between 1 and 64!")
                except ValueError:
                    self.show_error("Invalid Input", "Please enter a valid number!")

        except Exception as e:
            self.show_error("Error", f"Failed to select slot: {str(e)}")

    def select_midi_channel_dialog(self):
        """Open dialog to select MIDI channel (1-16)."""
        try:
            current = self.core.trigger.channel
            ch_str, ok = QInputDialog.getText(self, "Select MIDI Channel",
                                              f"Enter MIDI channel (1-16):\nCurrent: {current}",
                                              text=str(current))
            if ok and ch_str:
                try:
                    channel_value = int(ch_str)
                    if 1 <= channel_value <= 16:
                        self.core.trigger.set_channel(channel_value)
                        self.LCD_CH.setText(f"CH:{channel_value:02d}")
                        self.show_warning("Channel Changed", f"MIDI channel changed to {channel_value}")
                    else:
                        self.show_error("Invalid Input", "Channel must be between 1 and 16!")
                except ValueError:
                    self.show_error("Invalid Input", "Please enter a valid number!")

        except Exception as e:
            self.show_error("Error", f"Failed to select channel: {str(e)}")

    # ── Device Status ──────────────────────────────────────────────────────

    def audio_input(self):
        """Update audio input device display."""
        devices = sd.query_devices()
        input_device = devices[self.core.recorder.device]
        name = input_device['name']

        if '(' in name:
            start = name.find('(') + 1
            if ')' in name:
                end = name.find(')')
                display_name = name[start:end]
            else:
                display_name = name[start:]
        else:
            display_name = name[:24]

        self.lcd.update_audio_input(display_name[:24])

    def audio_output(self):
        """Update audio output device display."""
        devices = sd.query_devices()
        output_device_id = sd.default.device[1]
        output_device = devices[output_device_id]
        name = output_device['name']

        if '(' in name:
            start = name.find('(') + 1
            if ')' in name:
                end = name.find(')')
                display_name = name[start:end]
            else:
                display_name = name[start:]
        else:
            display_name = name[:24]

        self.lcd.update_audio_output(display_name[:24])

    def show_midi_device(self):
        """Update MIDI device display."""
        available_ports = mido.get_input_names()

        if available_ports:
            all_devices = ", ".join(available_ports)
            if len(all_devices) > 100:
                all_devices = all_devices[:100] + "..."
            display_name = all_devices
        else:
            display_name = "NO DEVICES FOUND"

        self.lcd.update_midi_device(display_name)

    # ── Dialog Helpers ─────────────────────────────────────────────────────

    def show_error(self, title, message):
        """Show error dialog."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

    def show_warning(self, title, message):
        """Show warning dialog."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()
