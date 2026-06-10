"""
Lamp Module
===========
Simple LED lamp widget with on/off states.
"""

from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap


class Lamp(QLabel):
    """LED lamp widget that can display on/off states."""

    # ── Initialization ─────────────────────────────────────────────────────

    def __init__(self, parent=None):
        super().__init__(parent)
        self.on_image = None
        self.off_image = None

    # ── Configuration ──────────────────────────────────────────────────────

    def setImages(self, on_path, off_path):
        """Set the on and off images for the lamp."""
        self.on_image = QPixmap(on_path)
        self.off_image = QPixmap(off_path)
        self.turnOff()

    # ── State Control ──────────────────────────────────────────────────────

    def turnOn(self):
        """Turn the lamp on."""
        if self.on_image:
            self.setPixmap(self.on_image)

    def turnOff(self):
        """Turn the lamp off."""
        if self.off_image:
            self.setPixmap(self.off_image)
