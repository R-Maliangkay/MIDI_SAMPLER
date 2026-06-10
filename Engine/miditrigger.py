"""
MidiTrigger Module
==================
Handles MIDI input and sample triggering.
"""

import sounddevice as sd
import mido
import numpy as np
import time
import threading


class MidiTrigger:
    """MIDI trigger class that handles MIDI input and audio playback."""

    # ── Initialization ─────────────────────────────────────────────────────

    def __init__(self, sample_bank, channel=6):
        self.sample_bank = sample_bank
        self.channel = channel
        self.samplerate = 48000
        self.blocksize = 64
        self.device = self.get_default_output_device()
        self._running = False
        self.voices = []
        self.stream = sd.OutputStream(
            device=self.device,
            samplerate=self.samplerate,
            channels=2,
            blocksize=self.blocksize,
            dtype='float32',
            callback=self.callback
        )
        self.stream.start()

    # ── MIDI Processing ────────────────────────────────────────────────────

    def midi_callback(self, msg):
        """Handle incoming MIDI messages."""
        if msg.type == 'note_on' and msg.channel == self.channel and msg.velocity > 0:
            self.trigger_sample(msg.note)

    def trigger_sample(self, midi_note):
        """Trigger sample playback for the given MIDI note."""
        if midi_note in self.sample_bank.note_map:
            slot = self.sample_bank.note_map[midi_note]

            if self.sample_bank.mutes[slot]:
                return

            sample_data = self.sample_bank.sample_slots[slot]
            if sample_data is not None:
                self.voices.append({
                    'slot': slot,
                    'sample': sample_data.astype(np.float32),
                    'pointer': 0,
                })

    # ── Audio Playback ─────────────────────────────────────────────────────

    def callback(self, outdata, frames, time_info, status):
        """Audio output callback for sample playback."""
        outdata.fill(0)
        still_playing = []

        for voice in self.voices:
            pointer = voice['pointer']
            sample = voice['sample']
            samples_left = len(sample) - pointer

            if samples_left > 0:
                copy_amount = min(samples_left, frames)
                chunk = sample[pointer:pointer + copy_amount].copy()
                outdata[:copy_amount] += chunk
                voice['pointer'] += copy_amount
                still_playing.append(voice)

        self.voices = still_playing
        outdata[:] = np.clip(outdata, -1.0, 1.0)

    def stop_playback(self):
        """Stop all audio playback."""
        self.voices = []

    # ── MIDI Listening ─────────────────────────────────────────────────────

    def start_listening(self, device_name=None):
        """Start listening for MIDI input on a separate thread."""
        self._running = True
        listener_thread = threading.Thread(target=self.listen_loop, args=(device_name,), daemon=True)
        listener_thread.start()

    def listen_loop(self, device_name=None):
        """Main loop for MIDI input listening."""
        available_ports = mido.get_input_names()
        if not available_ports:
            print("No MIDI devices found")
            return

        opened_ports = [mido.open_input(name=port, callback=self.midi_callback) for port in available_ports]
        print(f"Luistert op: {available_ports}")

        while self._running:
            time.sleep(0.01)

        for port in opened_ports:
            port.close()

    # ── Configuration ──────────────────────────────────────────────────────

    def set_channel(self, channel):
        """Set MIDI channel (1-16)."""
        if 1 <= channel <= 16:
            self.channel = channel - 1
        else:
            print(f"Invalid MIDI channel: {channel}. Must be 1-16")

    def get_default_output_device(self):
        """Get default audio output device dynamically."""
        try:
            devices = sd.query_devices()
            default_output = sd.default.device[1]
            if default_output is not None and default_output >= 0:
                return default_output
            for i, dev in enumerate(devices):
                if dev['max_output_channels'] > 0:
                    return i
            return None
        except Exception:
            return None
