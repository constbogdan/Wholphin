[CmdletBinding()]
param(
    [ValidateSet('Guided', 'Audit', 'Validate', 'Stage', 'Commit', 'Publish')]
    [string]$Phase = 'Guided',
    [string[]]$Files = @(),
    [string[]]$Exclude = @(),
    [ValidateSet('Standard', 'Full')]
    [string]$Level = 'Standard',
    [string[]]$TestFilter = @(),
    [string]$Title,
    [switch]$ConfirmScope,
    [switch]$ConfirmCommit,
    [switch]$ConfirmPublish,
    [switch]$NoFetch,
    [switch]$NonInteractive
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$configPath = Join-Path $PSScriptRoot 'prepare-pr.config.psd1'
$config = Import-PowerShellDataFile -LiteralPath $configPath
$startingLocation = Get-Location
$logPath = Join-Path $repoRoot 'prepare-pr.log'
$logStream = [IO.FileStream]::new($logPath, [IO.FileMode]::Create, [IO.FileAccess]::Write, [IO.FileShare]::Read)
$logWriter = [IO.StreamWriter]::new($logStream, [Text.UTF8Encoding]::new($false))
$logWriter.AutoFlush = $true

function Write-PrepareLog([string]$Message) {
    $logWriter.WriteLine(("{0} {1}" -f [DateTimeOffset]::Now.ToString('o'), $Message))
}

Write-PrepareLog "Invocation started. Phase=$Phase RequestedLevel=$Level"

function Write-Section([string]$Name) {
    Write-Host ''
    Write-Host "=== $Name ===" -ForegroundColor Cyan
    Write-PrepareLog "Phase started: $Name"
}

function Invoke-Git {
    param(
        [Parameter(Mandatory)]
        [string[]]$Arguments,
        [switch]$AllowFailure
    )
    $stderrPath = [IO.Path]::GetTempFileName()
    $previousErrorAction = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $rawOutput = @(& git -c core.quotepath=false @Arguments 2> $stderrPath)
        $exitCode = $LASTEXITCODE
        $errorOutput = if ((Get-Item -LiteralPath $stderrPath).Length) {
            $captured = @(Get-Content -LiteralPath $stderrPath)
            $nativeLines = @()
            foreach ($line in $captured) {
                if ($line -match '^At .+:\d+ char:\d+$') { break }
                if ($line -match '^\s*\+ ' -or $line -match '^\s*\+ CategoryInfo' -or $line -match '^\s*\+ FullyQualifiedErrorId') { continue }
                $nativeLines += ($line -replace '^git(?:\.exe)?\s*:\s*', '')
            }
            @($nativeLines)
        } else { @() }
    } finally {
        $ErrorActionPreference = $previousErrorAction
        Remove-Item -LiteralPath $stderrPath -Force -ErrorAction SilentlyContinue
    }
    $output = @($rawOutput | ForEach-Object { $_.ToString() })
    if ($exitCode -ne 0) {
        $details = @($output + $errorOutput) -join [Environment]::NewLine
        Write-PrepareLog "Git command failed (exit $exitCode): git $($Arguments -join ' ')"
        if ($details) { Write-PrepareLog "Git diagnostics: $details" }
    }
    if ($exitCode -ne 0 -and -not $AllowFailure) {
        throw "git $($Arguments -join ' ') failed (exit $exitCode):`n$details"
    }
    return [pscustomobject]@{ Output = $output; ErrorOutput = @($errorOutput); ExitCode = $exitCode }
}

function Get-GitText([string[]]$Arguments) {
    return ((Invoke-Git -Arguments $Arguments).Output -join "`n").Trim()
}

