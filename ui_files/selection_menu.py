"""
SelectionMenu Module
====================
Handles slot and MIDI channel selection via LCD display.
"""

from PyQt5.QtCore import QTimer


class SelectionMenu:
    """Menu for selecting sample slots and MIDI channels."""

    # ── Initialization ─────────────────────────────────────────────────────

    def __init__(self, sample_bank, main_window, core):
        self.sample_bank = sample_bank
        self.core = core
        self.main_window = main_window
        self.timer = QTimer()
        self.timer.timeout.connect(self.toggle_blink)
        self.state = None
        self.temp_value = ""
        self.blink_speed = 300
        self.blink_visible = True

    # ── Selection Modes ────────────────────────────────────────────────────

    def select_slot(self):
        """Start slot selection mode (1-64)."""
        if self.state in ['slot_select', 'slot_input']:
            return

        self.stop_blink()
        self.state = 'slot_select'
        self.main_window.LCD_SLOT.setVisible(True)
        self.main_window.LCD_CH.setVisible(True)
        self.timer.start(self.blink_speed)

    def select_channel(self):
        """Start channel selection mode (1-16)."""
        if self.state in ['channel_select', 'channel_input']:
            return

        self.stop_blink()
        self.state = 'channel_select'
        self.main_window.LCD_SLOT.setVisible(True)
        self.main_window.LCD_CH.setVisible(True)
        self.timer.start(self.blink_speed)

    # ── Input Handling ─────────────────────────────────────────────────────

    def handle_enter(self):
        """Handle ENTER button press based on current state."""
        if self.state == 'slot_select':
            self.state = 'slot_input'
            self.temp_value = ""
            self.blink_visible = True
            self.main_window.LCD_SLOT.setVisible(True)
            self.main_window.LCD_SLOT.setText("SLOT:00")

        elif self.state == 'channel_select':
            self.state = 'channel_input'
            self.temp_value = ""
            self.blink_visible = True
            self.main_window.LCD_CH.setVisible(True)
            self.main_window.LCD_CH.setText("CH:00")

        elif self.state == 'slot_input':
            if self.temp_value:
                slot_value = int(self.temp_value)
                if 1 <= slot_value <= 64:
                    actual_slot = slot_value - 1
                    self.main_window.current_slot = actual_slot
                    self.main_window.LCD_SLOT.setText(f"SLOT:{slot_value:02d}")
                    self.stop_blink()
                else:
                    self.main_window.LCD_SLOT.setText("ERR:1-64")

        elif self.state == 'channel_input':
            if self.temp_value:
                channel_value = int(self.temp_value)
                if 1 <= channel_value <= 16:
                    self.core.trigger.set_channel(channel_value)
                    self.main_window.LCD_CH.setText(f"CH:{channel_value:02d}")
                    self.stop_blink()
                else:
                    self.main_window.LCD_CH.setText("ERR:1-16")

    def number_input(self, num):
        """Handle numeric input from keypad."""
        if self.state in ['slot_input', 'channel_input']:
            if not str(num).isdigit():
                return

            self.temp_value += str(num)
            if len(self.temp_value) > 2:
                self.temp_value = self.temp_value[-2:]
            self.update_display()

            if self.temp_value:
                self.timer.stop()

    # ── Display Updates ────────────────────────────────────────────────────

    def toggle_blink(self):
        """Toggle LCD visibility for blink effect."""
        if self.state == 'slot_select':
            visible = self.main_window.LCD_SLOT.isVisible()
            self.main_window.LCD_SLOT.setVisible(not visible)

        elif self.state == 'channel_select':
            visible = self.main_window.LCD_CH.isVisible()
            self.main_window.LCD_CH.setVisible(not visible)

        elif self.state == 'slot_input':
            if self.blink_visible:
                self.main_window.LCD_SLOT.setText("SLOT:")
            else:
                formatted = self.temp_value.zfill(2)
                self.main_window.LCD_SLOT.setText(f"SLOT:{formatted}")
            self.blink_visible = not self.blink_visible

        elif self.state == 'channel_input':
            if self.blink_visible:
                self.main_window.LCD_CH.setText("CH:")
            else:
                formatted = self.temp_value.zfill(2)
                self.main_window.LCD_CH.setText(f"CH:{formatted}")
            self.blink_visible = not self.blink_visible

    def update_display(self):
        """Update LCD display with current input value."""
        formatted = self.temp_value.zfill(2)
        if self.state == 'slot_input':
            self.main_window.LCD_SLOT.setText(f"SLOT:{formatted}")
            self.blink_visible = False
        elif self.state == 'channel_input':
            self.main_window.LCD_CH.setText(f"CH:{formatted}")
            self.blink_visible = False

    def stop_blink(self):
        """Stop blinking and reset state."""
        self.timer.stop()
        self.main_window.LCD_SLOT.setVisible(True)
        self.main_window.LCD_CH.setVisible(True)
        self.state = None
        self.temp_value = ""
        self.blink_visible = True
