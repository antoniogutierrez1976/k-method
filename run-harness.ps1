<#
.SYNOPSIS
    k-method Windows Skills Runner Launcher.
    Runs the Antigravity-style SDLC execution harness with Copilot or Antigravity SDKs.

.EXAMPLE
    .\run-harness.ps1 --provider copilot --model gpt-6-luna --task "Implement metrics endpoint"
    .\run-harness.ps1 --provider antigravity --task "Add unit tests"
#>
param(
    [string]$Provider = "",
    [string]$Model = "",
    [string]$Task = "",
    [switch]$AutoApprove
)

# Enforce UTF-8 encoding in PowerShell console
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$PythonBin = "python"
$RunnerScript = Join-Path $PSScriptRoot "scripts\harness\k_runner.py"

$CliArgs = @()
if ($Provider) { $CliArgs += "--provider", $Provider }
if ($Model) { $CliArgs += "--model", $Model }
if ($Task) { $CliArgs += "--task", $Task }
if ($AutoApprove) { $CliArgs += "--auto-approve" }

# Append any remaining raw arguments passed to the script
$CliArgs += $args

& $PythonBin $RunnerScript @CliArgs
exit $LASTEXITCODE
