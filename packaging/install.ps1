[CmdletBinding()]
param(
    [string]$Version = $(if ($env:LEGALFLOW_VERSION) { $env:LEGALFLOW_VERSION } else { "0.1.0" }),
    [switch]$SkipSetup
)

# AI LegalFlow MX Windows bootstrap. It performs no account login and never
# prompts for or reads a password, token, passkey or MFA code.
$ErrorActionPreference = "Stop"
$Repository = "hassanvfx/legalflow-mx"
$DocsBase = "https://hassanvfx.github.io/legalflow-mx/setup"
$ReleaseBase = if ($env:LEGALFLOW_RELEASE_BASE) { $env:LEGALFLOW_RELEASE_BASE } else { "https://github.com/$Repository/releases/download/v$Version" }
$InstallRoot = Join-Path $env:LOCALAPPDATA "AI-LegalFlow-MX"
$ReleaseRoot = Join-Path $InstallRoot (Join-Path "releases" $Version)
$BinRoot = Join-Path $InstallRoot "bin"

function Info([string]$Message) { Write-Host "[AI LegalFlow MX] $Message" -ForegroundColor Cyan }
function Stop-Install([string]$Message, [string]$Guide) {
    Write-Error "[AI LegalFlow MX] $Message"
    if ($Guide) { Write-Host "Guía: $Guide" -ForegroundColor Yellow }
    exit 1
}

Info "Hassan Uriostegui y Aurora Cotne"
Info "Este instalador es reanudable y no solicita credenciales de GitHub."

if ($PSVersionTable.PSVersion.Major -lt 5) {
    Stop-Install "Se necesita Windows PowerShell 5.1 o posterior." "$DocsBase/windows.html"
}

$Architecture = [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture.ToString()
if ($Architecture -notin @("X64", "Arm64")) {
    Stop-Install "La arquitectura $Architecture aún no tiene un bundle compatible." "$DocsBase/windows.html"
}

$Python = Get-Command python -ErrorAction SilentlyContinue
if (-not $Python) { $Python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $Python) {
    Stop-Install "Python 3 es necesario hasta que publiquemos un bundle autónomo." "$DocsBase/python.html"
}
$PythonLauncher = if ($Python.Name -match '^py(\.exe)?$') { "py" } else { "python" }

try {
    [Net.Dns]::GetHostEntry("github.com") | Out-Null
} catch {
    Stop-Install "No se pudo resolver github.com. Revisa red, DNS o proxy y vuelve a ejecutar este mismo comando." "$DocsBase/network.html"
}

try {
    $parent = Split-Path -Parent $InstallRoot
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    $probe = Join-Path $parent ".ai-legalflow-mx-write-probe"
    [IO.File]::WriteAllText($probe, "ok")
    Remove-Item -LiteralPath $probe -Force
} catch {
    Stop-Install "No hay permiso para escribir en $parent. No uses una cuenta administradora: elige una cuenta o carpeta escribible." "$DocsBase/permissions.html"
}

$drive = Get-Item $InstallRoot -ErrorAction SilentlyContinue
if (-not $drive) { $drive = Get-Item (Split-Path -Qualifier $InstallRoot) }
if ($drive.PSDrive.Free -lt 250MB) {
    Stop-Install "Se necesitan al menos 250 MB libres para descargar y extraer AI LegalFlow MX." "$DocsBase/windows.html"
}

$validRelease = Test-Path (Join-Path $ReleaseRoot "src\legalflow\cli.py")
if (-not $validRelease) {
    $TempRoot = Join-Path ([IO.Path]::GetTempPath()) ("ai-legalflow-mx-" + [Guid]::NewGuid().ToString("N"))
    $Archive = Join-Path $TempRoot "legalflow-mx-$Version.tar.gz"
    $Checksum = Join-Path $TempRoot "legalflow-mx-$Version.sha256"
    $Staging = Join-Path $TempRoot "release"
    try {
        New-Item -ItemType Directory -Force -Path $TempRoot, $Staging | Out-Null
        Info "Descargando la release verificada $Version."
        Invoke-WebRequest -UseBasicParsing -Uri "$ReleaseBase/legalflow-mx-$Version.tar.gz" -OutFile $Archive
        Invoke-WebRequest -UseBasicParsing -Uri "$ReleaseBase/legalflow-mx-$Version.sha256" -OutFile $Checksum
        $expected = ((Get-Content -LiteralPath $Checksum -Raw).Trim() -split '\s+')[0].ToLowerInvariant()
        $actual = (Get-FileHash -LiteralPath $Archive -Algorithm SHA256).Hash.ToLowerInvariant()
        if (-not $expected -or $expected -ne $actual) {
            throw "La huella SHA-256 no coincide"
        }
        $tar = Get-Command tar -ErrorAction SilentlyContinue
        if (-not $tar) { throw "Windows no tiene la herramienta tar requerida para extraer la release" }
        & $tar.Source -xzf $Archive -C $Staging --strip-components=1
        if ($LASTEXITCODE -ne 0 -or -not (Test-Path (Join-Path $Staging "src\legalflow\cli.py"))) {
            throw "La release no contiene la estructura esperada"
        }
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $ReleaseRoot) | Out-Null
        Move-Item -LiteralPath $Staging -Destination $ReleaseRoot
    } catch {
        Stop-Install "La descarga o verificación falló: $($_.Exception.Message). No se instaló ningún archivo de producto." "$DocsBase/network.html"
    } finally {
        if (Test-Path $TempRoot) { Remove-Item -LiteralPath $TempRoot -Recurse -Force -ErrorAction SilentlyContinue }
    }
} else {
    Info "La release $Version ya está instalada y es válida. Se conserva sin cambios."
}

New-Item -ItemType Directory -Force -Path $BinRoot | Out-Null
$Launcher = Join-Path $BinRoot "legalflow.cmd"
$LauncherText = "@echo off`r`nset \"PYTHONPATH=$ReleaseRoot\src;%PYTHONPATH%\"`r`n$PythonLauncher -m legalflow.cli %*`r`n"
[IO.File]::WriteAllText($Launcher, $LauncherText, [Text.UTF8Encoding]::new($false))

$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (($UserPath -split ';') -notcontains $BinRoot) {
    [Environment]::SetEnvironmentVariable("Path", (($UserPath.TrimEnd(';') + ";" + $BinRoot).TrimStart(';')), "User")
    $env:Path = "$BinRoot;$env:Path"
    Info "Se añadió el comando legalflow para tu usuario. Abre una nueva ventana de PowerShell después de esta sesión."
}

if (-not $SkipSetup) {
    Info "Ejecutando el diagnóstico reanudable."
    & $PythonLauncher -m legalflow.cli setup --resume
    exit $LASTEXITCODE
}

Info "Instalación terminada. Ejecuta: legalflow setup --resume"
