; Inno Setup script for the Androidbox installer. build.ps1 compiles it and passes the version.
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppId={{A34B18DE-2373-4C2B-8241-2922464CCACB}
AppName=Androidbox
AppVersion={#AppVersion}
AppPublisher=Wolklaw
AppPublisherURL=https://github.com/Wolklaw/Androidbox
AppSupportURL=https://github.com/Wolklaw/Androidbox/issues
AppUpdatesURL=https://github.com/Wolklaw/Androidbox/releases
DefaultDirName={autopf}\Androidbox
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
LicenseFile=LICENSE
SetupIconFile=assets\androidbox.ico
UninstallDisplayIcon={app}\Androidbox.exe
WizardStyle=modern
Compression=lzma2/max
SolidCompression=yes
OutputDir=dist
OutputBaseFilename=Androidbox-Setup-{#AppVersion}
AppMutex=Local\Androidbox
CloseApplications=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\Androidbox\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Androidbox"; Filename: "{app}\Androidbox.exe"
Name: "{autodesktop}\Androidbox"; Filename: "{app}\Androidbox.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Androidbox.exe"; Description: "{cm:LaunchProgram,Androidbox}"; Flags: nowait postinstall skipifsilent runasoriginaluser

[Code]
// The emulator, its Android images, instances and profiles live outside the install folder.
// Keep them unless the user says otherwise, since the images take a long time to download again.
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  Data: String;
begin
  if CurUninstallStep <> usPostUninstall then
    Exit;
  Data := ExpandConstant('{localappdata}\Androidbox');
  if UninstallSilent or not DirExists(Data) then
    Exit;
  if MsgBox('Also delete your Android images, instances and profiles?' + #13#10 + #13#10 +
            Data + #13#10 + #13#10 +
            'Choose No to keep them for a later reinstall.',
            mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES then
    DelTree(Data, True, True, True);
end;
