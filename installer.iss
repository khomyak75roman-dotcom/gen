[Setup]
AppName=Video Generator
AppVersion=4.0.0
AppPublisher=khomyak75roman-dotcom
DefaultDirName={pf}\VideoGenerator
DefaultGroupName=Video Generator
OutputDir=dist
OutputBaseFilename=VideoGenerator-Setup
Compression=lzma2
SolidCompression=yes

[Files]
Source: "dist\VideoGenerator.exe"; DestDir: "{app}"
Source: "ffmpeg.exe"; DestDir: "{app}"

[Icons]
Name: "{commondesktop}\Video Generator"; Filename: "{app}\VideoGenerator.exe"; WorkingDir: "{app}"
Name: "{group}\Video Generator"; Filename: "{app}\VideoGenerator.exe"; WorkingDir: "{app}"

[Run]
Filename: "{app}\VideoGenerator.exe"; Flags: postinstall nowait skipifsilent
