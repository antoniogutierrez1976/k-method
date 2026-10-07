# PowerShell Build Script: k-method Antigravity 2.0 GUI Standalone Executable (.exe)
# Generates: dist/k-method-studio.exe

$ErrorActionPreference = "Stop"

Write-Host "════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   📦 EMPAQUETADOR DE EJECUTABLE WINDOWS (.EXE) - k-method Studio   " -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

# 1. Verificar PyInstaller
$pyinstallerCheck = Get-Command pyinstaller -ErrorAction SilentlyContinue
if (-not $pyinstallerCheck) {
    Write-Host "⚠️ PyInstaller no está instalado en el entorno actual." -ForegroundColor Yellow
    Write-Host "Instalando PyInstaller..." -ForegroundColor Green
    python -m pip install pyinstaller --quiet
}

# 2. Compilar con la especificación
Write-Host "🚀 Iniciando compilación de 'dist/k-method-studio.exe'..." -ForegroundColor Green
pyinstaller packaging/k-method-studio.spec --noconfirm --distpath dist --workpath build

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "════════════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "🎉 COMPILACIÓN EXITOSA: dist/k-method-studio.exe generado." -ForegroundColor Green
    Write-Host "════════════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "Puedes ejecutarlo directamente con: .\dist\k-method-studio.exe"
} else {
    Write-Host "❌ Error durante la compilación con PyInstaller." -ForegroundColor Red
    exit 1
}
