"""
SamplerCore Module
==================
Core class that manages the MIDI sampler functionality.
"""

import numpy as np
from Engine.sample_bank import Sample_Bank
from Engine.recorder import Recorder
from Engine.miditrigger import MidiTrigger
from Engine.editor import Editor


class SamplerCore:
    """Core class that coordinates all sampler components."""

    # ── Initialization ─────────────────────────────────────────────────────

    def __init__(self, main_window=None):
        self.main_window = main_window
        self.bank = Sample_Bank(main_window=main_window)
        self.recorder = Recorder(main_window=main_window)
        self.editor = Editor(self.bank)
        self.trigger = MidiTrigger(self.bank)
        self.trigger.start_listening()

    # ── Sample Management ──────────────────────────────────────────────────

    def add_sample(self, slot, sample):
        """Add a sample to the specified slot and map to MIDI note."""
        self.bank.sample_slots[slot] = sample
        self.bank.crude_slots[slot] = sample.copy()
        self.bank.envelope_arrays[slot] = np.ones(len(sample), dtype=np.float32)
        midi_note = 28 + slot
        self.bank.note_map[midi_note] = slot

    def play_slot(self, slot):
        """Play the sample in the specified slot."""
        sample = self.bank.sample_slots[slot]
        if sample is not None:
            self.trigger.voices.append({
                'slot': slot,
                'sample': sample.astype(np.float32),
                'pointer': 0,
            })

    def toggle_mute(self, slot):
        """Toggle mute state for the specified slot."""
        self.editor.edit_mute(slot, not self.bank.mutes[slot])

    # ── Recording ──────────────────────────────────────────────────────────

    def start_recording(self):
        """Start recording audio input."""
        self.recorder.start_recording()

    def stop_recording(self):
        """Stop recording and return the recorded sample."""
        return self.recorder.stop_recording()

    # ── Playback ───────────────────────────────────────────────────────────

    def stop_playback(self):
        """Stop all audio playback."""
        self.trigger.stop_playback()
