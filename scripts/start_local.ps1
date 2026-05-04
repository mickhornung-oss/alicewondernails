$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

$RuntimeDir = Join-Path $ProjectRoot "data\runtime"
$PidFile = Join-Path $RuntimeDir "uvicorn.pid"
$ReqStampFile = Join-Path $RuntimeDir "requirements.sha256"
$OutLog = Join-Path $RuntimeDir "uvicorn.out.log"
$ErrLog = Join-Path $RuntimeDir "uvicorn.err.log"
$RequirementsPath = Join-Path $ProjectRoot "backend\requirements.txt"

New-Item -ItemType Directory -Path $RuntimeDir -Force | Out-Null

function Get-RequiredPackages {
    param([string]$Path)

    $packages = @()
    foreach ($line in Get-Content -Path $Path -Encoding UTF8) {
        $trimmed = $line.Trim()
        if ([string]::IsNullOrWhiteSpace($trimmed) -or $trimmed.StartsWith("#")) {
            continue
        }
        if ($trimmed -match "^([A-Za-z0-9_.-]+)") {
            $packages += $Matches[1]
        }
    }
    return $packages
}

function Test-DependenciesInstalled {
    param([string[]]$Packages)

    foreach ($package in $Packages) {
        & python -m pip show $package *> $null
        if ($LASTEXITCODE -ne 0) {
            return $false
        }
    }
    return $true
}

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    throw "Python wurde nicht gefunden. Bitte Python installieren und erneut starten."
}

if (Test-Path $PidFile) {
    $existingPidRaw = (Get-Content $PidFile -Encoding UTF8 | Select-Object -First 1).Trim()
    if ($existingPidRaw -match "^\d+$") {
        $existingPid = [int]$existingPidRaw
        $existingProc = Get-CimInstance Win32_Process -Filter "ProcessId = $existingPid" -ErrorAction SilentlyContinue
        if ($existingProc) {
            $cmdLine = ""
            if ($null -ne $existingProc.CommandLine) {
                $cmdLine = $existingProc.CommandLine.ToLowerInvariant()
            }
            if ($cmdLine.Contains("uvicorn") -and $cmdLine.Contains("backend.app:app")) {
                Write-Host "Server laeuft bereits (PID $existingPid)."
                Write-Host ""
                Write-Host "Landingpage:"
                Write-Host "http://127.0.0.1:8000/public/index.html"
                Write-Host ""
                Write-Host "Admin:"
                Write-Host "http://127.0.0.1:8000/admin/login"
                exit 0
            }
        }
    }
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
}

if (-not (Test-Path $RequirementsPath)) {
    throw "Requirements-Datei nicht gefunden: $RequirementsPath"
}

$requirementsHash = (Get-FileHash -Path $RequirementsPath -Algorithm SHA256).Hash.ToLowerInvariant()
$requiredPackages = Get-RequiredPackages -Path $RequirementsPath
$needsInstall = $true

if ((Test-Path $ReqStampFile) -and ((Get-Content $ReqStampFile -Encoding UTF8 | Select-Object -First 1).Trim().ToLowerInvariant() -eq $requirementsHash)) {
    if (Test-DependenciesInstalled -Packages $requiredPackages) {
        $needsInstall = $false
    }
}

if ($needsInstall) {
    Write-Host "Installiere/aktualisiere lokale Python-Abhaengigkeiten..."
    & python -m pip install -r $RequirementsPath
    if ($LASTEXITCODE -ne 0) {
        throw "Abhaengigkeiten konnten nicht installiert werden."
    }
    Set-Content -Path $ReqStampFile -Value $requirementsHash -Encoding UTF8
} else {
    Write-Host "Abhaengigkeiten sind bereits aktuell."
}

if (Test-Path $OutLog) { Remove-Item $OutLog -Force -ErrorAction SilentlyContinue }
if (Test-Path $ErrLog) { Remove-Item $ErrLog -Force -ErrorAction SilentlyContinue }

$process = Start-Process `
    -FilePath "python" `
    -ArgumentList @("-m", "uvicorn", "backend.app:app", "--host", "127.0.0.1", "--port", "8000") `
    -WorkingDirectory $ProjectRoot `
    -PassThru `
    -WindowStyle Hidden `
    -RedirectStandardOutput $OutLog `
    -RedirectStandardError $ErrLog

$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Milliseconds 500
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get -TimeoutSec 3
        if ($health.status -eq "ok") {
            $ready = $true
            break
        }
    } catch {
        # waiting for startup
    }
}

if (-not $ready) {
    if (-not $process.HasExited) {
        Stop-Process -Id $process.Id -ErrorAction SilentlyContinue
    }
    throw "Serverstart fehlgeschlagen. Siehe Logs: $OutLog und $ErrLog"
}

Set-Content -Path $PidFile -Value $process.Id -Encoding UTF8

Write-Host "FastAPI lokal gestartet (PID $($process.Id))."
Write-Host ""
Write-Host "Landingpage:"
Write-Host "http://127.0.0.1:8000/public/index.html"
Write-Host ""
Write-Host "Admin:"
Write-Host "http://127.0.0.1:8000/admin/login"
Write-Host ""
Write-Host "Logs:"
Write-Host $OutLog
Write-Host $ErrLog
