[Setup]
AppName=PyAutoInputer
AppVersion=1.0.0
DefaultDirName={pf}\PyAutoInputer
OutputDir=installer
OutputBaseFilename=PyAutoInputer_Setup
Compression=lzma2
PrivilegesRequired=admin

[Files]
Source: "dist\PyAutoInputer.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.txt"; DestDir: "{app}"; Flags: onlyifdoesntexist
Source: "VC_redist.x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
; 为当前用户创建桌面快捷方式（二选一）
Name: "{userdesktop}\AutoInputer"; Filename: "{app}\PyAutoInputer.exe"

[Run]
Filename: "{tmp}\VC_redist.x64.exe"; Parameters: "/install /quiet /norestart"; StatusMsg: "安装运行库..."