"""
LCD Module
==========
Helper class for updating LCD display widgets.
"""


class LCD:
    """LCD display helper for updating text on LCD widgets."""

    # ── Initialization ─────────────────────────────────────────────────────

    def __init__(self, main_window):
        self.window = main_window

    # ── Envelope Updates ───────────────────────────────────────────────────

    def update_attack(self, value):
        """Update attack LCD display."""
        self.window.LCD_ATTACK.setText(f"ATTACK:{value}%")

    def update_decay(self, value):
        """Update decay LCD display."""
        self.window.LCD_DECAY.setText(f"DECAY:{value}%")

    def update_sustain(self, value):
        """Update sustain LCD display."""
        self.window.LCD_SUSTAIN.setText(f"SUSTAIN:{value}%")

    def update_release(self, value):
        """Update release LCD display."""
        self.window.LCD_RELEASE.setText(f"RELEASE:{value}%")

    # ── Volume / Pan ───────────────────────────────────────────────────────

    def update_volume(self, value):
        """Update volume LCD display."""
        self.window.LCD_MAIN.setText(f"MAIN VOL:{value}%")

    def update_pan(self, value):
        """Update pan LCD display."""
        self.window.LCD_PAN.setText(f"PAN:{value}%")

    # ── EQ Updates ─────────────────────────────────────────────────────────

    def update_high(self, value):
        """Update high EQ LCD display."""
        self.window.LCD_HI.setText(f"HIGH:{value}%")

    def update_mid(self, value):
        """Update mid EQ LCD display."""
        self.window.LCD_MID.setText(f"MID:{value}%")

    def update_low(self, value):
        """Update low EQ LCD display."""
        self.window.LCD_LOW.setText(f"LOW:{value}%")

    # ── Slot / Channel ─────────────────────────────────────────────────────

    def update_slot(self, value):
        """Update slot LCD display."""
        self.window.select_right.setText(f"SLOT:{value:>2}")

    def update_channel(self, value):
        """Update channel LCD display."""
        self.window.select_left.setText(f"CH:{value:>2}")

    # ── Device Status ──────────────────────────────────────────────────────

    def update_audio_input(self, device_name):
        """Update audio input device LCD display."""
        self.window.LCD_AUDIO_INPUT.setText(f"INPUT:{device_name}")

    def update_audio_output(self, device_name):
        """Update audio output device LCD display."""
        self.window.LCD_AUDIO_OUTPUT.setText(f"OUTPUT:{device_name}")

    def update_midi_device(self, device_name):
        """Update MIDI device LCD display."""
        self.window.LCD_MIDI_STATUS.setText(f"MIDI:{device_name}")
