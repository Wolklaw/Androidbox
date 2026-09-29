$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path .venv)) {
    python -m venv .venv
}
.venv\Scripts\python.exe -m pip install --quiet --disable-pip-version-check -r requirements.txt pyinstaller

.venv\Scripts\pyinstaller.exe "$PSScriptRoot\Androidbox.pyw" `
    --name Androidbox `
    --onefile `
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

Write-Host "Built dist\Androidbox.exe"
