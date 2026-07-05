param(
  [string]$Output = ".\data\latest_windows_telemetry.json",
  [switch]$RenderDashboard
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$argsList = @(".\windows_agent.py", "--output", $Output)
if ($RenderDashboard) {
  $argsList += "--render-dashboard"
}

python @argsList
