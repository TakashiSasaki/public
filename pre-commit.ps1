$ErrorActionPreference = "Stop"

$manifestPath = Join-Path $PSScriptRoot "..\\manifest.webmanifest"

if (-not (Test-Path $manifestPath)) {
  Write-Error "pre-commit: manifest not found: $manifestPath"
}

$manifestText = Get-Content -Raw -Encoding UTF8 $manifestPath
$versionPattern = '"version"\s*:\s*"(?<major>\d+)\.(?<minor>\d+)\.(?<patch>\d+)"'
$match = [regex]::Match($manifestText, $versionPattern)

if (-not $match.Success) {
  Write-Error "pre-commit: version field (x.y.z) not found in manifest.webmanifest"
}

$major = [int]$match.Groups["major"].Value
$minor = [int]$match.Groups["minor"].Value
$patch = [int]$match.Groups["patch"].Value + 1
$nextVersion = "$major.$minor.$patch"

$updatedText = [regex]::Replace(
  $manifestText,
  $versionPattern,
  ('"version": "{0}"' -f $nextVersion),
  1
)

Set-Content -Path $manifestPath -Value $updatedText -Encoding UTF8NoBOM
git add -- $manifestPath

Write-Host "pre-commit: manifest version bumped to $nextVersion"
