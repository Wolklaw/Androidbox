$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$version = (Select-String -Path androidbox\__init__.py -Pattern 'VERSION = "(.+)"').Matches[0].Groups[1].Value

$inno = @((Get-Command ISCC.exe -ErrorAction SilentlyContinue).Source,
          "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
          "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
          "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe") |
    Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
if (-not $inno) {
    throw "Inno Setup 6 builds the installer. Install it with: winget install JRSoftware.InnoSetup"
}

if (-not (Test-Path .venv)) {
    python -m venv .venv
}
.venv\Scripts\python.exe -m pip install --quiet --disable-pip-version-check -r requirements.txt pyinstaller

# An earlier build can leave read-only folders behind, which PyInstaller can't clear by itself
foreach ($folder in "build\Androidbox", "dist\Androidbox") {
    if (Test-Path $folder) {
        attrib -R $folder /S /D
        Remove-Item -Recurse -Force $folder
    }
}

# An exe with no version resource (company/product/description) is a classic signal that unsigned
# antivirus ML heuristics (e.g. Defender's Bearfoos) use to flag PyInstaller apps as trojans
$parts = @(($version -split '\.') + @("0", "0", "0", "0"))[0..3]
$fileVers = $parts -join ", "
New-Item -ItemType Directory -Force -Path "$PSScriptRoot\build" | Out-Null
Set-Content -Path "$PSScriptRoot\build\version_info.txt" -Encoding utf8 -Value @"
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=($fileVers),
    prodvers=($fileVers),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Wolklaw'),
        StringStruct(u'FileDescription', u'Androidbox'),
        StringStruct(u'FileVersion', u'$version.0'),
        StringStruct(u'InternalName', u'Androidbox'),
        StringStruct(u'LegalCopyright', u'Wolklaw'),
        StringStruct(u'OriginalFilename', u'Androidbox.exe'),
        StringStruct(u'ProductName', u'Androidbox'),
        StringStruct(u'ProductVersion', u'$version.0')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"@

.venv\Scripts\pyinstaller.exe "$PSScriptRoot\Androidbox.pyw" `
    --name Androidbox `
    --onedir `
    --windowed `
    --noupx `
    --icon "$PSScriptRoot\assets\androidbox.ico" `
    --add-data "$PSScriptRoot\assets\androidbox.ico;assets" `
    --version-file "$PSScriptRoot\build\version_info.txt" `
    --exclude-module tkinter `
    --collect-all sdl2dll `
    --distpath "$PSScriptRoot\dist" `
    --workpath "$PSScriptRoot\build" `
    --specpath "$PSScriptRoot\build" `
    --noconfirm `
    --clean `
    --log-level WARN
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed"
}

& $inno /Qp "/DAppVersion=$version" "$PSScriptRoot\setup.iss"
if ($LASTEXITCODE -ne 0) {
    throw "Inno Setup failed"
}

Write-Host "Built dist\Androidbox-Setup-$version.exe"
