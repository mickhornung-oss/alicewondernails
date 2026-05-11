param()

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$repoRoot = Resolve-Path (Join-Path $projectRoot '..')
$envPath = Join-Path $repoRoot '.env'
$examplePath = Join-Path $repoRoot 'backend\.env.example'

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

$dotenv = @{}
$localValues = Read-DotEnvFile -Path $envPath
foreach ($key in $localValues.Keys) {
    $dotenv[$key] = $localValues[$key]
}

$exampleValues = Read-DotEnvFile -Path $examplePath
foreach ($key in $exampleValues.Keys) {
    if (-not $dotenv.ContainsKey($key)) {
        $dotenv[$key] = $exampleValues[$key]
    }
}

$pgHost = if ($dotenv.ContainsKey('POSTGRES_HOST')) { $dotenv['POSTGRES_HOST'] } else { 'localhost' }
$pgPort = if ($dotenv.ContainsKey('POSTGRES_PORT')) { [int]$dotenv['POSTGRES_PORT'] } else { 5432 }
$pgDb = if ($dotenv.ContainsKey('POSTGRES_DB')) { $dotenv['POSTGRES_DB'] } else { 'alice_wonder_nails' }
$pgUser = if ($dotenv.ContainsKey('POSTGRES_USER')) { $dotenv['POSTGRES_USER'] } else { 'alice_local' }
$pgPassword = if ($dotenv.ContainsKey('POSTGRES_PASSWORD')) { $dotenv['POSTGRES_PASSWORD'] } else { '' }

Write-Host "PostgreSQL Ziel: Datenbank='$pgDb', Benutzer='$pgUser', Host='$pgHost', Port=$pgPort"
if (-not $pgPassword) {
    Write-Error 'POSTGRES_PASSWORD ist in .env nicht gesetzt. Bitte .env anpassen.'
    exit 1
}
if ($pgPassword -eq 'change-me') {
    Write-Error 'POSTGRES_PASSWORD ist noch der Platzhalterwert. Bitte in der lokalen .env einen lokalen Entwicklungswert setzen.'
    exit 1
}

$adminUser = Read-Host 'PostgreSQL-Admin-Benutzername (Standard: postgres)'
if (-not $adminUser) { $adminUser = 'postgres' }
$adminPasswordSecure = Read-Host 'PostgreSQL-Admin-Passwort' -AsSecureString
$adminPassword = [System.Net.NetworkCredential]::new('', $adminPasswordSecure).Password
if (-not $adminPassword) {
    Write-Error 'Kein PostgreSQL-Admin-Passwort eingegeben. In nicht-interaktiven Umgebungen muss das Setup manuell in einer PowerShell-Konsole gestartet werden.'
    exit 1
}

$python = Join-Path $repoRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    $python = Get-Command python -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
}
if (-not $python) {
    Write-Error 'Python wurde nicht gefunden. Bitte erstellen Sie die .venv oder installieren Sie Python im PATH.'
    exit 1
}

$env:PGHOST = $pgHost
$env:PGPORT = $pgPort
$env:PGDATABASE = $pgDb
$env:PGUSER = $pgUser
$env:PGPASSWORD = $pgPassword
$env:PGADMINUSER = $adminUser
$env:PGADMINPASSWORD = $adminPassword

$pythonScript = @'
import os
import sys

try:
    import psycopg
    from psycopg import sql
except Exception as exc:
    print('PYTHON_IMPORT_ERROR', type(exc).__name__)
    sys.exit(2)

host = os.environ['PGHOST']
port = int(os.environ['PGPORT'])
dbname = os.environ['PGDATABASE']
pguser = os.environ['PGUSER']
pgpassword = os.environ['PGPASSWORD']
adminuser = os.environ['PGADMINUSER']
adminpassword = os.environ['PGADMINPASSWORD']

try:
    conn = psycopg.connect(
        host=host,
        port=port,
        dbname='postgres',
        user=adminuser,
        password=adminpassword,
        connect_timeout=10,
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute('SELECT 1 FROM pg_roles WHERE rolname = %s', (pguser,))
    if cur.fetchone() is None:
        cur.execute(
            sql.SQL('CREATE ROLE {} WITH LOGIN PASSWORD {}').format(
                sql.Identifier(pguser),
                sql.Literal(pgpassword),
            )
        )
    else:
        cur.execute(
            sql.SQL('ALTER ROLE {} WITH LOGIN PASSWORD {}').format(
                sql.Identifier(pguser),
                sql.Literal(pgpassword),
            )
        )

    cur.execute('SELECT 1 FROM pg_database WHERE datname = %s', (dbname,))
    if cur.fetchone() is None:
        cur.execute(
            sql.SQL('CREATE DATABASE {} OWNER {}').format(
                sql.Identifier(dbname),
                sql.Identifier(pguser),
            )
        )
    else:
        cur.execute(
            sql.SQL('ALTER DATABASE {} OWNER TO {}').format(
                sql.Identifier(dbname),
                sql.Identifier(pguser),
            )
        )

    cur.execute(
        sql.SQL('GRANT ALL PRIVILEGES ON DATABASE {} TO {}').format(
            sql.Identifier(dbname),
            sql.Identifier(pguser),
        )
    )
    cur.close()
    conn.close()

    target = psycopg.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=adminuser,
        password=adminpassword,
        connect_timeout=10,
    )
    target.autocommit = True
    target_cur = target.cursor()
    target_cur.execute(sql.SQL('ALTER SCHEMA public OWNER TO {}').format(sql.Identifier(pguser)))
    target_cur.execute(sql.SQL('GRANT USAGE, CREATE ON SCHEMA public TO {}').format(sql.Identifier(pguser)))
    target_cur.execute(sql.SQL('GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {}').format(sql.Identifier(pguser)))
    target_cur.execute(sql.SQL('GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {}').format(sql.Identifier(pguser)))
    target_cur.close()
    target.close()
except Exception as exc:
    print('POSTGRES_SETUP_ERROR', type(exc).__name__, str(exc).encode('unicode_escape').decode('ascii'))
    sys.exit(1)

print('PYTHON_OK')
'@

Write-Host 'Richte PostgreSQL-Rolle und -Datenbank mit Python/psycopg ein...' -ForegroundColor Cyan
& $python -c $pythonScript
$pythonExit = $LASTEXITCODE
Remove-Item Env:PGPASSWORD, Env:PGADMINPASSWORD, Env:PGADMINUSER -ErrorAction SilentlyContinue
if ($pythonExit -ne 0) {
    Write-Error "Die PostgreSQL-Einrichtung mit Python ist fehlgeschlagen (Exit-Code $pythonExit)."
    exit $pythonExit
}

Write-Host 'PostgreSQL-Rolle und -Datenbank wurden mit Python/psycopg vorbereitet.' -ForegroundColor Green
Write-Host 'Fuehren Sie anschliessend scripts\check_postgres.ps1 aus, um die Verbindung zu pruefen.' -ForegroundColor Cyan
