[Setup]
AppName=Video Generator
AppVersion=4.0.0
DefaultDirName={autopf}\VideoGenerator
DefaultGroupName=Video Generator
OutputDir=dist
OutputBaseFilename=VideoGenerator-Setup
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\VideoGenerator.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Video Generator"; Filename: "{app}\VideoGenerator.exe"; WorkingDir: "{app}"
Name: "{commondesktop}\Video Generator"; Filename: "{app}\VideoGenerator.exe"; WorkingDir: "{app}"

[Run]
Filename: "{app}\VideoGenerator.exe"; Description: "Launch Video Generator"; Flags: postinstall nowait skipifsilent
