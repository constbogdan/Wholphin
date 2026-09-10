function Format-MosaicDuration {
    param([TimeSpan]$Elapsed)
    if ($Elapsed.TotalHours -ge 1) { return $Elapsed.ToString('h\:mm\:ss') }
    if ($Elapsed.TotalMinutes -ge 1) { return ('{0}m{1:00}s' -f [int]$Elapsed.TotalMinutes, $Elapsed.Seconds) }
    return ('{0:0.0}s' -f $Elapsed.TotalSeconds)
}

function New-MosaicRunOutput {
    param(
        [Parameter(Mandatory)][string]$RepositoryRoot,
        [Parameter(Mandatory)][ValidateSet('validation', 'prepare-pr')][string]$Kind,
        [Parameter(Mandatory)][string]$LegacyLogPath
    )
    $runId = '{0}-{1}' -f (Get-Date -Format 'yyyyMMdd-HHmmss'), $PID
    $runDirectory = Join-Path $RepositoryRoot ".logs\$Kind\$runId"
    New-Item -ItemType Directory -Path $runDirectory -Force | Out-Null
    [pscustomobject]@{
        Kind = $Kind
        RunDirectory = [IO.Path]::GetFullPath($runDirectory)
        SummaryPath = [IO.Path]::GetFullPath((Join-Path $runDirectory 'summary.txt'))
        LegacyLogPath = [IO.Path]::GetFullPath($LegacyLogPath)
        StageLogs = [Collections.Generic.List[string]]::new()
        LegacyLogPublished = $false
        CurrentStageLog = $null
        CurrentStageName = $null
        CurrentStageNumber = 0
        TotalStages = 0
        Timer = [Diagnostics.Stopwatch]::StartNew()
        StageTimer = $null
    }
}

function Write-MosaicRunLog {
    param([Parameter(Mandatory)]$Context, [Parameter(Mandatory)][string]$Message)
    $line = '{0} {1}' -f [DateTimeOffset]::Now.ToString('o'), $Message
    Add-Content -LiteralPath $Context.SummaryPath -Value $line -Encoding UTF8
    if ($Context.CurrentStageLog) {
        Add-Content -LiteralPath $Context.CurrentStageLog -Value $Message -Encoding UTF8
    }
}

function Publish-MosaicLegacyLog {
    param([Parameter(Mandatory)]$Context)
    if ($Context.LegacyLogPublished) { return $true }

    $snapshotPath = Join-Path $Context.RunDirectory 'compatibility.log'
    try {
        $lines = [Collections.Generic.List[string]]::new()
        $lines.Add("Mosaic $($Context.Kind) compatibility log - $(Get-Date -Format o)")
        $lines.Add('')
        $lines.Add('=== Run summary ===')
        if (Test-Path -LiteralPath $Context.SummaryPath) {
            foreach ($line in Get-Content -LiteralPath $Context.SummaryPath) { $lines.Add([string]$line) }
        }
        foreach ($stageLog in $Context.StageLogs) {
            $lines.Add('')
            $lines.Add("=== Stage log: $([IO.Path]::GetFileName($stageLog)) ===")
            if (Test-Path -LiteralPath $stageLog) {
                foreach ($line in Get-Content -LiteralPath $stageLog) { $lines.Add([string]$line) }
            }
        }

        [IO.File]::WriteAllLines($snapshotPath, $lines, [Text.UTF8Encoding]::new($false))
        [IO.File]::Copy($snapshotPath, $Context.LegacyLogPath, $true)
        $Context.LegacyLogPublished = $true
        return $true
    } catch {
        $message = "Compatibility log could not be refreshed: $($_.Exception.Message)"
        Add-Content -LiteralPath $Context.SummaryPath -Value ('{0} {1}' -f [DateTimeOffset]::Now.ToString('o'), $message) -Encoding UTF8 -ErrorAction SilentlyContinue
        Write-Warning "$message Complete logs remain available at $($Context.RunDirectory)."
        return $false
    }
}