function Normalize-Path([string]$Path) {
    $value = $Path.Trim().Replace('\', '/')
    while ($value.StartsWith('./')) { $value = $value.Substring(2) }
    if (-not $value -or [IO.Path]::IsPathRooted($value) -or $value -match '(^|/)\.\.(/|$)') {
        throw "Path must be a repository-relative path: '$Path'."
    }
    return $value
}

function Get-ChangedEntries {
    $lines = (Invoke-Git -Arguments @('status', '--short', '--untracked-files=all')).Output
    $entries = @()
    foreach ($line in $lines) {
        if (-not $line -or $line.Length -lt 4) { continue }
        $code = $line.Substring(0, 2)
        $pathText = $line.Substring(3).Trim()
        $paths = if ($pathText -match ' -> ') { @($pathText -split ' -> ', 2) } else { @($pathText) }
        foreach ($path in $paths) {
            $entries += [pscustomobject]@{
                Code = $code
                Path = Normalize-Path $path.Trim('"')
                Staged = $code -ne '??' -and $code[0] -ne ' '
                Unstaged = $code -eq '??' -or $code[1] -ne ' '
                Untracked = $code -eq '??'
            }
        }
    }
    return @($entries)
}

function Get-RepositorySlug([string]$Url) {
    $normalized = $Url.Trim() -replace '\.git$', ''
    if ($normalized -match 'github\.com[:/](?<slug>[^/]+/[^/]+)$') { return $Matches.slug }
    return $null
}

function Test-Approval([string]$Prompt, [switch]$Confirmed) {
    if ($Confirmed) { return $true }
    if ($NonInteractive) { return $false }
    return (Read-Host "$Prompt [y/N]").Trim() -match '^(?i:y|yes)$'
}

function Test-RecommendedApproval([string]$Prompt) {
    if ($NonInteractive) { return $false }
    $answer = (Read-Host "$Prompt [Y/n]").Trim()
    return -not $answer -or $answer -match '^(?i:y|yes)$'
}

function Get-OperationStates {
    $names = @('MERGE_HEAD', 'rebase-merge', 'rebase-apply', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'BISECT_LOG')
    $active = @()
    foreach ($name in $names) {
        $path = Get-GitText @('rev-parse', '--git-path', $name)
        if (Test-Path -LiteralPath $path) { $active += $name }
    }
    return $active
}

function Assert-Preflight([switch]$RefreshBase) {
    Write-Section 'PREFLIGHT'
    $topLevel = Get-GitText @('rev-parse', '--show-toplevel')
    if ([IO.Path]::GetFullPath($topLevel) -ne [IO.Path]::GetFullPath($repoRoot)) {
        throw "Expected repository root '$repoRoot', but Git reported '$topLevel'."
    }
    $branch = Get-GitText @('branch', '--show-current')
    if (-not $branch) { throw 'Detached HEAD is not supported.' }
    if ($branch -eq $config.BaseBranch) { throw "Refusing to prepare or publish protected '$($config.BaseBranch)'." }
    $operations = @(Get-OperationStates)
    if ($operations.Count) { throw "An active Git operation must be completed or aborted manually first: $($operations -join ', ')." }
    $unmerged = Get-GitText @('diff', '--name-only', '--diff-filter=U')
    if ($unmerged) { throw "Unmerged paths remain:`n$unmerged" }

    foreach ($remoteName in @($config.OriginRemote, $config.UpstreamRemote)) {
        $remote = Invoke-Git -Arguments @('remote', 'get-url', $remoteName) -AllowFailure
        if ($remote.ExitCode -ne 0) { throw "Required remote '$remoteName' is missing." }
        $slug = Get-RepositorySlug ($remote.Output -join '')
        $expected = if ($remoteName -eq $config.OriginRemote) { $config.ExpectedOriginRepositories } else { $config.ExpectedUpstreamRepositories }
        if ($slug -notin $expected) { throw "Remote '$remoteName' points to unexpected repository '$slug'. Expected: $($expected -join ', ')." }
        Write-Host "$remoteName -> $slug"
    }
    foreach ($requiredPath in @($config.ValidationScript, $config.PullRequestTemplate)) {
        if (-not (Test-Path -LiteralPath (Join-Path $repoRoot $requiredPath) -PathType Leaf)) {
            throw "Required repository file is missing: $requiredPath"
        }
    }

    if ($RefreshBase -and -not $NoFetch) {
        Write-Host "Refreshing $($config.OriginRemote)/$($config.BaseBranch)..."
        Invoke-Git -Arguments @('fetch', '--no-tags', $config.OriginRemote, $config.BaseBranch) | Out-Null
    }
    $baseRef = "$($config.OriginRemote)/$($config.BaseBranch)"
    $baseCommit = Get-GitText @('rev-parse', $baseRef)
    $head = Get-GitText @('rev-parse', 'HEAD')
    $ancestor = Invoke-Git -Arguments @('merge-base', '--is-ancestor', $baseRef, 'HEAD') -AllowFailure
    if ($ancestor.ExitCode -ne 0) { throw "Current branch does not descend from validated $baseRef." }
    $trackingResult = Invoke-Git -Arguments @('rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{upstream}') -AllowFailure
    $tracking = if ($trackingResult.ExitCode -eq 0) { ($trackingResult.Output -join '').Trim() } else { '(none)' }
    $commits = @((Invoke-Git -Arguments @('log', '--oneline', "$baseRef..HEAD")).Output | Where-Object { $_ })
    $committedPaths = @(
        (Invoke-Git -Arguments @('diff', '--name-only', '--diff-filter=ACDMRTUXB', "$baseRef...HEAD", '--')).Output |
            Where-Object { $_ } |
            ForEach-Object { Normalize-Path $_ } |
            Sort-Object -Unique
    )
    $relationship = (Get-GitText @('rev-list', '--left-right', '--count', "$baseRef...HEAD")) -split '\s+'
    Write-Host "Branch: $branch"
    Write-Host "HEAD: $head"
    Write-Host "Base: $baseRef ($baseCommit)"
    Write-Host "Tracking: $tracking"
    $remoteBranchRef = "refs/remotes/$($config.OriginRemote)/$branch"
    $remoteBranchKnown = (Invoke-Git -Arguments @('show-ref', '--verify', '--quiet', $remoteBranchRef) -AllowFailure).ExitCode -eq 0
    Write-Host "Known remote branch: $(if ($remoteBranchKnown) { $remoteBranchRef } else { '(none in local refs)' })"
    Write-Host "Relationship to ${baseRef}: ahead $($relationship[1]), behind $($relationship[0])"
    Write-Host "Branch-only commits: $($commits.Count)"
    $commits | ForEach-Object { Write-Host "  $_" }
    Write-Host "Already committed PR paths: $($committedPaths.Count)"
    $committedPaths | ForEach-Object { Write-Host "  $_" }
    Write-PrepareLog "Preflight passed. Branch=$branch Base=$baseRef BaseCommit=$baseCommit HEAD=$head Tracking=$tracking"
    return [pscustomobject]@{
        Branch = $branch
        Head = $head
        BaseRef = $baseRef
        BaseCommit = $baseCommit
        Tracking = $tracking
        BranchCommits = $commits
        CommittedPaths = $committedPaths
    }
}

function Test-Pattern([string]$Path, [string[]]$Patterns) {
    foreach ($pattern in $Patterns) { if ($Path -like $pattern) { return $true } }
    return $false
}

function Resolve-Scope([object[]]$Entries) {
    if (-not $Entries.Count) { throw 'No modified, deleted, staged, or untracked paths were found.' }
    [string[]]$candidatePaths = if ($Files.Count) { $Files | ForEach-Object { Normalize-Path $_ } | Sort-Object -Unique } else { $Entries.Path | Sort-Object -Unique }
    [string[]]$excludedPaths = @($Exclude | ForEach-Object { Normalize-Path $_ })

    Write-Section 'AUDIT CHANGES'
    for ($i = 0; $i -lt $candidatePaths.Count; $i++) {
        $entry = $Entries | Where-Object Path -eq $candidatePaths[$i] | Select-Object -First 1
        $code = if ($entry) { $entry.Code } else { '--' }
        Write-Host ("[{0}] {1} {2}" -f ($i + 1), $code, $candidatePaths[$i])
    }
    if (-not $Files.Count -and -not $NonInteractive) {
        $answer = (Read-Host 'Numbers to exclude (comma-separated, blank keeps all)').Trim()
        if ($answer) {
            foreach ($token in $answer -split ',') {
                $number = 0
                if (-not [int]::TryParse($token.Trim(), [ref]$number) -or $number -lt 1 -or $number -gt $candidatePaths.Count) {
                    throw "Invalid exclusion number '$token'."
                }
                $excludedPaths += $candidatePaths[$number - 1]
            }
        }
    }
    $scope = @($candidatePaths | Where-Object { $_ -notin $excludedPaths } | Sort-Object -Unique)
    if (-not $scope.Count) { throw 'The confirmed scope cannot be empty.' }
    foreach ($path in $scope) {
        $entry = $Entries | Where-Object Path -eq $path | Select-Object -First 1
        if (-not $entry) { throw "Scoped path '$path' is not currently changed." }
        if ($entry.Untracked) {
            $ignored = Invoke-Git -Arguments @('check-ignore', '--no-index', '--quiet', '--', $path) -AllowFailure
            if ($ignored.ExitCode -eq 0) { throw "Refusing ignored untracked path '$path'." }
        }
        if (Test-Pattern $path $config.RefusedArtifactPatterns) { throw "Refusing likely local, generated, or sensitive artifact '$path'." }
    }
    Write-Host 'Proposed scope:'
    $scope | ForEach-Object { Write-Host "  $_" }
    return $scope
}

function Assert-NoOutOfScope([string[]]$Scope, [object[]]$Entries) {
    $outside = @($Entries.Path | Where-Object { $_ -notin $Scope } | Sort-Object -Unique)
    if ($outside.Count) {
        throw "Out-of-scope dirty paths would make validation differ from the intended commit. Preserve them in a separate worktree, then rerun:`n$($outside -join [Environment]::NewLine)"
    }
}

function Get-ManifestHash([string[]]$Lines) {
    $sha256 = [Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [Text.Encoding]::UTF8.GetBytes(($Lines -join "`n"))
        return ([BitConverter]::ToString($sha256.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant()
    } finally {
        $sha256.Dispose()
    }
}

function Get-GitObjectType([string]$Mode) {
    if ($Mode -eq '160000') { return 'commit' }
    return 'blob'
}

function Get-UntrackedFileMode([object]$Item) {
    if ($Item.PSObject.Properties.Name -contains 'LinkType' -and $Item.LinkType -eq 'SymbolicLink') { return '120000' }
    $isWindowsPlatform = if (Get-Variable IsWindows -ErrorAction SilentlyContinue) { $IsWindows } else { $env:OS -eq 'Windows_NT' }
    if (-not $isWindowsPlatform -and [IO.File].GetMethod('GetUnixFileMode', [type[]]@([string]))) {
        $unixMode = [IO.File]::GetUnixFileMode($Item.FullName)
        $executeBits = [IO.UnixFileMode]::UserExecute -bor [IO.UnixFileMode]::GroupExecute -bor [IO.UnixFileMode]::OtherExecute
        if (($unixMode -band $executeBits) -ne 0) { return '100755' }
    }
    return '100644'
}

function Get-WorkingEntryIdentity([string]$Path) {
    $fullPath = Join-Path $repoRoot $Path
    $indexEntry = (Invoke-Git -Arguments @('ls-files', '--stage', '--', $Path)).Output | Select-Object -First 1
    $indexMode = if ($indexEntry -and $indexEntry -match '^(?<mode>\d{6})\s+') { $Matches.mode } else { $null }
    $item = Get-Item -LiteralPath $fullPath -Force -ErrorAction SilentlyContinue
    if (-not $item) { return 'DELETE' }

    $rawLine = (Invoke-Git -Arguments @('diff', '--raw', '--no-abbrev', 'HEAD', '--', $Path)).Output | Select-Object -First 1
    $mode = if ($rawLine -and $rawLine -match '^:\d{6}\s+(?<mode>\d{6})\s+') { $Matches.mode } else { $indexMode }
    if (-not $mode) { $mode = Get-UntrackedFileMode $item }

    if ($mode -eq '160000') {
        $objectId = Get-GitText @('-C', $Path, 'rev-parse', 'HEAD')
    } else {
        $objectId = Get-GitText @('hash-object', '--path', $Path, '--', $Path)
    }
    $type = Get-GitObjectType $mode
    return "MODE=$mode`tTYPE=$type`tOID=$objectId"
}

function Get-WorkingSnapshotHash([string[]]$Scope) {
    $manifest = @()
    foreach ($path in @($Scope | Sort-Object -Unique)) {
        $manifest += "$path`t$(Get-WorkingEntryIdentity $path)"
    }
    return Get-ManifestHash $manifest
}

function Get-StagedSnapshotHash([string[]]$Scope) {
    $manifest = @()
    foreach ($path in @($Scope | Sort-Object -Unique)) {
        $entry = Invoke-Git -Arguments @('ls-files', '--stage', '--', $path)
        $line = ($entry.Output | Select-Object -First 1)
        if ($line -and $line -match '^(?<mode>\d{6})\s+(?<object>[0-9a-f]+)\s+\d+\s+') {
            $mode = $Matches.mode
            $objectId = $Matches.object
            $type = Get-GitObjectType $mode
            $manifest += "$path`tMODE=$mode`tTYPE=$type`tOID=$objectId"
        } else {
            $manifest += "$path`tDELETE"
        }
    }
    return Get-ManifestHash $manifest
}

function Get-StatePath {
    return Get-GitText @('rev-parse', '--git-path', 'wholphin-prepare-pr-state.json')
}

function Save-State([hashtable]$State) {
    $State.updatedAt = [DateTimeOffset]::UtcNow.ToString('o')
    $State | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Get-StatePath) -Encoding UTF8
}

function Load-State([object]$Preflight) {
    $path = Get-StatePath
    if (-not (Test-Path -LiteralPath $path)) { throw 'No resumable prepare-pr state exists. Run the guided workflow or Audit first.' }
    $state = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
    if ($state.version -ne 1) { throw 'Saved prepare-pr state uses an unsupported version. Run Audit again.' }
    if ($state.branch -ne $Preflight.Branch -or $state.baseCommit -ne $Preflight.BaseCommit -or $state.branchHead -ne $Preflight.Head) {
        throw 'Saved prepare-pr state is stale because the branch, base, or HEAD changed. Run Audit again.'
    }
    return $state
}

function Show-Audit([string[]]$Scope, [object[]]$Entries, [object]$Preflight) {
    Write-Section 'COMPLETE EVENTUAL PR SCOPE'
    Write-Host "Already committed branch content: $(@($Preflight.CommittedPaths).Count) path(s) in $(@($Preflight.BranchCommits).Count) commit(s)"
    @($Preflight.BranchCommits) | ForEach-Object { Write-Host "  commit: $_" }
    @($Preflight.CommittedPaths) | ForEach-Object { Write-Host "  committed: $_" }
    Write-Host "Current working-tree candidates: $($Scope.Count) path(s)"
    $Scope | ForEach-Object { Write-Host "  candidate: $_" }
    $publicationPaths = @(@($Preflight.CommittedPaths) + $Scope | Sort-Object -Unique)
    Write-Host "TOTAL COMPLETE PR SCOPE: $($publicationPaths.Count) UNIQUE PATH(S)" -ForegroundColor Green
    $publicationPaths | ForEach-Object { Write-Host "  PR: $_" }

    Write-Section 'INTENDED SNAPSHOT'
    $scopedEntries = @($Entries | Where-Object Path -in $Scope)
    $added = @($scopedEntries | Where-Object { $_.Untracked -or $_.Code -match 'A' })
    $deleted = @($scopedEntries | Where-Object { $_.Code -match 'D' })
    $renamed = @($scopedEntries | Where-Object { $_.Code -match 'R' })
    $modified = @($scopedEntries | Where-Object { -not $_.Untracked -and $_.Code -match 'M' })
    Write-Host "Tracked modified candidates: $($modified.Count)"
    Write-Host "Added/new candidates (including untracked): $($added.Count)"
    Write-Host "Deleted: $($deleted.Count)"
    Write-Host "Rename path entries: $($renamed.Count)"
    Write-Host "Staged: $(@($scopedEntries | Where-Object Staged).Count)"
    Write-Host "Unstaged: $(@($scopedEntries | Where-Object Unstaged).Count)"
    Write-Host "Untracked/new files outside tracked diff statistics: $(@($scopedEntries | Where-Object Untracked).Count)"
    Write-Host 'Tracked working-tree diff statistics (untracked/new files are listed separately below):'
    Invoke-Git -Arguments (@('diff', '--stat', 'HEAD', '--') + $Scope) | Select-Object -ExpandProperty Output | ForEach-Object { Write-Host $_ }
    Write-Host "Committed branch diff versus $($Preflight.BaseRef):"
    Invoke-Git -Arguments @('diff', '--stat', "$($Preflight.BaseRef)...HEAD") | Select-Object -ExpandProperty Output | ForEach-Object { Write-Host $_ }
    $untracked = @($scopedEntries | Where-Object Untracked)
    if ($untracked.Count) { Write-Host 'Untracked/new files included in eventual PR scope:' }
    $untracked | ForEach-Object { Write-Host "  untracked/new: $($_.Path)" }
    Write-PrepareLog "Audit scope: committedPaths=$(@($Preflight.CommittedPaths).Count) candidatePaths=$($Scope.Count) totalUniquePaths=$($publicationPaths.Count)"
    $publicationPaths | ForEach-Object { Write-PrepareLog "Audited publication path: $_" }

    $risks = @($publicationPaths | Where-Object { Test-Pattern $_ $config.HighRiskPatterns })
    if ($risks.Count) {
        Write-Host 'High-risk/review-sensitive paths:' -ForegroundColor Yellow
        $risks | ForEach-Object { Write-Host "  $_" }
    }

    $diffCheck = Invoke-Git -Arguments (@('diff', '--check', 'HEAD', '--') + $Scope) -AllowFailure
    if ($diffCheck.ExitCode -ne 0) { throw "git diff --check failed:`n$($diffCheck.Output -join [Environment]::NewLine)" }
    $committedDiffCheck = Invoke-Git -Arguments @('diff', '--check', "$($Preflight.BaseRef)...HEAD") -AllowFailure
    if ($committedDiffCheck.ExitCode -ne 0) { throw "Committed PR diff check failed:`n$($committedDiffCheck.Output -join [Environment]::NewLine)" }
    Write-Host 'git diff --check: PASS'

    $markers = @()
    foreach ($path in $publicationPaths) {
        $fullPath = Join-Path $repoRoot $path
        if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) { continue }
        try {
            $matches = Select-String -LiteralPath $fullPath -Pattern '^(<<<<<<< .+|=======|>>>>>>> .+)$' -ErrorAction Stop
            if ($matches) { $markers += $path }
        } catch { }
    }
    if ($markers.Count) { throw "Canonical conflict markers require review:`n$($markers -join [Environment]::NewLine)" }
    Write-Host 'Conflict-marker check: PASS'
    return $risks
}

function Confirm-AndSaveScope([object]$Preflight) {
    $entries = @(Get-ChangedEntries)
    $scope = @(Resolve-Scope $entries)
    Assert-NoOutOfScope $scope $entries
    $risks = @(Show-Audit $scope $entries $Preflight)
    if (-not (Test-Approval 'Confirm this exact path scope?' -Confirmed:$ConfirmScope)) { throw 'Scope was not confirmed.' }
    return Save-ConfirmedScope $Preflight $scope $risks
}

function Save-ConfirmedScope([object]$Preflight, [string[]]$Scope, [string[]]$Risks) {
    $snapshotHash = Get-WorkingSnapshotHash $Scope
    $state = @{
        version = 1
        branch = $Preflight.Branch
        baseRef = $Preflight.BaseRef
        baseCommit = $Preflight.BaseCommit
        branchHead = $Preflight.Head
        scope = $Scope
        committedPaths = @($Preflight.CommittedPaths)
        publicationPaths = @(@($Preflight.CommittedPaths) + $Scope | Sort-Object -Unique)
        branchCommits = @($Preflight.BranchCommits)
        intendedSnapshotHash = $snapshotHash
        highRiskPaths = $Risks
        validationLevel = $null
        validationResults = @()
        stagedTree = $null
        stagedSnapshotHash = $null
        approvedTitle = $null
        completedPhase = 'ScopeConfirmed'
    }
    Save-State $state
    Write-Host "Scope confirmed. Intended snapshot: $snapshotHash"
    Write-PrepareLog "Scope confirmed. IntendedSnapshot=$snapshotHash"
    @($state.publicationPaths) | ForEach-Object { Write-PrepareLog "Confirmed publication path: $_" }
    return [pscustomobject]$state
}

function Invoke-Validation([object]$Preflight, [object]$State, [string]$RequestedLevel) {
    Write-Section 'VALIDATE'
    $scope = @($State.scope)
    $entries = @(Get-ChangedEntries)
    Assert-NoOutOfScope $scope $entries
    $beforeSnapshot = Get-WorkingSnapshotHash $scope
    if ($beforeSnapshot -ne $State.intendedSnapshotHash) { throw 'The intended snapshot changed after scope confirmation. Run Audit again.' }

    $isUpstreamSync = $Preflight.Branch -like $config.UpstreamSyncBranchPattern
    $filters = @($TestFilter | Where-Object { $_ })
    if ($RequestedLevel -eq 'Standard' -and -not $filters.Count) {
        if (-not $NonInteractive) {
            $entered = (Read-Host 'Focused JVM test pattern(s) for Standard validation (comma-separated; for example *DownloadsPageTest*; blank when none apply)').Trim()
            if ($entered) { $filters = @($entered -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ }) }
        }
        if (-not $filters.Count) {
            if ($isUpstreamSync) {
                throw 'Upstream-sync preparation requires Standard validation with meaningful focused JVM test patterns followed by Full. Supply -TestFilter.'
            }
            if (Test-RecommendedApproval 'No honest focused JVM test pattern is available. Switch to Full validation (recommended)?') {
                $RequestedLevel = 'Full'
                Write-Host 'Using Full validation; no test filter was invented.'
                Write-PrepareLog 'Validation selection changed from Standard to Full because no focused JVM test pattern was available.'
            } else {
                throw 'Validation selection was declined. Nothing was staged; rerun with valid -TestFilter values or -Level Full.'
            }
        }
    }

    $levels = if ($isUpstreamSync) { @('Standard', 'Full') } else { @($RequestedLevel) }
    Write-PrepareLog "Validation selected: $($levels -join '+'); FocusedFilters=$($filters -join ',')"
    $results = @()
    foreach ($validationLevel in $levels) {
        $arguments = @('-Level', $validationLevel)
        if ($validationLevel -eq 'Standard') {
            if (-not $filters.Count) { throw 'Standard validation requires at least one actual focused JVM test pattern. Supply -TestFilter or choose Full.' }
            foreach ($filter in $filters) { $arguments += @('-TestFilter', $filter) }
        }
        Write-Host ".\$($config.ValidationScript) $($arguments -join ' ')"
        if ($validationLevel -eq 'Standard') {
            & (Join-Path $repoRoot $config.ValidationScript) -Level $validationLevel -TestFilter $filters
        } else {
            & (Join-Path $repoRoot $config.ValidationScript) -Level $validationLevel
        }
        $validationExitCode = $LASTEXITCODE
        if ($validationExitCode -ne 0) {
            Write-PrepareLog "$validationLevel validation failed with exit code $validationExitCode."
            $failedEntries = @(Get-ChangedEntries)
            $failedPaths = @($failedEntries.Path | Sort-Object -Unique)
            $failedOutside = @($failedPaths | Where-Object { $_ -notin $scope })
            $failedSnapshot = Get-WorkingSnapshotHash $scope
            if ($failedOutside.Count -or $failedSnapshot -ne $beforeSnapshot) {
                Write-Host 'Failed validation/autofix changed the working tree. Nothing was staged.' -ForegroundColor Yellow
                $failedEntries | ForEach-Object { Write-Host "$($_.Code) $($_.Path)" }
                throw 'Review the diff and rerun Audit/Validate against the reviewed snapshot.'
            }
            throw "$validationLevel validation failed with exit code $validationExitCode; the intended snapshot was unchanged."
        }
        $results += [pscustomobject]@{ level = $validationLevel; passed = $true; completedAt = [DateTimeOffset]::UtcNow.ToString('o') }
        Write-PrepareLog "$validationLevel validation passed."
    }

    $afterEntries = @(Get-ChangedEntries)
    $afterPaths = @($afterEntries.Path | Sort-Object -Unique)
    $scopePaths = @($scope | Sort-Object -Unique)
    $outside = @($afterPaths | Where-Object { $_ -notin $scopePaths })
    $afterSnapshot = Get-WorkingSnapshotHash $scope
    if ($outside.Count -or $afterSnapshot -ne $beforeSnapshot) {
        Write-Host 'Validation or autofix changed the working tree. Nothing was staged.' -ForegroundColor Yellow
        $afterEntries | ForEach-Object { Write-Host "$($_.Code) $($_.Path)" }
        throw 'Review the diff and rerun Audit/Validate against the reviewed snapshot.'
    }

    $updated = @{}
    $State.psobject.Properties | ForEach-Object { $updated[$_.Name] = $_.Value }
    $updated.validationLevel = ($levels -join '+')
    $updated.validationResults = $results
    $updated.completedPhase = 'Validated'
    Save-State $updated
    Write-Host "Validation passed for unchanged snapshot $afterSnapshot."
    Write-PrepareLog "Validation completed for unchanged snapshot $afterSnapshot."
    return [pscustomobject]$updated
}

