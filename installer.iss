; Video Generator Installer Script
; Inno Setup 6

[Setup]
AppName=Video Generator
AppVersion=4.0.0
AppPublisher=khomyak75roman-dotcom
AppPublisherURL=https://github.com/khomyak75roman-dotcom
AppExeName=VideoGenerator.exe
DefaultDirName={autopf}\VideoGenerator
DefaultGroupName=Video Generator
OutputDir=dist
OutputBaseFilename=VideoGenerator-Setup
SetupIconFile=icon.ico
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin

[Languages]
Name: "ukrainian"; MessagesFile: "compiler:Languages\Ukrainian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; Main executable
Source: "dist\VideoGenerator.exe"; DestDir: "{app}"; Flags: ignoreversion

; FFmpeg
Source: "ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion

; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "CHANGELOG.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

; Configuration
Source: ".env.example"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu
Name: "{group}\Video Generator"; Filename: "{app}\VideoGenerator.exe"; WorkingDir: "{app}"; IconFilename: "{app}\VideoGenerator.exe"
Name: "{group}\Documentation"; Filename: "{app}\README.md"; WorkingDir: "{app}"
Name: "{group}\Changelog"; Filename: "{app}\CHANGELOG.md"; WorkingDir: "{app}"

; Desktop
Name: "{commondesktop}\Video Generator"; Filename: "{app}\VideoGenerator.exe"; WorkingDir: "{app}"; IconFilename: "{app}\VideoGenerator.exe"

[Run]
; Run after installation
Filename: "{app}\VideoGenerator.exe"; Description: "Launch Video Generator"; Flags: postinstall nowait skipifsilent

[UninstallRun]
; Clean up after uninstall
Filename: "cmd.exe"; Parameters: "/C ping 127.0.0.1 -n 3 > nul & del /f /q ""{app}\*.exe"" 2> nul"; StatusMsg: Removing temporary files...