function Start-MosaicStage {
    param(
        [Parameter(Mandatory)]$Context,
        [Parameter(Mandatory)][int]$Number,
        [Parameter(Mandatory)][int]$Total,
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][string]$LogName
    )
    $Context.CurrentStageNumber = $Number
    $Context.TotalStages = $Total
    $Context.CurrentStageName = $Name
    $Context.CurrentStageLog = [IO.Path]::GetFullPath((Join-Path $Context.RunDirectory $LogName))
    $Context.StageLogs.Add($Context.CurrentStageLog)
    $Context.StageTimer = [Diagnostics.Stopwatch]::StartNew()
    Set-Content -LiteralPath $Context.CurrentStageLog -Value ("Stage: $Name`nStarted: $(Get-Date -Format o)") -Encoding UTF8
    Write-Host ('[{0}/{1}] {2} [RUN]' -f $Number, $Total, $Name)
    Write-MosaicRunLog $Context "Stage started: $Name; Log=$($Context.CurrentStageLog)"
}

function Complete-MosaicStage {
    param([Parameter(Mandatory)]$Context)
    $Context.StageTimer.Stop()
    $duration = Format-MosaicDuration $Context.StageTimer.Elapsed
    Write-MosaicRunLog $Context "Stage passed: $($Context.CurrentStageName); Duration=$duration"
    Write-Host ('[{0}/{1}] {2} [PASS] {3} -> {4}' -f $Context.CurrentStageNumber, $Context.TotalStages, $Context.CurrentStageName, $duration, $Context.CurrentStageLog)
    $Context.CurrentStageLog = $null
    $Context.CurrentStageName = $null
}

function Get-MosaicErrorExcerpt {
    param([Parameter(Mandatory)][string]$LogPath, [int]$MaximumLines = 16)
    if (-not (Test-Path -LiteralPath $LogPath)) { return @() }
    $lines = @(Get-Content -LiteralPath $LogPath)
    $matches = @($lines | Where-Object {
        $_ -match '(?i)(^|\s)(error|exception|failed|failure|fatal)(:|\s)' -or
        $_ -match '(^|\s)e:\s+.+:\d+(?::\d+)?'
    })
    if ($matches.Count) { return @($matches | Select-Object -Last $MaximumLines) }
    return @($lines | Select-Object -Last $MaximumLines)
}

function Fail-MosaicStage {
    param([Parameter(Mandatory)]$Context, [Parameter(Mandatory)][string]$Reason)
    if ($Context.StageTimer) { $Context.StageTimer.Stop() }
    $duration = if ($Context.StageTimer) { Format-MosaicDuration $Context.StageTimer.Elapsed } else { '0.0s' }
    $logPath = $Context.CurrentStageLog
    Write-MosaicRunLog $Context "Stage failed: $($Context.CurrentStageName); Duration=$duration; Reason=$Reason"
    Write-Host ('[{0}/{1}] {2} [FAIL] {3}' -f $Context.CurrentStageNumber, $Context.TotalStages, $Context.CurrentStageName, $duration) -ForegroundColor Red
    Write-Host ''
    Write-Host "FAILED: $($Context.CurrentStageName)" -ForegroundColor Red
    Write-Host $Reason
    if ($logPath) {
        Write-Host ''
        Write-Host 'Relevant output:'
        Get-MosaicErrorExcerpt $logPath | ForEach-Object { Write-Host "  $_" }
        Write-Host ''
        Write-Host "Full log: $logPath"
    }
}

function Complete-MosaicRun {
    param([Parameter(Mandatory)]$Context, [Parameter(Mandatory)][string]$Message)
    $Context.Timer.Stop()
    $duration = Format-MosaicDuration $Context.Timer.Elapsed
    Write-MosaicRunLog $Context "$Message; Total=$duration"
    Write-Host ''
    Write-Host $Message
    Write-Host "Total: $duration"
    Write-Host "Logs: $($Context.RunDirectory)"
}

function Invoke-MosaicLoggedCommand {
    param(
        [Parameter(Mandatory)]$Context,
        [Parameter(Mandatory)][string]$FilePath,
        [Parameter(Mandatory)][string[]]$Arguments,
        [Parameter(Mandatory)][string]$DisplayCommand
    )
    Write-MosaicRunLog $Context "Command: $DisplayCommand"
    Add-Content -LiteralPath $Context.CurrentStageLog -Value "Command: $DisplayCommand" -Encoding UTF8
    $previousErrorAction = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & $FilePath @Arguments 2>&1 | ForEach-Object {
            $line = [string]$_
            Add-Content -LiteralPath $Context.CurrentStageLog -Value $line -Encoding UTF8
        }
        return $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorAction
    }
}