function Invoke-Stage([object]$Preflight, [object]$State) {
    Write-Section 'STAGE CONFIRMED SCOPE'
    if ($State.completedPhase -ne 'Validated') { throw 'Current state is not validated.' }
    $scope = @($State.scope)
    Assert-NoOutOfScope $scope @(Get-ChangedEntries)
    if ((Get-WorkingSnapshotHash $scope) -ne $State.intendedSnapshotHash) { throw 'Validated snapshot is stale. Run Audit and Validate again.' }
    $outsideStaged = @(Get-ChangedEntries | Where-Object { $_.Staged -and $_.Path -notin $scope })
    if ($outsideStaged.Count) { throw "Staged paths exist outside the confirmed scope:`n$($outsideStaged.Path -join [Environment]::NewLine)" }
    $pathsToAdd = @()
    foreach ($path in $scope) {
        $trackedInIndex = (Invoke-Git -Arguments @('ls-files', '--error-unmatch', '--', $path) -AllowFailure).ExitCode -eq 0
        if ((Test-Path -LiteralPath (Join-Path $repoRoot $path)) -or $trackedInIndex) { $pathsToAdd += $path }
    }
    if ($pathsToAdd.Count) { Invoke-Git -Arguments (@('add', '-A', '--') + $pathsToAdd) | Out-Null }
    $stagedSnapshotHash = Get-StagedSnapshotHash $scope
    $stagedTree = Get-GitText @('write-tree')
    if ($stagedSnapshotHash -ne $State.intendedSnapshotHash) { throw 'The staged snapshot does not match the validated intended snapshot.' }
    Invoke-Git -Arguments @('status', '--short', '--untracked-files=all') | Select-Object -ExpandProperty Output | ForEach-Object { Write-Host $_ }
    Invoke-Git -Arguments @('diff', '--cached', '--stat') | Select-Object -ExpandProperty Output | ForEach-Object { Write-Host $_ }
    Write-Host 'Complete staged diff:'
    Invoke-Git -Arguments @('diff', '--cached') | Select-Object -ExpandProperty Output | ForEach-Object { Write-Host $_ }
    $updated = @{}
    $State.psobject.Properties | ForEach-Object { $updated[$_.Name] = $_.Value }
    $updated.stagedTree = $stagedTree
    $updated.stagedSnapshotHash = $stagedSnapshotHash
    $updated.completedPhase = 'Staged'
    Save-State $updated
    Write-PrepareLog "Staging completed. StagedSnapshot=$stagedSnapshotHash StagedTree=$stagedTree"
    return [pscustomobject]$updated
}

