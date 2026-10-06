<#
Baut pro Skill eine ZIP-Datei in dist\ zum Hochladen in claude.ai (Customize > Skills).
Der Skill-Ordner liegt jeweils als oberster Eintrag im ZIP. Pfade im ZIP verwenden "/",
damit der Upload auch mit aelteren PowerShell-Versionen funktioniert.
#>
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression, System.IO.Compression.FileSystem

$repoRoot = Split-Path -Parent $PSScriptRoot
$dist = Join-Path $repoRoot 'dist'

if (Test-Path -LiteralPath $dist) { Remove-Item -Recurse -Force -LiteralPath $dist }
New-Item -ItemType Directory -Path $dist | Out-Null

Get-ChildItem -Directory -Path (Join-Path $repoRoot 'plugins\*\skills\*') | ForEach-Object {
    $skillsDir = $_.Parent.FullName
    $zipPath = Join-Path $dist "$($_.Name).zip"
    $zip = [System.IO.Compression.ZipFile]::Open($zipPath, 'Create')
    try {
        Get-ChildItem -Recurse -File -LiteralPath $_.FullName | ForEach-Object {
            $entry = $_.FullName.Substring($skillsDir.Length + 1) -replace '\\', '/'
            [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $_.FullName, $entry) | Out-Null
        }
    } finally {
        $zip.Dispose()
    }
    Write-Host "  + dist\$($_.Name).zip"
}
