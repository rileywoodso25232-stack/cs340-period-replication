param(
    [string]$RecordDirectory
)

$ErrorActionPreference = 'Stop'
$taskRepoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
if (-not $RecordDirectory) {
    $RecordDirectory = Join-Path $taskRepoRoot 'environment/records/windows-setup'
}
New-Item -ItemType Directory -Force -Path $RecordDirectory | Out-Null
$taskStatePath = Join-Path $RecordDirectory 'wsl-install-state.json'
$taskLogPath = Join-Path $RecordDirectory 'wsl-install.log'
$taskState = [ordered]@{
    updated_at_utc = [DateTime]::UtcNow.ToString('o')
    stage = 'starting'
    restart_required = $false
    wsl_installed = $false
    linux_smoke_test_run = $false
    features = @()
}

function Save-TaskState {
    $taskState.updated_at_utc = [DateTime]::UtcNow.ToString('o')
    $taskState | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $taskStatePath -Encoding UTF8
}

try {
    $taskPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    if (-not $taskPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw 'Run this script from an administrator PowerShell session.'
    }
    $taskState.stage = 'enabling_windows_features'
    Save-TaskState
    foreach ($taskFeatureName in @('Microsoft-Windows-Subsystem-Linux', 'VirtualMachinePlatform')) {
        $taskBefore = Get-WindowsOptionalFeature -Online -FeatureName $taskFeatureName
        $taskFeatureRecord = [ordered]@{ name = $taskFeatureName; before = [string]$taskBefore.State }
        if ($taskBefore.State -ne 'Enabled') {
            $taskEnableResult = Enable-WindowsOptionalFeature -Online -FeatureName $taskFeatureName -All -NoRestart
            $taskFeatureRecord.restart_needed = [bool]$taskEnableResult.RestartNeeded
            if ($taskEnableResult.RestartNeeded) { $taskState.restart_required = $true }
        }
        $taskAfter = Get-WindowsOptionalFeature -Online -FeatureName $taskFeatureName
        $taskFeatureRecord.after = [string]$taskAfter.State
        if ([string]$taskAfter.State -match 'Pending') { $taskState.restart_required = $true }
        $taskState.features += $taskFeatureRecord
        Save-TaskState
    }
    if ($taskState.restart_required) {
        $taskState.stage = 'restart_required_before_runtime_install'
        Save-TaskState
        exit 0
    }
    $taskState.stage = 'installing_wsl_runtime'
    Save-TaskState
    & "$env:SystemRoot/System32/wsl.exe" --install --no-distribution --web-download 2>&1 |
        Out-File -LiteralPath $taskLogPath -Encoding UTF8
    $taskWslExit = $LASTEXITCODE
    $taskState.wsl_install_exit_code = $taskWslExit
    if ($taskWslExit -eq 3010) { $taskState.restart_required = $true }
    if ($taskWslExit -notin @(0, 3010)) {
        throw "WSL installation returned $taskWslExit. Inspect wsl-install.log."
    }
    $taskState.wsl_installed = $true
    $taskState.stage = if ($taskState.restart_required) { 'restart_required' } else { 'ready_for_distribution' }
    Save-TaskState
} catch {
    $taskState.stage = 'failed'
    $taskState.error = $_.Exception.Message
    Save-TaskState
    $_ | Out-String | Add-Content -LiteralPath $taskLogPath -Encoding UTF8
    exit 1
}
