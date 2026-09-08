[CmdletBinding()]
param(
    [ValidateSet('Fast', 'Standard', 'Full')]
    [string]$Level = 'Fast',

    [string[]]$TestFilter = @()
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$logPath = Join-Path $repoRoot 'validation.log'
$gradleWrapper = Join-Path $repoRoot 'gradlew.bat'
$totalTimer = [System.Diagnostics.Stopwatch]::StartNew()
$completedSteps = [System.Collections.Generic.List[string]]::new()
$logStream = [System.IO.FileStream]::new(
    $logPath,
    [System.IO.FileMode]::Create,
    [System.IO.FileAccess]::Write,
    [System.IO.FileShare]::ReadWrite
)
$script:logWriter = [System.IO.StreamWriter]::new(
    $logStream,
    [System.Text.UTF8Encoding]::new($false)
)
$script:logWriter.AutoFlush = $true

$script:logWriter.WriteLine("Wholphin local validation ($Level) - $(Get-Date -Format o)")

function Write-ValidationLine {
    param([string]$Message)
    Write-Host $Message
    $script:logWriter.WriteLine($Message)
}

function Write-LoggedOutput {
    process {
        $line = [string]$_
        Write-Host $line
        $script:logWriter.WriteLine($line)
    }
}

function Initialize-JavaEnvironment {
    if ($env:JAVA_HOME -and (Test-Path -LiteralPath (Join-Path $env:JAVA_HOME 'bin\java.exe'))) {
        Write-ValidationLine "JAVA_HOME: $env:JAVA_HOME"
    } elseif (Get-Command java.exe -ErrorAction SilentlyContinue) {
        Write-ValidationLine 'JAVA_HOME is unset; using java.exe from PATH.'
    } else {
        $androidStudioJbr = Join-Path $env:ProgramFiles 'Android\Android Studio\jbr'
        if (-not (Test-Path -LiteralPath (Join-Path $androidStudioJbr 'bin\java.exe'))) {
            throw 'No Java runtime found. Set JAVA_HOME or install Android Studio with its bundled JBR.'
        }
        $env:JAVA_HOME = $androidStudioJbr
        Write-ValidationLine "JAVA_HOME discovered: $env:JAVA_HOME"
    }

    if ($env:JAVA_HOME) {
        $javaBin = Join-Path $env:JAVA_HOME 'bin'
        $normalizedJavaBin = $javaBin.TrimEnd('\')
        $pathEntries = @($env:PATH -split ';' | ForEach-Object { $_.Trim().TrimEnd('\') })
        if ($normalizedJavaBin -notin $pathEntries) {
            $env:PATH = if ($env:PATH) { "$javaBin;$env:PATH" } else { $javaBin }
            Write-ValidationLine "Added Java to validation process PATH: $javaBin"
        }
    }

    $resolvedJava = Get-Command java.exe -ErrorAction SilentlyContinue
    if (-not $resolvedJava) {
        throw 'JAVA_HOME was resolved, but java.exe is still unavailable on the validation process PATH.'
    }

    $previousErrorAction = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    & $resolvedJava.Source -version 2>&1 | Out-Null
    $javaExitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorAction
    if ($javaExitCode -ne 0) {
        throw "java.exe could not be executed from the validation process PATH (exit code $javaExitCode)."
    }
    Write-ValidationLine "java.exe resolved for Gradle and pre-commit: $($resolvedJava.Source)"

    if (-not $env:GRADLE_USER_HOME) {
        if (-not $env:USERPROFILE) {
            throw 'USERPROFILE is unavailable. Set GRADLE_USER_HOME to a writable Gradle cache directory.'
        }
        $env:GRADLE_USER_HOME = Join-Path $env:USERPROFILE '.gradle'
    }
    Write-ValidationLine "GRADLE_USER_HOME: $env:GRADLE_USER_HOME"
}

function Invoke-ValidationStep {
    param(
        [string]$Name,
        [scriptblock]$Action
    )

    Write-ValidationLine ''
    Write-ValidationLine "=== $Name ==="
    $timer = [System.Diagnostics.Stopwatch]::StartNew()
    $script:validationStepExitCode = 0
    & $Action
    $exitCode = $script:validationStepExitCode
    $timer.Stop()
    Write-ValidationLine ("Elapsed: {0:c}" -f $timer.Elapsed)
    if ($null -ne $exitCode -and $exitCode -ne 0) {
        Write-ValidationLine "FAILED: $Name (exit code $exitCode)"
        exit $exitCode
    }
    $completedSteps.Add($Name)
}

function Invoke-GradleStep {
    param(
        [string]$Name,
        [string[]]$Arguments
    )

    $displayCommand = '.\gradlew ' + ($Arguments -join ' ')
    Invoke-ValidationStep $Name {
        Write-ValidationLine "Command: $displayCommand"
        $previousErrorAction = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        & $gradleWrapper @Arguments 2>&1 | Write-LoggedOutput
        $script:validationStepExitCode = $LASTEXITCODE
        $ErrorActionPreference = $previousErrorAction
    }
}

function Invoke-PreCommitStep {
    $preCommitCommand = Get-Command pre-commit -ErrorAction SilentlyContinue
    if (-not $preCommitCommand) {
        throw "pre-commit is required for $Level validation but was not found on PATH. Install it once with 'py -m pip install pre-commit' (install Python first if the py launcher is unavailable), then open a new terminal and rerun validation."
    }

    Invoke-ValidationStep 'Repository-wide pre-commit' {
        Write-ValidationLine 'Command: pre-commit run --all-files'
        $previousErrorAction = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        & $preCommitCommand.Source run --all-files 2>&1 | Write-LoggedOutput
        $script:validationStepExitCode = $LASTEXITCODE
        $ErrorActionPreference = $previousErrorAction
        if ($script:validationStepExitCode -ne 0) {
            Write-ValidationLine 'Pre-commit failed and autofix hooks may have modified files. Inspect the working tree before rerunning validation.'
        }
    }
}

try {
    Set-Location -LiteralPath $repoRoot
    Initialize-JavaEnvironment
    Write-ValidationLine "Validation level: $Level"

    if ($Level -in @('Fast', 'Standard') -and $TestFilter.Count -eq 0) {
        throw "-TestFilter is required for $Level validation so targeted tests match the current change."
    }

    $targetedTestArguments = @(':app:testDefaultDebugUnitTest')
    foreach ($filter in $TestFilter) {
        $targetedTestArguments += @('--tests', $filter)
    }

    if ($Level -in @('Standard', 'Full')) {
        Invoke-PreCommitStep
    }

    switch ($Level) {
        'Fast' {
            Invoke-GradleStep 'Targeted JVM tests' $targetedTestArguments
        }
        'Standard' {
            Invoke-GradleStep 'Targeted JVM tests' $targetedTestArguments
            Invoke-GradleStep 'Production Kotlin compile' @(':app:compileDefaultDebugKotlin')
            Invoke-GradleStep 'Acquisition model regression tests' @(
                ':app:testDefaultDebugUnitTest',
                '--tests', '*SeerrAcquisitionTest'
            )
            Invoke-GradleStep 'Acquisition tracker regression tests' @(
                ':app:testDefaultDebugUnitTest',
                '--tests', '*SeerrAcquisitionTrackerTest'
            )
            Invoke-GradleStep 'Seerr pagination regression tests' @(
                ':app:testDefaultDebugUnitTest',
                '--tests', '*SeerrRequestPaginationTest'
            )
            Invoke-GradleStep 'Downloads page regression tests' @(
                ':app:testDefaultDebugUnitTest',
                '--tests', '*DownloadsPageTest'
            )
            Invoke-ValidationStep 'Git whitespace check' {
                Write-ValidationLine 'Command: git diff --check'
                $previousErrorAction = $ErrorActionPreference
                $ErrorActionPreference = 'Continue'
                & git diff --check 2>&1 | Write-LoggedOutput
                $script:validationStepExitCode = $LASTEXITCODE
                $ErrorActionPreference = $previousErrorAction
            }
        }
        'Full' {
            Invoke-GradleStep 'Production Kotlin compile' @(':app:compileDefaultDebugKotlin')
            Invoke-GradleStep 'Full default-debug JVM unit suite' @(':app:testDefaultDebugUnitTest')
            Invoke-GradleStep 'Default-debug APK assembly' @(':app:assembleDefaultDebug')
            Invoke-ValidationStep 'Git whitespace check' {
                Write-ValidationLine 'Command: git diff --check'
                $previousErrorAction = $ErrorActionPreference
                $ErrorActionPreference = 'Continue'
                & git diff --check 2>&1 | Write-LoggedOutput
                $script:validationStepExitCode = $LASTEXITCODE
                $ErrorActionPreference = $previousErrorAction
            }
        }
    }

    $totalTimer.Stop()
    Write-ValidationLine ''
    Write-ValidationLine "SUCCESS: $Level validation completed."
    Write-ValidationLine "Steps: $($completedSteps -join '; ')"
    Write-ValidationLine ("Total elapsed: {0:c}" -f $totalTimer.Elapsed)
    Write-ValidationLine "Complete log: $logPath"
} catch {
    $totalTimer.Stop()
    Write-ValidationLine ''
    Write-ValidationLine "FAILED: $($_.Exception.Message)"
    Write-ValidationLine ("Total elapsed: {0:c}" -f $totalTimer.Elapsed)
    Write-ValidationLine "Complete log: $logPath"
    exit 1
} finally {
    $script:logWriter.Dispose()
    Set-Location -LiteralPath $repoRoot
}