function Invoke-Commit([object]$Preflight, [object]$State) {
    Write-Section 'COMMIT'
    if ($State.completedPhase -ne 'Staged') { throw 'Current state is not at the reviewed staged phase.' }
    if ((Get-GitText @('write-tree')) -ne $State.stagedTree) { throw 'The staged snapshot changed after review.' }
    $scope = @($State.scope)
    Assert-NoOutOfScope $scope @(Get-ChangedEntries)
    if ((Get-WorkingSnapshotHash $scope) -ne $State.intendedSnapshotHash) { throw 'The working snapshot changed after validation/staging. Review and validate it again.' }
    $commitTitle = $Title
    if (-not $commitTitle -and -not $NonInteractive) { $commitTitle = (Read-Host 'Commit title (for example, chore: add safe PR preparation)').Trim() }
    if (-not $commitTitle) { throw 'An explicit commit title is required.' }
    if ($commitTitle -notmatch '^(feat|fix|chore|ci|docs|test|refactor)(\([^)]+\))?: .+') {
        Write-Host 'Warning: title does not use a recognized conventional prefix.' -ForegroundColor Yellow
    }
    Write-Host "Title: $commitTitle"
    Invoke-Git -Arguments @('diff', '--cached', '--stat') | Select-Object -ExpandProperty Output | ForEach-Object { Write-Host $_ }
    if (-not (Test-Approval 'Commit this reviewed staged snapshot?' -Confirmed:$ConfirmCommit)) { throw 'Commit was not approved.' }
    Invoke-Git -Arguments @('commit', '-m', $commitTitle) | Select-Object -ExpandProperty Output | ForEach-Object { Write-Host $_ }
    $commit = Get-GitText @('rev-parse', 'HEAD')
    $committedTree = Get-GitText @('rev-parse', 'HEAD^{tree}')
    if ($committedTree -ne $State.stagedTree) {
        Write-PrepareLog "Commit tree mismatch. Commit=$commit CommittedTree=$committedTree ReviewedTree=$($State.stagedTree)"
        throw "The produced commit tree '$committedTree' does not match the reviewed staged tree '$($State.stagedTree)'. A hook or concurrent process changed the commit; publication is refused."
    }
    $updated = @{}
    $State.psobject.Properties | ForEach-Object { $updated[$_.Name] = $_.Value }
    $updated.approvedTitle = $commitTitle
    $updated.commit = $commit
    $updated.branchHead = $commit
    $updated.completedPhase = 'Committed'
    Save-State $updated
    Write-PrepareLog "Commit completed. Commit=$commit Tree=$committedTree Title=$commitTitle"
    return [pscustomobject]$updated
}

