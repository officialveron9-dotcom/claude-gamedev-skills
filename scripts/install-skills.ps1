<#
Kopiert die Skills in den .claude\skills-Ordner eines Projekts (oder nach ~\.claude\skills).
Plugins: unreal-engine, unreal-engine-reference, fivem, brotato, blender-modeling, general-dev, gamedev-general, web-dev (Ordner unter plugins\).
Ohne -Plugin werden alle installiert. Gleichnamige Skills im Ziel werden ueberschrieben.

Beispiele:
  .\scripts\install-skills.ps1 -Project C:\Dev\MeinSpiel -Plugin unreal-engine, unreal-engine-reference, general-dev
  .\scripts\install-skills.ps1 -Project C:\FiveM\server-data -Plugin fivem, general-dev
  .\scripts\install-skills.ps1 -Personal
#>
param(
    [string]$Project,
    [switch]$Personal,
    [string[]]$Plugin = @('all')
)
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot

if ($Personal) {
    $target = Join-Path $HOME '.claude\skills'
} elseif ($Project) {
    if (-not (Test-Path -LiteralPath $Project -PathType Container)) {
        throw "Projektordner nicht gefunden: $Project"
    }
    $target = Join-Path (Resolve-Path -LiteralPath $Project).Path '.claude\skills'
} else {
    throw 'Bitte -Project <Ordner> oder -Personal angeben.'
}

if ($Plugin -contains 'all') {
    $plugins = Get-ChildItem -Directory -LiteralPath (Join-Path $repoRoot 'plugins') | ForEach-Object { $_.Name }
} else {
    $plugins = $Plugin
    foreach ($p in $plugins) {
        if (-not (Test-Path -LiteralPath (Join-Path $repoRoot "plugins\$p\skills") -PathType Container)) {
            throw "Unbekanntes Plugin: $p"
        }
    }
}

New-Item -ItemType Directory -Force -Path $target | Out-Null
foreach ($p in $plugins) {
    Get-ChildItem -Directory -LiteralPath (Join-Path $repoRoot "plugins\$p\skills") | ForEach-Object {
        $dest = Join-Path $target $_.Name
        if (Test-Path -LiteralPath $dest) { Remove-Item -Recurse -Force -LiteralPath $dest }
        Copy-Item -Recurse -LiteralPath $_.FullName -Destination $dest
        Write-Host "  + $($_.Name)"
    }
}
Write-Host "Skills installiert nach: $target"
