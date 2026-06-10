"""
Sample_Bank Module
==================
Manages sample storage, project save/load, and audio parameters.
"""

import numpy as np
import pickle
from PyQt5.QtWidgets import QFileDialog


class Sample_Bank:
    """Manages 64 sample slots with their audio parameters."""

    # ── Initialization ─────────────────────────────────────────────────────

    def __init__(self, main_window=None):
        self.main_window = main_window
        self.sample_slots = [None] * 64
        self.crude_slots = [None] * 64
        self.envelope_arrays = [None] * 64
        self.slot_index = 0
        self.midi_note = 28
        self.note_map = {}
        self.samples = []
        self.padded = []

        # Audio parameters per slot
        self.volumes = [1.0] * 64
        self.mutes = [False] * 64
        self.pans = [0.5] * 64
        self.eq_low = [1.0] * 64
        self.eq_mid = [1.0] * 64
        self.eq_high = [1.0] * 64
        self.attacks = [0] * 64
        self.decays = [0] * 64
        self.sustains = [1.0] * 64
        self.releases = [0] * 64

    # ── Sample Management ──────────────────────────────────────────────────

    def add_sample_to_slot(self, recording):
        """Add a recording to the current slot and increment slot index."""
        self.sample_slots[self.slot_index] = recording
        self.crude_slots[self.slot_index] = recording.copy()
        self.envelope_arrays[self.slot_index] = np.ones(len(recording), dtype=np.float32)
        self.note_map[28 + self.slot_index] = self.slot_index
        self.slot_index += 1

    def overview(self):
        """Print overview of all slots."""
        for i in range(64):
            sample = self.sample_slots[i]
            if sample is None:
                print(f"{i:02d} : empty")
            else:
                print(f"{i:02d} : sample ({len(sample)})")

    # ── Project Save ───────────────────────────────────────────────────────

    def save_project(self, project_name):
        """Save project with optimized storage (only used slots)."""
        try:
            used_slots = {}
            for i in range(64):
                if self.sample_slots[i] is not None:
                    used_slots[i] = {
                        'sample': self.sample_slots[i],
                        'crude': self.crude_slots[i],
                        'envelope': self.envelope_arrays[i],
                        'volume': self.volumes[i],
                        'pan': self.pans[i],
                        'mute': self.mutes[i],
                        'eq_low': self.eq_low[i],
                        'eq_mid': self.eq_mid[i],
                        'eq_high': self.eq_high[i],
                        'attack': self.attacks[i],
                        'decay': self.decays[i],
                        'sustain': self.sustains[i],
                        'release': self.releases[i],
                    }

            project_data = {
                'version': '2.0',
                'used_slots': used_slots,
                'slot_index': self.slot_index,
                'note_map': self.note_map,
            }

            file_name = project_name + ".pkl"
            with open(file_name, 'wb') as file:
                pickle.dump(project_data, file, protocol=pickle.HIGHEST_PROTOCOL)

            print(f"Project saved: {len(used_slots)} samples")

        except PermissionError:
            print("Error: Permission denied - cannot save to this location")
            if self.main_window:
                self.main_window.show_error("Save Failed", "Permission denied - cannot save to this location")

        except FileNotFoundError:
            print("Error: Directory not found - check the file path")
            if self.main_window:
                self.main_window.show_error("Save Failed", "Directory not found - check the file path")

        except Exception as e:
            print(f"Error: Failed to save project - {e}")
            if self.main_window:
                self.main_window.show_error("Save Failed", f"Failed to save project: {str(e)}")

    # ── Project Load ───────────────────────────────────────────────────────

    def load_project(self, project_name):
        """Load project from file with error handling."""
        try:
            file_name = project_name + ".pkl"
            with open(file_name, 'rb') as file:
                project_data = pickle.load(file)

            # Reset all slots first
            self._reset_all_slots()

            # Check if this is new format or old format
            if 'used_slots' in project_data:
                self._load_new_format(project_data)
            else:
                self._load_old_format(project_data)

            # Load common fields
            self.slot_index = project_data.get('slot_index', 0)
            self.note_map = project_data.get('note_map', {})

            print(f"Project loaded: {len(project_data.get('used_slots', project_data.get('sample_slots', [])))} samples")

        except FileNotFoundError:
            print(f"Error: Project file not found - {project_name}.pkl")
            if self.main_window:
                self.main_window.show_error("Load Failed", f"Project file not found: {project_name}.pkl")

        except pickle.PickleError:
            print("Error: Corrupted project file")
            if self.main_window:
                self.main_window.show_error("Load Failed", "Corrupted project file - cannot load")

        except KeyError as e:
            print(f"Error: Invalid project format - missing {e}")
            if self.main_window:
                self.main_window.show_error("Load Failed", f"Invalid project format - missing {str(e)}")

        except Exception as e:
            print(f"Error: Failed to load project - {e}")
            if self.main_window:
                self.main_window.show_error("Load Failed", f"Failed to load project: {str(e)}")

    def _reset_all_slots(self):
        """Reset all slots to default values."""
        self.sample_slots = [None] * 64
        self.crude_slots = [None] * 64
        self.envelope_arrays = [None] * 64
        self.volumes = [1.0] * 64
        self.mutes = [False] * 64
        self.pans = [0.5] * 64
        self.eq_low = [1.0] * 64
        self.eq_mid = [1.0] * 64
        self.eq_high = [1.0] * 64
        self.attacks = [0] * 64
        self.decays = [0] * 64
        self.sustains = [1.0] * 64
        self.releases = [0] * 64

    def _load_new_format(self, project_data):
        """Load project in new format (used_slots)."""
        for slot_id, slot_data in project_data['used_slots'].items():
            self.sample_slots[slot_id] = slot_data['sample']
            self.crude_slots[slot_id] = slot_data['crude']
            self.envelope_arrays[slot_id] = slot_data['envelope']
            self.volumes[slot_id] = slot_data.get('volume', 1.0)
            self.pans[slot_id] = slot_data.get('pan', 0.5)
            self.mutes[slot_id] = slot_data.get('mute', False)
            self.eq_low[slot_id] = slot_data.get('eq_low', 1.0)
            self.eq_mid[slot_id] = slot_data.get('eq_mid', 1.0)
            self.eq_high[slot_id] = slot_data.get('eq_high', 1.0)
            self.attacks[slot_id] = slot_data.get('attack', 0)
            self.decays[slot_id] = slot_data.get('decay', 0)
            self.sustains[slot_id] = slot_data.get('sustain', 1.0)
            self.releases[slot_id] = slot_data.get('release', 0)

    def _load_old_format(self, project_data):
        """Load project in old format (sample_slots)."""
        self.sample_slots = project_data['sample_slots']
        self.crude_slots = project_data['crude_slots']
        self.envelope_arrays = project_data.get('envelope_arrays', [None] * 64)
        self.volumes = project_data.get('volumes', [1.0] * 64)
        self.mutes = project_data.get('mutes', [False] * 64)
        self.pans = project_data.get('pans', [0.5] * 64)
        self.eq_low = project_data.get('eq_low', [1.0] * 64)
        self.eq_mid = project_data.get('eq_mid', [1.0] * 64)
        self.eq_high = project_data.get('eq_high', [1.0] * 64)
        self.attacks = project_data.get('attacks', [0] * 64)
        self.decays = project_data.get('decays', [0] * 64)
        self.sustains = project_data.get('sustains', [1.0] * 64)
        self.releases = project_data.get('releases', [0] * 64)

    # ── File Dialogs ───────────────────────────────────────────────────────

    def open_project(self):
        """Open file dialog to select and load a project."""
        path, _ = QFileDialog.getOpenFileName(None, "Open Project", "", "Project Files (*.pkl)")
        if path:
            name = path.replace(".pkl", "")
            self.load_project(name)
            return name
        return None

    def save_project_as(self):
        """Open file dialog to select save location and save project."""
        path, _ = QFileDialog.getSaveFileName(None, "Save Project As", "", "Project Files (*.pkl)")
        if path:
            name = path.replace(".pkl", "")
            self.save_project(name)
            return name
        return None