function New-PullRequestBody([object]$State) {
    $riskText = if (@($State.highRiskPaths).Count) { (@($State.highRiskPaths) | ForEach-Object { "- ``$($_)``" }) -join "`n" } else { 'None flagged.' }
    $docPaths = @($State.publicationPaths | Where-Object { $_ -like 'docs/*' })
    $docsText = if ($docPaths.Count) { ($docPaths | ForEach-Object { "- ``$($_)``" }) -join "`n" } else { 'Not applicable.' }
    $uiChanged = @($State.publicationPaths | Where-Object { $_ -like 'app/src/*/java/*/ui/*' -or $_ -like 'app/src/*/res/*' }).Count -gt 0
    $applicationChanged = @($State.publicationPaths | Where-Object { $_ -like 'app/*' }).Count -gt 0
    $screenshots = if ($uiChanged) { 'Not supplied by prepare-pr; add screenshots or explain why they are not applicable before merge.' } else { 'Not applicable; no UI path was detected.' }
    $scopeText = (@($State.publicationPaths) | ForEach-Object { "- ``$($_)``" }) -join "`n"
    return @"
## Description

$($State.approvedTitle)

Confirmed paths:

$scopeText

Application paths changed: $(if ($applicationChanged) { 'yes' } else { 'no' }).
UI paths changed: $(if ($uiChanged) { 'yes' } else { 'no' }).

### Related issues

Not recorded by prepare-pr. Add references or state that none apply.

### Testing

- Local validation: $($State.validationLevel) passed for the committed snapshot.
- Required `CI / Full validation`: pending.
- Android TV/manual runtime validation: not recorded by prepare-pr; update if applicable.

### Review-sensitive paths

$riskText

### Documentation

$docsText

## Screenshots

$screenshots

## AI or LLM usage

Not recorded automatically. Disclose applicable assistance and human verification before merge.
"@
}

