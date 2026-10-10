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

.venv\Scripts\pyinstaller.exe "$PSScriptRoot\Androidbox.pyw" `
    --name Androidbox `
    --onedir `
    --windowed `
    --icon "$PSScriptRoot\assets\androidbox.ico" `
    --add-data "$PSScriptRoot\assets\androidbox.ico;assets" `
    --exclude-module tkinter `
    --collect-all sdl2dll `
    --distpath "$PSScriptRoot\dist" `
    --workpath "$PSScriptRoot\build" `
    --specpath "$PSScriptRoot\build" `
    --noconfirm `
    --clean `
    --log-level WARN

& $inno /Qp "/DAppVersion=$version" "$PSScriptRoot\setup.iss"
if ($LASTEXITCODE -ne 0) {
    throw "Inno Setup failed"
}

Write-Host "Built dist\Androidbox-Setup-$version.exe"
