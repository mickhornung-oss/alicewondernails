$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

$BaseUrl = "http://127.0.0.1:8000"
$DbPath = Join-Path $ProjectRoot "data\db\alicewonder_v1.sqlite"

$results = @()

function Add-Result {
    param(
        [string]$Name,
        [bool]$Ok,
        [string]$Details = ""
    )
    $script:results += [pscustomobject]@{
        Name = $Name
        Ok = $Ok
        Details = $Details
    }
}

function Invoke-HeadlessGet {
    param([string]$Url)
    return Invoke-WebRequest -Uri $Url -Method Get -UseBasicParsing -TimeoutSec 8
}

try {
    $health = Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get -TimeoutSec 8
    Add-Result -Name "/health erreichbar" -Ok ($health.status -eq "ok") -Details ($health.status | Out-String).Trim()
} catch {
    Add-Result -Name "/health erreichbar" -Ok $false -Details $_.Exception.Message
}

try {
    $landing = Invoke-HeadlessGet -Url "$BaseUrl/public/index.html"
    Add-Result -Name "Landingpage erreichbar" -Ok ($landing.StatusCode -eq 200) -Details ("HTTP " + $landing.StatusCode)
} catch {
    Add-Result -Name "Landingpage erreichbar" -Ok $false -Details $_.Exception.Message
}

try {
    $adminLogin = Invoke-HeadlessGet -Url "$BaseUrl/admin/login"
    $loginHtml = $adminLogin.Content
    $hasAdminCssRef = $loginHtml -match "/static/css/admin.css"
    Add-Result -Name "Admin-Login erreichbar" -Ok ($adminLogin.StatusCode -eq 200) -Details ("HTTP " + $adminLogin.StatusCode)
    Add-Result -Name "Admin-CSS im Login referenziert" -Ok $hasAdminCssRef -Details ""

    $adminCss = Invoke-HeadlessGet -Url "$BaseUrl/static/css/admin.css"
    Add-Result -Name "Admin-CSS ladbar" -Ok ($adminCss.StatusCode -eq 200) -Details ("HTTP " + $adminCss.StatusCode)
} catch {
    Add-Result -Name "Admin-Login/CSS" -Ok $false -Details $_.Exception.Message
}

$email = "localtest_{0}@example.local" -f ([DateTime]::UtcNow.ToString("yyyyMMddHHmmss"))
$payload = @{
    email = $email
    privacy_accepted = $true
    interest = "Press-On-Anfrage"
    one_time_notice_accepted = $false
} | ConvertTo-Json

try {
    $leadResponse = Invoke-RestMethod -Uri "$BaseUrl/api/lead" -Method Post -ContentType "application/json" -Body $payload -TimeoutSec 10
    Add-Result -Name "Test-Lead via API" -Ok ($leadResponse.success -eq $true) -Details ("lead_id=" + $leadResponse.lead_id)
} catch {
    Add-Result -Name "Test-Lead via API" -Ok $false -Details $_.Exception.Message
}

if (Test-Path $DbPath) {
    $pythonCheck = "import sqlite3,sys; conn=sqlite3.connect(sys.argv[1]); cur=conn.execute('SELECT COUNT(*) FROM leads WHERE email = ?', (sys.argv[2],)); print(cur.fetchone()[0]); conn.close()"
    $countRaw = (& python -c $pythonCheck $DbPath $email | Out-String).Trim()
    $count = 0
    [void][int]::TryParse($countRaw, [ref]$count)
    Add-Result -Name "Test-Lead in SQLite sichtbar" -Ok ($count -ge 1) -Details ("Treffer=" + $count)
} else {
    Add-Result -Name "SQLite-Datei vorhanden" -Ok $false -Details $DbPath
}

Write-Host ""
Write-Host "=== Local Test Report ==="
$allOk = $true
foreach ($result in $results) {
    $prefix = if ($result.Ok) { "[OK] " } else { "[FAIL] " }
    if (-not $result.Ok) { $allOk = $false }

    if ([string]::IsNullOrWhiteSpace($result.Details)) {
        Write-Host ($prefix + $result.Name)
    } else {
        Write-Host ($prefix + $result.Name + " - " + $result.Details)
    }
}

Write-Host ""
if ($allOk) {
    Write-Host "Ergebnis: GRUEN - lokale Basispruefungen erfolgreich."
    exit 0
}

Write-Host "Ergebnis: GELB/ROT - mindestens ein Check ist fehlgeschlagen."
exit 1
