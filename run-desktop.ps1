<#
.SYNOPSIS
    k-method app Electron Desktop Launcher.
    Runs the native desktop application (Vite + React + Tailwind + Electron)
    communicating with the k-method Python SDLC engine.

.EXAMPLE
    .\run-desktop.ps1
    .\run-desktop.ps1 -Dev
#>
param(
    [switch]$Dev
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$DesktopDir = Join-Path $PSScriptRoot "desktop"
$PackagedExe = Join-Path $DesktopDir "release\win-unpacked\k-method app.exe"

# If -Dev flag passed, run Vite + Electron in development mode with HMR
if ($Dev) {
    Write-Host "[k-method app] Iniciando en Modo Desarrollo (Vite + Electron HMR)..." -ForegroundColor Cyan
    Push-Location $DesktopDir
    try {
        & pnpm run dev
    } finally {
        Pop-Location
    }
    exit $LASTEXITCODE
}

# If packaged executable exists, run it directly
if (Test-Path $PackagedExe) {
    Write-Host "[k-method app] Lanzando aplicación empaquetada..." -ForegroundColor Green
    Start-Process -FilePath $PackagedExe
    exit 0
} else {
    Write-Host "[k-method app] Aplicación empaquetada no encontrada. Ejecutando compilación previa..." -ForegroundColor Yellow
    Push-Location $DesktopDir
    try {
        & pnpm run build
        if (Test-Path $PackagedExe) {
            Start-Process -FilePath $PackagedExe
        }
    } finally {
        Pop-Location
    }
    exit $LASTEXITCODE
}
