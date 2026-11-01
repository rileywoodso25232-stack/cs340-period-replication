param(
    [Parameter(Mandatory = $true)][string]$KernelPackagePath,
    [int]$BootstrapProcessId = 0,
    [int]$BootstrapParentProcessId = 0
)

$ErrorActionPreference = 'Stop'
$taskRepoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$taskRecordDir = Join-Path $taskRepoRoot 'environment/records/windows-setup'
$taskStatePath = Join-Path $taskRecordDir 'wsl-install-state.json'
$taskState = Get-Content -Raw -LiteralPath $taskStatePath | ConvertFrom-Json
try {
    $taskSignature = Get-AuthenticodeSignature -LiteralPath $KernelPackagePath
    if ($taskSignature.Status -ne 'Valid' -or $taskSignature.SignerCertificate.Subject -notmatch 'O=Microsoft Corporation') {
        throw 'The kernel MSI must have a valid Microsoft Corporation signature.'
    }
    if ($BootstrapProcessId -gt 0) {
        $taskBootstrap = Get-CimInstance Win32_Process -Filter "ProcessId=$BootstrapProcessId"
        if ($taskBootstrap) {
            if ($taskBootstrap.Name -ne 'wsl.exe' -or $taskBootstrap.ParentProcessId -ne $BootstrapParentProcessId) {
                throw 'The bootstrap process identity changed; refusing to stop it.'
            }
            Stop-Process -Id $BootstrapProcessId
            if (Get-Process -Id $BootstrapParentProcessId -ErrorAction SilentlyContinue) {
                Wait-Process -Id $BootstrapParentProcessId -Timeout 20
            }
        }
    }
    $taskState = Get-Content -Raw -LiteralPath $taskStatePath | ConvertFrom-Json
    $taskState.stage = 'installing_inbox_kernel_package'
    $taskState | Add-Member -Force NoteProperty runtime_route 'windows_inbox_wsl2'
    $taskState | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $taskStatePath -Encoding UTF8
    $taskMsiLog = Join-Path $taskRecordDir 'inbox-kernel-msi.log'
    $taskArguments = '/i "' + $KernelPackagePath + '" /qn /norestart /l*v "' + $taskMsiLog + '"'
    $taskMsi = Start-Process -FilePath 'msiexec.exe' -ArgumentList $taskArguments -Wait -PassThru -WindowStyle Hidden
    $taskState | Add-Member -Force NoteProperty kernel_msi_exit_code $taskMsi.ExitCode
    if ($taskMsi.ExitCode -notin @(0, 3010)) { throw "Kernel MSI returned $($taskMsi.ExitCode); inspect inbox-kernel-msi.log." }
    $taskState | Add-Member -Force NoteProperty kernel_package_installed $true
    $taskState | Add-Member -Force NoteProperty kernel_package_signer $taskSignature.SignerCertificate.Subject
    $taskState | Add-Member -Force NoteProperty linux_distribution_installed $false
    $taskState.restart_required = $true
    $taskState.stage = 'restart_required'
    $taskState.updated_at_utc = [DateTime]::UtcNow.ToString('o')
    $taskState.PSObject.Properties.Remove('error')
    $taskState | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $taskStatePath -Encoding UTF8
} catch {
    $taskState.stage = 'inbox_setup_failed'
    $taskState | Add-Member -Force NoteProperty error $_.Exception.Message
    $taskState | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $taskStatePath -Encoding UTF8
    exit 1
}
