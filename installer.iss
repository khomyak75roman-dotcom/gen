; Video Generator Installer Script
; Inno Setup 6

[Setup]
AppName=Video Generator
AppVersion=4.0.0
AppPublisher=khomyak75roman-dotcom
AppPublisherURL=https://github.com/khomyak75roman-dotcom
DefaultDirName={autopf}\VideoGenerator
DefaultGroupName=Video Generator
OutputDir=dist
OutputBaseFilename=VideoGenerator-Setup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin

[Files]
; Executable and FFmpeg
Source: "dist\VideoGenerator.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion

; Configuration
Source: ".env.example"; DestDir: "{app}"; Flags: ignoreversion

; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "CHANGELOG.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Desktop icon
Name: "{commondesktop}\Video Generator"; Filename: "{app}\VideoGenerator.exe"; WorkingDir: "{app}"; IconFilename: "{app}\VideoGenerator.exe"

; Start menu
Name: "{group}\Video Generator"; Filename: "{app}\VideoGenerator.exe"; WorkingDir: "{app}"
Name: "{group}\Documentation"; Filename: "{app}\README.md"; WorkingDir: "{app}"

[Run]
Filename: "{app}\VideoGenerator.exe"; Description: "Launch Video Generator"; Flags: postinstall nowait skipifsilent
