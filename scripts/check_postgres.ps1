param()

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$repoRoot = Resolve-Path (Join-Path $projectRoot '..')
$venvPython = Join-Path $repoRoot '.venv\Scripts\python.exe'
$python = if (Test-Path $venvPython) { $venvPython } else { Get-Command python -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source }

if (-not $python) {
    Write-Error 'Kein Python gefunden. Installieren Sie Python oder erstellen Sie zuerst die .venv-Umgebung.'
    exit 1
}

function Read-DotEnvFile {
    param([string]$Path)

    $values = @{}
    if (-not (Test-Path $Path)) {
        return $values
    }

    Get-Content $Path | ForEach-Object {
        if ($_ -match '^\s*([^#=]+?)\s*=\s*(.*)$') {
            $values[$matches[1].Trim()] = $matches[2].Trim()
        }
    }
    return $values
}

$envPath = Join-Path $repoRoot '.env'
$examplePath = Join-Path $repoRoot 'backend\.env.example'
$dotenv = @{}

if (Test-Path $envPath) {
    $localValues = Read-DotEnvFile -Path $envPath
    foreach ($key in $localValues.Keys) {
        $dotenv[$key] = $localValues[$key]
    }
} else {
    Write-Warning '.env nicht gefunden. Die Pruefung verwendet nur Fallback-Werte aus backend\.env.example.'
}

$missingPostgresKeys = @()
foreach ($key in @('POSTGRES_HOST','POSTGRES_PORT','POSTGRES_DB','POSTGRES_USER','POSTGRES_PASSWORD')) {
    if (-not $dotenv.ContainsKey($key)) { $missingPostgresKeys += $key }
}
if ($missingPostgresKeys.Count -gt 0 -and (Test-Path $examplePath)) {
    Write-Warning "Lokale .env fehlt Postgres-Schluessel: $($missingPostgresKeys -join ', '). Fallback auf backend\.env.example."
    $exampleValues = Read-DotEnvFile -Path $examplePath
    foreach ($key in $exampleValues.Keys) {
        if (-not $dotenv.ContainsKey($key)) {
            $dotenv[$key] = $exampleValues[$key]
        }
    }
}

$pgHost = if ($dotenv.ContainsKey('POSTGRES_HOST')) { $dotenv['POSTGRES_HOST'] } else { 'localhost' }
$pgPort = if ($dotenv.ContainsKey('POSTGRES_PORT')) { [int]$dotenv['POSTGRES_PORT'] } else { 5432 }
$pgDb = if ($dotenv.ContainsKey('POSTGRES_DB')) { $dotenv['POSTGRES_DB'] } else { 'alice_wonder_nails' }
$pgUser = if ($dotenv.ContainsKey('POSTGRES_USER')) { $dotenv['POSTGRES_USER'] } else { 'alice_local' }

Write-Host "PostgreSQL Host: $pgHost"
Write-Host "PostgreSQL Port: $pgPort"
Write-Host "PostgreSQL Datenbank: $pgDb"
Write-Host "PostgreSQL User: $pgUser"

Write-Host 'Pruefe Postgres-Port...' -ForegroundColor Cyan
$portTest = Test-NetConnection -ComputerName $pgHost -Port $pgPort -WarningAction SilentlyContinue
if ($portTest.TcpTestSucceeded) {
    Write-Host 'Postgres-Port ist erreichbar.' -ForegroundColor Green
} else {
    Write-Error 'Postgres-Port ist nicht erreichbar. Bitte PostgreSQL-Server und Firewall pruefen.'
    exit 1
}

$managePath = Join-Path $repoRoot 'backend\manage.py'
if (-not (Test-Path $managePath)) {
    Write-Error 'backend\manage.py wurde nicht gefunden.'
    exit 1
}

Write-Host 'Pruefe DB-Login mit psycopg...' -ForegroundColor Cyan
$connectionScript = @"
import os
import sys
from pathlib import Path

try:
    import psycopg
except Exception as exc:
    print('PYTHON_IMPORT_ERROR', type(exc).__name__)
    sys.exit(2)

root = Path(r'$($repoRoot.Path)')
params = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'alice_wonder_nails',
    'user': 'alice_local',
    'password': None,
}

def read_values(path):
    values = {}
    if not path.exists():
        return values
    for line in path.read_text().splitlines():
        if '=' in line and not line.strip().startswith('#'):
            key, value = line.split('=', 1)
            values[key.strip()] = value.strip()
    return values

values = read_values(root / '.env')
fallback = read_values(root / 'backend' / '.env.example')
for key, value in fallback.items():
    values.setdefault(key, value)

mapping = {
    'POSTGRES_HOST': 'host',
    'POSTGRES_PORT': 'port',
    'POSTGRES_DB': 'dbname',
    'POSTGRES_USER': 'user',
    'POSTGRES_PASSWORD': 'password',
}
for env_key, param_key in mapping.items():
    if env_key in values:
        params[param_key] = int(values[env_key]) if param_key == 'port' else values[env_key]

if not params['password'] or params['password'] == 'change-me':
    print('DB_CONNECTION_ERROR MissingOrPlaceholderPassword')
    sys.exit(1)

try:
    conn = psycopg.connect(
        host=params['host'],
        port=params['port'],
        dbname=params['dbname'],
        user=params['user'],
        password=params['password'],
        connect_timeout=5,
    )
    cur = conn.cursor()
    cur.execute('select 1;')
    cur.fetchone()
    conn.close()
except Exception as exc:
    print('DB_CONNECTION_ERROR', type(exc).__name__, str(exc).encode('unicode_escape').decode('ascii'))
    sys.exit(1)

print('DB_CONNECTION_OK')
"@

& $python -c $connectionScript
if ($LASTEXITCODE -ne 0) {
    Write-Error 'PostgreSQL-Verbindungstest mit psycopg ist fehlgeschlagen.'
    exit 1
}
Write-Host 'DB-Login mit Zieluser erfolgreich.' -ForegroundColor Green

Write-Host 'Pruefe Django DB-Zugriff...' -ForegroundColor Cyan
$djangoDbScript = @"
import os
import sys
from pathlib import Path

root = Path(r'$($repoRoot.Path)')
sys.path.insert(0, str(root / 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

try:
    import django
    django.setup()
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute('select 1;')
        cursor.fetchone()
except Exception as exc:
    print('DJANGO_DB_ERROR', type(exc).__name__, str(exc).encode('unicode_escape').decode('ascii'))
    sys.exit(1)

print('DJANGO_DB_OK')
"@

& $python -c $djangoDbScript
if ($LASTEXITCODE -ne 0) {
    Write-Error 'Django DB-Zugriff ist fehlgeschlagen.'
    exit 1
}
Write-Host 'Django DB-Zugriff erfolgreich.' -ForegroundColor Green

Write-Host 'Pruefe Django manage.py check...' -ForegroundColor Cyan
& $python $managePath check
$manageExit = $LASTEXITCODE
if ($manageExit -ne 0) {
    Write-Error "Django manage.py check ist fehlgeschlagen mit Exit-Code $manageExit."
    exit $manageExit
}

Write-Host 'Django manage.py check erfolgreich.' -ForegroundColor Green
Write-Host 'PostgreSQL-Pruefung abgeschlossen.' -ForegroundColor Green
