$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

$PidFile = Join-Path $ProjectRoot "data\runtime\uvicorn.pid"

function Stop-ProjectProcess {
    param([int]$ProcessId)

    $proc = Get-CimInstance Win32_Process -Filter "ProcessId = $ProcessId" -ErrorAction SilentlyContinue
    if (-not $proc) {
        return $false
    }

    $cmdLine = ""
    if ($null -ne $proc.CommandLine) {
        $cmdLine = $proc.CommandLine.ToLowerInvariant()
    }

    if (-not ($cmdLine.Contains("uvicorn") -and $cmdLine.Contains("backend.app:app"))) {
        Write-Host "PID $ProcessId gehoert nicht zum lokalen Alice-Wonder-Backend. Prozess wird nicht beendet."
        return $false
    }

    Stop-Process -Id $ProcessId -ErrorAction Stop
    for ($i = 0; $i -lt 20; $i++) {
        Start-Sleep -Milliseconds 200
        if (-not (Get-Process -Id $ProcessId -ErrorAction SilentlyContinue)) {
            break
        }
    }
    return $true
}

if (-not (Test-Path $PidFile)) {
    Write-Host "Kein PID-File gefunden. Nichts zu stoppen."
    exit 0
}

$pidRaw = (Get-Content $PidFile -Encoding UTF8 | Select-Object -First 1).Trim()
if (-not ($pidRaw -match "^\d+$")) {
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    Write-Host "PID-File war ungueltig und wurde entfernt."
    exit 0
}

$processId = [int]$pidRaw
if (Stop-ProjectProcess -ProcessId $processId) {
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    Write-Host "Lokaler FastAPI-Server wurde beendet (PID $processId)."
    exit 0
}

Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
Write-Host "Kein passender laufender Prozess gefunden. PID-File wurde bereinigt."
