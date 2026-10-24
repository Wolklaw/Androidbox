; Inno Setup script for the Androidbox installer. build.ps1 compiles it and passes the version.
; The wizard artwork in installer\ comes from installer\make_art.py.
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
VersionInfoVersion={#AppVersion}.0
VersionInfoCompany=Wolklaw
VersionInfoDescription=Androidbox Setup
; Program Files for everyone by default. The first page offers "just for me" to people without admin rights
DefaultDirName={autopf}\Androidbox
DisableProgramGroupPage=yes
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
LicenseFile=LICENSE
SetupIconFile=assets\androidbox.ico
UninstallDisplayIcon={app}\Androidbox.exe
UninstallDisplayName=Androidbox
WizardStyle=modern dark
DisableWelcomePage=no
WizardSizePercent=110
WizardImageFile=installer\welcome-202.png,installer\welcome-336.png,installer\welcome-534.png
WizardImageBackColor=#17191c
WizardSmallImageFile=installer\badge-58.png,installer\badge-77.png,installer\badge-97.png,installer\badge-124.png,installer\badge-159.png
Compression=lzma2/max
SolidCompression=yes
OutputDir=dist
OutputBaseFilename=Androidbox-Setup-{#AppVersion}
AppMutex=Local\Androidbox
CloseApplications=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
WelcomeLabel1=Android on your PC.%nNo ads.
WelcomeLabel2=Androidbox runs Google's official Android Emulator on your graphics card, with Google Play, game controls and several Androids at once.%n%nThis installs Androidbox {#AppVersion}. Android itself downloads from Google the first time you open it.
LicenseLabel=Androidbox is free and open source. Here is its license.
SelectTasksLabel2=Pick what Setup should do besides installing Androidbox.
FinishedHeadingLabel=Androidbox is ready
FinishedLabelNoIcons=Androidbox is installed. Open it and choose Download and install to get Android.
FinishedLabel=Androidbox is installed. Open it from the Start menu and choose Download and install to get Android.
FinishedRestartLabel=Windows needs to restart to finish turning on the Windows Hypervisor Platform, which Android needs in order to run. Restart now?

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "hypervisor"; Description: "Turn on Windows Hypervisor Platform (Android can't start without it, and it needs a restart)"; GroupDescription: "Windows:"; Check: HypervisorOff

[Files]
Source: "dist\Androidbox\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Androidbox"; Filename: "{app}\Androidbox.exe"
Name: "{autodesktop}\Androidbox"; Filename: "{app}\Androidbox.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Androidbox.exe"; Description: "{cm:LaunchProgram,Androidbox}"; Flags: nowait postinstall skipifsilent runasoriginaluser; Check: not RestartNeeded

[Code]
const
  UninstallKey = 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{A34B18DE-2373-4C2B-8241-2922464CCACB}_is1';

var
  Restart: Boolean;

function RestartNeeded: Boolean;
begin
  Result := Restart;
end;

function NeedRestart: Boolean;
begin
  Result := Restart;
end;

// Android's emulator runs on Windows Hypervisor Platform, whose library only exists while the feature is on
function HypervisorOff: Boolean;
begin
  Result := IsAdminInstallMode and not FileExists(ExpandConstant('{sys}\WinHvPlatform.dll'));
end;

procedure TurnOnHypervisor;
var
  Code: Integer;
begin
  WizardForm.StatusLabel.Caption := 'Turning on Windows Hypervisor Platform...';
  WizardForm.FilenameLabel.Caption := '';
  if Exec(ExpandConstant('{sys}\dism.exe'), '/online /enable-feature /featurename:HypervisorPlatform /all /norestart',
          '', SW_HIDE, ewWaitUntilTerminated, Code) and ((Code = 0) or (Code = 3010)) then
    Restart := True
  else
    SuppressibleMsgBox('Windows would not turn on the Windows Hypervisor Platform. Androidbox shows how to turn it ' +
                       'on yourself the first time you open it.', mbInformation, MB_OK, IDOK);
end;

// Earlier versions installed for the current user only. Remove that copy when installing for everyone, so there
// aren't two Androidboxes and two Start menu entries. Its instances and profiles are not touched.
procedure RemoveUserInstall;
var
  Uninstaller: String;
  Code: Integer;
begin
  if IsAdminInstallMode and RegQueryStringValue(HKCU, UninstallKey, 'UninstallString', Uninstaller) then
  begin
    Uninstaller := RemoveQuotes(Uninstaller);
    if FileExists(Uninstaller) then
      Exec(Uninstaller, '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART', '', SW_HIDE, ewWaitUntilTerminated, Code);
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
    RemoveUserInstall
  else if (CurStep = ssPostInstall) and WizardIsTaskSelected('hypervisor') then
    TurnOnHypervisor;
end;

// Where the user moved Androidbox's files to, if they did. Androidbox writes the folder into location.txt
function MovedDataFolder: String;
var
  Lines: TArrayOfString;
begin
  Result := '';
  if LoadStringsFromFile(ExpandConstant('{localappdata}\Androidbox\location.txt'), Lines) and
     (GetArrayLength(Lines) > 0) then
    Result := Trim(Lines[0]);
end;

// The emulator, its Android images, instances and profiles live outside the install folder.
// Keep them unless the user says otherwise, since the images take a long time to download again.
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  Data, Moved, Shown: String;
begin
  if CurUninstallStep <> usPostUninstall then
    Exit;
  Data := ExpandConstant('{localappdata}\Androidbox');
  Moved := MovedDataFolder;
  if UninstallSilent or not DirExists(Data) then
    Exit;
  Shown := Data;
  if (Moved <> '') and DirExists(Moved) then
    Shown := Moved;
  if MsgBox('Also delete your Android images, instances and profiles?' + #13#10 + #13#10 +
            Shown + #13#10 + #13#10 +
            'Choose No to keep them for a later reinstall.',
            mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES then
  begin
    if Moved <> '' then
      DelTree(Moved, True, True, True);
    DelTree(Data, True, True, True);
  end;
end;
