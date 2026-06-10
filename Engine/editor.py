"""
Editor Module
=============
Handles audio editing: ADSR, EQ, Volume, Pan, and Undo/Redo.
"""

from Engine.sample_bank import Sample_Bank
import numpy as np
from scipy import signal

SAMPLE_RATE = 48000


class Editor:
    """Audio editor with non-destructive editing and undo/redo support."""

    # ── Initialization ─────────────────────────────────────────────────────

    def __init__(self, bank):
        self.bank = bank
        self.undo_stack = []
        self.redo_stack = []

    # ── Snapshot Helpers ───────────────────────────────────────────────────

    def save_snapshot(self):
        """Save current state to undo stack."""
        snapshot_sample_slots = []
        for sample in self.bank.sample_slots:
            if sample is not None:
                snapshot_sample_slots.append(sample.copy())
            else:
                snapshot_sample_slots.append(None)

        snapshot = {
            'sample_slots': snapshot_sample_slots,
            'eq_low': self.bank.eq_low[:],
            'eq_mid': self.bank.eq_mid[:],
            'eq_high': self.bank.eq_high[:],
            'volumes': self.bank.volumes[:],
            'pans': self.bank.pans[:],
            'attacks': self.bank.attacks[:],
            'decays': self.bank.decays[:],
            'sustains': self.bank.sustains[:],
            'releases': self.bank.releases[:],
        }
        self.undo_stack.append(snapshot)
        self.redo_stack.clear()

    def current_snapshot(self):
        """Get current state without modifying stacks."""
        snapshot_sample_slots = []
        for sample in self.bank.sample_slots:
            if sample is not None:
                snapshot_sample_slots.append(sample.copy())
            else:
                snapshot_sample_slots.append(None)

        return {
            'sample_slots': snapshot_sample_slots,
            'eq_low': self.bank.eq_low[:],
            'eq_mid': self.bank.eq_mid[:],
            'eq_high': self.bank.eq_high[:],
            'volumes': self.bank.volumes[:],
            'pans': self.bank.pans[:],
            'attacks': self.bank.attacks[:],
            'decays': self.bank.decays[:],
            'sustains': self.bank.sustains[:],
            'releases': self.bank.releases[:],
        }

    def restore(self, snapshot):
        """Restore state from snapshot."""
        self.bank.sample_slots = snapshot['sample_slots']
        self.bank.eq_low = snapshot['eq_low']
        self.bank.eq_mid = snapshot['eq_mid']
        self.bank.eq_high = snapshot['eq_high']
        self.bank.volumes = snapshot['volumes']
        self.bank.pans = snapshot['pans']
        self.bank.attacks = snapshot['attacks']
        self.bank.decays = snapshot['decays']
        self.bank.sustains = snapshot['sustains']
        self.bank.releases = snapshot['releases']

    def undo(self):
        """Undo last edit operation."""
        if len(self.undo_stack) == 0:
            return None

        self.redo_stack.append(self.current_snapshot())
        snapshot = self.undo_stack.pop()
        self.restore(snapshot)
        return snapshot

    def redo(self):
        """Redo last undone edit operation."""
        if len(self.redo_stack) == 0:
            return None

        self.undo_stack.append(self.current_snapshot())
        snapshot = self.redo_stack.pop()
        self.restore(snapshot)
        return snapshot

    # ── ADSR Envelope ──────────────────────────────────────────────────────

    def _build_envelope(self, slot):
        """
        Build ADSR gain array for the sample.
        Phases: Attack -> Decay -> Sustain -> Release
        All phases are percentages of total sample length.
        """
        crude = self.bank.crude_slots[slot]
        if crude is None:
            return

        sample_length = len(crude)
        attack_percent = self.bank.attacks[slot]
        decay_percent = self.bank.decays[slot]
        sustain_level = self.bank.sustains[slot]
        release_percent = self.bank.releases[slot]

        total_percent = attack_percent + decay_percent + release_percent

        # Scale proportionally if total exceeds 100%
        if total_percent > 100:
            scale = 100.0 / total_percent
            attack_percent = attack_percent * scale
            decay_percent = decay_percent * scale
            release_percent = release_percent * scale

        attack_length = int(sample_length * (attack_percent / 100))
        decay_length = int(sample_length * (decay_percent / 100))
        release_length = int(sample_length * (release_percent / 100))
        sustain_length = sample_length - attack_length - decay_length - release_length

        gain = np.empty(sample_length, dtype=np.float64)

        # Attack: 0.0 -> 1.0
        if attack_length > 0:
            gain[:attack_length] = np.linspace(0.0, 1.0, attack_length) ** 3

        # Decay: 1.0 -> sustain_level
        if decay_length > 0:
            gain[attack_length:attack_length + decay_length] = np.linspace(1.0, sustain_level, decay_length, endpoint=False)

        # Sustain: constant at sustain_level
        if sustain_length > 0:
            gain[attack_length + decay_length:attack_length + decay_length + sustain_length] = sustain_level

        # Release: sustain_level -> 0.0
        if release_length > 0:
            gain[sample_length - release_length:] = np.linspace(sustain_level, 0.0, release_length)

        self.bank.envelope_arrays[slot] = gain.astype(np.float32)

    # ── Audio Processing ───────────────────────────────────────────────────

    def overwrite(self, slot):
        """
        Rebuild sample from crude_slots with all edits applied.
        Order: ADSR -> EQ -> Volume -> Pan
        """
        crude = self.bank.crude_slots[slot]
        if crude is None:
            return

        sample = crude.copy().astype(np.float64)

        # ADSR
        self._build_envelope(slot)
        gain = self.bank.envelope_arrays[slot]
        sample[:, 0] *= gain
        sample[:, 1] *= gain

        # EQ
        eq_low = self.bank.eq_low[slot]
        eq_mid = self.bank.eq_mid[slot]
        eq_high = self.bank.eq_high[slot]

        min_length = 50
        if len(sample) >= min_length:
            for channel in range(sample.shape[1]):
                audio = sample[:, channel]

                b, a = signal.butter(4, 200, btype='low', fs=SAMPLE_RATE)
                low_band = signal.filtfilt(b, a, audio)

                b, a = signal.butter(4, [200, 3000], btype='band', fs=SAMPLE_RATE)
                mid_band = signal.filtfilt(b, a, audio)

                b, a = signal.butter(4, 3000, btype='high', fs=SAMPLE_RATE)
                high_band = signal.filtfilt(b, a, audio)

                sample[:, channel] = low_band * eq_low + mid_band * eq_mid + high_band * eq_high

        # Volume
        sample *= self.bank.volumes[slot]

        # Pan
        pan_value = self.bank.pans[slot]
        pan_angle = pan_value * (np.pi / 2)
        sample[:, 0] *= np.cos(pan_angle)
        sample[:, 1] *= np.sin(pan_angle)

        self.bank.sample_slots[slot] = sample.astype(np.float32)

    # ── EQ Editing ─────────────────────────────────────────────────────────

    def edit_eq_3band(self, slot, low=None, mid=None, high=None):
        """Edit 3-band EQ for the specified slot."""
        if self.bank.crude_slots[slot] is None:
            return False

        self.save_snapshot()

        if low is not None:
            self.bank.eq_low[slot] = low
        if mid is not None:
            self.bank.eq_mid[slot] = mid
        if high is not None:
            self.bank.eq_high[slot] = high

        self.overwrite(slot)
        return True

    # ── Envelope Editing ───────────────────────────────────────────────────

    def edit_attack(self, slot, percent):
        """Edit attack percentage for the specified slot."""
        if self.bank.crude_slots[slot] is None:
            return False

        self.save_snapshot()
        self.bank.attacks[slot] = percent
        self.overwrite(slot)
        return True

    def edit_decay(self, slot, percent):
        """Edit decay percentage for the specified slot."""
        if self.bank.crude_slots[slot] is None:
            return False

        self.save_snapshot()
        self.bank.decays[slot] = percent
        self.overwrite(slot)
        return True

    def edit_sustain(self, slot, sustain_level):
        """Edit sustain level for the specified slot."""
        if self.bank.crude_slots[slot] is None:
            return False

        self.save_snapshot()
        self.bank.sustains[slot] = sustain_level
        self.overwrite(slot)
        return True

    def edit_release(self, slot, percent):
        """Edit release percentage for the specified slot."""
        if self.bank.crude_slots[slot] is None:
            return False

        self.save_snapshot()
        self.bank.releases[slot] = percent
        self.overwrite(slot)
        return True

    # ── Volume / Pan / Mute ────────────────────────────────────────────────

    def edit_volume(self, slot, volume_level):
        """Edit volume level for the specified slot."""
        if self.bank.crude_slots[slot] is None:
            return False

        self.save_snapshot()
        self.bank.volumes[slot] = volume_level
        self.overwrite(slot)
        return True

    def edit_pan(self, slot, pan_value):
        """Edit pan value for the specified slot."""
        if self.bank.crude_slots[slot] is None:
            return False

        self.save_snapshot()
        self.bank.pans[slot] = pan_value
        self.overwrite(slot)
        return True

    def edit_mute(self, slot, mute):
        """Toggle mute state for the specified slot."""
        self.bank.mutes[slot] = mute
        return True