function Invoke-Publish([object]$Preflight, [object]$State) {
    Write-Section 'PUBLISH'
    if ($State.completedPhase -ne 'Committed') { throw 'A reviewed commit created by prepare-pr is required before publication.' }
    if ((Get-GitText @('rev-parse', 'HEAD')) -ne $State.commit) { throw 'HEAD changed after the approved commit.' }
    if (Get-GitText @('status', '--porcelain=v1', '--untracked-files=all')) { throw 'The working tree must be clean before publication.' }
    $pullRequestBody = New-PullRequestBody $State
    Write-Host 'Proposed pull-request body:'
    Write-Host $pullRequestBody
    if (-not (Test-Approval 'Publish this branch and create/provide its PR?' -Confirmed:$ConfirmPublish)) { throw 'Publication was not approved.' }

    $branch = $Preflight.Branch
    $remoteRef = "refs/heads/$branch"
    $remoteQuery = Invoke-Git -Arguments @('ls-remote', '--heads', $config.OriginRemote, $remoteRef) -AllowFailure
    if ($remoteQuery.ExitCode -ne 0) { throw 'Could not inspect the remote branch safely.' }
    $remoteExists = [bool](($remoteQuery.Output -join '').Trim())
    if ($remoteExists) {
        $remoteCommit = (($remoteQuery.Output | Select-Object -First 1) -split '\s+')[0]
        Invoke-Git -Arguments @('fetch', '--no-tags', $config.OriginRemote, $remoteRef) | Out-Null
        $fastForward = Invoke-Git -Arguments @('merge-base', '--is-ancestor', $remoteCommit, 'HEAD') -AllowFailure
        if ($fastForward.ExitCode -ne 0) { throw 'Remote branch is divergent or ahead; publication would require a force push. Refusing.' }
        Invoke-Git -Arguments @('push', $config.OriginRemote, $branch) | Select-Object -ExpandProperty Output | ForEach-Object { Write-Host $_ }
    } else {
        Invoke-Git -Arguments @('push', '-u', $config.OriginRemote, $branch) | Select-Object -ExpandProperty Output | ForEach-Object { Write-Host $_ }
    }

    $originUrl = Get-GitText @('remote', 'get-url', $config.OriginRemote)
    $slug = Get-RepositorySlug $originUrl
    $gh = Get-Command gh -ErrorAction SilentlyContinue
    $prResult = $null
    if ($gh) {
        & $gh.Source auth status 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $existing = @(& $gh.Source pr list --repo $slug --base $config.BaseBranch --head $branch --state open --json number,url --jq '.[] | "#\(.number) \(.url)"' 2>&1)
            if ($LASTEXITCODE -ne 0) { throw "GitHub CLI could not inspect existing PRs:`n$($existing -join [Environment]::NewLine)" }
            if ($existing.Count) {
                Write-Host "Existing PR: $($existing -join ', ')"
                $prResult = 'existing PR reported; description unchanged'
                Write-PrepareLog "Existing PR: $($existing -join ', ')"
            } else {
                $bodyFile = Join-Path ([IO.Path]::GetTempPath()) ("wholphin-pr-{0}.md" -f [guid]::NewGuid())
                try {
                    $pullRequestBody | Set-Content -LiteralPath $bodyFile -Encoding UTF8
                    $created = @(& $gh.Source pr create --repo $slug --base $config.BaseBranch --head $branch --title $State.approvedTitle --body-file $bodyFile 2>&1)
                    if ($LASTEXITCODE -ne 0) { throw "GitHub CLI could not create the PR:`n$($created -join [Environment]::NewLine)" }
                    Write-Host "PR created: $($created -join '')"
                    $prResult = 'PR created'
                    Write-PrepareLog "PR created: $($created -join '')"
                } finally { Remove-Item -LiteralPath $bodyFile -Force -ErrorAction SilentlyContinue }
            }
        }
    }
    if (-not $prResult) {
        $encodedBranch = [Uri]::EscapeDataString($branch)
        $url = "https://github.com/$slug/compare/$($config.BaseBranch)...${encodedBranch}?expand=1"
        Write-Host 'GitHub CLI is unavailable or unauthenticated; PR existence was not queried.' -ForegroundColor Yellow
        Write-Host "Create the PR manually: $url"
        $prResult = 'PR creation link provided'
        Write-PrepareLog "PR URL provided: $url"
    }
    Write-Host 'Branch published.'
    Write-Host "$prResult."
    Write-Host 'Required CI / Full validation pending.'
    Write-Host 'Merge remains manual.'
    if ($gh) { Write-Host "Optional follow-up: gh pr checks --repo $slug --watch" }
    Write-PrepareLog "Publication completed. Branch=$branch Result=$prResult"
}

