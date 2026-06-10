"""
ImageDial Module
================
Custom rotary dial widget with image rendering.
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPointF, pyqtSignal, QRect
from PyQt5.QtGui import QPainter, QPixmap, QRegion
import math


class ImageDial(QWidget):
    """Custom rotary dial widget that emits valueChanged signal."""

    valueChanged = pyqtSignal(int)

    # ── Initialization ─────────────────────────────────────────────────────

    def __init__(self, parent=None, image_path=None):
        super().__init__(parent)
        self.image = QPixmap(image_path) if image_path else None
        self.angle = 12.5
        self.rotation_offset = 0
        self.value = 0
        self.min_angle = -135
        self.max_angle = 160
        self.dragging = False
        self.last_valid_angle = -135
        self.scale = 1.0
        self.mask_scale = 1.0
        self.mask_offset_x = 0
        self.mask_offset_y = 0
        self.offset_x = 0
        self.offset_y = 0
        self.setMinimumSize(100, 100)

    # ── Configuration ──────────────────────────────────────────────────────

    def setImage(self, image_path):
        """Set the dial image."""
        self.image = QPixmap(image_path)
        self.update()

    def setScale(self, scale):
        """Set the image scale factor."""
        self.scale = scale
        self.update()

    def setMaskScale(self, scale):
        """Set the mask scale factor."""
        self.mask_scale = scale
        self.updateMask()

    def setMaskOffset(self, x, y):
        """Set the mask offset."""
        self.mask_offset_x = x
        self.mask_offset_y = y
        self.updateMask()

    def setOffset(self, x, y):
        """Set the image offset."""
        self.offset_x = x
        self.offset_y = y
        self.update()

    def setRotationOffset(self, offset):
        """Set the rotation offset in degrees."""
        self.rotation_offset = offset
        self.update()

    # ── Mask / Paint ───────────────────────────────────────────────────────

    def updateMask(self):
        """Update the circular mask for the widget."""
        size = min(self.width(), self.height()) * self.mask_scale
        x = (self.width() - size) / 2 + self.mask_offset_x
        y = (self.height() - size) / 2 + self.mask_offset_y
        mask_rect = QRect(int(x), int(y), int(size), int(size))
        self.setMask(QRegion(mask_rect, QRegion.Ellipse))

    def resizeEvent(self, event):
        """Handle widget resize."""
        self.updateMask()
        super().resizeEvent(event)

    def paintEvent(self, event):
        """Paint the dial image with rotation."""
        if not self.image:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center = QPointF(self.width() / 2 + self.offset_x, self.height() / 2 + self.offset_y)
        painter.translate(center)
        painter.rotate(self.angle + self.rotation_offset)
        painter.scale(self.scale, self.scale)
        painter.translate(-self.image.width() / 2, -self.image.height() / 2)
        painter.drawPixmap(0, 0, self.image)

    # ── Mouse Events ───────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        """Handle mouse press."""
        self.dragging = True
        self.updateValue(event.pos())

    def mouseMoveEvent(self, event):
        """Handle mouse move."""
        if self.dragging:
            self.updateValue(event.pos())

    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        self.dragging = False

    def updateValue(self, pos):
        """Update dial value based on mouse position."""
        dx = pos.x() - self.width() / 2
        dy = pos.y() - self.height() / 2
        raw_angle = math.degrees(math.atan2(dy, dx)) + 90

        if raw_angle > 180:
            raw_angle -= 360

        in_valid_range = False
        if self.min_angle < 0 and self.max_angle > 0:
            in_valid_range = (raw_angle >= self.min_angle and raw_angle <= self.max_angle)

        if not in_valid_range:
            return

        self.angle = raw_angle

        angle_range = self.max_angle - self.min_angle
        normalized = (self.angle - self.min_angle) / angle_range
        self.value = int(normalized * 100)

        self.valueChanged.emit(self.value)
        self.update()
