"""
Recorder Module
===============
Handles audio recording from input devices.
"""

import sounddevice as sd
import numpy as np
import time
from collections import deque
import noisereduce as nr
from scipy.signal import sosfiltfilt, butter


class Recorder:
    """Audio recording class with threshold-based recording start."""

    # ── Initialization ─────────────────────────────────────────────────────

    def __init__(self, main_window=None):
        self.main_window = main_window
        self.samplerate = 48000
        self.channels = 2
        self.threshold = 0.02
        self.recording = []
        self.started = False
        self.stream = None
        self.blocksize = 128
        self.pre_buffer = deque(maxlen=10)
        self.is_recording = False
        self.device = self.get_windows_default_device()

    # ── Audio Processing ───────────────────────────────────────────────────

    def get_volume(self, data):
        """Calculate average volume level from audio data."""
        return float(np.mean(np.abs(data)))

    def callback(self, indata, frames, time_info, status):
        """Audio stream callback for processing input data."""
        try:
            volume = self.get_volume(indata)

            if not self.started:
                self.pre_buffer.append(indata.copy())
                if volume > self.threshold:
                    self.started = True
                    self.recording.extend(list(self.pre_buffer))
                    self.pre_buffer.clear()
            else:
                self.recording.append(indata.copy())
        except Exception as e:
            print(f"Error in recording callback: {e}")
            self.cancel_recording()
            if self.main_window:
                self.main_window.show_error("Recording Error", f"Error during recording: {str(e)}")

    # ── Recording Control ──────────────────────────────────────────────────

    def start_recording(self):
        """Start recording audio input."""
        if self.device is None:
            if self.main_window:
                self.main_window.show_error("Recording Error", "No audio input device available. Please connect a device.")
            self.is_recording = False
            return False

        self.recording = []
        self.started = False
        self.pre_buffer.clear()
        self.is_recording = True

        sd.stop()
        time.sleep(0.2)

        try:
            self.stream = sd.InputStream(
                device=self.device,
                samplerate=self.samplerate,
                channels=self.channels,
                callback=self.callback,
                blocksize=self.blocksize
            )
            self.stream.start()
            return True
        except Exception as e:
            self.is_recording = False
            if self.main_window:
                self.main_window.show_error("Recording Error", f"Failed to start recording: {str(e)}")
            return False

    def stop_recording(self):
        """Stop recording and return the processed audio sample."""
        if not self.is_recording:
            return None

        self.is_recording = False

        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception as e:
                if self.main_window:
                    self.main_window.show_error("Recording Error", f"Error stopping recording: {str(e)}")
            finally:
                self.stream = None

        if self.recording:
            try:
                self.recording = np.concatenate(self.recording)
                self.recording = nr.reduce_noise(y=self.recording.T, sr=self.samplerate).T
                sos = butter(1, 8000, btype='high', fs=self.samplerate, output='sos')
                highs = sosfiltfilt(sos, self.recording, axis=0)
                self.recording = self.recording - highs * 0.6
                return self.recording
            except Exception as e:
                if self.main_window:
                    self.main_window.show_error("Recording Error", f"Error processing audio: {str(e)}")
                return None

        self.pre_buffer.clear()
        return None

    def cancel_recording(self):
        """Cancel ongoing recording and clear buffer."""
        if self.stream:
            self.stream.stop()
        self.is_recording = False
        self.recording = []

    # ── Device Management ──────────────────────────────────────────────────

    def get_windows_default_device(self):
        """Get Windows default audio input device with validation."""
        try:
            devices = sd.query_devices()
            default_input = sd.default.device[0]

            if default_input is None or default_input < 0:
                print("Warning: No default audio input device set in Windows")
                return None

            if default_input >= len(devices):
                print("Warning: Default device not found in available devices")
                return None

            device_info = devices[default_input]
            if device_info['max_input_channels'] == 0:
                print("Warning: Default device has no input channels")
                return None

            print(f"Audio input device: {device_info['name']}")
            return default_input

        except Exception as e:
            if self.main_window:
                self.main_window.show_error("Device Error", f"Failed to find audio device: {str(e)}")
            return None

    def refresh_device(self):
        """Refresh device selection when device might have changed."""
        try:
            if self.device is not None:
                devices = sd.query_devices()
                if self.device < len(devices):
                    device_info = devices[self.device]
                    if device_info['max_input_channels'] > 0:
                        return True
        except Exception:
            pass

        self.device = self.get_windows_default_device()
        return self.device is not None
