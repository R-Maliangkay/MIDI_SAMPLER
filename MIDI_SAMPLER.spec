# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# ── Bundled Images ─────────────────────────────────────────────────────────
# Only the images the app actually uses. Personal screenshots and AI images stay out.
IMAGE_FILES = [
    'asset_free.png',
    'dial.png',
    'display_background.png',
    'lamp_on.png',
    'lamp_off.png',
    'mute_toggle_on.png',
    'mute_toggle_off.png',
    'slider_handle.png',
    'empty_horizontal_slider.png',
    'slider_vertical_empty.png',
    'button_large.png',
    'button_large_pressed.png',
    'button_small.png',
    'button_small_pressed.png',
    'button_square.png',
    'button_square_pressed.png',
]
for digit in range(10):
    IMAGE_FILES.append(f'button_{digit}.png')
    IMAGE_FILES.append(f'button_{digit}_pressed.png')

bundled_datas = [('UI1.ui', '.')] + [(f'Images/{name}', 'Images') for name in IMAGE_FILES]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=bundled_datas,
    hiddenimports=[
        'ui_files.image_dial',
        'ui_files.lamp',
        'ui_files.lcd',
        'ui_files.selection_menu',
        'ui_files.main_window',
        'mido.backends.rtmidi',
        'numpy',
        'sounddevice',
        'PyQt5',
        'PyQt5.sip',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MIDI Sampler',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    icon='Images/icon.ico',
)
