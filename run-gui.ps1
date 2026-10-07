<#
.SYNOPSIS
    k-method Antigravity 2.0 Webview GUI Launcher.
    Starts the local ASGI server and launches the graphical SDLC interface.

.EXAMPLE
    .\run-gui.ps1
    .\run-gui.ps1 -Port 8080 -NoBrowser
#>
param(
    [int]$Port = 8000,
    [string]$HostAddress = "127.0.0.1",
    [switch]$NoBrowser
)

# Enforce UTF-8 encoding in PowerShell console
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$PythonBin = "python"
$LauncherScript = Join-Path $PSScriptRoot "scripts\harness\gui\launch.py"

$CliArgs = @(
    "--port", $Port,
    "--host", $HostAddress
)
if ($NoBrowser) {
    $CliArgs += "--no-browser"
}

# Append any remaining raw arguments passed to the script
$CliArgs += $args

& $PythonBin $LauncherScript @CliArgs
exit $LASTEXITCODE
