; MIDI Sampler - Windows installer (Inno Setup 6)
; Build: open this file in Inno Setup Compiler and press Compile,
; or run ISCC.exe on this file. Run `pyinstaller MIDI_SAMPLER.spec` first
; so that ..\dist\MIDI Sampler.exe exists.
; Installs per user (no administrator rights needed).

#define MyAppName "MIDI Sampler"
#define MyAppVersion "1.0.0"
#define MyAppExeName "MIDI Sampler.exe"

[Setup]
AppId={{B7E1C2A4-5D3F-4E8A-9C61-2F7A8D4B1E90}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=R. Maliangkay
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\dist
OutputBaseFilename=MIDI_Sampler_Setup
SetupIconFile=..\Images\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "dutch"; MessagesFile: "compiler:Languages\Dutch.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Snelkoppeling op het bureaublad maken"; GroupDescription: "Extra snelkoppelingen:"; Flags: unchecked

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