try {
    Set-Location -LiteralPath $repoRoot
    if ($NoFetch -and -not $NonInteractive) { throw '-NoFetch is reserved for isolated non-interactive testing.' }
    $refresh = $Phase -in @('Guided', 'Validate', 'Publish')
    $preflight = Assert-Preflight -RefreshBase:$refresh

    if ($Phase -eq 'Guided') {
        $state = Confirm-AndSaveScope $preflight
        $state = Invoke-Validation $preflight $state $Level
        $state = Invoke-Stage $preflight $state
        if (-not (Test-Approval 'The staged diff is displayed above. Continue to title and commit?' -Confirmed:$ConfirmCommit)) { throw 'Stopped for staged snapshot review. Resume with -Phase Commit.' }
        $state = Invoke-Commit $preflight $state
        if (Test-Approval 'Commit complete. Publish now?' -Confirmed:$ConfirmPublish) {
            $ConfirmPublish = $true
            Invoke-Publish $preflight $state
        } else {
            Write-Host 'Commit complete; publication deferred. Resume with -Phase Publish.'
        }
        exit 0
    }

    switch ($Phase) {
        'Audit' {
            $entries = @(Get-ChangedEntries)
            $scope = @(Resolve-Scope $entries)
            Assert-NoOutOfScope $scope $entries
            $risks = @(Show-Audit $scope $entries $preflight)
            if (Test-Approval 'Save this exact scope for resumable preparation?' -Confirmed:$ConfirmScope) {
                Save-ConfirmedScope $preflight $scope $risks | Out-Null
            }
        }
        'Validate' {
            $state = if ($Files.Count) { Confirm-AndSaveScope $preflight } else { Load-State $preflight }
            Invoke-Validation $preflight $state $Level | Out-Null
        }
        'Stage' { Invoke-Stage $preflight (Load-State $preflight) | Out-Null }
        'Commit' { Invoke-Commit $preflight (Load-State $preflight) | Out-Null }
        'Publish' { Invoke-Publish $preflight (Load-State $preflight) }
    }
} catch {
    Write-PrepareLog "FAILED: $($_.Exception.Message)"
    Write-Error $_.Exception.Message
    $global:LASTEXITCODE = 1
    exit 1
} finally {
    Write-PrepareLog 'Invocation finished.'
    $logWriter.Dispose()
    $logStream.Dispose()
    Set-Location -LiteralPath $startingLocation
    Write-Host "Prepare-pr log: $logPath"
}
