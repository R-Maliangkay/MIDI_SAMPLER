# MIDI Sampler

A Python-based MIDI sampler application with a PyQt5 interface.

## Features

- 64 sample slots
- 3-band EQ (Low, Mid, High)
- ADSR envelope (Attack, Decay, Sustain, Release)
- Volume and Pan control
- Audio recording from microphone/instrument
- MIDI trigger support
- Save/Load projects
- Undo/Redo functionality

## Installation

### Option 1: Download and install (Recommended, Windows)

1. Download `MIDI_Sampler_Setup.exe` from the latest release
2. Double-click the file and follow the steps
3. Start **MIDI Sampler** from the Start menu

No Python or terminal needed. The installer does not need administrator rights.

### Option 2: From source code

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/MIDI_SAMPLER01.git
   cd MIDI_SAMPLER01
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python main.py
   ```

## Usage

### Basic functionality

1. **Record**: Press the REC button to start recording audio
2. **Play**: Press the PLAY button to play the selected slot
3. **Stop**: Press the STOP button to stop recording/playback

### Slot Selection

- Press the left SELECT button to start slot selection
- Enter a number (1-64) using the numeric keys
- Press ENTER to confirm

### MIDI Channel

- Press the right SELECT button to select MIDI channel
- Enter a number (1-16)
- Press ENTER to confirm

### Via Menu

- **Settings > Select Audio Input** - Choose audio input device
- **Settings > Select Audio Output** - Choose audio output device
- **Settings > Select MIDI Device** - Choose MIDI device
- **Settings > Select Slot** - Choose sample slot
- **Settings > Select MIDI Channel** - Choose MIDI channel

## Technical Details

### Dependencies

- Python 3.8+
- PyQt5 - GUI framework
- NumPy - Audio processing
- sounddevice - Audio recording/playback
- mido - MIDI processing

### Project Structure

```
MIDI_SAMPLER01/
├── main.py              # Main entry point
├── Engine/
│   ├── core.py          # Sampler core
│   ├── sample_bank.py   # Sample storage
│   ├── recorder.py      # Audio recording
│   ├── miditrigger.py   # MIDI trigger
│   └── editor.py        # Audio editing
├── ui_files/
│   ├── main_window.py   # Main window
│   ├── selection_menu.py # Selection menu
│   ├── lcd.py           # LCD display
│   └── image_dial.py    # Rotary dial
├── Images/              # Image assets
├── requirements.txt     # Dependencies
└── MIDI_Sampler.spec    # PyInstaller config
```

## Known Limitations

- Audio device (dis)connection is not detected in real-time
- Maximum sample length is limited by available memory
- Windows .exe only (other platforms require source code)

## License

MIT License - See LICENSE file for details.

## Contact

- GitHub: [R-Maliangkay](https://github.com/R-Maliangkay)
- Email: rick.maliangkaij@gmail.com
```
